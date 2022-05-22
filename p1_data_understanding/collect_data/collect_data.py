# Importo librerias
import pandas as pd
import random
from time import sleep
from selenium import webdriver
from p1_data_understanding.collect_data.mercadolibre_crawler import MercadoLibreCrawler
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

################################################ FUNCIONES PRINCIPALES ################################################
def get_product_attributes(home_page_url):
    """
    Obtiene los atributos mas relevantes de un producto.
    :param home_page_url: String que contiene URL de la pagina principal de un producto en Mercado Libre
    :return: Lista de atributos mas relevantes del producto
    """
    # DEFINO VARIABLES
    PAG_A_VISITAR = 20  # cantidad de publicaciones a visitar
    d_attr_frec = {}  # diccionario donde guardare los atributos y su frecuencia

    # INICIALIZO UN DRIVER
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Hace que no se abra un web browser en tu compu
    crawler = MercadoLibreCrawler(driver=webdriver.Chrome(executable_path='/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/p1_data_understanding/collect_data/chromedriver', options=options))  # Defino a Chrome como Web Browser)

    # INGRESO A PAGINA PRINCIPAL DEL PRODUCTO A BUSCAR
    crawler.driver.get(home_page_url)

    # EXTRAIGO URLS DE PUBLICACIONES (recordar que 1 pag tiene entre 50 y 55 pubs)
    l_url_publicaciones = crawler.get_publications_url()

    # POR CADA PUBLICACION
    for publicacion in l_url_publicaciones[:PAG_A_VISITAR]:

        # INGRESO A PUBLICACION
        crawler.driver.get(publicacion)

        # OBTENGO CODIGO HTML DE LA PUBLICACION USANDO LIBRERIA BEAUTIFULSOUP
        pageSource = crawler.driver.page_source
        bs = BeautifulSoup(pageSource, 'html.parser')

        # BUSCO, EN EL CODIGO HTML, TAGS QUE CONTIENEN UN ATRIBUTO
        # para publicaciones tipo 1 (atributos en seccion oculta "Ver mas caracteristicas")
        tags_attrs = bs.find_all('th', {'class': "andes-table__header andes-table__header--left ui-vpp-striped-specs__row__column ui-vpp-striped-specs__row__column--id"})

        # para publicaciones tipo 2 (atributos en secciones "Caracteristicas ppales" y "Otras caracteristicas"). Solo si la pub no es de tipo 1
        if len(tags_attrs) == 0:  # un find_all() devuelve una lista vacia en lugar de None
            tags_attrs = bs.find_all('th', {'class': 'andes-table__header andes-table__header--left ui-pdp-specs__table__column ui-pdp-specs__table__column-title'})  # Busco en seccion "Caracteristicas principales"
            tags_attrs2 = bs.find_all('span', {'class': "ui-pdp-color--BLACK ui-pdp-size--XSMALL ui-pdp-family--BOLD"})  # Busco en seccion "Otras caracteristicas"
            # Uno tags de ambas secciones
            for elemento in tags_attrs2:
                tags_attrs.append(elemento)
            # print("Atributos en otras carac: ", tags_attrs)

        # POR CADA TAG (que contiene un atributo)
        for tag in tags_attrs:

            # OBTENGO EL ATRIBUTO (es el texto del tag)
            attr = tag.text

            # LE SUMO 1 A SU FRECUENCIA
            if attr not in d_attr_frec.keys():  # si el atributo es nuevo
                d_attr_frec[attr] = 1  # Lo agrego y le pongo frecuencia 1
            else:  # Si el atributo no es nuevo
                frec = d_attr_frec.get(attr)  # creo que con un d_attr_frec[attr] += 1 ya es suficiente, probar!!!
                d_attr_frec[attr] = frec + 1  # Obtengo su frecuencia y le sumo 1

        # CLICKEO EN BOTON "VOLVER" PARA SALIR DE PUBLICACION
        crawler.driver.back()

    # FINALIZADA LA EXTRACCION, CIERRO EL WEB BROWSER AUTOMATICO
    crawler.driver.close()

    # SELECCIONO LOS ATRIBUTOS RELEVANTES
    l_atributos = select_relevant_attributes(d_attr_frec)

    return l_atributos

def create_dataframe_alternativas(campos_especificos):
    """
    Crea DataFrame de alternativas con los nombres de las columnas correspondientes y sin filas (vacio).
    Los nombres de las columnas dependeran de cada producto, por lo que, son pasados como parametro.
    :param campos_especificos: Lista de campos especificos (o "atributos") del producto de Mercado Libre que deseo
        extraer. Por ejemplo, "tamano de pantalla" para el producto "celulares". Su largo dependera de cada producto.
    :return: Dataframe "alternativas" con los nombres de las columnas correspondientes y sin filas (vacio)
    """
    # DEFINO LISTA CON CAMPOS QUE SON INDEPENDIENTES DEL PRODUCTO
    campos_a_extraer = ['id_alternativa', 'precio']

    # POR CAMPO ESPECIFICO
    for campos_especifico in campos_especificos:

        # LO AGREGO A LA LISTA ANTERIOR
        campos_a_extraer.append(campos_especifico)

    # CREO DATAFRAME DONDE CADA ELEMENTO DE LA LISTA ES EL NOMBRE DE UNA DE SUS COLUMNAS
    df = pd.DataFrame(columns=campos_a_extraer)

    return df

def data_extractor(df_alt, df_opi, home_page_url):
    """
    Extrae datos de opiniones y de las publicaciones de un producto mediante web scraping y los almacena en los
    DataFrames pasados como parametro. Representa toda la logica de extraccion.
    :param df_alt: DataFrame vacio con columnas id_alternativa, precio y una por cada campo especifico del
    producto.
    :param df_opi: DataFrame vacio con columnas id_alternativa y opinion.
    :return: Dataframes opiniones y alterenativas cargados con los datos extraidos del producto
    """
    # CREO OBJETO DE CLASE MercadoLibreCrawler(), TAL QUE TENGO DISPONIBLE METODOS PARA HACER WEB SCRAPING
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("enable-automation")
    options.add_argument("--headless") # Hace que no se abra un web browser en tu compu
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(executable_path='/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/p1_data_understanding/collect_data/chromedriver', options=options)  # Defino a Chrome como Web Browser
    crawler = MercadoLibreCrawler(driver)

    # DEFINO PARAMETROS DE CORTE, TIEMPOS DE ESPERA Y VARIABLES UTILES
    # Defino parametros de corte de la extraccion
    PORC_MIN_ULT_PUB_EXTRAIDAS, CANT_ULT_PUB, ult_pub_sin_data = 0.1, 30, 0  # param 1: De las ultimas <CANT_ULT_PUB> paginas, pido extraer  datos en al menos <porc_min_ult_pub> de ellas
    pag_num, PAG_MAX = 0, 25  # param 2: Hasta pagina <PAG_MAX>, o bien, hasta la ultima
    no_mas_paginas = 0  # param 3: Hasta la ultima pagina (si hay menos que PAG_MAX)

    # Defino tiempo de espera entre acciones del crawler para humanizarlo y evitar deteccion
    SLEEP_MIN, SLEEP_MAX = 0.5, 2

    # Defino variables utiles
    l_prim_opiniones = []  # lista que guardara las primeras opiniones de cada pub. Ayudara a no extraer opi repetidas
    historico_paginas = []  # lista que guardara un 1 si la pub fue extraida, o bien, 0 (la pub no fue extraida). Ayuda
    # a parametro de corte 2

    # INGRESO A PAGINA PRINCIPAL DE MERCADO LIBRE DEL PRODUCTO
    crawler.driver.get(home_page_url)  # hasta que no se carga toda la pagina, no sigue...

    # POR PAGINA DE PAGINACION
    while (ult_pub_sin_data == 0) and (pag_num < PAG_MAX) and (no_mas_paginas == 0):  # Hasta que los param de corte lo indiquen...

        # EXTRAIGO URLS DE PUBLICACIONES DE LA PAGINA Y URL DE SIGUIENTE PAGINA
        urls_publicaciones = crawler.get_publications_url()
        url_paginacion = crawler.get_pagination_url()
        print("Cantidad de pubs:", len(urls_publicaciones))

        # POR CADA PUBLICACION DE LA PAGINA (tipicamente 1 pagina tiene 50 a 55 publicaciones)
        for url_publicacion in urls_publicaciones:
            print("Publicacion numero:", len(historico_paginas), ". URL:", url_publicacion)  # imprimo nro de pub y url

            pagina_extraida = 0  # A priori, asumo que no pude extraer datos de la publicacion (param de corte 1)

            # CLICKEO EN LA PUBLICACION
            crawler.driver.get(url_publicacion)
            sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))  # Intentando humanizar mis acciones...

            # OBTENGO SU IDENTIFICADOR DE PUBLICACION ("id_publicacion")
            id_alternativa = crawler.get_publication_id(url_publicacion)

            # EXTRAIGO DATOS DE LA PUBLICACION
            d_data_alternativas = crawler.get_modelo_data(id_publicacion=id_alternativa, l_atributos=df_alt.columns[2:])  # excluyo id y precio

            # SI LA ALTERNATIVA ES NUEVA
            if is_alternative_new(df_alt, d_data_alternativas):

                # GUARDO DATOS DE ALTERNATIVA EN DATAFRAME ("df_alternativas")
                df_alt = add_lines_to_dataframe(d_data_alternativas, df_alt)
                print(df_alt)

                # BUSCO EL BOTON "VER TODAS LAS OPINIONES" DENTRO DE LA PUBLICACION
                url_ver_todas_las_opiniones = crawler.get_ver_todas_las_opiniones_url()

                # SI EXISTE EL BOTON (en ese caso, la publicacion tiene opiniones)
                if url_ver_todas_las_opiniones is not None:

                    # CLICKEO EN BOTON "VER TODAS LAS OPINIONES"
                    crawler.driver.get(url_ver_todas_las_opiniones)
                    sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))  # Intentando humanizar mis acciones...

                    # SI LAS OPINIONES SON NUEVAS (pues ≠ publicaciones pueden tener = opiniones)
                    if crawler.are_opinions_new(l_prim_opiniones):

                        pagina_extraida = 1  # Cambio su valor a 1 pues pude extraer datos de la pub (param de corte 1)

                        # HAGO SCROLL DOWN PARA CARGAR TODAS LAS OPINIONES
                        sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))  # Intentando humanizar mis acciones...
                        crawler.ScrollDown()

                        # EXTRAIGO OPINIONES Y LAS GUARDO EN UN DATAFRAME ("df_opiniones")
                        d_opiniones_alternativa = crawler.get_publication_opinions_data(id_alternativa)
                        l_prim_opiniones.append(d_opiniones_alternativa['opinion'][0])  # Guardo la primera opinion de la
                        # publicacion para poder hacer la verificacion de opiniones nuevas
                        df_opi = add_lines_to_dataframe(d_opiniones_alternativa, df_opi)
                        print(df_opi)

                    # SI LAS OPINIONES NO SON NUEVAS (ES DECIR, SE REPITEN)
                    else:
                        # ENTONCES NO EXTRAIGO OPINIONES
                        print("OPINIONES REPETIDAS")

                    # CLICKEO EN BOTON "VOLVER" PARA SALIR DE SECCION "VER TODAS LAS OPINIONES"
                    crawler.driver.back()
                    sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))  # Intentando humanizar mis acciones...

                # SI NO EXISTE EL BOTON "VER TODAS LAS OPINIONES" (pub sin opiniones)
                else:
                    # ENTONCES NO EXTRAIGO OPINIONES
                    print("PUBLICACION SIN OPINIONES")

                # VERIFICO PARAMETRO DE CORTE
                historico_paginas.append(pagina_extraida)  # Agrego un boolean segun si extraje o no la publicacion
                # Si las ultimas publicaciones tienen muy pocos datos
                if ultimas_pub_sin_data(historico_paginas, PORC_MIN_ULT_PUB_EXTRAIDAS, CANT_ULT_PUB):
                    # corto la extraccion de datos (parametro de corte 1)
                    ult_pub_sin_data = True  # parametro de corte 1 (corta si las ultimas publicaciones no tienen datos)
                    break

            # CLICKEO EN BOTON "VOLVER" PARA SALIR DE LA PAGINA DE LA PUBLICACION
            crawler.driver.back()
            print()
            sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))  # Intentando humanizar mis acciones...

        # HAGO CLICK EN SIGUIENTE PAGINA DE PAGINACION
        # Si encontre url de siguiente pagina
        print("Proxima pagina a relevar: ", url_paginacion)
        if url_paginacion is not None:

            # Hago click en la siguiente pagina
            crawler.driver.get(url_paginacion)
            sleep(random.uniform(3, 5))  # Intentando humanizar mis acciones y tambien esperar a carga de nueva pagina
            pag_num += 1  # variable que si llega a <PAG_MAX>, hace cortar la extraccion de datos (parametro de corte 2)

        # Si no encontre la url de la siguiente pagina
        else:
            # Corto la extraccion de datos
            no_mas_paginas = True  # parametro de corte 3

        print(" CAMBIO DE PAGINA ".center(120, '#'))

    # FINALIZADA LA EXTRACCION, CIERRO EL WEB BROWSER AUTOMATICO
    crawler.driver.close()

    # EXPLICO POR QUE CORTO LA EXTRACCION DE DATOS
    explicacion_corte(pag_num, PAG_MAX, ult_pub_sin_data)

    return df_alt, df_opi



################################################ FUNCIONES SECUNDARIAS ################################################
# UTILIZADA EN GET_PRODUCT_ATTRIBUTES()
def select_relevant_attributes(d_attr_frec):
    """
    Selecciono los atributos mas relevantes de todos los atributos posibles del producto
    # Recomendacion: Tener a mano publicaciones del producto para ver que valor toma cada atributo y asi entender de que se trata el atributo
    :param d_attr_frec: Diccionario cuyas keys son cada atributo del producto y sus values son la frecuencia (segun
    frecuencia de aparicion en publicacionse del producto en mercado libre) del respectivo atributo.
    :return: Lista de atributos mas relevantes
    """
    # Defino variables
    frecuencias = list(d_attr_frec.values())
    porc_frec_min = 0.2  # al menos en el 30% de las publicaciones
    l_atributos = []
    print("Los {} atributos y su frecuencia: {}".format(len(frecuencias), d_attr_frec))

    # Por atributo
    for atributo in d_attr_frec.keys():

        # Obtengo porcentaje de frecuencia
        porc_frec = d_attr_frec[atributo] / max(frecuencias)

        # Si su porcentaje de frecuencia es mayor al minimo
        if porc_frec > porc_frec_min:

            # Solicito al administrador si tendra en cuena o no el atributo
            input_admin = int(input("Ingrese 1 si se usara el atributo '{}' de frecuencia {:.2f}%: ".format(atributo.upper(), porc_frec * 100)))

            # Si lo tiene en cuenta
            if input_admin == 1:

                # Guardo atributo
                l_atributos.append(atributo)

    # Resumo los resultados de la extraccion de atributos
    print('Los {} atributos mas relevantes: {}'.format(len(l_atributos), l_atributos))

    return l_atributos


# UTILIZADA EN DATA_EXTRACTOR()
def is_alternative_new(df_alt, new_alt):
    """
    Verifica si una nueva alternativa se repite o no con otra alternativa ya extraida
    :param df_alt: Dataframe alternativas
    :param new_alt: Diccionario con las colummas del dataframe alternativas como keys y sus respectivos valores como
    values.
    :return: True si la nueva alternativa es nueva, de lo contrario, False.
    """
    # Defino variables
    new_id = new_alt['id_alternativa']  # id de la nueva alternativa
    new_atrib = list(new_alt.values())[2:]  # valores de atributos de la nueva alternativa (excluyo id y precio)

    # Por alternativa
    for i in range(len(df_alt)):

        # Defino variables
        id_alt = df_alt.iloc[i, 0]  # id de alternativa
        atrib_alt = list(df_alt.iloc[i, 2:])  # valores de atributos de la alternativa (excluyo id y precio)

        # Si el id de la nueva alternativa es igual al de la alternativa ya cargada
        if new_id == id_alt:
            print("La alternativa tiene el mismo id que una alternativa ya extraida")
            print(new_id, id_alt)
            return False

        # Si los atributos de la nueva alternativa son iguales al de la alternativa ya cargada
        if new_atrib == atrib_alt:
            print("La alternativa tiene los mismos valores de los atributos que una alternativa ya extraida")
            print(new_atrib, atrib_alt)
            return False

    # Si la alternativa nueva no se repite
    return True

def add_lines_to_dataframe(d_data, df):
    """
    Agrega filas a un DataFrame
    :param df: DataFrame (puede estar vacio aunque si o si con los nombres de las columnas)
    :param d_data: diccionario con datos. Sus keys deben ser igual a los nombres de las columnas del dataframe pasado
    como parametro. Sus value pueden ser tanto un solo valor como una lista de valores.
    :return: DataFrame incluyendo datos del diccionario
    """
    # CONVIERTO DICCIONARIO PASADO COMO PARAMETRO A DATAFRAME
    try:
        new_df = pd.DataFrame(data=d_data)
    except:
        new_df = pd.DataFrame(data=d_data, index=[0])

    # CONCATENO EL NUEVO DATAFRAME CON EL DATAFRAME PASADO COMO PARAMETRO
    df = pd.concat([df, new_df])

    return df

def ultimas_pub_sin_data(historico_paginas, porc_min_ult_pub_extraidas, cant_ult_pub):
    """
    Evalua si conviene seguir extrayendo datos o no segun el % de las ultimas x publicaciones en que el crawler extrajo
    datos.
    :param historico_paginas: Lista de 0 y 1. Tiene un 1 por cada publicacion de la cual extrajo datos y un 0 en caso
    contrario
    :param porc_min_ult_pub_extraidas: Porcentaje minimo de las ultimas x publicaciones en que el crawler extrajo
    datos (Float de 0 a 1)
    :param cant_ult_pub: Numero que determina cuantas publicaciones son consideradas como las "ultimas publicaciones"
    :return: True si conviene dejar de extraer datos, o bien, False si conviene continuar extrayendo.
    """
    # DEFINO MINIMO DE PUBLICACIONES A VISITAR
    MIN_PUB_A_VISITAR = 50  # es mas de 50 para que se estabilicen los % de publicaciones extraidas

    # SI YA VISITE AL MENOS <MIN_PUB_A_VISITAR> PUBLICACIONES
    if len(historico_paginas) > MIN_PUB_A_VISITAR:

        # SELECCIONO LOS BOOLEAN DE LAS ULTIMAS <CANT_ULT_PUB> PUBLICACIONES
        ultimas_paginas = historico_paginas[-cant_ult_pub:]
        # print("Ultimas {}:".format(cant_ult_pag), ultimas_paginas)

        # DEFINO CANTIDAD x DE LAS ULTIMAS <CANT_ULT_PUB> PUBS EN QUE LOGRE EXTRAER DATOS
        cant_ult_pag_extraidas = sum(ultimas_paginas)

        # DEFINO PORCENTAJE DE LAS ULTIMAS <CANT_ULT_PUB> PUBLICACIONES EN QUE LOGRE EXTRAER DATOS
        porc_ult_pub_extraidas = cant_ult_pag_extraidas / cant_ult_pub
        # print("Porcentaje de extraidas de ultimas", porc_ult_pag_extraidas)

        # SI EL PORCENTAJE ANTERIOR ES MENOR AL PORCENTAJE MINIMO
        if porc_ult_pub_extraidas < porc_min_ult_pub_extraidas:

            # DEJO DE EXTRAER DATOS
            print("Dejare extraccion de datos pues el Crawler ingreso al {} de las ultimas {} paginas".format(
                porc_ult_pub_extraidas, cant_ult_pub))
            return True

    return False

def explicacion_corte(pag_num, pag_max, ult_pub_sin_data):
    """
    Imprime por pantalla la razon por la que finalizo la extraccion de datos
    :param pag_num: Cantidad de paginas visitadas (de paginacion)
    :param pag_max: Cantidad de pagonas maximas a visitas (de paginacion)
    :param ult_pub_sin_data: Boolean, 1 si extraje muy pocos datos de las ultimas publicaciones y 0 en caso contrario
    :return: funcion sin return
    """
    # Si extraje pocos datos de las ultimas paginas (Parametro de corte 1)
    if ult_pub_sin_data == 1:
        # Imprimo mensaje
        print("Corto pues el Crawler ingreso a muy pocas de las publicaciones")

    # Si alcance el maximo de paginas a visitar (de paginacion) (Parametro de corte 2)
    elif pag_num == pag_max:
        # Imprimo mensaje
        print("Corto porque se visitaron las {} primeras paginas".format(pag_max))

    # Si no hay siguiente pagina (de paginacion) (Parametro de corte 3)
    else:
        # Imprimo mensaje
        print("Corto por no haber mas paginas. Se recorrieron {} paginas".format(pag_num))

def main(home_page_url):
    # (1) Obtengo atributos del producto
    print("Buscando atributos del producto...".center(120))
    atributos = get_product_attributes(home_page_url)
    print()

    # (2) En base al producto a buscar, creo los dataframes
    print("Creando dataframes del producto...".center(120))
    df_alternativas = create_dataframe_alternativas(atributos)
    df_opiniones = pd.DataFrame(columns=['id_alternativa', 'opinion'])
    print("Se han creado con exito los dataframes"), print()

    print("Extrayendo datos del producto...".center(120))
    # (3) Carga de datos a dataframes
    df_alternativas, df_opiniones = data_extractor(df_alternativas, df_opiniones, home_page_url)

    return df_alternativas, df_opiniones

''' # para correr pruebas en archivo independientemente de main.py
main("https://listado.mercadolibre.com.ar/celulares#D[A:celulares]")
'''
