import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.request import urlopen
from utils.web_scraping.crawler import Crawler


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
        # Convierto el codigo html de la pagina de la publicacion en un objeto de la clase BeautifulSoup
        pageSource = driver.page_source
        bs = BeautifulSoup(pageSource, "html.parser")

        # EXTRAIGO ESTADO
        texto_estado = bs.find('div',{'class':"ui-pdp-header__subtitle"}).span.text
        try:
            idx = texto_estado.index('|')
            estado = texto_estado[:idx - 2]
        except:
            estado = "Reacondicionado"

        # EXTRAIGO NOMBRE DE PUBLICACION
        nombre_publicacion = bs.find('h1',{'class':"ui-pdp-title"}).text

        # EXTRAIGO PRECIO
        precio = bs.find('div',{'class':"ui-pdp-price__second-line"}).find('span',{'class':"andes-money-amount__fraction"}).text

        # EXTRAIGO ENVIO. envio = 1 es que es gratis, 0 si no.
        texto = bs.find('div',{"class":"ui-pdp-container__row ui-pdp-container__row--shipping-summary"})
        if texto == None:
            texto = bs.find('div',{'class':"ui-pdp-media ui-pdp-shipping ui-pdp-shipping--md mb-20 ui-pdp-color--GREEN"})

        texto = texto.p.text
        print(texto)

         # Usan "Llega gratis" o "Envio gratis a tod@ el pais"
        if "gratis" in texto:
            envio = 1
        else:
            envio = 0


        # EXTRAIGO DEVOLUCION
        try:
            driver.find_element(By.XPATH, '//div[@class="class="ui-pdp-container__row"]//p[contains("Devolución gratis")]')
            devolucion = 1
        except:
            devolucion = 0


        # EXTRAIGO COMPRA PROTEGIDA
        compra_protegida = bs.find('a',{'href':"https://www.mercadolibre.com.ar/compra-protegida"})
        if compra_protegida == None:
            compra_protegida = 0
        else:
            compra_protegida = 1

        print(estado, nombre_publicacion, precio, envio, devolucion, compra_protegida)

        '''
        d = {}

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
        '''

        return None




