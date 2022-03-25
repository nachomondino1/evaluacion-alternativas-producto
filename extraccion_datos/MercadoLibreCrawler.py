# Importo librerias
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from utils.web_scraping.crawler import Crawler
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep


class MercadoLibreCrawler(Crawler):
    """ A tool to extract data from Mercado Libre using Web Scraping """

    def __init__(self, driver, producto):
        # super().__init__(driver) # no se si esta bien """Initialize attributes of the parent class."""
        self.driver = driver
        self.producto = producto # Deberia ser un objeto de la clase producto...


    def getPublicationsUrl(self):
        """
        Obtiene los links de cada publicacion en la pagina principal de Mercado Libre

        :return: Lista de links de las publicaciones en la pagina principal
        """

        # Implicit wait: Extraigo recien cuando carga la pagina tal que encuentra el tag donde se encuentran las url
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="ui-search-result__image"]')))

        finally:
            # Busco todos los tags que contienen un link a una publicacion
            # No le puedo hacer get_attribute al ser mas de un elemento
            tag_urls_publicaciones = self.driver.find_elements(By.XPATH, '//div[@class="ui-search-result__image"]/a')

            # Defino lista vacia en donde guardare los links de las publicaciones
            l_url_publicaciones = []

            # Recorro cada tag (cada uno contiene un link)
            for tag_url in tag_urls_publicaciones:
                # Obtengo el atributo href (que es el url) del tag y lo guardo en la lista
                l_url_publicaciones.append(tag_url.get_attribute("href"))

            return l_url_publicaciones


    def getPaginacionUrl(self):
        """
        Obtiene el link a la siguiente pagina principal de Mercado Libre

        :return: Url de la siguiente pagina de Mercado Libre
        """

        # Implicit wait: hasta que aparezca la seccion en donde cambio de pagina
        try: #esta fallando en la carga? pues no encuntrs la url cuando deberia encontrarla...
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//ul[@class="ui-search-pagination andes-pagination"]')))

        finally:

            # Obtengo el url de la siguiente pagina
            try:
                url_next_page = self.driver.find_element_by_xpath(
                './/li[@class="andes-pagination__button andes-pagination__button--next"]/a').get_attribute('href')
                print("Encontro siguiente pagina", url_next_page)

            # No hay "siguiente pagina", es la ultima
            except:
                url_next_page = None

            return url_next_page


    def getVerTodasLasOpinionesUrl(self):
        """
        Obtiene, si existe, el URL del boton "Ver todas las opiniones" dentro de una publicacion de Mercado Libre

        :return: URL del boton "Ver todas las opiniones", o bien, None si no existe tal boton
        """
        # implicit or explicit wait
        # WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//meta[@property="og:url"]')))
        sleep(2) # solucion rabina
        try:
            url_ver_todas_las_opi = self.driver.find_element(By.XPATH,'//div[@class="ui-pdp-reviews__actions__container"]/a').get_attribute("href")
        except:
            url_ver_todas_las_opi = None

        return url_ver_todas_las_opi


    def getPublicationOpinionsData(self, id_publicacion):
        """
        Extrae opiniones de seccion "Ver todas las opiniones" dentro de una publicacion de Mercado Libre

        :param id_publicacion: Identificador de cada publicacion
        :return: Diccionario cuyas keys son los nombres de los campos a extraer (id, titulo, content, rate, fecha, likes,
        dislikes) y los values son una lista (pues una publicacion tiene varias opiniones) de valores para ese campo.
        Uso diccionario por la facilidad que representa  transformarlo en fila/s de un DataFrame.
        """

        # Inicializo el diccionario en donde guardare las listas con los datos extraidos
        d = {'id_publicacion': None, 'title': None, 'content': None,'rate': None, 'likes': None, 'dislikes': None}

        # Inicializo una lista por cada campo a extraer. Dentro guardare un valor por cada opinion de la publicacion
        l_id_publicacion, l_title, l_content, l_rate, l_likes, l_dislikes = [], [], [], [], [], []

        # Obtengo tags donde cada uno contiene una opinion
        opiniones_publicacion = self.driver.find_elements(By.XPATH, '//div[@class="infinite-scroll-component "]/article')

        # Recorro cada opinion
        for opinion in opiniones_publicacion:

            # Extraigo Title
            try:
                l_title.append(opinion.find_element_by_xpath('.//h2').text)
            except:
                l_title.append(None)

            # Extraigo Content
            try:
                l_content.append(opinion.find_element_by_xpath('.//p').text) # EXTRAE LO QUE HAY DE TEXXTO EN EL SPAN POR ESO EXTRAE EL "HACE..."
            except:
                l_content.append(None)

            # Extraigo Rate
            try:
                n = 0
                stars = opinion.find_elements_by_class_name("ui-review-view__comments__review-comment__rating__star")

                # Recorro cada una de las 5 estrellas
                for star in stars:
                    if star.find_element_by_tag_name("path").get_attribute("fill") == "#3483FA":
                        n += 1
                    else:
                        # Dejo de recorrer las estrellas al encontrar la primera que no ha sido llenada
                        break
                l_rate.append(n)
            except:
                l_rate.append(None)

            #Extraigo Likes y dislikes
            try:
                l_likes.append(int(opinion.find_element_by_xpath('.//a[@data-testid="like-button"]').text))
                l_dislikes.append(int(opinion.find_element_by_xpath('.//a[@data-testid="dislike-button"]').text))
            except:
                l_likes.append(None)
                l_dislikes.append(None)

        # Creo lista de id_publicacion segun la cantidad de opiniones
        for i in range(len(l_title)):  # podria haber puesto cualquier campo en lugar de title
            l_id_publicacion.append(id_publicacion)

        # Creo lista que contiene todas las listas con los datos extraidos
        data = [l_id_publicacion, l_title, l_content, l_rate, l_likes, l_dislikes]

        # Por cada campo a extraer, guardo su lista en el diccionario
        idx = 0
        for key in d.keys():
            d[key] = data[idx]
            idx += 1

        return d


    def verificationNewOpinions(self, l_prim_opiniones):
        """
        Dentro de la seccion "Ver todas las opiniones" pero antes de extraer las opiniones, verifico que sean
        opiniones nuevas (es decir, que no las haya extraido)

        :param l_prim_opiniones: Lista de primeras opiniones de cada publicacion ya visitada
        :return: True si son opiniones nuevas, o bien, False en caso que sean repetidas
        """
        # A priori, asumo que la opinion es nueva
        bool = True

        try:
            prim_opinion = self.driver.find_element(By.XPATH,
                                                        '//div[@class="infinite-scroll-component "]/article/p').text

        except:
            print("Fallo la verificacion de opiniones nuevas. No se pudo extraer la primera opinion")
            prim_opinion = None

        # Me fijo si la primera opinion es repetida
        if (prim_opinion in l_prim_opiniones) or (prim_opinion == None): # con la segunda condicion no estaria extrayendo las opiniones cdo falla la extraccion anterior
            # La opinion es repetida, o bien, fallo la verificacion. En cualquier caso, devuelvo False
            bool = False

        return bool


    def getModeloData(self, id_publicacion, campos_especificos):
        """
        De una sola publicacion, extrae el precio de ésta y, segun la subcategoria del producto, cada campo especifico
        por ejemplo tamaño de pantalla o resolucion de camara para publicaciones de la subcategoria "Celulares y
        smartphones".

        :param id_publicacion: Identificador de publicacion
        :param campos_especificos: Lista de campos especificos (o "atributos") de una subcategoria de productos de
        Mercado Libre que deseo extraer. Por ejemplo, "tamano de pantalla" para la subcategoria "Celulares y
        Smartphones". Su largo dependera de cada subcategoria
        :return: Diccionario cuyas keys son cada campo a extraer de una publicacion (no solo son los atributos) y cuyos
        value son el valor que toma el respectivo campo para una publicacion en particular. Uso diccionario por la
        facilidad que representa transformarlo en fila/s de un DataFrame.
        """

        # Defino el diccionario donde guardare los campos a extraer y su valor para una publicacion. Agrego al
        # diccionario el unico campo que extraigo de antemano
        d = {'id_publicacion': id_publicacion}

        # Implicit wait: hasta que aparezca la seccion "Caracteristicas principales
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//section[@id="highlighted-specs"]')))

        finally:
            # Para facilitar la extraccion, convierto el codigo html de la pagina de la publicacion en un objeto de la
            # clase BeautifulSoup
            pageSource = self.driver.page_source
            bs = BeautifulSoup(pageSource, "html.parser")

            # EXTRAIGO VALOR DE PRECIO
            try:
                d['precio'] = bs.find('div',{'class':"ui-pdp-price__second-line"}).\
                    find('span',{'class':"andes-money-amount__fraction"}).text
            except:
                print("No encontro el precio")
                d['precio'] = None # en un futuro podria intentar extraer precio de las que fallan

            # EXTRAIGO VALORES DE CAMPOS ESPECIFICOS
            # Por campo especifico
            for campo_especifico in campos_especificos:

                # Obtengo el tag, si existe, donde esta el atributo (en particular, uno de los que me interesa). Puede
                # encontrarse en la seccion "Caracteristicas principales", o bien, en "Otras caracteristicas"
                attr = bs.find('th', text=campo_especifico)
                attr_otras_carac = bs.find('span', {'class':"ui-pdp-color--BLACK ui-pdp-size--XSMALL ui-pdp-family--BOLD"},
                                           text=campo_especifico)

                # print("Fijate que encuentra el th pero como esta en carac gen, no lo extrae pues no tiene nextsibling", attr)
                # FALTA IMPLEMENTAR EXTRACCION DE VALORES DE SECCION "CARACTERISTICAS GENERALES". EL TH ESTA BIEN PEOR NO TIENE NEXT SIBLING
                # En realidad si tiene next sibling... Esto parece estar bien, lo que esta mal es que por alguna razon no busca todos los atributos...
                # el problema es que en las publicaciones que tienene atributos en "caracteristicas generales" y en "otras caracteristicas" solo extrae de "caracteristicas generales" pues el attr no es None


                # Si existe el tag, entonces guardo el atributo y su valor en el diccionario
                if attr != None:
                    valor = attr.nextSibling.text
                    attr = attr.text
                    d[attr] = valor
                    # print("Atributo:", attr,"Valor:", valor)


                # Si no existe el tag, puede que se encuentre en "Otras caracteristicas" y entonces guardo el atributo
                # y su valor en el diccionario
                elif attr_otras_carac != None: # era un elif pero lo tuve que hacer if porque -->  el problema es que en las publicaciones que tienene atributos en "caracteristicas generales" y en "otras caracteristicas" solo extrae de "caracteristicas generales" pues el attr no es None
                    valor = attr_otras_carac.nextSibling.text
                    attr_otras_carac = attr_otras_carac.text
                    d[attr_otras_carac] = valor[2:]
                    # print("Atributo:", attr_otras_carac,"Valor:", valor)


                # Si no existe el tag en ninguna seccion, entonces guardo el atributo con valor None en el diccionario
                else:
                    d[campo_especifico] = None
                    # print("Atributo:", campo_especifico,"Valor:", None)

            print("Fila a cargar", d)
            return d


    def getIdPublicacion(self, url_publicacion):
        """
        Extrae el id de una publicacion dentro de la URL de esta. En caso que no este, es porque la URL no es de las
        comunes, y por ende, busca la URL dentro del codigo html de la publicacion. Solo en el eventual caso que no
         encuentra la url, entonces no encontro el id.

        :param url_publicacion: URL de una publiacacion de Mercado Libre (en formato string)
        :return: id de la publicacion (en formato string), o bien, None si no lo encontro
        """
        # Defino reglas con las que extraer el id de la url y variable en la que guardare el id
        construyo_id = str()
        regla1 = 'p/MLA'
        regla2 = 'MLA-'

        # Si es una URL de la forma "www.click1.mercadolibre..."
        if (regla1 not in url_publicacion) and (regla2 not in url_publicacion):
            print("url con url de la forma www.click1.mercadolibre... ")

            # Reemplazo la URL
            try:
                # Extraigo URL de la publicacion
                tag_url_publicacion = self.driver.find_element_by_xpath('//meta[@property="og:url"]')

                # Reemplazo URL pasada por parametro por la URL extraida
                url_publicacion = tag_url_publicacion.attrs['content']
                print("LA URL DE LA PUBLICACION ES CLICK PERO ENCONTRE LA URL DENTRO DE LA PAGINA")

            # Si encontro el tag donde esta la URL de la publicacion
            except:
                # Defino el id como None al no encontrar la URL del cual extraerlo
                url_publicacion = None
                id = None
                # print("LA URL DE LA PUBLICACION ES CLICK Y ENCIMA NO ENCONTRE LA URL DENTRO DE LA PAGINA")

        # Si tengo la URL de la cual extraer el ID
        if url_publicacion != None:

            # Busco el id dentro de la url a partir de reglas
            # Regla 1: URLs que son del tipo "...p/MLA<id>"
            try:
                idx_ini = url_publicacion.index(regla1)
                url_restante = url_publicacion[idx_ini + len(regla1):]

            # Regla 2: URLs que son del tipo "...MLA-<id>..."
            except:
                idx_ini = url_publicacion.index(regla2)
                url_restante = url_publicacion[idx_ini + len(regla2):]

            # Recorro cada elemento de la url restante, tener en cuenta que el id es de largo variable
            for elemento in url_restante:

                # Si es numero
                if elemento.isdigit():
                    # Lo guardo
                    construyo_id += elemento
                # Si no es numero
                else:
                    # dejo de recorrer los elementos de la url pues el id es numerico
                    break

            # Construido el id elemento a elemento, lo guardo en id
            id = construyo_id

        return id