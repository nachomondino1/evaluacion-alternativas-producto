from selenium import webdriver
from MercadoLibreApi import MercadoLibreApi
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib.request import urlopen


class Product():
    """ A simple model of a Mercado Libre's Product """

    def __init__(self, nombre, HomePageUrl=None, nombre_subcat=None, id_subcat=None, atributos = None):
        """
        Defino atributos de clase Product. Las caracteristicas que tendra tod@ producto

        :param nombre: Nombre del producto
        :param HomePageUrl: Pagina Principal de Mercado Libre para ese producto
        :param nombre_subcat: Nombre de subcategoria de productos a la que pertenece el producto
        :param id_subcat: Id de subcategoria de productos a la que pertenece el producto
        :param atributos: Lista de atributos mas relevantes del producto
        """
        self.nombre = nombre
        self.HomePageUrl = HomePageUrl
        self.nombre_subcat = nombre_subcat
        self.id_subcat = id_subcat
        self.atributos = atributos


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
        self.HomePageUrl = self.getHomePageUrl()

        # Implemento BeatifulSoup para acceder el codigo html de la pagina sin que se me abra el Chrome...
        html = urlopen(self.HomePageUrl)
        bs = BeautifulSoup(html, 'html.parser')

        # Valido la busqueda solo si encuentro subcategoria del producto
        tag_nombre_subcat = bs.find('div', {'class': "ui-search-breadcrumb"}).find("meta", {"content": "2"})
        if tag_nombre_subcat == None:  # Antes buscaba solo si habia hasta el tag "ol" pero habia BUSQUEDAS QUE SON DE UNA SUBCATEGORIA Y EN LA HOMEPAGE SOLO APARECE SU CATEGORIA ppal y no la subcategoria... POR EJ:'comida preparada'  Lo podria solucionar en validacionBusqueda() buscando no solo el tag ol sino buscando el segundo tag li
            print('Busqueda muy amplia, por favor sea mas especifico.', end=' ')
            self.nombre = str(input("Ingrese producto a buscar: "))

            # Funcion recursiva, hasta que la busqueda no sea acotada, sigue pidiendo ingreso de producto a buscar
            self.validacionBusqueda()

        # Actualizo atributo "nombre subcategoria" del producto
        self.nombre_subcat = tag_nombre_subcat.find_previous_sibling().attrs['title']

        return True


    def getHomePageUrl(self):
        """
        Busca URL de la Pagina principal de Mercado Libre de un producto (a partir del nombre de este)

        :return: Url en formato string (string pues asi es como lo necesita el driver.get(url))
        """

        # Implemento reglas que  siguen las url de mercado libre tras introducir un producto en su barra de busquedas
        a = self.nombre.replace(" ", "-")
        b = self.nombre.replace(" ", "%20")

        # Defino url del producto agregando las reglas
        url = 'https://listado.mercadolibre.com.ar/' + a + "#D[A:" + b + "]"
        return url


    def getAtributos(self):
        """
        Obtiene los atributos de un producto, es decir, las caracteristicas tecnicas principales.
        En una primera instancia, llama a la API de Meli para obtener los atributos. Si son pocos, agrega atributos
        que aparecen en seccion "Otras caracteristicas" de las publicaciones.

        :return: Lista de atributos relevantes para un producto
        """

        # Obtengo datos de las categorias, sus id y sus subcategorias usando la API de mercado libre
        api = MercadoLibreApi()
        df_categorias = api.getCategoriasID()

        # Extraigo fila del df de la subcategoria del producto
        datos_subcategoria = df_categorias[df_categorias.nombre_subcategoria == self.nombre_subcat]

        # De dicha fila me interesa solo la columna del id (numero 2)
        self.id_subcat_prod = datos_subcategoria.iloc[0, 2]

        # Segun la subcategoria del producto, busco sus atributos
        # este proceso tarda mucho, seria ideal que se corra independiente de programa (main.py) pero no lo pude hacer en categorias.py
        atributos = api.getAtributosSubcategoria(self.id_subcat_prod)
        print('atributos:', atributos)

        # Si la subcategoria tiene pocos atributos
        if len(atributos) < 5:
            # Le agrego atributos de seccion "Otras caracteristicas"
            attr_otras_carac = self.getAttrOtrasCarac()
            for attr in attr_otras_carac:
                atributos.append(attr)

        self.atributos = atributos

        return True


    def getAttrOtrasCarac(self):
        """
        Obtiene atributos de un producto mas frecuentes en seccion "Otras caracteristicas" de las publicaciones de
        Mercado Libre.

        :return: Lista de atributos mas frecuentes en seccion "Otras caracteristicas"
        """
        # Inicializo un nuevo driver que correra por detras (no abre Web Browser)
        driver = webdriver.PhantomJS(
            executable_path='/Users/nachomondino/PycharmProjects/Utils/web_scraping_browsers/phantomjs-2.1.1-macosx/bin/phantomjs')

        # Inicializo variables
        d = {}  # diccionario donde guardare los atributos y su frecuencia
        atributos = []  # lista donde guardare los atributos
        l_url_publicaciones = [] #  lista vacia en donde guardare los links de las publicaciones

        # Inicializo parametros
        c = 10  # cantidad de publicaciones a visitar
        f = 0.75  # flexibilidad para aceptar atributos

        # Ingreso a Pagina Principal del producto a buscar
        driver.get(self.HomePageUrl)

        # Busco todos los tags que contienen un link a una publicacion
        # No le puedo hacer get_attribute al ser mas de un elemento
        tag_urls_publicaciones = driver.find_elements(By.XPATH, '//div[@class="ui-search-result__image"]/a')

        # Recorro cada tag (cada uno contiene un link)
        for tag_url in tag_urls_publicaciones:
            # Obtengo el atributo href (que es el url) del tag y lo guardo en la lista
            l_url_publicaciones.append(tag_url.get_attribute("href"))

        for publicacion in l_url_publicaciones[:c]:

            # Ingreso a publicacion
            driver.get(publicacion)

            # Obtengo los tags donde se ubican todos los atributos de "Otras caracteristicas"
            tags_attrs = driver.find_elements(By.XPATH,
                                              '//span[@class="ui-pdp-color--BLACK ui-pdp-size--XSMALL ui-pdp-family--BOLD"]')

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
        # Obtener los atributos de mayor frecuencia que al menos este en un 75% de las publicaciones
        for key in d.keys():
            if d[key] > (c * f):
                atributos.append(key)
                print("AGREGADO:", key)
            else:
                print("Desechado:", key)

        # print('atributos:', atributos)
        return atributos