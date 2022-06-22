# Importo librerias
import pandas as pd

from p1_data_understanding.utils.web_scraping.crawler import Crawler
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup


class MercadoLibreCrawler(Crawler):
    """ A tool to extract data from Mercado Libre using Web Scraping """

    def __init__(self, driver):
        """Initialize attributes of the parent class."""
        super().__init__(driver)  # si dejase de ser hija de Crawler(), haria self.driver = driver

    def get_publications_url(self):
        """
        Obtiene las URLs de cada una de las publicaciones de una pagina principal de Mercado Libre
        :return: Lista de URLs de las publicaciones de una pagina principal
        """
        # DEFINO LISTA VACIA DONDE GUARDARE LAS URLs DE LAS PUBLICACIONES
        l_url_publicaciones = []

        # ESPERO HASTA ENCONTRAR LOS TAGS QUE CONTIENEN LAS URLs
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="ui-search-result__image"]/a')))  # imagen de primera publicacion de la pagina

        # FINALMENTE
        finally:
            # OBTENGO LOS TAGS
            tag_urls_publicaciones = self.driver.find_elements(By.XPATH, '//div[@class="ui-search-result__image"]/a')  # No le puedo hacer get_attribute al ser mas de un elemento

            # POR CADA TAG
            for tag_url in tag_urls_publicaciones:

                # OBTENGO URL
                l_url_publicaciones.append(tag_url.get_attribute("href"))  # es el valor del atributo href del tag

            return l_url_publicaciones

    def get_pagination_url(self):
        """
        Obtiene, si existe, la URL a la siguiente pagina principal de Mercado Libre
        :return: URL de la siguiente pagina de Mercado Libre (en formato string), o bien, None si no la encontro
        """
        # SI EXISTE SIGUIENTE PAGINA
        try:
            # OBTENGO URL DE LA SIGUIENTE PAGINA
            url_next_page = self.driver.find_element(By.XPATH,
                '//li[@class="andes-pagination__button andes-pagination__button--next"]/a').get_attribute('href')

        # SI NO EXISTE SIGUIENTE PAGINA
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
        # SI TIENE BOTON "VER TODAS LAS OPINIONES"
        try:
            # OBTENGO URL DE "VER TODAS LAS OPINIONES"
            url = self.driver.find_element(By.XPATH, '//a[@class="andes-button ui-review-button__action andes-button--small andes-button--transparent"]').get_attribute("href")
            print("URL 'Ver todas las opiniones': ", url)

        # SI NO TIENE BOTON "VER TODAS LAS OPINIONES"
        except NoSuchElementException:

            # SETEO URL A NONE
            url = None

        return url

    def get_publication_opinions_data(self, id_publicacion):
        """
        Extrae opiniones de seccion "Ver todas las opiniones" dentro de una publicacion de Mercado Libre
        :param id_publicacion: Identificador de cada publicacion
        :return: Diccionario cuyas keys son los nombres de los campos a extraer (id y opinion) y los values son una
        lista (pues una publicacion tiene varias opiniones) de valores para ese campo. Uso diccionario por la facilidad
        que representa  transformarlo en fila/s de un DataFrame.
        """
        # DEFINO VARIABLES
        df = pd.DataFrame(columns=['id_alternativa', 'opinion'])  # Dataframe a retornar

        # OBTENGO TAGS QUE CONTIENEN UNA OPINION
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@id="reviews-capability.desktop"]//div[@class="infinite-scroll-component "]//article')))
        finally:
            tags_opiniones = self.driver.find_elements(By.XPATH, '//div[@id="reviews-capability.desktop"]//div[@class="infinite-scroll-component "]//article')

        # EXTRAIGO OPINIONES DE CADA TAG
        # Por cada tag
        for tag in tags_opiniones:

            # Si tiene valor para todos los campos a extraer
            try:
                # EXTRAIGO TODOS LOS CAMPOS
                # Extraigo Title
                # title = tag.find_element(By.XPATH, './/h3').text

                # Extraigo Opinion
                opinion = tag.find_element(By.XPATH, './/p').text  # EXTRAE LO QUE HAY DE TEXTO EN EL SPAN POR ESO EXTRAE EL "HACE..."

                # Extraigo Rate
                # stars = tag.find_elements_by_class_name("ui-review-view__comments__review-comment__rating__star")
                # num_stars = 0
                # Recorro cada una de las 5 estrellas
                # for star in stars:
                #     if star.find_element_by_tag_name("path").get_attribute("fill") == "#3483FA":
                #         num_stars += 1
                #     else:
                #         # Dejo de recorrer las estrellas al encontrar la primera que no ha sido llenada
                #         break

                # Extraigo Likes y dislikes
                # likes = int(tag.find_element(By.XPATH, './/button[@data-testid="like-button"]').text)
                # dislikes = int(tag.find_element(By.XPATH, './/button[@data-testid="dislike-button"]').text)

                # Guardo opinion y sus campos
                df.loc[len(df)] = [id_publicacion, opinion]  # [id_publicacion, opinion, title, rate, likes, dislikes]

            # SI NO TIENE VALOR PARA AL MENOS UNO DE LOS CAMPOS A EXTRAER
            except NoSuchElementException:
                # IMPRIMO MENSAJE DE FALLA
                print("Fallo extraccion de opinion. Pudo haber cambio el codigo html de la pagina (como ya ha pasado)")
        return df

    '''
    def get_publication_opinions_data(self, id_publicacion):
        """
        Extrae opiniones de seccion "Ver todas las opiniones" dentro de una publicacion de Mercado Libre
        :param id_publicacion: Identificador de cada publicacion
        :return: Diccionario cuyas keys son los nombres de los campos a extraer (id y opinion) y los values son una
        lista (pues una publicacion tiene varias opiniones) de valores para ese campo. Uso diccionario por la facilidad
        que representa  transformarlo en fila/s de un DataFrame.
        """
        # DEFINO VARIABLES
        campos_a_extraer = ['id_alternativa', 'opinion']
        l_id_alternativa, l_opinion = [], []  # lista por cada campo a extraer. Dentro guardare un valor por cada opinion de la publicacion
        d = {}  # diccionario en donde guardare las listas con los datos extraidos

        # OBTENGO TAGS QUE CONTIENEN UNA OPINION
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@id="reviews-capability.desktop"]//div[@class="infinite-scroll-component "]//article')))
        finally:
            tags_opiniones = self.driver.find_elements(By.XPATH, '//div[@id="reviews-capability.desktop"]//div[@class="infinite-scroll-component "]//article')

        # EXTRAIGO OPINIONES DE CADA TAG
        # Por cada tag
        for tag in tags_opiniones:

            # Si tiene valor para todos los campos a extraer
            try:
                # EXTRAIGO TODOS LOS CAMPOS
                # Extraigo Title
                # l_title.append(tag.find_element(By.XPATH, './/h3').text)

                # Extraigo Opinion
                l_opinion.append(tag.find_element(By.XPATH, './/p').text)  # EXTRAE LO QUE HAY DE TEXTO EN EL SPAN POR ESO EXTRAE EL "HACE..."

                # Extraigo Rate
                # stars = tag.find_elements_by_class_name("ui-review-view__comments__review-comment__rating__star")
                # num_stars = 0
                # Recorro cada una de las 5 estrellas
                # for star in stars:
                #     if star.find_element_by_tag_name("path").get_attribute("fill") == "#3483FA":
                #         num_stars += 1
                #     else:
                #         # Dejo de recorrer las estrellas al encontrar la primera que no ha sido llenada
                #         break
                # l_rate.append(num_stars)

                # Extraigo Likes y dislikes
                # l_likes.append(int(tag.find_element(By.XPATH, './/button[@data-testid="like-button"]').text))
                # l_dislikes.append(int(tag.find_element(By.XPATH, './/button[@data-testid="dislike-button"]').text))

            # SI NO TIENE VALOR PARA AL MENOS UNO DE LOS CAMPOS A EXTRAER
            except NoSuchElementException:
                # IMPRIMO MENSAJE DE FALLA
                print("Fallo extraccion de opinion. Cuidado pudo haber cambio el codigo html de la pagina (como ya ha "
                      "pasado) ")

        # GUARDO DATOS EXTRAIDOS
        # Creo lista de id_publicacion segun la cantidad de opiniones
        l_id_alternativa = [id_publicacion] * len(l_opinion)
        ''Reemplace por linea de arriba pero no lo probe
        for i in range(len(l_opinion)):  # podria haber puesto cualquier campo en lugar de title
            l_id_alternativa.append(id_publicacion)
        ''

        # Creo lista que contiene todas las listas con los datos extraidos
        data = [l_id_alternativa, l_opinion]

        # Guardo los datos propiamente
        for i in range(len(campos_a_extraer)):
            d[campos_a_extraer[i]] = data[i]
        return d
        '''

    def are_opinions_new(self, df_opi):
        """
        Identifico si las opiniones, proximas a extraer de la seccion "Ver todas las opiniones", son nuevas o no.
        :param df_opi: Dataframe. Unidad de analisis: opinion. Columnas: id_alternativa y opinion.
        :return: True si las opiniones nuevas, o bien, False en caso que sean repetidas o que falle en extraccion de
        primera opinion
        """
        l_prim_opiniones = []
        ids = df_opi['id_alternativa'].unique()  # Lista de ids unicos ya extraidos

        for id_alt in ids:
            df_opi_por_id= df_opi[df_opi['id_alternativa'] == id_alt]  # Opiniones de id
            prim_opinion = df_opi_por_id.loc[list(df_opi_por_id.index)[0], 'opinion']  # Primera opinion del id
            l_prim_opiniones.append(prim_opinion)

        # SI LOGRO EXTRAER PRIMERA OPINION
        try:
            # Extraigo primera opinion de la publicacion
            prim_opinion = self.driver.find_element(By.XPATH, '//div[@class="infinite-scroll-component "]//p').text
            # print("Primera opinion", prim_opinion)

            # Si la opinion es nueva
            if prim_opinion not in l_prim_opiniones:
                return True

            # Si la opinion es repetida
            else:
                return False

        # SI NO LOGRE EXTRAER PRIMERA OPINION (no deberia pero puede pasar)
        except NoSuchElementException:
            # imprimo mensaje de falla en extraccion y retorno False
            print("Fallo la verificacion de opiniones nuevas. No se pudo extraer la primera opinion")
            return False

    '''
    def are_opinions_new(self, l_prim_opiniones):
        """
        Identifico si las opiniones, proximas a extraer de la seccion "Ver todas las opiniones", son nuevas o no.
        :param l_prim_opiniones: Lista de primeras opiniones de cada publicacion ya extraida
        :return: True si las opiniones nuevas, o bien, False en caso que sean repetidas o que falle en extraccion de
        primera opinion
        """
        # SI LOGRO EXTRAER PRIMERA OPINION
        try:
            # Extraigo primera opinion de la publicacion
            prim_opinion = self.driver.find_element(By.XPATH,'//div[@class="infinite-scroll-component "]//p').text
            # print("Primera opinion", prim_opinion)

            # Si la opinion es nueva
            if prim_opinion not in l_prim_opiniones:
                return True

            # Si la opinion es repetida
            else:
                return False

        # SI NO LOGRE EXTRAER PRIMERA OPINION (no deberia pero puede pasar)
        except NoSuchElementException:
            # imprimo mensaje de falla en extraccion y retorno False
            print("Fallo la verificacion de opiniones nuevas. No se pudo extraer la primera opinion")
            return False
    '''

    def get_modelo_data(self, id_publicacion, l_atributos):
        """
        Extrae valor del atributo precio y valores de los otros atributos (definidos segun de que producto se trata)
        de una publicacion de Mercado Libre
        :param id_publicacion: Integer. Identificador de publicacion ("id_publicacion")
        :param l_atributos: Lista de atributos del producto. Por ejemplo, "tamano de pantalla" para el producto
        "celulares". Su largo dependera de cada producto.
        :return: Diccionario cuyas keys son cada campo a extraer de una publicacion (no solo son los atributos) y cuyos
        value son el valor que toma el respectivo campo para una publicacion en particular. Uso diccionario por la
        facilidad que representa transformarlo en fila/s de un DataFrame.
        """
        # DEFINO VARIABLES
        df = pd.DataFrame(columns=['id_alternativa', 'precio'] + l_atributos)
        l_valores_atrib = []

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
                precio = bs.find('div', {'class': "ui-pdp-price__second-line"}).find('span', {'class': "andes-money-amount__fraction"}).text

            except NoSuchElementException as error:
                precio = None  # en un futuro podria intentar extraer precio de las que fallan, son muy pocos
                print("Fallo extraccion de precio. {}, existe el XPATH pero no hay texto".format(error))  # creo que lo unico que falla es el text del final, confirmar

            except AttributeError as error:
                precio = None
                print("Fallo extraccion de precio. {}, no existe el XPATH para esta publicacion".format(error))

            # EXTRAIGO VALORES DE CAMPOS ESPECIFICOS PARA LA PUBLICACION CORRESPONDIENTE
            # Por campo especifico de los campos especificos (pasados como parametro)
            for atributo in l_atributos:

                # Obtengo el tag que lo contiene. Este podria estar en seccion "Caracteristicas pricipales" o en
                # "Otras caracteristicas"
                tag_attr = bs.find('th', text=atributo)
                tag_attr_otras_carac = bs.find('span', {'class': "ui-pdp-color--BLACK ui-pdp-size--XSMALL ui-pdp-family--BOLD"}, text=atributo)

                # Si el tag esta en "Ver mas caracteristicas" o "Caracteristicas pricipales"
                if tag_attr is not None:

                    # Guardo el atributo y su valor en el diccionario
                    attr, valor = tag_attr.text, tag_attr.nextSibling.text
                    # print("Atributo:", attr,"Valor:", valor)

                # Si no esta en seccion anterior pero esta en seccion "Otras caracteristicas"
                elif tag_attr_otras_carac is not None:

                    # Guardo el atributo y su valor en el diccionario
                    attr, valor = tag_attr_otras_carac.text, tag_attr_otras_carac.nextSibling.text
                    valor = valor[2:]
                    # print("Atributo:", attr_otras_carac,"Valor:", valor)

                # Si no esta en ningun seccion
                else:
                    # Guardo el atributo con valor None en el diccionario
                    valor = None
                    # print("Atributo:", campo_especifico,"Valor:", None)

                # Guardo atributo y su valor
                l_valores_atrib.append(valor)

            # Guardo fila
            df.loc[len(df)] = [id_publicacion, precio] + l_valores_atrib
            return df

    '''
    def get_modelo_data(self, id_publicacion, l_atributos):
        """
        Extrae valor del atributo precio y valores de los otros atributos (definidos segun de que producto se trata)
        de una publicacion de Mercado Libre
        :param id_publicacion: Integer. Identificador de publicacion ("id_publicacion")
        :param l_atributos: Lista de atributos del producto. Por ejemplo, "tamano de pantalla" para el producto
        "celulares". Su largo dependera de cada producto.
        :return: Diccionario cuyas keys son cada campo a extraer de una publicacion (no solo son los atributos) y cuyos
        value son el valor que toma el respectivo campo para una publicacion en particular. Uso diccionario por la
        facilidad que representa transformarlo en fila/s de un DataFrame.
        """
        # DEFINO DICCIONARIO DONDE GUARDARE DATOS
        data = {'id_alternativa': id_publicacion}  # lo defino con el unico campo que ya extraje previamente

        # ESPERO HASTA QUE APAREZCA LA SECCION "CARACTERISTICAS PRINCIPALES"
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//section[@id="highlighted-specs"]')))

        # FINALMENTE
        finally:
            # OBTENGO CODIGO HTML DE LA PUBLICACION USANDO BEAUTIFUL SOUP
            page_source = self.driver.page_source
            bs = BeautifulSoup(page_source, "html.parser")

            # EXTRAIGO VALOR DE PRECIO PARA LA PUBLICACION CORRESPONDIENTE
            try:
                data['precio'] = bs.find('div', {'class': "ui-pdp-price__second-line"}).find('span', {'class': "andes-money-amount__fraction"}).text

            except NoSuchElementException as error:
                print("Fallo extraccion de precio. {}, existe el XPATH pero no hay texto".format(error)) # creo que lo unico que falla es el text del final, confirmar
                data['precio'] = None  # en un futuro podria intentar extraer precio de las que fallan, son muy pocos

            except AttributeError as error:
                print("Fallo extraccion de precio. {}, no existe el XPATH para esta publicacion".format(error))
                data['precio'] = None

            # EXTRAIGO VALORES DE CAMPOS ESPECIFICOS PARA LA PUBLICACION CORRESPONDIENTE
            # Por campo especifico de los campos especificos (pasados como parametro)
            for atributo in l_atributos:

                # Obtengo el tag que lo contiene. Este podria estar en seccion "Caracteristicas pricipales" o en
                # "Otras caracteristicas"
                tag_attr = bs.find('th', text=atributo)
                tag_attr_otras_carac = bs.find('span',{'class': "ui-pdp-color--BLACK ui-pdp-size--XSMALL ui-pdp-family--BOLD"},text=atributo)

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
                    data[atributo] = None
                    # print("Atributo:", campo_especifico,"Valor:", None)

            # print("Fila a cargar", d)
            return data
    '''

    def get_publication_id(self, url):
        """
        Extrae el id de una publicacion dentro de la URL de esta. En caso que el id no este en la URL, es porque la URL
        no es de las comunes, y por ende, buscare la URL correcta dentro del codigo html de la publicacion. Solo en el
        eventual caso que no encuentra la nueva URL, entonces no encuentra el id.
        :param url: String. URL de una publicacion de Mercado Libre
        :return: String. Id de la publicación, o bien, None si no lo encontro
        """
        # Extriago id de url
        id_pub = self.extract_id_from_url(url)

        # Si no se encontro el id en la url
        if id_pub is None:
            print("No se encontro el id en la url de la publicacion por ser del tipo www.click1.mercado...")

            # Obtengo URL de codigo html de la publicacion
            new_url = self.get_new_url_publication()

            # Si obtuve la URL (puede no encontrarla dentro de la publicacion)
            if new_url is not None:

                # Extraigo id de nueva url
                id_pub = self.extract_id_from_url(new_url)

                # Si no encontre id en nueva url
                if id_pub is None:
                    print("Tampoco se encontro el id dentro de la publicacion")
                    return None

        # retorno id de publicacion
        return id_pub

    def get_new_url_publication(self):
        """
        Extrae URL de la publicacion dentro del codigo html de la propia publicacion
        :return: String con url de la publicacion de Mercado Libre
        """
        # OBTENGO CODIGO HTML DE LA PUBLICACION
        pageSource = self.driver.page_source
        bs = BeautifulSoup(pageSource, 'html.parser')

        # SI LA URL ESTA EN EL CODIGO
        try:
            # EXTRIAGO URL
            new_url = bs.find('meta', {'property': 'og:url'}).attrs['content']
            return new_url

        # SI LA URL NO ESTA EN EL CODIGO
        except:
            # RETORNO NONE
            return None

    def extract_id_from_url(self, url_publicacion):
        """
        Extrae el id de una publicacion dentro de la URL de esta.
        :param url_publicacion: String. URL de una publicacion de Mercado Libre
        :return: String. Id de la publicacion, o bien, None si no lo encontro
        """
        # DEFINO VARIABLES
        reglas = ['p/MLA', 'MLA-']
        id_pub = str()

        # POR REGLA
        for regla in reglas:

            # SI LA REGLA ESTA EN LA URL
            if regla in url_publicacion:

                # OBTENGO URL RESTANTE A PARTIR DEL ID
                idx_ini = url_publicacion.index(regla)
                url_restante = url_publicacion[idx_ini + len(regla):]

                # EXTRAIGO ID DE LA URL RESTANTE
                # Por elemento de la url restante
                for elemento in url_restante:
                    # Si es numero
                    if elemento.isdigit():
                        # Lo guardo
                        id_pub += elemento
                    # Si no es numero
                    else:
                        # dejo de recorrer los elementos de la url pues el id es numerico
                        break

                # RETORNO EL ID
                return id_pub

        # SI LAS REGLAS NO ESTAN EN LA URL, NO ENCONTRE EL ID
        return None

    def get_home_page_url_condition_new(self):  # PRUEBA
        """
        Obtiene URL de pagina principal del producto en Mercado libre filtrando productos de condicion "Nuevo"
        :return: String. URL de la pagina principal del producto (solo publicaciones de condicion "nuevo") en Mercado
        Libre
        """
        # Busco tag de filtros para el producto
        tag_filters = self.driver.find_element(By.XPATH,'//section[@class="ui-search-filter-groups"]')

        # Busco url de alternativas filtradas por Condicion=Nuevo
        url = tag_filters.find_element(By.XPATH, '//a[@aria-label="Nuevo"]').get_attribute("href") # el "." es para que siga desde 'section' aunque al usar la variable tag_filters no es necesario. Los "//" son 2 pues el tag a no es hijo del tag section sino que es hijo de sus hijos (si fuese hijo directo seria una barra "/")
        print(url)
        return url


