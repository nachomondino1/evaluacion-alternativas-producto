from selenium import webdriver
from MercadoLibreApi import MercadoLibreApi
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib.request import urlopen

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


    def validacionBusqueda(self): # ojo fallo cuando puse una busqueda erronea al ppio y luego una bien. Dice que no encontro el XPATH y que nombre_subcat esta haciendo un get attribute a un Nonetype
        """
        Validar la busqueda implica que sea lo suficientemente acotada tal que se refiere a un solo producto en
        particular. En esos casos, Mercado Libre le encuentra una subcategoria de producto.

        :return: Nombre de subcategoria del producto. Cabe resaltar, que retornara algo solo cuando la busqueda sea
         lo suficientemente acotada tal que Mercado Libre le encontro una subcategoria
        """

        # Obtengo URL semilla (en este caso, la pagina principal de mercado libre)
        self.home_page_url = self.getHomePageUrl()

        # Implemento BeatifulSoup para acceder el codigo html de la pagina sin que se me abra el Chrome...
        html = urlopen(self.home_page_url)
        bs = BeautifulSoup(html, 'html.parser')

        # Valido la busqueda solo si encuentro subcategoria del producto
        tag_nombre_subcat = bs.find('div', {'class': "ui-search-breadcrumb"}).find("meta", {"content": "2"})
        if tag_nombre_subcat == None:  # Antes buscaba solo si habia hasta el tag "ol" pero habia BUSQUEDAS QUE SON DE UNA SUBCATEGORIA Y EN LA HOMEPAGE SOLO APARECE SU CATEGORIA ppal y no la subcategoria... POR EJ:'comida preparada'  Lo podria solucionar en validacionBusqueda() buscando no solo el tag ol sino buscando el segundo tag li
            print('Busqueda muy amplia, por favor sea mas especifico.', end=' ')
            self.nombre = str(input("Ingrese producto a buscar: "))

            # Funcion recursiva, hasta que la busqueda no sea acotada, sigue pidiendo ingreso de producto a buscar
            self.validacionBusqueda()

        # Extraigo el nombre de la subcateegoria a la que pertenece el producto
        nombre_subcat = tag_nombre_subcat.find_previous_sibling().attrs['title']

        return nombre_subcat


    def getHomePageUrl(self):
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


    def getAtributos(self):  # implemento bs porque falla el driver.find_xpath al no estar visible lo que hay que extraer
        """
        # Ex nombre: getAttrAdicionales
        Obtiene atributos de un producto mas frecuentes en seccion "Otras caracteristicas" de las publicaciones de
        Mercado Libre.
        :return: Lista de atributos mas frecuentes en seccion "Otras caracteristicas"
        """
        # Inicializo parametros
        pag_a_vis = 20  # cantidad de publicaciones a visitar
        porcentaje_pub = 0.75  # flexibilidad para aceptar atributos
        frec_min = pag_a_vis * porcentaje_pub

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
            tags_attrs = bs.find_all('th', {'class': "andes-table__header andes-table__header--left ui-vpp-striped-specs__row__column ui-vpp-striped-specs__row__column--id"})
            # RECONTRA OJO, PENSE QUE SI UN BS NO ENCONTRABA EL XPATH DEVOLVIA NONE Y QUE SI HACIE IF BS== NONE DEBERIA DAR TRUE PERO NO. TE DEVUELVE FALSE PUES EL BS ES UNA LISTA VACIA
            # esto pueede ser la puta razon por la que falla varias cosas dee mi codigo comopor ej url_paginacion
            # Al parecer lo que devuelve None es find() y lo que devuelve lista vacia es find_all()

            # Publicaciones con atributos en "Otras  Caracteristicas"
            if len(tags_attrs) == 0: # por ahi no esta funcionando, agrego atributos que estan en "Caracteristicas generales". No entro y deberia haberlo hecho
                tags_attrs = tags_attrs_carac_gen = bs.find_all('th', {'class': 'andes-table__header andes-table__header--left ui-pdp-specs__table__column ui-pdp-specs__table__column-title'}) # el XPATH no esta en las pub de ver mas carac :
                tags_attrs2 = bs.find_all('span',{'class': "ui-pdp-color--BLACK ui-pdp-size--XSMALL ui-pdp-family--BOLD"})

                for elemento in tags_attrs2: #Pruebo unir los tags....
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

        # IMPLEMENTO ELEGIR LOS 10 MAS FRECUENTES y que esten en EL 75% DE LAS PUB
        atrib_desechados = []  # solo para ver que tiro
        frecuencias = list(d.values())
        frecuencias.sort()

        # Defino parametro de corte
        indice_frec_corte = int(len(frecuencias) * 0.8)

        frec_corte = frecuencias[indice_frec_corte]
        print("Frec corte", frec_corte)

        for key in d.keys():
            frec = d[key]
            if (frec >= frec_corte) and (frec >= frec_min):
                atributos.append(key)
            else:
                atrib_desechados.append(key)

        print('atributos agregados:', atributos, len(atributos))
        print('atributos no agregados:', atrib_desechados, len(atrib_desechados))


        '''
        # IMPLEMENTO ELEGIR LOS 10 MAS FRECUENTES (EN LUGAR DE TODOS LOS QUE ESTEN EN EL 75% DE LAS PUB)
        atrib_desechados = [] # solo para ver que tiro
        frecuencias = list(d.values())
        frecuencias.sort()
        frec_corte = frecuencias[len(frecuencias)-10]

        for key in d.keys():
            frec = d[key]
            if frec >= frec_corte:
                atributos.append(key)
            else:
                atrib_desechados.append(key)

        print('atributos:', atributos)
        print('atributos desechados:', atrib_desechados)
        '''

        '''
        # Obtener los atributos de mayor frecuencia que al menos este en un 75% de las publicaciones
        for key in d.keys():
            if d[key] > (c * f):
                atributos.append(key)
                print("AGREGADO:", key)
            else:
                print("Desechado:", key)

        print('atributos:', atributos)
        '''

        return atributos

    '''
    def getAtributos(self): # Esta funcion la deje de usar pues deje de usar la api para la extraccion de atributos. Ahora usare getAtributos() que solo usa WebScraping
        """
        Obtiene los atributos de un producto, es decir, las caracteristicas tecnicas principales.
        En una primera instancia, llama a la API de Meli para obtener los atributos. Si son pocos, agrega atributos
        que aparecen en seccion "Otras caracteristicas" de las publicaciones.

        :return: Lista de atributos relevantes para un producto
        """
        # Defino hiperparametro "cantidad de atributos minimo"
        cant_atrib_min = 8

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
        if len(atributos) < cant_atrib_min:

            # Le agrego atributos de seccion "Otras caracteristicas"
            # attr_otras_carac = self.getAttrOtrasCarac()
            attr_adicionales = self.getAtributosAdicionales()
            for attr in attr_adicionales:
                atributos.append(attr)

            # Saco repetidos (tipicamente Marca y modelo)
            atributos = set(atributos)

        print("Finalmente los atributos son", atributos, len(atributos))

        return atributos

    def getAtributosAdicionales(self):  # implemento bs porque falla el driver.find_xpath al no estar visible lo que hay que extraer
        """
        # Ex nombre: getAttrAdicionales
        Obtiene atributos de un producto mas frecuentes en seccion "Otras caracteristicas" de las publicaciones de
        Mercado Libre.
        :return: Lista de atributos mas frecuentes en seccion "Otras caracteristicas"
        """
        # Inicializo parametros
        pag_a_vis = 20  # cantidad de publicaciones a visitar
        porcentaje_pub = 0.75  # flexibilidad para aceptar atributos
        frec_min = pag_a_vis * porcentaje_pub

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
            # RECONTRA OJO, PENSE QUE SI UN BS NO ENCONTRABA EL XPATH DEVOLVIA NONE Y QUE SI HACIE IF BS== NONE DEBERIA DAR TRUE PERO NO. TE DEVUELVE FALSE PUES EL BS ES UNA LISTA VACIA
            # esto pueede ser la puta razon por la que falla varias cosas dee mi codigo comopor ej url_paginacion
            # Al parecer lo que devuelve None es find() y lo que devuelve lista vacia es find_all()

            # Publicaciones con atributos en "Otras  Caracteristicas"
            if len(tags_attrs) == 0:  # por ahi no esta funcionando, agrego atributos que estan en "Caracteristicas generales". No entro y deberia haberlo hecho
                tags_attrs = tags_attrs_carac_gen = bs.find_all('th', {
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

        # IMPLEMENTO ELEGIR LOS 10 MAS FRECUENTES y que esten en EL 75% DE LAS PUB
        atrib_desechados = []  # solo para ver que tiro
        frecuencias = list(d.values())
        frecuencias.sort()

        # Defino parametro de corte
        indice_frec_corte = int(len(frecuencias) * 0.8)

        frec_corte = frecuencias[indice_frec_corte]
        print("Frec corte", frec_corte)

        for key in d.keys():
            frec = d[key]
            if (frec >= frec_corte) and (frec >= frec_min):
                atributos.append(key)
            else:
                atrib_desechados.append(key)

        print('atributos agregados:', atributos, len(atributos))
        print('atributos no agregados:', atrib_desechados, len(atrib_desechados))

        return atributos
    '''