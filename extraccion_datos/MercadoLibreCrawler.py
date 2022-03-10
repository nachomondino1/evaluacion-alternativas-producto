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
        """Initialize attributes of the parent class."""
        super().__init__(driver)
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


    def getSubcategoriaProducto(self, home_page_url):
        '''
        Dada una pagina de Mercado Libre en donde se detallen las publicaciones de un mismo producto,
        encuentra el nombre de la categoria a la que pertenece dicho producto.
        :param home_page_url: pagina de Mercado Libre en donde se detallan las publicaciones de un mismo producto
        :return: nombre de la categoria a la que pertenece dicho producto
        '''
        # Podria implementar beatiful soup para acceder el codigo html de la pagina sin que se me abra el Chrome...
        html = urlopen(home_page_url)
        bs = BeautifulSoup(html, 'html.parser')
        nombre_categoria_producto = bs.find('div', {'class': "ui-search-breadcrumb"}).find('meta', {'content': "2"}).find_previous_sibling().attrs['title']
        return nombre_categoria_producto


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


    def getPublicacionOpinions(self, driver, id_publicacion):
        """
        Extrae opiniones de una publicacion

        :return: Dataframe cuya unidad de analisis es la opinion y sus columnas son titulo, content, rate, fecha, likes, dislikes
        """
        # Inicializo el diccionario
        d = {'id_publicacion': None, 'title': None, 'content': None,'rate': None, 'likes': None, 'dislikes': None}

        # Creo listas en donde guardare los valores de las distintas opiniones de una publicacion
        l_id_publicacion, title, content, rate, likes, dislikes = [], [], [], [], [], [] # agregarles la l al ppio

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

        # Creo lista de id_publicacion segun la cantidad de opiniones
        for i in range(len(title)):  # podria haber puesto cualquier campo en lugar de title
            l_id_publicacion.append(id_publicacion)

        # Creo lis
        data = [l_id_publicacion, title, content, rate, likes, dislikes]
        idx = 0

        for key in d.keys():
            d[key] = data[idx]
            idx += 1

        return d


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


    def PublicationExtractor(self, driver, id_publicacion ,campos_especificos):
        """
        Extrae el valor que toma cada campo (campos tanto generales a varias subcategorias de productos por ej precio o
        estado como especificos de una subcategoria por ej tamaño de pantalla o resolucion de camara para publicaciones
        de la subcategoria "Celulares y smartphones") para una sola publicacion

        :param driver: Web Borwser Automatico
        :param campos_especificos: Lista de campos especificos (o "atributos") de una subcategoria de productos de
        Mercado Libre que deseo extraer. Por ejemplo, "tamano de pantalla" para la subcategoria "Celulares y
        Smartphones". Su largo dependera de cada subcategoria
        :return: Diccionario cuyas keys son cada campo a extraer de una publicacion (no solo son los atributos) y cuyos
        value son el valor que toma el respectivo campo para una publicacion en particular. Uso diccionario por la
        facilidad que representa  transformarlo en fila/s de un DataFrame.
        """

        # Defino el diccionario donde guardare los campos a extraer y su valor para una publicacion. Agrego al
        # diccionario el unico campo que extraigo de antemano
        d = {'id_publicacion': id_publicacion}

        # Para facilitar la extraccion, convierto el codigo html de la pagina de la publicacion en un objeto de la
        # clase BeautifulSoup
        pageSource = driver.page_source
        bs = BeautifulSoup(pageSource, "html.parser")

        # EXTRAIGO NOMBRE DE PUBLICACION
        d["nombre_publicacion"] = bs.find('h1',{'class':"ui-pdp-title"}).text

        # EXTRAIGO ESTADO
        texto_estado = bs.find('div', {'class': "ui-pdp-header__subtitle"}).span.text
        try:
            idx = texto_estado.index('|')
            d["estado"] = texto_estado[:idx - 2]
        except:
            d["estado"] = "Reacondicionado"

        # EXTRAIGO PRECIO
        d['precio'] = bs.find('div',{'class':"ui-pdp-price__second-line"})\
            .find('span',{'class':"andes-money-amount__fraction"}).text

        # EXTRAIGO ENVIO. envio = 1 es que es gratis, 0 si no.
        texto = bs.find('div',{"class":"ui-pdp-container__row ui-pdp-container__row--shipping-summary"})
        if texto == None:
            texto = bs.find('div',{'class':"ui-pdp-media ui-pdp-shipping ui-pdp-shipping--md mb-20 ui-pdp-color--GREEN"})

        # Busco el paragraph una vez que encontre el texto sino salta error por hacerle un find() a un NoneType object
        texto = texto.p.text

         # Me fijo si el texto dice "gratis pues puede ser "Llega gratis" o "Envio gratis a tod@ el pais"
        if "gratis" in texto:
            d['envio'] = 1
        else:
            d['envio'] = 0

        # EXTRAIGO DEVOLUCION --> FALLA, hay muchas pub que dice devolucion gratis y le re chupa la pija.
        # Publicaciones que tienen el "Devolucion gratis" debajo del "comprar ahora"
        # dev_pub_tipo_1 = bs.find('a', {'data-testid': "action-modal-link", 'class': "ui-pdp-action-modal__link"})
        dev_pub_tipo_1 = bs.find('a', text='Devolución gratis.')
        # Publicaciones que tienen el "Devolucion gratis" arriba del "comprar ahora" (menos comunes)
        dev_pub_tipo_2 = bs.find('p', text='Devolución gratis.')
        print(dev_pub_tipo_1, dev_pub_tipo_2)
        if (dev_pub_tipo_1 == None) and (dev_pub_tipo_2 == None):
            d['devolucion'] = 0
        else:
            d['devolucion'] = 1
        print(d['devolucion'])

        '''
        try:
            driver.find_element(By.XPATH, '//div[@class="ui-pdp-container__row"]//p[contains("Devolución gratis")]')
            d['devolucion'] = 1
        except:
            d['devolucion'] = 0
        '''

        # EXTRAIGO COMPRA PROTEGIDA
        compra_protegida = bs.find('a',{'href':"https://www.mercadolibre.com.ar/compra-protegida"})
        if compra_protegida == None:
            d['compra_protegida'] = 0
        else:
            d['compra_protegida'] = 1

        # EXTRACCION DE LOS CAMPOS ESPECIFICOS DE LA SUBCATEGORIA DE PRODUCTOS QUE CORRESPONDA
        # Recorro cada campo especifico de la subcategoria
        # Si no hay  hacer si la categoria no tiene campos especificos?
        # tod@ esto me ahorraria el quilombo que hago despues en PublicationDataframe()

        for campo_especifico in campos_especificos:

            # Obtengo el tag, si existe, donde esta el atributo (en particular, uno de los que me interesa). Puede
            # encontrarse en la seccion "Caracteristicas principales", o bien, en "Otras caracteristicas"
            attr = bs.find('th', text=campo_especifico)
            attr_otras_carac = bs.find('span', {'class':"ui-pdp-color--BLACK ui-pdp-size--XSMALL ui-pdp-family--BOLD"}, text=campo_especifico)

            # Si existe el tag, entonces guardo el atributo y su valor en el diccionario
            if attr != None:
                valor = attr.nextSibling.text
                attr = attr.text
                d[attr] = valor

            # Si no existe el tag, puede que se encuentre en "Otras caracteristicas" y entonces guardo el atributo
            # y su valor en el diccionario
            elif attr_otras_carac != None:
                valor = attr_otras_carac.nextSibling.text
                attr_otras_carac = attr_otras_carac.text
                d[attr_otras_carac] = valor[2:]

            # Si no existe el tag en ninguna seccion, entonces guardo el atributo con valor None en el diccionario
            else:
                d[campo_especifico] = None

        return d


    def getIdPublicacion(self, driver):
        """
        Estando dentro de una publicacion de Mercado Libre, busca automaticamente el id que identifica como unica
        a dicha publicacion.
        :param driver: Web Browser automatico
        :return: id de la publicacion
        """
        # Obtengo la url de la publicacion
        url = driver.find_element(By.XPATH, '//meta[@property="og:url"]').get_attribute('content')

        # Busco el id dentro de la url a partir de reglas
        try:
            idx_ini = url.index('p/MLA')
            id = url[idx_ini + 5:]

        # Hago un try pues hay dos tipos de url
        except:
            idx_ini = url.index('MLA-')
            idx_fin = url.index('-')
            id = url[idx_ini + 4:idx_fin]

        return id
