# Importo librerias
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib.request import urlopen
from utils.web_scraping.crawler import Crawler
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class MercadoLibreCrawler(Crawler):
    """ A tool to extract data from Mercado Libre using Web Scraping """

    def __init__(self, driver, producto):
        """Initialize attributes of the parent class."""
        super().__init__(driver) # no se si esta biee.
        self.producto = producto # Deberia ser un objeto de la clase producto...


    def validacionBusqueda(self):
        """
        Validar la busqueda para que esta no sea muy amplia (hay un costo computacional).
        Si la busqueda es "acotada" Mercado Libre asocia la busqueda del usuario con una categoria de producto
        y el seria muy alto para una busqueda sin sentido

        :param busqueda: Producto que quiere comprar el cliente
        :return: Producto que quiere comprar el cliente validado, es decir, Mercado Libre le encontro categoria
        al producto buscado
        """

        # Obtengo URL semilla (en este caso, la pagina principal de mercado libre)
        self.producto.HomePageUrl = self.producto.getHomePageUrl()

        # Implemento BeatifulSoup para acceder el codigo html de la pagina sin que se me abra el Chrome...
        html = urlopen(self.producto.HomePageUrl)
        bs = BeautifulSoup(html, 'html.parser')

        # Valido la busqueda solo si encuentro subcategoria del producto
        tag_nombre_subcat = bs.find('div', {'class': "ui-search-breadcrumb"}).find("meta", {"content": "2"})
        if tag_nombre_subcat == None:  # Antes buscaba solo si habia hasta el tag "ol" pero habia BUSQUEDAS QUE SON DE UNA SUBCATEGORIA Y EN LA HOMEPAGE SOLO APARECE SU CATEGORIA ppal y no la subcategoria... POR EJ:'comida preparada'  Lo podria solucionar en validacionBusqueda() buscando no solo el tag ol sino buscando el segundo tag li
            print('Busqueda muy amplia, por favor sea mas especifico.', end=' ')
            self.producto.nombre = str(input("Ingrese producto a buscar: "))

            # Funcion recursiva, hasta que la busqueda no sea acotada, sigue pidiendo ingreso de producto a buscar
            self.validacionBusqueda()

        # Actualizo atributo "nombre subcategoria" del producto
        self.producto.nombre_subcat = tag_nombre_subcat.find_previous_sibling().attrs['title']

        return True


    def getPublicationsUrl(self):
        """
        Obtiene los links de cada publicacion en la pagina principal de Mercado Libre

        :return: Lista de links de las publicaciones en la pagina principal
        """

        # Implicit wait
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="ui-search-result__image"]')))
        finally:
            self.driver.quit()

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
        :param driver: Web browser automatico
        :return: Url de la siguiente pagina de Mercado Libre
        """

        # Implicit wait: hasta que aparezca la seccion en donde cambio de pagina
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//ul[@class="ui-search-pagination andes-pagination"]')))
        finally:
            self.driver.quit()

        # Obtengo el url de la siguiente pagina
        try:
            url_next_page = self.driver.find_element_by_xpath(
            './/li[@class="andes-pagination__button andes-pagination__button--next"]/a').get_attribute('href')

        # No hay "siguiente pagina", es la ultima
        except:
            print("No hay mas paginas")
            url_next_page = None

        return url_next_page


    def ClickVerTodasLasOpiniones(self):
        """
        Accede, si existe, al boton "Ver todas las opiniones" dentro de una publicacion de Mercado Libre
        :param driver: Web Browser Automatico
        :return: True si encontro el boton "Ver todas las opiniones" (y en ese caso ingreso) y False si no lo encontro
        """
        try:
            url_ver_opiniones = self.driver.find_element(By.XPATH,'//div[@class="ui-pdp-reviews__actions__container"]/a')\
                .get_attribute("href")
            # Solo ingresa a la pagina si encontro el boton "Ver todas las opiniones"
            self.driver.get(url_ver_opiniones)
            resp = True
        except:
            resp = False

        return resp


    def getPublicationOpinionsData(self, id_publicacion):
        """
        Extrae opiniones de seccion "Ver todas las opiniones" dentro de una publicacion de Mercado Libre

        :param id_publicacion: Identificador de cada publicacion
        :return: Diccionario cuyas keys son los nombres de los campos a extraer (titulo, content, rate, fecha, likes,
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
                l_content.append(opinion.find_element_by_xpath('.//p').text)
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


    def verificationNewOpinions(self, df):
        """
        Dentro de la seccion "Ver todas las opiniones" pero antes de extraer las opiniones, verifico que sean
        opiniones nuevas (es decir, que no las haya extraido)

        :param df: DataFrame cuya unidad de analisis es una opinion y las columnas son id_publicacion, titulo, content,
        rate, fecha, likes, dislikes
        :return: True si son opiniones nuevas, o bien, False en caso que sean repetidas
        """
        # A priori, asumo que la opinion es nueva
        bool = True

        # Extraigo la primera opinion
        prim_opinion = self.driver.find_element(By.XPATH, '//div[@class="infinite-scroll-component "]/article/p').text

        # Obtengo lista de opiniones extraidas
        opiniones_extraidas = df['content']

        # Veo si la primera opinion ya fue extraida
        if prim_opinion in opiniones_extraidas:
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
            self.driver.quit()

        # Para facilitar la extraccion, convierto el codigo html de la pagina de la publicacion en un objeto de la
        # clase BeautifulSoup
        pageSource = self.driver.page_source
        bs = BeautifulSoup(pageSource, "html.parser")

        # EXTRAIGO VALOR DE PRECIO
        d['precio'] = bs.find('div',{'class':"ui-pdp-price__second-line"})\
            .find('span',{'class':"andes-money-amount__fraction"}).text

        # EXTRAIGO VALORES DE CAMPOS ESPECIFICOS
        # Por campo especifico
        for campo_especifico in campos_especificos:

            # Obtengo el tag, si existe, donde esta el atributo (en particular, uno de los que me interesa). Puede
            # encontrarse en la seccion "Caracteristicas principales", o bien, en "Otras caracteristicas"
            attr = bs.find('th', text=campo_especifico)
            attr_otras_carac = bs.find('span', {'class':"ui-pdp-color--BLACK ui-pdp-size--XSMALL ui-pdp-family--BOLD"},
                                       text=campo_especifico)

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


    def getIdPublicacion(self):
        """
        Estando dentro de una publicacion de Mercado Libre, busca automaticamente el id que identifica como unica
        a dicha publicacion.

        :return: id de la publicacion (en formato string)
        """

        # Implicit wait
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//meta[@property="og:url"]')))
        finally:
            self.driver.quit()

        # Obtengo la url de la publicacion
        url = self.driver.find_element(By.XPATH, '//meta[@property="og:url"]').get_attribute('content')

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