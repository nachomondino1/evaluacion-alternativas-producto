import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.request import urlopen
import random
from time import sleep
from utils.web_scraping.crawler import Crawler
from MercadoLibreApi import MercadoLibreApi


class MercadoLibreCrawler(Crawler):
    """ A tool to extract information from Mercado Libre"""

    def __init__(self, driver, busqueda):
        self.driver = driver
        self.busqueda = busqueda


    def getHomePageUrl(self, busqueda):
        # Ingreso a URL semilla (en este caso, la pagina principal de mercado libre)
        a = busqueda.replace(" ", "-")
        b = busqueda.replace(" ", "%20")
        url = 'https://listado.mercadolibre.com.ar/' + a + "#D[A:" + b + "]"
        return url


    def validacionBusqueda(self, busqueda):
        """
        Validar la busqueda para que esta no sea muy amplia (hay un costo computacional).
        Si la busqueda es "acotada" Mercado Libre asocia la busqueda del usuario con una categoria de producto
        y el seria muy alto para una busqueda sin sentido

        :param driver: web browser automatico
        :param busqueda: Producto que quiere comprar el cliente
        :return: True si mercadolibre encuentra categoria a la busqueda o False en caso contrario
        """

        # Ingreso a URL semilla (en este caso, la pagina principal de mercado libre)
        a = busqueda.replace(" ", "-")
        b = busqueda.replace(" ", "%20")
        url = 'https://listado.mercadolibre.com.ar/' + a + "#D[A:" + b + "]"

        # Podria implementar beatiful soup para acceder el codigo html de la pagina sin que se me abra el Chrome...
        html = urlopen(url)
        bs = BeautifulSoup(html, 'html.parser')
        resp = bs.find('div', {'class': "ui-search-breadcrumb"}).find("meta", {"content": "2"}) #Antes buscaba solo si habia hasta el tag "ol" pero habia BUSQUEDAS QUE SON DE UNA SUBCATEGORIA Y EN LA HOMEPAGE SOLO APARECE SU CATEGORIA ppal y no la subcategoria... POR EJ:'comida preparada'  Lo podria solucionar en validacionBusqueda() buscando no solo el tag ol sino buscando el segundo tag li

        return resp


    def getCategoriaBusqueda(self, home_page_url):

        # Podria implementar beatiful soup para acceder el codigo html de la pagina sin que se me abra el Chrome...
        html = urlopen(home_page_url)
        bs = BeautifulSoup(html, 'html.parser')
        catergoria_busqueda = bs.find('div', {'class': "ui-search-breadcrumb"}).find('meta', {'content': "2"}).find_previous_sibling().attrs['title']
        return catergoria_busqueda


    def getPublicationsUrl(self, driver):
        # Podria intentar que sirva no solo para mercadolibre.com sino tambien para otras como amazon.com o Ebay.com
        # Nota: estan en un div#class=ui-search-result__image
        links = driver.find_elements(By.XPATH, '//div[@class="ui-search-result__image"]/a')
        links_pagina = []

        for link in links:
            links_pagina.append(link.get_attribute("href"))
        return links_pagina


    def getPaginacionUrl(self, driver):
        # Ubico link de siguiente pagina
        link_paginacion = driver.find_element_by_xpath(
            './/li[@class="andes-pagination__button andes-pagination__button--next"]/a').get_attribute('href')
        return link_paginacion


    def ClickVerTodasLasOpiniones(self, driver):
        # Busco link de "Ver todas las opiniones" y hago click
        # El boton "ver todas las opiniones" esta dentro de un tag unico div#class=ui-pdp-reviews__actions__container

        try:
            link_opiniones = driver.find_element(By.XPATH,'//div[@class="ui-pdp-reviews__actions__container"]/a').get_attribute("href")
            driver.get(link_opiniones)
            resp = True
        except:
            resp = None

        return resp


    def getPublicacionOpinions(self, driver):
        """
        Extrae opiniones de una publicacion

        :return: Dataframe cuya unidad de analisis es la opinion y sus columnas son titulo, content, rate, fecha, likes, dislikes
        """
        title, content, rate, likes, dislikes = [], [], [], [], []

        # Extraigo opiniones
        # Obtengo los XPATH donde se ubican los parrafos de cada una de las opiniones
        # Por opinion (recorda que cada publicacion tiene varias opiniones) Ojo que por ahi va solo al primer article y no a todos...
        opiniones_publicacion = driver.find_elements(By.XPATH, '//div[@class="infinite-scroll-component "]/article')

        for opinion in opiniones_publicacion:

            # Extraigo Title
            try:
                title.append(opinion.find_element_by_xpath('.//h2').text)
            except:
                title.append(None)

            # Extraigo Content
            try:
                content.append(opinion.find_element_by_xpath('.//p').text)
            except:
                content.append(None)

            # Extraigo Rate
            try:
                n = 0
                stars = opinion.find_elements_by_class_name("ui-review-view__comments__review-comment__rating__star")
                # print(stars)

                for star in stars:
                    if star.find_element_by_tag_name("path").get_attribute("fill") == "#3483FA":
                        n += 1
                    else:
                        break
                rate.append(n)
            except:
                rate.append(None)

            #Extraigo Likes y dislikes
            try:
                likes.append(int(opinion.find_element_by_xpath('.//a[@data-testid="like-button"]').text))
                dislikes.append(int(opinion.find_element_by_xpath('.//a[@data-testid="dislike-button"]').text))
            except:
                likes.append(None)
                dislikes.append(None)

        columns = [title,content,rate,likes,dislikes]
        return columns


        # Tendre que implementar extraccion de id o bien pasarlo como parametro

    def verificationNewOpinions(self, driver, df):
        """
        :param driver:
        :param df: dataframe cuya unidad de analisis es una opinion y las columnas son titulo, content, rate, fecha, likes, dislikes
        :return: True si son opiniones ya extraidas o False en caso que sean nuevas
        """
        # Preasumo que la opinion es nueva
        bool = True

        # Extraigo la primera opinion
        prim_opinion = driver.find_element(By.XPATH, '//div[@class="infinite-scroll-component "]/article/p').text

        # Veo si la primera opinion ya fue extraida
        if prim_opinion in df["content"]:
            bool = False

        return bool


    # Puedo hacer un buscador de atributos... que busque en publicaciones hasta que encuentre en alguna un cuadro comparativo de publicaciones entonces saco la primera columna de la tabla
    # o bien, en la seccion que dice "Caracteristicas de ..." aunque veo que es poco (por ej, en celulares falta sistema operativo, memoria ram, etc)
    def PublicationExtractor(self, driver, atributos):
        """Nota: los datos en las ≠ public estan en un div#class="ui-pdp-container ui-pdp-container--pdp".
        Por que hago un try?
        Publicaciones de celulares tienen datos en column center y objetos como roperos, banco de pesas en column right
        De aqui extraigo: nombre_publicacion ; precio ; envio gratis? ; estado (nuevo o usado) ; devolucion?

        NO HACE FALTA HACER UN TRY PUES LOS TAGS SON UNICOS MAS ALLA DE SI ESTAN EN UNA COLUMNA U OTRA POR LO QUE,
        NO IMPORTAN.
        """
        '''
        # Estado. Esta en un lugar unico tanto para usados como nuevos div#class="ui-pdp-header__subtitle"
        try:
            estado = driver.find_element(By.XPATH, '//div[@class="ui-pdp-header__subtitle"]/span').text
        except:
            estado = None

        # Nombre publicacion. Esta en un lugar unico tanto para usados como nuevos h1#class="ui - pdp - title"
        try:
            nombre_publicacion = driver.find_element(By.XPATH, '//h1[@class="ui-pdp-title"]').text
        except:
            nombre_publicacion = None

        # Precio.
        try:
            precio = driver.find_element(By.XPATH, '//div[@class="ui-pdp-price__second-line"]//span[@class="andes-money-amount__fraction"]').text
        except:
            precio = None

        # Envio. Hago try porque puede que no lo tengan si no es envio gratis...
        # envio = 1 es que es gratis, 0 si no.
        try:
            texto = driver.find_element(By.XPATH,
                                        '//div[@class="ui-pdp-container__row ui-pdp-container__row--shipping-summary"] or'
                                        '[@class="ui-pdp-media ui-pdp-shipping ui-pdp-shipping--md mb-20 ui-pdp-color--GREEN"]'
                                        '//p[@class="ui-pdp-color--GREEN ui-pdp-family--REGULAR ui-pdp-media__title ui-pdp-media__title--on-hover"]').text

            # Usan "Llega gratis" o "Envio gratis a todo el pais"
            if "gratis" in texto:
                envio = 1
        except:
            envio = 0

        # Devolucion
        try:
            driver.find_element(By.XPATH, '//div[@class="class="ui-pdp-container__row"]//p[contains("Devolución gratis")]')
            devolucion = 1
        except:
            devolucion = 0

        # Compra protegida
        try:
            driver.find_element(By.XPATH, '//a[@href="https://www.mercadolibre.com.ar/compra-protegida"]')
            compra_protegida = 1
        except:
            compra_protegida = 0
            
        '''
        d = {}
        pageSource = driver.page_source
        bs = BeautifulSoup(pageSource, "html.parser")

        '''
        # Recorro cada fila (que contiene atributo y valor) de la tabla de atributos de la publicacion en "Caracteristicas Principales"]
        tabla = bs.find_all('tr',{"class":"andes-table__row"}) # faltaria implementar la busqueda de tr de publicaciones tipo 2
        '''
        # Extraigo tabla de atributos de las publicaciones que tienen la info en "ver mas caracteristicas"
        tabla = bs.find_all('tr',{"class":"andes-table__row"}) # faltaria implementar la busqueda de tr de publicaciones tipo 2

        # Si corresponde a las publicaciones que tienen la info en "ver mas caracteristicas"
        if tabla == None:
            tabla = bs.find().find_all('tr', {"class": "andes-table__row ui-vpp-striped-specs__row"})  # faltaria implementar la busqueda de tr de publicaciones tipo 2

        for fila_tabla in tabla:
            atrib_pub = fila_tabla.find('th').text
            # print('b',atrib_pub)

            # Si el atributo de la publicacion es de interes, entonces lo guardo
            if atrib_pub in atributos:
                d[atrib_pub] = fila_tabla.find('td').text


        # Recorro cada fila (que contiene atributo y valor) de "otras caracteristicas"
        tabla_otras_carac = bs.find_all('p',{"class":"ui-pdp-family--REGULAR ui-pdp-list__text"}) # faltaria implementar la busqueda de tr de publicaciones tipo 2
        # creo que si es None no entra (por lo que, no tendria que poner != None). None te devuelve si no encuentra el xpath.
        if tabla_otras_carac != None:
            # print("Encontro la tabla")
            for fila_tabla in tabla_otras_carac:
                atrib_y_val = fila_tabla.text
                idx = atrib_y_val.index(':')  # Falla a veces. Por que? Vi la publicacion y tiene el "ver mas caracteristicas" podria ser eso. ahora no fallo mas...
                atrib_pub = atrib_y_val[:idx]

                # Si el atributo de la publicacion es de interes, entonces lo guardo
                if atrib_pub in atributos:
                    d[atrib_pub] = atrib_y_val[idx+2:]

        print(d)

        return None







        '''
        # INTENTO HACER CLICK EN "VER MAS CARACTERISTICAS" SI EXISTE DICHO BOTON..
        try:
            boton = driver.find_element(By.XPATH, '//span[@role="button" and @title="Ver más características"]')
            boton.click()
        except:
            print("NO LO ENCONTRO")
        '''


        '''
        INTENTO 1848

        # PUBLICACION TIPO 1
        # Intento extraer atributo
        try:
            # attr_y_val_pub = driver.find_elements(By.XPATH,'//h2[contains(text(),"Características principales")]//tr[@class="andes-table__row"]') #Faltaria aclararle que solo quieero dentro de carac ppales... podria ser con un //h2[contains("Características principales")]
            attr_y_val_pub = driver.find_element(By.XPATH,'//div[@class="ui-pdp-specs")]') # no se por que falla.
            print("Encontro al menos el div")
            attr_y_val_pub = attr_y_val_pub.find_elements(By.XPATH,'.//tr') # no se por que falla.
            print("Encontro los tr")


            # si la publicacion tiene seccion "Otras caracteristicas"...
            try:
                attr_y_val_pub_otras_carac = driver.find_elements(By.XPATH,'//div[@class="ui-pdp-list ui-pdp-specs__list"]//p')
            except:
                print("fallo z")

            for attr_y_val in attr_y_val_pub:
                print(attr_y_val.text)
                attr = attr_y_val.find_element(By.XPATH, './th').text
                val = attr_y_val.find_element(By.XPATH, './td').text # Por alguna razon a veces falla. RTA: claro es porque entra  a la tabla comparativa
                d[attr] = val

            for attr_y_val in attr_y_val_pub_otras_carac:
                atrib_y_val = attr_y_val.text
                idx = atrib_y_val.index(':')  # Falla a veces. Por que? Vi la publicacion y tiene el "ver mas caracteristicas" podria ser eso. ahora no fallo mas...
                attr = atrib_y_val[: idx]
                val = atrib_y_val[idx + 2:]
                d[attr] = val

        except:
            # PUBLICACION TIPO 2  --> puede ser que falle pq no termine de cargar la pagina
            # attr_y_val_pub_2 = driver.find_elements(By.XPATH,'//div[@class="ui-vpp-highlighted-specs__striped-specs"]//tr[@class="andes-table__row ui-vpp-striped-specs__row"]') #Faltaria aclararle que solo quieero dentro de carac ppales ocultas... //div[@class="ui-vpp-highlighted-specs__striped-specs"]
            attr_y_val_pub_2 = driver.find_elements(By.XPATH,'//div[@class="ui-vpp-highlighted-specs__striped-specs"]//tr') #Faltaria aclararle que solo quieero dentro de carac ppales ocultas... //div[@class="ui-vpp-highlighted-specs__striped-specs"]

            for attr_y_val in attr_y_val_pub_2:
                print(attr_y_val.text)
                attr = attr_y_val.find_element(By.XPATH, './th').text
                val = attr_y_val.find_element(By.XPATH, './td').text # Por alguna razon a veces falla. RTA: claro es porque entra  a la tabla comparativa
                d[attr] = val

        print(d)
      '''



        """ intento 15 
        d = {}
        attr_pub, val_attr_pub = [], []

        ''' PARA AMBAS PUBLICACIONES
         attrs_pub = driver.find_elements(By.XPATH, '//th[@class="andes-table__header andes-table__header--left ui-pdp-specs__table__column ui-pdp-specs__table__column-title" '
                                                           'or @class="andes-table__header andes-table__header--left ui-vpp-striped-specs__row__column ui-vpp-striped-specs__row__column--id"]')
         val_attrs_pub = driver.find_elements(By.XPATH,'//td[@class="andes-table__column andes-table__column--left ui-vpp-striped-specs__row__column" '
                                                 'or @class="andes-table__column andes-table__column--left ui-pdp-specs__table__column"]//span')
        '''
        # PUBLICACIONES TIPO 1 ("CARAC PPALES")
        # Busco atributos de una publicacion
        try:
            attrs_pub = driver.find_elements(By.XPATH,'//th[@class="andes-table__header andes-table__header--left ui-pdp-specs__table__column ui-pdp-specs__table__column-title"]')
            attrs_pub_otras_carac = driver.find_elements(By.XPATH,'//div[@class="ui-pdp-list ui-pdp-specs__list"]//span')
        except:
            print("Fallo atributos")

        try:
            val_attrs_pub = driver.find_elements(By.XPATH,'//td[@class="andes-table__column andes-table__column--left ui-pdp-specs__table__column"]//span')
            val_attrs_pub_otras_carac = driver.find_elements(By.XPATH,'//div[@class="ui-pdp-list ui-pdp-specs__list"]//p')
        except:
            print('Fallaron valores')

        '''
        # PUBLICACIONES TIPO 2
        # Busco atributos de una publicacion
        try:
            attrs_pub = driver.find_elements(By.XPATH,
                                             '//th[@class="andes-table__header andes-table__header--left ui-vpp-striped-specs__row__column ui-vpp-striped-specs__row__column--id"]')
        except:
            print("Fallo atributos")

        try:
            val_attrs_pub = driver.find_elements(By.XPATH,
                                                 '//td[@class="andes-table__column andes-table__column--left ui-vpp-striped-specs__row__column"]//span')
        except:
            print('Fallaron valores')
        '''


        # Guardo atributos de la publicacion
        for a in attrs_pub:
            attr_pub.append(a.text)

        for b in attrs_pub_otras_carac:
            attr_pub.append(b.text)

        for c in val_attrs_pub:
            val_attr_pub.append(c.text)

        for d in val_attrs_pub_otras_carac:
            val_y_atrib = d.text
            print(val_y_atrib)
            idx = val_y_atrib.index(":") + 2
            val_attr_pub.append(val_y_atrib[idx:])

        # Selecciono atributos de interes...

        print("atributo y valor", attr_pub, val_attr_pub)
"""


'''
        # FALTA IMPLEMENTAR BUSQUEDA DE VALORES DE ATRIBUTOS PARA LA DADA PUBLICACION
        d = {}

        # Defino la tabla de la publicacion donde cada fila es una atributo y su respectivo valor

        try:
            # tabla_atributos = driver.find_elements(By.XPATH, '//table[@class="andes-table"]//tr')
            tabla_atributos = driver.find_elements(By.XPATH, '//tr[@class="andes-table__row ui-vpp-striped-specs__row"]')

        except:
            # tabla_atributos = driver.find_elements(By.XPATH, '//section[@class=”ui-vpp-highlighted-specs  pl-45 pr-45"]//tr')
            #tabla_atributos = driver.find_elements(By.XPATH, '//div[@class=”ui-pdp-collapsable__container"]//tr')
            print('Fallo :(')

        # Tuve que aclarar la section primero antes de los tr porque si la publicacion tiene tabla comparativa de publicaciones entraba..
        # tendria que probar:  tabla_atributos = driver.find_elements(By.XPATH, '/section[@class="ui-vpp-highlighted-specs  pl-45 pr-45"] or section[@class="ui-pdp-specs pl-45 pr-45"]//tr')


        # Recorro cada fila de la tabla
        for fila in tabla_atributos:

            # Cada fila contiene un atributo y su valor
            # Los try despues vere de sacarlos...
            try:
                atributo = fila.find_element(By.XPATH, '/th').text
                print(atributo)
            except:
                print('Fallo 2')

            try:
                valor = fila.find_element(By.XPATH, '//td').text
            except:
                print('Fallo 3')

            # Si el atributo de la publicacion es de interes, lo extraigo
            if atributo in atributos:
                d[atributo] = valor
            print('Cambia de atributo...')

        return d
'''





'''
        1er intento
        atributo_pub, val_atributo_pub = [], []
        d ={}

        # Publicaciones que tienen sus attrs descriptos en tabla dentro de "Caracteristicas principales"
        try:
            # Extraigo atributos de la publicacion en "caracteristicas principales"
            for tag in driver.find_elements(By.XPATH, '//th[@class="andes-table__header andes-table__header--left ui-pdp-specs__table__column ui-pdp-specs__table__column-title"]'):
                atributo_pub.append(tag.text)

            # Extraigo valores de los atributos de la publicacion en "caracteristicas principales"
            for tag in driver.find_elements(By.XPATH, '//td[@class="andes-table__column andes-table__column--left ui-pdp-specs__table__column"]//span'):
                val_atributo_pub.append(tag.text)

            # Extraigo atributos de la publicacion en "Otras" o "Otras caracteristicas"
            for tag in driver.find_elements(By.XPATH, '//div[@class="ui-pdp-list ui-pdp-specs__list"]//span'):
                atributo_pub.append(tag.text)

            # Extraigo valores de atributos de la publicacion en "Otras" o "Otras caracteristicas"
            for tag in driver.find_elements(By.XPATH, '//div[@class="ui-pdp-list ui-pdp-specs__list"]//p'):
                # tiene el problema que el text de ese tag es ineevitablemente "<atributo> : <valor>" y no solo el valor
                atrib_valor = tag.text
                idx = atrib_valor.index(':') + 2
                valor = atrib_valor[idx:]
                val_atributo_pub.append(valor)

        # Publicaciones que tienen sus attrs dentro de "ver mas caracteristicas" --> aun no funciona
        except:
            driver.find_element(By.XPATH, 'span[@title="Ver más características"]').click()

            # Extraigo atributos de la publicacion
            for tag in driver.find_elements(By.XPATH, '//th[@class="andes-table__header andes-table__header--left ui-vpp-striped-specs__row__column ui-vpp-striped-specs__row__column--id"]'):
                atributo_pub.append(tag.text)

            # Extraigo valores de los atributos
            for tag in driver.find_elements(By.XPATH, '//td[@class="andes-table__column andes-table__column--left ui-vpp-striped-specs__row__column"]//span'):
                val_atributo_pub.append(tag.text)

        
        # Para cada atributo de interes veo si consegui su valor en la publicacion (puede que la publicacion no de su valor)
        for atributo in atributos:
            if atributo in atributo_pub:
                idx_atrib = atributo_pub.index(atributo)
                d[atributo] = val_atributo_pub[idx_atrib]
            else:
                d[atributo] = None
        print(d)
        
        Asi NO:
        idx = 0
        for atributo in atributo_pub:
            if atributo in atributos:
                d[atributo] = val_atributo_pub[idx]
            idx += 1

        print(d)
        
        # tengo que retornar  [estado, nombre_publicacion, precio, envio, devolucion, compra_protegida, marca, modelo, atributos..]
        # return [estado, nombre_publicacion, precio, envio, devolucion, compra_protegida]
        return atributo_pub, val_atributo_pub
        
        
        
'''



"""
Faltaria extraer: marca ; modelo
"""
