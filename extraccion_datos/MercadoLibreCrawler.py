# Importo librerias
from utils.web_scraping.crawler import Crawler
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib.request import urlopen


class MercadoLibreCrawler(Crawler):
    """ A tool to extract data from Mercado Libre using Web Scraping """

    def __init__(self, driver, producto):
        """Initialize attributes of the parent class."""
        super().__init__(driver)  # si falla,  # self.driver = driver
        self.producto = producto  # Deberia ser un objeto de la clase producto...


    def get_publications_url(self):
        """
        Obtiene las URLs de cada una de las publicaciones de una pagina principal de Mercado Libre

        :return: Lista de URLs de las publicaciones de una pagina principal
        """
        # Defino lista vacia en donde guardare los links de las publicaciones
        l_url_publicaciones = []

        # Espero hasta que aparece el tag en donde se encuentran las URLs
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="ui-search-result__image"]/a')))

        # finalmente
        finally:
            # Busco los tags que contienen una URL de una publicacion
            tag_urls_publicaciones = self.driver.find_elements(By.XPATH,
                                                               '//div[@class="ui-search-result__image"]/a')  # No le puedo hacer get_attribute al ser mas de un elemento

            # Recorro cada tag (cada uno contiene un link)
            for tag_url in tag_urls_publicaciones:
                # Obtengo el atributo href (que es el url) del tag y lo guardo en la lista
                l_url_publicaciones.append(tag_url.get_attribute("href"))

            return l_url_publicaciones


    def get_pagination_url(self):
        """
        Obtiene, si existe, la URL a la siguiente pagina principal de Mercado Libre

        :return: URL de la siguiente pagina de Mercado Libre (en formato string), o bien, None si no la encontro
        """
        # Intento obtener URL de la siguiente pagina
        try:
            url_next_page = self.driver.find_element_by_xpath(
                '//li[@class="andes-pagination__button andes-pagination__button--next"]/a').get_attribute('href')
            # url_next_page = driver.find_element(By.XPATH, '//a[contains(@href, "Desde") and @title = "Siguiente"]').get_attribute('href') #XPATH alternativo

        # Si no la encuentra, seteo URL a None
        except:
            url_next_page = None
            print("NO ENCONTRO SIGUIENTE PAGINA")

        return url_next_page


    def get_ver_todas_las_opiniones_url(self):
        """
        Obtiene, si existe, el URL del boton "Ver todas las opiniones" dentro de una publicacion de Mercado Libre

        :return: URL del boton "Ver todas las opiniones", o bien, None si no existe tal boton
        """
        # Intento obtener la URL de seccion "Ver todas las opiniones"
        try:
            url = self.driver.find_element(By.XPATH, '//div[@class="ui-pdp-reviews__actions__container"]/a') \
                .get_attribute("href")

        # Si no la encuentra, seteo URL a None
        except:
            url = None

        return url


    def get_publication_opinions_data(self, id_publicacion):
        """
        Extrae opiniones de seccion "Ver todas las opiniones" dentro de una publicacion de Mercado Libre

        :param id_publicacion: Identificador de cada publicacion
        :return: Diccionario cuyas keys son los nombres de los campos a extraer (id, titulo, content, rate, fecha, likes,
        dislikes) y los values son una lista (pues una publicacion tiene varias opiniones) de valores para ese campo.
        Uso diccionario por la facilidad que representa  transformarlo en fila/s de un DataFrame.
        """

        # Inicializo el diccionario en donde guardare las listas con los datos extraidos
        d = {'id_publicacion': None, 'title': None, 'content': None, 'rate': None, 'likes': None, 'dislikes': None}

        # Inicializo una lista por cada campo a extraer. Dentro guardare un valor por cada opinion de la publicacion
        l_id_publicacion, l_title, l_content, l_rate, l_likes, l_dislikes = [], [], [], [], [], []

        # Busco tags que contienen una opinion
        tags_opiniones = self.driver.find_elements(By.XPATH, '//div[@class="infinite-scroll-component "]/article')

        # Recorro cada tag
        for tag in tags_opiniones:

            # Extraigo Title
            try:
                l_title.append(tag.find_element_by_xpath('.//h2').text)
            except:
                l_title.append(None)

            # Extraigo Content
            try:
                l_content.append(tag.find_element_by_xpath(
                    './/p').text)  # EXTRAE LO QUE HAY DE TEXXTO EN EL SPAN POR ESO EXTRAE EL "HACE..."
            except:
                l_content.append(None)

            # Extraigo Rate
            try:
                n = 0
                stars = tag.find_elements_by_class_name("ui-review-view__comments__review-comment__rating__star")

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

            # Extraigo Likes y dislikes
            try:
                l_likes.append(int(tag.find_element_by_xpath('.//a[@data-testid="like-button"]').text))
                l_dislikes.append(int(tag.find_element_by_xpath('.//a[@data-testid="dislike-button"]').text))
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


    def verification_new_opinions(self, l_prim_opiniones):
        """
        Dentro de la seccion "Ver todas las opiniones" pero antes de extraer las opiniones, verifico que sean
        opiniones nuevas (es decir, que no las haya extraido)

        :param l_prim_opiniones: Lista de primeras opiniones de cada publicacion ya visitada
        :return: True si son opiniones nuevas, o bien, False en caso que sean repetidas o que falle en extraccion de
        primera opinion
        """
        # Intento obtener primera opinion de la publicacion
        try:
            prim_opinion = self.driver.find_element(By.XPATH,
                                                    '//div[@class="infinite-scroll-component "]/article/p').text

            print(prim_opinion)

            # Si la opinion es nueva, return True
            if prim_opinion not in l_prim_opiniones:
                return True

            # La opinion es repetida, return False
            else:
                return False

        # Si no lo encontro (no deberia pero puede pasar), retorno False
        except:
            print("Fallo la verificacion de opiniones nuevas. No se pudo extraer la primera opinion")
            return False


    def get_modelo_data(self, id_publicacion, campos_especificos):
        """
        De una sola publicacion, extrae el precio de ésta y, segun el producto, cada campo especifico. Por ejemplo,
        para publicaciones del producto "celulares", algunos campos especificos pueden ser tamaño de pantalla,
        resolucion de camara, entre otros.

        :param id_publicacion: Identificador de publicacion
        :param campos_especificos: Lista de campos especificos (o "atributos") del producto de Mercado Libre que deseo
        extraer. Por ejemplo, "tamano de pantalla" para el producto "celulares". Su largo dependera de cada producto.
        :return: Diccionario cuyas keys son cada campo a extraer de una publicacion (no solo son los atributos) y cuyos
        value son el valor que toma el respectivo campo para una publicacion en particular. Uso diccionario por la
        facilidad que representa transformarlo en fila/s de un DataFrame.
        """
        # Defino el diccionario donde guardare los campos a extraer y su valor para una publicacion. Agrego al
        # diccionario el unico campo que extraigo por fuera de esta funcion
        data = {'id_publicacion': id_publicacion}

        # Implicit wait: hasta que aparezca la seccion "Caracteristicas principales"
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//section[@id="highlighted-specs"]')))

        # finalmente
        finally:
            # Para facilitar la extraccion, convierto el codigo html de la pagina de la publicacion en un objeto de la
            # clase BeautifulSoup
            pageSource = self.driver.page_source
            bs = BeautifulSoup(pageSource, "html.parser")

            # EXTRAIGO VALOR DE PRECIO
            try:
                precio = bs.find('div', {'class': "ui-pdp-price__second-line"}).find('span', {'class': "andes-money-amount__fraction"}).text
                data['precio'] = precio

            except:
                print("No encontro el precio")
                data['precio'] = None  # en un futuro podria intentar extraer precio de las que fallan, son muy pocos

            # EXTRAIGO VALORES DE CAMPOS ESPECIFICOS
            # Por campo especifico
            for campo_especifico in campos_especificos:

                # Obtengo el tag, si existe, donde esta el atributo (en particular, uno de los que me interesa). Puede
                # encontrarse en la seccion "Caracteristicas principales", o bien, en "Otras caracteristicas"
                tag_attr = bs.find('th', text=campo_especifico)
                tag_attr_otras_carac = bs.find('span',
                                           {'class': "ui-pdp-color--BLACK ui-pdp-size--XSMALL ui-pdp-family--BOLD"},
                                           text=campo_especifico)

                # Si existe el tag, entonces guardo el atributo y su valor en el diccionario
                if tag_attr != None:
                    attr, valor = tag_attr.text, tag_attr.nextSibling.text
                    data[attr] = valor
                    # print("Atributo:", attr,"Valor:", valor)

                # Si no existe el tag, puede que se encuentre en "Otras caracteristicas" y entonces guardo el atributo
                # y su valor en el diccionario
                elif tag_attr_otras_carac != None:
                    attr, valor = tag_attr_otras_carac.text, tag_attr_otras_carac.nextSibling.text
                    data[attr] = valor[2:]
                    # print("Atributo:", attr_otras_carac,"Valor:", valor)

                # Si no existe el tag en ninguna seccion, entonces guardo el atributo con valor None en el diccionario
                else:
                    data[campo_especifico] = None
                    # print("Atributo:", campo_especifico,"Valor:", None)

            # print("Fila a cargar", d)
            return data


    def get_publication_id(self, url_publicacion):
        """
        Extrae el id de una publicacion dentro de la URL de esta. En caso que no este, es porque la URL no es de las
        comunes, y por ende, busca la URL dentro del codigo html de la publicacion. Solo en el eventual caso que no
        encuentra la url, entonces no encontro el id.

        :param url_publicacion: URL de una publiacacion de Mercado Libre (en formato string)
        :return: id de la publicacion (en formato string), o bien, None si no lo encontro
        """
        # Defino reglas con las que extraer el id de la url y variable en la que guardare el id
        id = str()
        regla1 = 'p/MLA'
        regla2 = 'MLA-'

        # Si es una URL de la forma "www.click1.mercadolibre..."
        if (regla1 not in url_publicacion) and (regla2 not in url_publicacion):
            print("URL de la forma www.click1.mercadolibre... ")

            # Reemplazo la URL
            try:
                pageSource = self.driver.page_source
                bs = BeautifulSoup(pageSource, 'html.parser')
                url_publicacion = bs.find('meta', {'property': 'og:url'}).attrs['content']
                print("LA URL DE LA PUBLICACION ES CLICK PERO ENCONTRE LA URL DENTRO DE LA PAGINA")

            # Si no encontro el tag donde esta la URL de la publicacion
            except:
                # Defino el id como None al no encontrar la URL del cual extraerlo
                print("LA URL DE LA PUBLICACION ES CLICK Y ENCIMA NO ENCONTRE LA URL DENTRO DE LA PAGINA")
                return None

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
                id += elemento
            # Si no es numero
            else:
                # dejo de recorrer los elementos de la url pues el id es numerico
                break

        return id


class Product():
    """ A simple model of a Mercado Libre's Product """

    def __init__(self, nombre, home_page_url=None, nombre_subcat=None, id_subcat=None, atributos=None):
        """
        Defino atributos de clase Product. Las caracteristicas que tendra tod@ producto

        :param nombre: Nombre del producto
        :param home_page_url: Pagina Principal de Mercado Libre para ese producto
        :param nombre_subcat: Nombre de subcategoria de productos a la que pertenece el producto
        :param id_subcat: Id de subcategoria de productos a la que pertenece el producto
        :param atributos: Lista de atributos mas relevantes del producto
        """
        self.nombre = nombre
        self.home_page_url = home_page_url
        self.nombre_subcat = nombre_subcat
        self.id_subcat = id_subcat
        self.atributos = atributos


    def search_validation(self):  # ojo fallo cuando puse una busqueda erronea al ppio y luego una bien. Dice que no encontro el XPATH y que nombre_subcat esta haciendo un get attribute a un Nonetype
        """
        Validar la busqueda implica que sea lo suficientemente acotada tal que se refiere a un solo producto en
        particular. En esos casos, Mercado Libre le encuentra una subcategoria de producto.

        :return: ??
        Nombre de subcategoria del producto. Cabe resaltar, que retornara algo solo cuando la busqueda sea
         lo suficientemente acotada tal que Mercado Libre le encontro una subcategoria
        """
        # Obtengo URL semilla (en este caso, la pagina principal de mercado libre)
        self.home_page_url = self.get_home_page_url()

        # Implemento BeatifulSoup para acceder el codigo html de la pagina sin que se me abra el Chrome...
        html = urlopen(self.home_page_url)
        bs = BeautifulSoup(html, 'html.parser')

        # Obtengo tag donde esta la subcategoria del producto
        tag_nombre_subcat = bs.find('div', {'class': "ui-search-breadcrumb"}).find("meta", {"content": "2"})

        if tag_nombre_subcat is None:  # Antes buscaba solo si habia hasta el tag "ol" pero habia BUSQUEDAS QUE SON DE UNA SUBCATEGORIA Y EN LA HOMEPAGE SOLO APARECE SU CATEGORIA ppal y no la subcategoria... POR EJ:'comida preparada'  Lo podria solucionar en validacionBusqueda() buscando no solo el tag ol sino buscando el segundo tag li
            print('Busqueda muy amplia, por favor sea mas especifico.', end=' ')
            self.nombre = str(input("Ingrese producto a buscar: "))

            # Funcion recursiva, hasta que la busqueda no sea acotada, sigue pidiendo ingreso de producto a buscar
            self.search_validation()

        else:
            # Extraigo el nombre de la subcateegoria a la que pertenece el producto
            self.nombre_subcat = tag_nombre_subcat.find_previous_sibling().attrs['title']


    def get_home_page_url(self):
        """
        Busca URL de la Pagina principal de Mercado Libre de un producto (a partir del nombre de este)

        :return: URL en formato string (string pues asi es como lo necesita el driver.get(url))
        """

        # Implemento reglas que  siguen las url de mercado libre tras introducir un producto en su barra de busquedas
        a = self.nombre.replace(" ", "-")
        b = self.nombre.replace(" ", "%20")

        # Defino url del producto agregando las reglas
        url = 'https://listado.mercadolibre.com.ar/' + a + "#D[A:" + b + "]"
        return url


    def get_atributos(self):  # terminar de agregar notas
        """
        Obtiene atributos de un producto mas frecuentes en seccion "Otras caracteristicas" de las publicaciones de
        Mercado Libre.

        :return: Lista de atributos mas frecuentes en seccion "Otras caracteristicas"
        """
        # Inicializo parametros
        pag_a_vis = 20  # cantidad de publicaciones a visitar

        # Inicializo un nuevo driver que correra por detras (no abre Web Browser)
        # Defino a Chrome como Web Browser
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Hace que no se abra un web browser en tu compu
        driver = webdriver.Chrome(
            executable_path='/Users/nachomondino/PycharmProjects/Utils/web_scraping_browsers/chromedriver',
            options=options)

        # Inicializo variables
        d = {}  # diccionario donde guardare los atributos y su frecuencia
        atributos = []  # lista donde guardare los atributos
        l_url_publicaciones = []  # lista vacia en donde guardare los links de las publicaciones

        # Ingreso a Pagina Principal del producto a buscar
        driver.get(self.home_page_url)

        # Busco todos los tags que contienen un link a una publicacion
        # No le puedo hacer get_attribute al ser mas de un elemento
        tag_urls_publicaciones = driver.find_elements(By.XPATH, '//div[@class="ui-search-result__image"]/a')

        # Recorro cada tag (cada uno contiene un link)
        for tag_url in tag_urls_publicaciones:
            # Obtengo el atributo href (que es el url) del tag y lo guardo en la lista
            l_url_publicaciones.append(tag_url.get_attribute("href"))

        for publicacion in l_url_publicaciones[:pag_a_vis]:

            # Ingreso a publicacion
            driver.get(publicacion)

            # Hago bs object del codigo html dentro de la publicacion
            pageSource = driver.page_source
            bs = BeautifulSoup(pageSource, 'html.parser')

            # Publicaciones con atributos en "Ver mas Caracteristicas"
            tags_attrs = bs.find_all('th', {
                'class': "andes-table__header andes-table__header--left ui-vpp-striped-specs__row__column ui-vpp-striped-specs__row__column--id"})

            # Publicaciones con atributos en "Otras  Caracteristicas"
            if len(tags_attrs) == 0:  # un find_all() devuelve una lista vacia en lugar de None
                tags_attrs = bs.find_all('th', {
                    'class': 'andes-table__header andes-table__header--left ui-pdp-specs__table__column ui-pdp-specs__table__column-title'})  # el XPATH no esta en las pub de ver mas carac :
                tags_attrs2 = bs.find_all('span',
                                          {'class': "ui-pdp-color--BLACK ui-pdp-size--XSMALL ui-pdp-family--BOLD"})

                for elemento in tags_attrs2:  # Pruebo unir los tags....
                    tags_attrs.append(elemento)

                print("Atributos en otras carac", tags_attrs)

            # Por cada tag (que contiene un atributo)
            for tag in tags_attrs:

                # Obtengo el atributo (es el texto del tag)
                attr = tag.text

                # Si el atributo es nuevo
                if attr not in d.keys():

                    # Lo agrego y le pongo frecuencia 1
                    d[attr] = 1

                # Si el atributo no es nuevo
                else:
                    # Obtengo su frecuencia y le sumo 1
                    frec = d.get(attr)
                    d[attr] = frec + 1

            # Salgo de publicacion
            driver.back()

        print(d)
        print("Cant de atributos:", len(d.keys()))

        frecuencias = list(d.values())
        frecuencias.sort()

        # Defino parametro de corte
        percentil_frec = 0.2
        idx = int(len(frecuencias) * (1 - percentil_frec))

        j = 0

        frec_corte = frecuencias[idx]
        print("Frec corte", frec_corte)

        for key in d.keys():
            frec = d[key]

            if frec >= frec_corte:
                atributos.append(key)
            else:
                j += 1
                pass

        print('atributos agregados:', atributos, len(atributos))
        print("Cant atrib desechados por frec_corte:", j)

        return atributos


'''
    def get_publication_id(self, url_publicacion):
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
            print("URL de la forma www.click1.mercadolibre... ")

            # Reemplazo la URL
            try:
                # Explicit wait
                # sleep(2) #tal vez no termina de cargar la pagina...

                pageSource = self.driver.page_source
                bs = BeautifulSoup(pageSource, 'html.parser')
                url_publicacion = bs.find('meta', {'property': 'og:url'}).attrs['content']

                print("LA URL DE LA PUBLICACION ES CLICK PERO ENCONTRE LA URL DENTRO DE LA PAGINA")

            # Si no encontro el tag donde esta la URL de la publicacion
            except:
                # Defino el id como None al no encontrar la URL del cual extraerlo
                url_publicacion = None
                id = None
                print("LA URL DE LA PUBLICACION ES CLICK Y ENCIMA NO ENCONTRE LA URL DENTRO DE LA PAGINA")

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

'''







''' Fallido intento de get_URL_paginacion que extraia mientras visitaba cada pagina..

    def alternativa_get_URL_paginacion(self, pag_max): #si funciona, cambiar nombre a get_urls_pag_y_pub()
        """
        Obtiene las URL de las paginas principales de Mercado Libre a visitar

        :return: Lista de URLs de las paginas de Mercado Libre (en formato string)
        """

        # Defino lista donde guardare las URLs
        l_url_paginacion = []

        # Obtengo html de la primera pagina principal
        html = urlopen(self.producto.home_page_url)
        bs = BeautifulSoup(html, 'html.parser')

        # Por cada pagina a visitar
        for i in range(pag_max):

            try:
                url_paginacion = bs.find("li", {'class': 'andes-pagination__button andes-pagination__button--next'}).a.attrs['href']
                l_url_paginacion.append(url_paginacion)

                # Cambio de pagina
                html = urlopen(url_paginacion)
                bs = BeautifulSoup(html, 'html.parser')

            except: # si no hay mas paginas...
                pass

        # verr si dejo esto, es para explicar si no hay mas paginas..
        if len(l_url_paginacion) == pag_max:
            print("En principio, se recorreran {} paginas".format(len(l_url_paginacion)))
        else:
            print("Se deberian recorrer {} pero se recorreran {} paginas pues no hay mas".format(pag_max, len(l_url_paginacion)))

        return l_url_paginacion


    def alternativa_get_URL_pub_y_pag(self, pag_max): #si funciona, cambiar nombre a get_urls_pag_y_pub()
        """
        Obtiene las URL de las paginas principales de Mercado Libre a visitar

        :return: Lista de URLs de las paginas de Mercado Libre (en formato string)
        """

        # Defino lista donde guardare las URLs
        l_url_paginacion = []
        l_url_publicaciones = []

        # Obtengo html de la primera pagina principal
        html = urlopen(self.producto.home_page_url)
        bs = BeautifulSoup(html, 'html.parser')


        # Por cada pagina a visitar
        for i in range(pag_max):

            try:
                url_paginacion = bs.find("li", {'class': 'andes-pagination__button andes-pagination__button--next'}).a.attrs['href']
                l_url_paginacion.append(url_paginacion)

                # pruebo a obtener urls de publicaciones
                tag_urls_publicaciones = bs.find_all('div', {'class', 'ui-search-result__image'})

                for tag_url in tag_urls_publicaciones: # lo tuve que agregar porque falla la busqueda de urls
                    # Obtengo el atributo href (que es el url) del tag y lo guardo en la lista
                    l_url_publicaciones.append(tag_url.a.attrs["href"])

                # Cambio de pagina
                html = urlopen(url_paginacion)
                bs = BeautifulSoup(html, 'html.parser')

            except: # si no hay mas paginas...
                pass

        # verr si dejo esto, es para explicar si no hay mas paginas..
        if len(l_url_paginacion) == pag_max:
            print("En principio, se recorreran {} paginas".format(len(l_url_paginacion)))
        else:
            print("Se deberian recorrer {} pero se recorreran {} paginas pues no hay mas".format(pag_max, len(l_url_paginacion)))

        return l_url_paginacion, l_url_publicaciones
    
'''
