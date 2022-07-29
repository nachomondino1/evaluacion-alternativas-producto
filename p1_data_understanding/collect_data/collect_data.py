# Importo librerias
import pandas as pd
import random
from time import sleep
from p1_data_understanding.collect_data.mercadolibre_crawler import MercadoLibreCrawler
from bs4 import BeautifulSoup

################################################ FUNCIONES PRINCIPALES ################################################
def get_product_attributes(home_page_url):
    """
    Obtiene los atributos mas relevantes de un producto mediante Web Scraping
    :param home_page_url: String. URL de la pagina principal de un producto en Mercado Libre
    :return: Lista. Atributos mas relevantes del producto
    """
    # DEFINO VARIABLES
    PAG_A_VISITAR = 30  # cantidad de publicaciones a visitar
    d_attr_frec = {}  # diccionario donde guardare los atributos y su frecuencia
    SLEEP_MIN, SLEEP_MAX = 1, 2
    # crawler = MercadoLibreCrawler(driver=inicialize_driver())  # objeto de clase MercadoLibreCrawler()
    crawler = MercadoLibreCrawler()  # objeto de clase MercadoLibreCrawler()

    # INGRESO A PAGINA PRINCIPAL DEL PRODUCTO A BUSCAR
    crawler.driver.get(home_page_url)

    # EXTRAIGO URLS DE PUBLICACIONES (recordar que 1 pag tiene entre 50 y 55 pubs)
    l_url_publicaciones = crawler.get_publications_url()

    # POR CADA PUBLICACION
    for publicacion in l_url_publicaciones[:PAG_A_VISITAR]:

        # INGRESO A PUBLICACION
        crawler.driver.get(publicacion)
        sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))  # Intentando humanizar mis acciones...

        # OBTENGO CODIGO HTML DE LA PUBLICACION USANDO LIBRERIA BEAUTIFULSOUP
        pageSource = crawler.driver.page_source
        bs = BeautifulSoup(pageSource, 'html.parser')

        # BUSCO, EN EL CODIGO HTML, TAGS QUE CONTIENEN UN ATRIBUTO
        # para publicaciones tipo 1 (atributos en seccion oculta "Ver mas caracteristicas")
        tags_attrs = bs.find_all('th', {'class': "andes-table__header andes-table__header--left ui-vpp-striped-specs__row__column ui-vpp-striped-specs__row__column--id"})
        sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))  # Intentando humanizar mis acciones...

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
            # OBTENGO EL ATRIBUTO(es el texto del tag)
            attr = tag.text
            # SUMO UNO A SU FRECUENCIA
            d_attr_frec[attr] = d_attr_frec[attr]+1 if attr in d_attr_frec.keys() else 1

        # CLICKEO EN BOTON "VOLVER" PARA SALIR DE PUBLICACION
        crawler.driver.back()
        sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))  # Intentando humanizar mis acciones...

    # FINALIZADA LA EXTRACCION, CIERRO EL WEB BROWSER AUTOMATICO
    crawler.driver.close()

    # SELECCIONO LOS ATRIBUTOS RELEVANTES
    l_atributos = select_relevant_attributes(d_attr_frec)
    return l_atributos

def data_extractor(df_alt, df_opi, home_page_url):
    """
    Extrae datos de opiniones y de las publicaciones de un producto mediante web scraping y los almacena en los
    DataFrames pasados como parametro. Representa toda la logica de extraccion.
    :param df_alt: DataFrame. Unidad de analisis: alternativa. Columnas: id_alternativa, precio y una por cada campo
    especifico del producto. Cantidad de filas: vacio
    :param df_opi: DataFrame. Unidad de analisis: opinion. Columnas: id_alternativa y opinion. Cantidad de filas: vacio
    :param home_page_url: String. URL de pagina principal del producto en Mercado Libre
    :return: Dataframes pasados como parametro cargados con datos
    """
    # DEFINO PARAMETROS DE CORTE, TIEMPOS DE ESPERA Y VARIABLES UTILES
    # Defino parametros de corte de la extraccion
    PORC_MIN_ULT_PUB_EXTRAIDAS, CANT_ULT_PUB, ult_pub_sin_data = 0.1, 40, 0  # param 1: De las ultimas <CANT_ULT_PUB> paginas, pido extraer  datos en al menos <porc_min_ult_pub> de ellas
    pag_num, PAG_MAX = 0, 25  # param 2: Hasta pagina <PAG_MAX>, o bien, hasta la ultima
    no_mas_paginas = 0  # param 3: Hasta la ultima pagina (si hay menos que PAG_MAX)
    # Defino otras variables
    SLEEP_MIN, SLEEP_MAX = 1, 2  # tiempo de espera entre acciones del crawler para humanizarlo y evitar deteccion
    l_historial_pag = []  # lista que guardara un 1 si la pub fue extraida, o bien, 0 (la pub no fue extraida). Ayuda
    # a parametro de corte 2
    crawler = MercadoLibreCrawler()  # objeto de clase MercadoLibreCrawler()

    # INGRESO A PAGINA PRINCIPAL DE MERCADO LIBRE DEL PRODUCTO Y SELECCIONO CONDICION="NUEVO"
    crawler.driver.get(home_page_url), sleep(3)  # hasta que no se carga toda la pagina, no sigue...
    crawler.driver.get(crawler.get_home_page_url_condition_new())  # Filtro para ingresar a publicaciones con Condicion=Nuevo (Evito publicaciones con condicion usado)

    # POR PAGINA DE PAGINACION
    while (ult_pub_sin_data == 0) and (pag_num < PAG_MAX) and (no_mas_paginas == 0):  # Hasta que los param de corte lo indiquen...

        # EXTRAIGO URLS DE PUBLICACIONES DE LA PAGINA Y URL DE SIGUIENTE PAGINA
        urls_publicaciones = crawler.get_publications_url()
        url_paginacion = crawler.get_pagination_url()
        print("Cantidad de pubs:", len(urls_publicaciones))

        # POR CADA PUBLICACION DE LA PAGINA (tipicamente 1 pagina tiene 50 a 55 publicaciones)
        for url_publicacion in urls_publicaciones:
            print("Publicacion numero: {} \t URL: {}".format(len(l_historial_pag)+1, url_publicacion))  # imprimo nro de pub y url

            pagina_extraida = 0  # A priori, asumo que no pude extraer datos de la publicacion (param de corte 1)

            # CLICKEO EN LA PUBLICACION
            crawler.driver.get(url_publicacion)
            sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))  # Intentando humanizar mis acciones...

            # OBTENGO SU IDENTIFICADOR DE PUBLICACION ("id_publicacion")
            id_alternativa = crawler.get_publication_id(url_publicacion)

            # EXTRAIGO DATOS DE LA PUBLICACION
            df_new_pub = crawler.get_modelo_data(id_publicacion=id_alternativa, l_atributos=list(df_alt.columns)[2:])  # excluyo id y precio

            # SI LA ALTERNATIVA ES NUEVA
            if is_alternative_new(df_alt, df_new_pub):

                # GUARDO DATOS DE ALTERNATIVA EN DATAFRAME ("df_alternativas")
                df_alt = pd.concat([df_alt, df_new_pub], ignore_index=True)
                print("Nº alternativas extraidas: {}".format(df_alt.shape[0]))

                # BUSCO EL BOTON "VER TODAS LAS OPINIONES" DENTRO DE LA PUBLICACION
                url_ver_todas_las_opiniones = crawler.get_ver_todas_las_opiniones_url()

                # SI EXISTE EL BOTON (en ese caso, la publicacion tiene opiniones)
                if url_ver_todas_las_opiniones is not None:

                    # CLICKEO EN BOTON "VER TODAS LAS OPINIONES"
                    crawler.driver.get(url_ver_todas_las_opiniones)
                    sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))  # Intentando humanizar mis acciones...

                    # SI LAS OPINIONES SON NUEVAS (pues ≠ publicaciones pueden tener = opiniones)
                    if crawler.are_opinions_new(df_opi):

                        pagina_extraida = 1  # Cambio su valor a 1 pues pude extraer datos de la pub (param de corte 1)

                        # HAGO SCROLL DOWN PARA CARGAR TODAS LAS OPINIONES
                        sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))  # Intentando humanizar mis acciones...
                        crawler.ScrollDown()

                        # EXTRAIGO OPINIONES Y LAS GUARDO EN UN DATAFRAME ("df_opiniones")
                        df_opi_new_alt = crawler.get_publication_opinions_data(id_alternativa)
                        df_opi = pd.concat([df_opi, df_opi_new_alt], ignore_index=True)
                        print("Nº opiniones extraidas: {}".format(df_opi.shape[0]))

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

                # VERIFICO PARAMETRO DE CORTE 1
                l_historial_pag.append(pagina_extraida)  # Agrego un boolean segun si extraje o no la publicacion
                # Si las ultimas publicaciones tienen muy pocos datos
                if ultimas_pub_sin_data(l_historial_pag, PORC_MIN_ULT_PUB_EXTRAIDAS, CANT_ULT_PUB):
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
    Recomendacion: Tener a mano publicaciones del producto para ver que valor toma cada atributo y asi entender de que
    se trata el atributo
    :param d_attr_frec: Diccionario. Key: atributo del producto. Value: frecuencia (cantidad de publicaciones de Mercado
    Libre en que aparece el atributo)
    :return: Lista. Atributos mas relevantes del producto
    """
    # DEFINO VARIABLES
    l_frecuencias = list(d_attr_frec.values())  # Lista de frecuencias de todos los atributos
    PORC_FREC_MIN = 0.2  # atributos en al menos el x% de las publicaciones
    l_atributos = []  # Lista de atributos a retornar
    print("Los {} atributos y su frecuencia: {}".format(len(l_frecuencias), d_attr_frec))

    # POR ATRIBUTO
    for atributo in d_attr_frec.keys():

        # OBTENGO SU PORCENTAJE DE FRECUENCIA
        porc_frec = d_attr_frec[atributo] / max(l_frecuencias)

        # SI EL ATRIBUTO ES LO SUFICIENTIMENTE FRECUENTE
        if porc_frec > PORC_FREC_MIN:

            # SOLICITO A ADMINISTRADOR SI SELECCIONAR EL ATRIBUTO O NO
            # Mientras que la carga sea invalida
            while True:
                # Si la carga es un numero
                try:
                    # Solicito al administrador si tendra en cuenta o no el atributo
                    input_admin = int(input("Ingrese 1 si se usara el atributo '{}' de frecuencia {:.2f}%: ".format(atributo.upper(), porc_frec * 100)))
                    # Si cargo un "1"
                    if input_admin == 1:
                        # Guardo atributo
                        l_atributos.append(atributo)
                    # La carga es valida
                    break
                # si la carga no es un numero
                except:
                    pass

    # Imprimo atributos seleeccionados
    print('Los {} atributos mas relevantes: {}'.format(len(l_atributos), l_atributos))
    return l_atributos


# UTILIZADA EN DATA_EXTRACTOR()
def is_alternative_new(df_alt, df_new_pub):  # Probar con celulares a ver si funciona
    """
    Verifica si la publicacion proxima a extraer corresponde a una nueva alternativa o no
    :param df_alt: Dataframe. Unidad de analisis: alternativa del producto. Columnas: id_alternativa y atributos del
    producto.
    :param df_new_pub: Dataframe. Unidad de analisis: publicacion del producto. Columnas: id_alternativa y atributos del
    producto.
    :return: True si la publicacion corresponde a una nueva alternativa, de lo contrario, False.
    """
    # Defino variables
    l_attr_modelo_unico = ['Modelo'] # En celulares: , 'Memoria interna', 'Memoria RAM']  # lista de atributos sobre los cuales identificar modelos unicos
    id_new_alt = df_new_pub.loc[0, 'id_alternativa']  # id y modelo de nueva publicacion
    l_val_attr_new_alt = []  # Valores de atributos de nueva publicacion para identificar modelo unico (en miniscula)
    for attr in l_attr_modelo_unico:
        l_val_attr_new_alt.append(str(df_new_pub.loc[0, attr]).lower())

    # POR ALTERNATIVA EXTRAIDA
    for i in df_alt.index:

        # Defino variables
        id_alt = df_alt.loc[i, 'id_alternativa']  # Id de alternativa extraida
        l_val_attr_alt = []  # Valores de atributos de alternativa extraida para identificar modelo unico (en miniscula)
        for attr in l_attr_modelo_unico:
            l_val_attr_alt.append(str(df_alt.loc[i, attr]).lower())

        # SI EL ID COINCIDE CON EL DE LA NUEVA PUBLICACION
        if id_new_alt == id_alt:
            print("ALTERNATIVA REPETIDA. Mismo id")
            print(l_val_attr_alt, l_val_attr_new_alt)
            return False

        # SI EL MODELO COINCIDE CON EL DE LA NUEVA PUBLICACION
        elif l_val_attr_new_alt == l_val_attr_alt:
            print("ALTERNATIVA REPETIDA. Mismo modelo")
            print(l_val_attr_alt, l_val_attr_new_alt)
            return False

    # Si el id y el modelo es nuevo
    print("La alternativa es nueva!")
    return True

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


# para correr pruebas en archivo independientemente de main.py
l_atributos = get_product_attributes("https://listado.mercadolibre.com.ar/celulares#D[A:celulares]")
print(" b) Creando dataframes del producto...".center(120))
df_alt = pd.DataFrame(columns=['id_alternativa', 'precio'] + l_atributos)
df_opi = pd.DataFrame(columns=['id_alternativa', 'opinion'])
print(" c) Extrayendo datos del producto...".center(120))
df_alt, df_opi = data_extractor(df_alt, df_opi, "https://listado.mercadolibre.com.ar/celulares#D[A:celulares]")
