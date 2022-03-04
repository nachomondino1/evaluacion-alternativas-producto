import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.request import urlopen


class MercadoLibreCrawler():
    """ A tool to extract information from Mercado Libre"""
    # Los metodos dentro de la clase seran acciones que pueda hacer el crawler
    # Para usar la clase tendre que definir un driver (Chrome, Firefox, Phantom, etc) y un producto a buscar


    def __init__(self, driver, busqueda):
        self.driver = driver
        self.busqueda = busqueda


    def getHomePageUrl(self, busqueda):
        # Ingreso a URL semilla (en este caso, la pagina principal de mercado libre)
        a = busqueda.replace(" ", "-")
        b = busqueda.replace(" ", "%20")
        url = 'https://listado.mercadolibre.com.ar/' + a + "#D[A:" + b + "]"
        return url


    def validacionBusqueda(self, driver, busqueda):
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
        resp = bs.find('div', {'class': "ui-search-breadcrumb"}).find("ol", {"class": "andes-breadcrumb"})
        return resp


        """
        Lo viejo
        # Ingreso a URL semilla (en este caso, la pagina principal de mercado libre)
        a = busqueda.replace(" ", "-")
        b = busqueda.replace(" ", "%20")
        url = 'https://listado.mercadolibre.com.ar/' + a + "#D[A:" + b + "]"
        # driver.get(url)

        try:
            driver.find_element(By.XPATH, '//div[@class="ui-search-breadcrumb"]/ol[@class="andes-breadcrumb"]')
            return True
        except:
            return False
        """


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

        # Creo el dataframe
        df = pd.DataFrame(columns=['title', 'content', 'rate','likes','dislikes']) # Falta el id en primera row
        idx = 0

        # Tendre que implementar extraccion de id o bien pasarlo como parametro


        # Extraigo opiniones
        # Obtengo los XPATH donde se ubican los parrafos de cada una de las opiniones
        # Por opinion (recorda que cada publicacion tiene varias opiniones) Ojo que por ahi va solo al primer article y no a todos...
        opiniones_publicacion = driver.find_elements(By.XPATH, '//div[@class="infinite-scroll-component "]/article')

        for opinion in opiniones_publicacion:

            # Extraigo Title
            try:
                title = opinion.find_element_by_xpath('.//h2').text
            except:
                title = None

            # Extraigo Content
            try:
                content = opinion.find_element_by_xpath('.//p').text
            except:
                content = None

            # Extraigo Rate
            try:
                n = 0
                stars = opinion.find_elements_by_class_name("ui-review-view__comments__review-comment__rating__star")
                # print(stars)

                for star in stars:
                    # print(star.find_element_by_tag_name("path").get_attribute("fill"))
                    # print(type(star.find_element_by_tag_name("path").get_attribute("fill")))
                    # print(star.find_elements_by_class_name("fill"))

                    if star.find_element_by_tag_name("path").get_attribute("fill") == "#3483FA":
                        n += 1
                    else:
                        break
                rate = n
            except:
                rate = None

            #Extraigo Likes y dislikes
            try:
                likes = int(opinion.find_element_by_xpath('.//a[@data-testid="like-button"]').text)
                dislikes = int(opinion.find_element_by_xpath('.//a[@data-testid="dislike-button"]').text)
            except:
                likes, dislikes = None, None

            # Cargo nueva fila al df
            df.loc[idx] = [title,content,rate,likes,dislikes] # falta el id
            idx += 1


        return df


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

    """ old version
    def getOpinionTitle(self, opinion):
        title = opinion.find_element_by_xpath('.//h2').text
        return title
    
    
    def getOpinionRate(self, opinion):
        '''

        :param opinion: tag article con rate, content, titulo, likes y dislikes
        :return: Numero de estrellas de la opinion
        '''
        n = 0
        stars = opinion.find_elements_by_class_name("ui-review-view__comments__review-comment__rating__star")
        # print(stars)

        for star in stars:
            # print(star.find_element_by_tag_name("path").get_attribute("fill"))
            # print(type(star.find_element_by_tag_name("path").get_attribute("fill")))
            # print(star.find_elements_by_class_name("fill"))

            if star.find_element_by_tag_name("path").get_attribute("fill") == "#3483FA":
                n += 1
            else:
                break
        return n


    def getOpinionContent(self, opinion):
        try:
            content = opinion.find_element_by_xpath('.//p').text
        except:
            pass
        return content


    def getOpinionLikes(self, opinion):
        # falta implementar handle exception
        likes = int(opinion.find_element_by_xpath('.//a[@data-testid="like-button"]').text)
        dislikes = int(opinion.find_element_by_xpath('.//a[@data-testid="dislike-button"]').text)
        return likes, dislikes

"""

    # Puedo hacer un buscador de atributos... que busque en publicaciones hasta que encuentre en alguna un cuadro comparativo de publicaciones entonces saco la primera columna de la tabla
    # o bien, en la seccion que dice "Caracteristicas de ..." aunque veo que es poco (por ej, en celulares falta sistema operativo, memoria ram, etc)

    def PublicationExtractor(self, driver):

        """Nota: los datos en las ≠ public estan en un div#class="ui-pdp-container ui-pdp-container--pdp".
        Por que hafo un try?
        Publicaciones de celulares tienen datos en column center y objetos como roperos, banco de pesas en column right
        De aqui extraigo: nombre_publicacion ; precio ; envio gratis? ; estado (nuevo o usado) ; devolucion?

        NO HACE FALTA HACER UN TRY PUES LOS TAGS SON UNICOS MAS ALLA DE SI ESTAN EN UNA COLUMNA U OTRA POR LO QUE,
        NO IMPORTAN.
        """
        # Tendre que implementar extraccion de id o bien pasarlo como parametro


        # Estado. Esta en un lugar unico tanto para usados como nuevos div#class="ui-pdp-header__subtitle"
        driver.find_element(By.XPATH, '//div[@class="ui-pdp-header__subtitle"]/span]').text

        # Nombre publicacion. Esta en un lugar unico tanto para usados como nuevos h1#class="ui - pdp - title"
        driver.find_element(By.XPATH, '//h1[@class="ui - pdp - title"]').text

        # Precio.
        driver.find_element(By.XPATH, '//div[@class="ui - pdp - price__second - line"]'
                                          '/span[@class="andes-money-amount__fraction"]').text
        # Envio. Hago try porque puede que no lo tengan si no es envio gratis...
        envio = getEnvio(driver)

        # Devolucion
        devolucion = getDevolucion(driver)

        # Compra protegida





        """
        Faltaria extraer: marca ; modelo
        Por que hago un try?
        Por que los celularers tienen marca y modelo en el nombre de la seccion "Caracteristicas de ...".
        En cambio, los roperos y los bancos de pesas dice "caracteristicas principales" y dentro de esta, hay una tabla
        donde especifica marca, linea y modelo.
        """



    """
    Este sera un ciclo que recorra publicaciones hasta que encuentre la primera que tenga la info.
    Extraigo atributos del producto atrib_prod_1 ; atrib_prod_2 ; ... ; atrib_prodn
    Por que hago un try?
    Porque los celulares tienen datos de atributos en columncenter (tendre que ver como extraerlos) OJO! NO USO TABLA COMPARATIVA PORQUE SON ATRIBUTOS IRRELEVANTES
    En cambio los roperos y bancos de pesas los tienen en la seccion "otras caracteristicas"
    """


    def getEnvio(self, driver):
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
        return envio


    def getDevolucion(self, driver):
        try:
            driver.find_element(By.XPATH, '//div[@class="class="ui-pdp-container__row"]//p[contains("Devolución gratis")]')
            devolucion = 1
        except:
            devolucion = 0
        return devolucion



    # def getCompraProtegida(self, driver):

    # def getIdentificadorProducto(url):
    # los dos df tienen que tener el id pero no creo que este bien pasarlo como parametro en los get()
    # es mejor llamar a esta funcion dentro de las funciones get()
    # FALTA IMPLEMENTAR