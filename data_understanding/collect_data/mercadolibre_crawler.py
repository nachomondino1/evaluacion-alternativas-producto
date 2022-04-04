# Importo librerias
from data_understanding.utils.web_scraping.crawler import Crawler
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib.request import urlopen


class MercadoLibreCrawler(Crawler):
    """ A tool to extract data from Mercado Libre using Web Scraping """

    def __init__(self, driver, producto):
        """Initialize attributes of the parent class."""
        super().__init__(driver)  # si dejase de ser hija de Crawler(), haria self.driver = driver
        self.producto = producto  # Deberia ser un objeto de la clase producto...

    def get_publications_url(self):
        """
        Obtiene las URLs de cada una de las publicaciones de una pagina principal de Mercado Libre

        :return: Lista de URLs de las publicaciones de una pagina principal
        """
        # DEFINO LISTA VACIA DONDE GUARDARE LAS URLs DE LAS PUBLICACIONES
        l_url_publicaciones = []

        # ESPERO HASTA ENCONTRAR LOS TAGS QUE CONTIENEN LAS URLs
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="ui-search-result__image"]/a')))

        # FINALMENTE
        finally:
            # OBTENGO LOS TAGS
            tag_urls_publicaciones = self.driver.find_elements(By.XPATH,
                                                               '//div[@class="ui-search-result__image"]/a')  # No le puedo hacer get_attribute al ser mas de un elemento

            # POR CADA TAG DE LOS TAGS
            for tag_url in tag_urls_publicaciones:

                # OBTENGO URL
                l_url_publicaciones.append(tag_url.get_attribute("href"))  # es el valor del atributo href del tag

            return l_url_publicaciones

    def get_pagination_url(self):
        """
        Obtiene, si existe, la URL a la siguiente pagina principal de Mercado Libre

        :return: URL de la siguiente pagina de Mercado Libre (en formato string), o bien, None si no la encontro
        """
        # INTENTO OBTENER URL DE LA SIGUIENTE PAGINA
        try:
            url_next_page = self.driver.find_element_by_xpath(
                '//li[@class="andes-pagination__button andes-pagination__button--next"]/a').get_attribute('href')
            # url_next_page = driver.find_element(By.XPATH, '//a[contains(@href, "Desde") and @title = "Siguiente"]').get_attribute('href') #XPATH alternativo

        # SI NO LA ENCONTRE
        except NoSuchElementException:

            # SETEO URL A NONE
            url_next_page = None
            print("NO ENCONTRO SIGUIENTE PAGINA")

        return url_next_page

    def get_ver_todas_las_opiniones_url(self):
        """
        Obtiene, si existe, el URL del boton "Ver todas las opiniones" dentro de una publicacion de Mercado Libre

        :return: URL del boton "Ver todas las opiniones", o bien, None si no existe tal boton
        """
        # INTENTO OBTENER URL DE "VER TODAS LAS OPINIONES"
        try:
            url = self.driver.find_element(By.XPATH, '//div[@class="ui-pdp-reviews__actions__container"]/a') \
                .get_attribute("href")

        # SI NO LA ENCONTRE
        except NoSuchElementException:

            # SETEO URL A NONE
            url = None

        return url

    def get_publication_opinions_data(self, id_publicacion):
        """
        Extrae opiniones de seccion "Ver todas las opiniones" dentro de una publicacion de Mercado Libre

        :param id_publicacion: Identificador de cada publicacion
        :return: Diccionario cuyas keys son los nombres de los campos a extraer (id, titulo, content, rate, fecha,
        likes, dislikes) y los values son una lista (pues una publicacion tiene varias opiniones) de valores para ese
        campo. Uso diccionario por la facilidad que representa  transformarlo en fila/s de un DataFrame.
        """
        # INICIALIZO VARIABLES
        campos_a_extraer = ['id_publicacion', 'title', 'content', 'rate', 'likes', 'dislikes']
        l_id_publicacion, l_title, l_content, l_rate, l_likes, l_dislikes = [], [], [], [], [], []  # lista por cada campo a extraer. Dentro guardare un valor por cada opinion de la publicacion
        d = {}  # diccionario en donde guardare las listas con los datos extraidos

        # OBTENGO TAGS QUE CONTIENEN UNA OPINION
        tags_opiniones = self.driver.find_elements(By.XPATH, '//div[@class="infinite-scroll-component "]//article')

        # POR CADA TAG DE LOS TAGS
        for tag in tags_opiniones:

            # INTENTO EXTRAER TODOS LOS CAMPOS QUE QUIERO
            try:
                # Extraigo Title
                l_title.append(tag.find_element_by_xpath('.//h3').text)

                # Extraigo Content
                l_content.append(tag.find_element_by_xpath(
                    './/p').text)  # EXTRAE LO QUE HAY DE TEXXTO EN EL SPAN POR ESO EXTRAE EL "HACE..."

                # Extraigo Rate
                stars = tag.find_elements_by_class_name("ui-review-view__comments__review-comment__rating__star")
                num_stars = 0
                # Recorro cada una de las 5 estrellas
                for star in stars:
                    if star.find_element_by_tag_name("path").get_attribute("fill") == "#3483FA":
                        num_stars += 1
                    else:
                        # Dejo de recorrer las estrellas al encontrar la primera que no ha sido llenada
                        break
                l_rate.append(num_stars)

                # Extraigo Likes y dislikes
                l_likes.append(int(tag.find_element_by_xpath('.//button[@data-testid="like-button"]').text))
                l_dislikes.append(int(tag.find_element_by_xpath('.//button[@data-testid="dislike-button"]').text))

            # FALLO EXTRACCION DE ALGUN CAMPO
            except NoSuchElementException:
                print("Fallo extraccion de al menos un campo. Probablemente cambio el codigo html de la pagina "
                      "(como ya ha pasado) ")
                pass

        # GUARDO DATOS EXTRAIDOS
        # Creo lista de id_publicacion segun la cantidad de opiniones
        for i in range(len(l_title)):  # podria haber puesto cualquier campo en lugar de title
            l_id_publicacion.append(id_publicacion)

        # Creo lista que contiene todas las listas con los datos extraidos
        data = [l_id_publicacion, l_title, l_content, l_rate, l_likes, l_dislikes]

        # Guardo los datos propiamente
        for i in range(len(campos_a_extraer)):
            d[campos_a_extraer[i]] = data[i]

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
            prim_opinion = self.driver.find_element(By.XPATH,'//div[@class="infinite-scroll-component "]//p').text
            # print("Primera opinion", prim_opinion)

            # Si la opinion es nueva, return True
            if prim_opinion not in l_prim_opiniones:
                return True

            # La opinion es repetida, return False
            else:
                return False

        # Si no lo encontro (no deberia pero puede pasar), retorno False
        except NoSuchElementException:
            print("Fallo la verificacion de opiniones nuevas. No se pudo extraer la primera opinion")
            return False

    def get_modelo_data(self, id_publicacion, campos_especificos):
        """
        De una sola publicacion, extrae el precio de ésta y, segun el producto, cada campo especifico. Por ejemplo,
        para publicaciones del producto "celulares", algunos campos especificos pueden ser tamaño de pantalla,
        resolucion de camara, entre otros.

        :param id_publicacion: Identificador de publicacion (unico cmapo previamente extraiado)
        :param campos_especificos: Lista de campos especificos (o "atributos") del producto de Mercado Libre que deseo
        extraer. Por ejemplo, "tamano de pantalla" para el producto "celulares". Su largo dependera de cada producto.
        :return: Diccionario cuyas keys son cada campo a extraer de una publicacion (no solo son los atributos) y cuyos
        value son el valor que toma el respectivo campo para una publicacion en particular. Uso diccionario por la
        facilidad que representa transformarlo en fila/s de un DataFrame.
        """
        # DEFINO DICCIONARIO DONDE GUARDARE DATOS. AGREGO EL UNICO CAMPO PREVIAMENTE EXTRAIDO.
        data = {'id_publicacion': id_publicacion}

        # ESPERO HASTA QUE APAREZCA LA SECCION "CARACTERISTICAS PRINCIPALES"
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//section[@id="highlighted-specs"]')))

        # FINALMENTE
        finally:
            # OBTENGO CODIGO HTML DE LA PUBLICACION USANDO BEAUTIFUL SOUP
            page_source = self.driver.page_source
            bs = BeautifulSoup(page_source, "html.parser")

            # EXTRAIGO VALOR DE PRECIO PARA LA PUBLICACION CORRESPONDIENTE
            try:
                data['precio'] = bs.find('div', {'class': "ui-pdp-price__second-line"}).find('span', {'class': "andes-money-amount__fraction"}).text

            except NoSuchElementException as e:
                print("Fallo extraccion de precio. {}, existe el XPATH pero no hay texto") # creo que lo unico que falla es el text del final, confirmar
                data['precio'] = None  # en un futuro podria intentar extraer precio de las que fallan, son muy pocos

            except AttributeError as error:
                print("Fallo extraccion de precio. {}, no existe el XPATH para esta publicacion".format(error))
                data['precio'] = None

            # EXTRAIGO VALORES DE CAMPOS ESPECIFICOS PARA LA PUBLICACION CORRESPONDIENTE
            # Por campo especifico de los campos especificos (pasados como parametro)
            for campo_especifico in campos_especificos:

                # Obtengo el tag que lo contiene. Este podria estar en seccion "Caracteristicas pricipales" o en
                # "Otras caracteristicas"
                tag_attr = bs.find('th', text=campo_especifico)
                tag_attr_otras_carac = bs.find('span',
                                               {'class': "ui-pdp-color--BLACK ui-pdp-size--XSMALL ui-pdp-family--BOLD"},
                                               text=campo_especifico)

                # Si el tag esta en "Ver mas caracteristicas" o "Caracteristicas pricipales"
                if tag_attr is not None:

                    # Guardo el atributo y su valor en el diccionario
                    attr, valor = tag_attr.text, tag_attr.nextSibling.text
                    data[attr] = valor
                    # print("Atributo:", attr,"Valor:", valor)

                # Si no esta en seccion anterior pero esta en seccion "Otras caracteristicas"
                elif tag_attr_otras_carac is not None:

                    # Guardo el atributo y su valor en el diccionario
                    attr, valor = tag_attr_otras_carac.text, tag_attr_otras_carac.nextSibling.text
                    data[attr] = valor[2:]
                    # print("Atributo:", attr_otras_carac,"Valor:", valor)

                # Si no esta en ningun seccion
                else:
                    # Guardo el atributo con valor None en el diccionario
                    data[campo_especifico] = None
                    # print("Atributo:", campo_especifico,"Valor:", None)

            # print("Fila a cargar", d)
            return data

    def get_publication_id(self, url_publicacion):
        """
        Extrae el id de una publicacion dentro de la URL de esta. En caso que el id no este en la URL, es porque la URL
        no es de las comunes, y por ende, buscare la URL correcta dentro del codigo html de la publicacion. Solo en el
        eventual caso que no encuentra la nueva URL, entonces no encuentra el id.

        :param url_publicacion: URL de una publiacacion de Mercado Libre (en formato string)
        :return: id de la publicacion (en formato string), o bien, None si no lo encontro
        """
        # DEFINO REGLAS CON LAS QUE EXTRAER EL ID Y VARIABLE DONDE LO GUARDARE
        regla1, regla2 = 'p/MLA', 'MLA-'
        id_pub = str()

        # SI LA URL NO CONTIENE EL ID (URL de la forma "www.click1.mercadolibre...")
        if (regla1 not in url_publicacion) and (regla2 not in url_publicacion):
            print("URL de la forma www.click1.mercadolibre... ")

            # INTENTO REEMPLAZAR LA URL POR LA URL CORRECTA
            try:
                pageSource = self.driver.page_source
                bs = BeautifulSoup(pageSource, 'html.parser')
                url_publicacion = bs.find('meta', {'property': 'og:url'}).attrs['content']
                print("LA URL DE LA PUBLICACION ES CLICK PERO ENCONTRE LA URL DENTRO DE LA PAGINA")

            # SI NO ENCONTRE LA URL CORRECTA
            except:
                # RETORNO NONE (no encontre el id de la publicacion)
                # Defino el id como None al no encontrar la URL del cual extraerlo
                print("LA URL DE LA PUBLICACION ES CLICK Y ENCIMA NO ENCONTRE LA URL DENTRO DE LA PAGINA")
                return None

        # BUSCO EL ID DENTRO DE LA URL A PARTIR DE LAS REGLAS
        # Busco indice donde comienza el id en pubs que siguen la regla 1 (URLs que son del tipo "...p/MLA<id>")
        try:
            idx_ini = url_publicacion.index(regla1)
            url_restante = url_publicacion[idx_ini + len(regla1):]

        # Busco indice donde comienza el id en pubs que siguen la regla 2 (URLs que son del tipo "...MLA-<id>...")
        except:
            idx_ini = url_publicacion.index(regla2)
            url_restante = url_publicacion[idx_ini + len(regla2):]

        # Desde el indice, recorro cada elemento que sigue en la url (id es de largo variable)
        for elemento in url_restante:

            # Si es numero
            if elemento.isdigit():
                # Lo guardo
                id_pub += elemento
            # Si no es numero
            else:
                # dejo de recorrer los elementos de la url pues el id es numerico
                break

        return id_pub


class Product:
    """ A simple model of a Mercado Libre's Product """

    def __init__(self, nombre, home_page_url=None, nombre_subcat=None, id_subcat=None, atributos=None):
        """
        Defino atributos de clase Product. Las caracteristicas que tendra cualquier producto

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
        Valida la busqueda, es decir, que sea lo suficientemente acotada tal que se refiera a un solo producto en
        particular. En esos casos, Mercado Libre le encuentra una subcategoria de producto.
        En caso que la busqueda no sea valida, pedira un producto hasta el primero que sea valido.

        :return: Funcion sin retorno
        """
        # DEFINO PAGINA PRINCIPAL DEL PRODUCTO
        self.home_page_url = self.get_home_page_url()

        # ACCEDO AL CODIGO HTML DE LA PAGINA PRINCIPAL DEL PRODUCTO
        html = urlopen(self.home_page_url)
        bs = BeautifulSoup(html, 'html.parser')

        # BUSCO TAG DONDE ESTA LA SUBCATEGORIA DEL PRODUCTO
        tag_nombre_subcat = bs.find('div', {'class': "ui-search-breadcrumb"}).find("meta", {"content": "2"})

        # SI NO ENCONTRE EL TAG DE LA SUBCATEGORIA (PRODUCTO NO VALIDO)
        if tag_nombre_subcat is None:  # Antes buscaba solo si habia hasta el tag "ol" pero habia BUSQUEDAS QUE SON DE UNA SUBCATEGORIA Y EN LA HOMEPAGE SOLO APARECE SU CATEGORIA ppal y no la subcategoria... POR EJ:'comida preparada'  Lo podria solucionar en validacionBusqueda() buscando no solo el tag ol sino buscando el segundo tag li
            print('Busqueda muy amplia, por favor sea mas especifico.', end=' ')

            # PIDO NUEVO PRODUCTO
            self.nombre = str(input("Ingrese producto a buscar: "))

            # VUELVO A LLAMAR A LA FUNCION (RECURSIVA)
            self.search_validation()

        else:
            # DEFINO EL NOMBRE DE LA SUBCATEGORIA A LA QUE PERTENECE EL PRODUCTO
            self.nombre_subcat = tag_nombre_subcat.find_previous_sibling().attrs['title']

    def get_home_page_url(self):
        """
        Busca URL de la Pagina principal de un producto en Mercado Libre

        :return: URL en formato string (string pues asi es como lo necesita el driver.get(url))
        """
        # DEFINO REGLAS QUE SIGUE LA URL DE LA PAGINA PRINCIPAL DE UN PRODUCTO EN MERCADO LIBRE
        # si el producto tiene mas de una palabra, reemplazo espacios en blanco por guiones
        reg1 = self.nombre.replace(" ", "-")

        # si el producto tiene mas de una palabra, reemplazo espacios en blanco por string "%20"
        reg2 = self.nombre.replace(" ", "%20")

        return 'https://listado.mercadolibre.com.ar/{}#D[A:{}]'.format(reg1, reg2)

    def get_product_attributes(self):
        """
        Obtiene los atributos mas frecuentes de un producto en las publicaciones de Mercado Libre.

        :return: Lista de atributos mas frecuentes
        """
        # INICIALIZO PARAMETROS DE CORTE, DRIVER Y VARIABLES
        PAG_A_VISITAR = 20  # cantidad de publicaciones a visitar
        PERCENTIL_FREC = 0.2

        # Inicializo un nuevo driver que correra por detras (no abre Web Browser)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Hace que no se abra un web browser en tu compu
        driver = webdriver.Chrome(executable_path='/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data_understanding/collect_data/chromedriver', options=options)  # Defino a Chrome como Web Browser

        # Inicializo variables
        d = {}  # diccionario donde guardare los atributos y su frecuencia
        atributos = []  # lista donde guardare los atributos
        l_url_publicaciones = []  # lista vacia en donde guardare los links de las publicaciones

        # INGRESO A PAGINA PRINCIPAL DEL PRODUCTO A BUSCAR
        driver.get(self.home_page_url)

        # EXTRAIGO URLS DE PUBLICACIONES (recordar que 1 pag tiene entre 50 y 55 pubs)
        # Busco todos los tags que contienen un link a una publicacion
        tag_urls_publicaciones = driver.find_elements(By.XPATH, '//div[@class="ui-search-result__image"]/a')  # No le puedo hacer get_attribute al ser mas de un elemento

        # Recorro cada tag (cada uno contiene un link)
        for tag_url in tag_urls_publicaciones:
            # Obtengo el atributo href (que es el url) del tag y lo guardo en la lista
            l_url_publicaciones.append(tag_url.get_attribute("href"))

        # POR CADA PUBLICACION
        for publicacion in l_url_publicaciones[:PAG_A_VISITAR]:

            # INGRESO A PUBLICACION
            driver.get(publicacion)

            # OBTENGO CODIGO HTML DE LA PUBLICACION USANDO LIBRERIA BEAUTIFULSOUP
            pageSource = driver.page_source
            bs = BeautifulSoup(pageSource, 'html.parser')

            # BUSCO, EN EL CODIGO HTML, TAGS QUE CONTIENEN UN ATRIBUTO
            # para publicaciones tipo 1 (atributos en seccion oculta "Ver mas caracteristicas")
            tags_attrs = bs.find_all('th', {
                'class': "andes-table__header andes-table__header--left ui-vpp-striped-specs__row__column ui-vpp-striped-specs__row__column--id"})

            # para publicaciones tipo 2 (atributos en secciones "Caracteristicas ppales" y "Otras caracteristicas"). Solo si la pub no es de tipo 1
            if len(tags_attrs) == 0:  # un find_all() devuelve una lista vacia en lugar de None
                tags_attrs = bs.find_all('th', {
                    'class': 'andes-table__header andes-table__header--left ui-pdp-specs__table__column ui-pdp-specs__table__column-title'})  # Busco en seccion "Caracteristicas principales"
                tags_attrs2 = bs.find_all('span',
                                          {'class': "ui-pdp-color--BLACK ui-pdp-size--XSMALL ui-pdp-family--BOLD"})  # Busco en seccion "Otras caracteristicas"

                # Uno tags de ambas secciones
                for elemento in tags_attrs2:
                    tags_attrs.append(elemento)

                print("Atributos en otras carac", tags_attrs)

            # POR CADA TAG (que contiene un atributo)
            for tag in tags_attrs:

                # OBTENGO EL ATRIBUTO (es el texto del tag)
                attr = tag.text

                # LE SUMO 1 A SU FRECUENCIA
                # si el atributo es nuevo
                if attr not in d.keys():
                    # Lo agrego y le pongo frecuencia 1
                    d[attr] = 1

                # Si el atributo no es nuevo
                else:
                    # Obtengo su frecuencia y le sumo 1
                    frec = d.get(attr)
                    d[attr] = frec + 1

            # CLICKEO EN BOTON "VOLVER" PARA SALIR DE PUBLICACION
            driver.back()

        # FINALIZADA LA EXTRACCION, CIERRO EL WEB BROWSER AUTOMATICO
        driver.close()

        # SELECCIONO LOS ATRIBUTOS MAS FRECUENTES
        # obtengo frecuencia de corte
        frecuencias = list(d.values())
        frecuencias.sort()
        idx_frec_corte = int(len(frecuencias) * (1 - PERCENTIL_FREC))
        frec_corte = frecuencias[idx_frec_corte]

        # selecciono los atributos mas frecuentes propiamente
        for key in d.keys():
            frec = d[key]

            if frec >= frec_corte:
                atributos.append(key)

        # RESUMO LOS RESULTADOS DE LA EXTRACCION DE ATRIBUTOS
        print("Los {} atributos y su frecuencia (cortare en frec {}):".format(len(d.keys()), frec_corte), d)
        print('Los {} atributos mas frecuentes:'.format(len(atributos)), atributos)

        return atributos
