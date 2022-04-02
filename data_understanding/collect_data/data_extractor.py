# Importo librerias
import random
from time import sleep
from selenium import webdriver
import dataframe_creator as df_creator
from mercadolibre_crawler import MercadoLibreCrawler
import corte_extraccion_datos


def data_extractor(producto, df_opiniones, df_modelos):
    """
    Extrae datos de opiniones y de las publicaciones de un producto mediante web scraping y la API de Mercado Libre
    y los almacena en los DataFrames pasados como parametro. Representa toda la logica de extraccion.

    :param producto: producto pasado por el usuario para el cual extraer informacion
    :param df_opiniones: DataFrame solo con los nombres de las columnas para ser llenado con opiniones
    :param df_modelos: DataFrame solo con los nombres de las columnas para ser llenado con datos de publicaciones
    :return: Ambos Datafranes cargados con todos los datos extraidos
    """
    # CREO OBJETO "CRAWLER" DE CLASE MercadoLibreCrawler(), ASI TENGO DISPONIBLE METODOS PARA HACER WEB SCRAPING
    options = webdriver.ChromeOptions()
    # options.setPageLoadStrategy(PageLoadStrategy.NONE)
    options.add_argument("start-maximized")
    options.add_argument("enable-automation")
    options.add_argument("--headless") # Hace que no se abra un web browser en tu compu
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(executable_path='chromedriver', options=options)  # Defino a Chrome como Web Browser
    crawler = MercadoLibreCrawler(driver, producto)

    # DEFINO PARAMETROS DE CORTE, TIEMPOS DE ESPERA Y VARIABLES UTILES
    # Defino parametros de corte de la extraccion
    PORC_MIN_ULT_PUB_EXTRAIDAS, CANT_ULT_PUB, ult_pub_sin_data = 0.2, 30, 0  # param 1: De las ultimas <CANT_ULT_PUB> paginas, pido extraer  datos en al menos <porc_min_ult_pub> de ellas
    pag_num, PAG_MAX = 0, 25  # param 2: Hasta pagina <PAG_MAX>, o bien, hasta la ultima
    no_mas_paginas = 0  # param 3: Hasta la ultima pagina (si hay menos que PAG_MAX)
    url_sin_opi = [] #prueba

    # Defino tiempo de espera entre acciones del crawler para humanizarlo y evitar deteccion
    SLEEP_MIN, SLEEP_MAX = 0.5, 1

    # Defino variables utiles
    l_prim_opiniones = []  # lista que guardara las primeras opiniones de cada pub. Ayudara a no extraer opi repetidas
    historico_paginas = []  # lista que guardara un 1 si la pub fue extraida, o bien, 0 (la pub no fue extraida). Ayuda
    # a parametro de corte 2

    # INGRESO A PAGINA PRINCIPAL DE MERCADO LIBRE DEL PRODUCTO
    crawler.driver.get(producto.home_page_url)  # hasta que no se carga toda la pagina, no sigue...

    # INGRESO A CICLO QUE RECORRERA EL CRAWLER PARA EXTRAR LOS DATOS
    while (ult_pub_sin_data == 0) and (pag_num < PAG_MAX) and (no_mas_paginas == 0):  # Hasta que los param de corte lo indiquen...

        # EXTRAIGO URLS QUE EL CRAWLER SEGUIRA. (A) X URLS DE PUBLICACIONES DE 1 PAG Y (B) 1 URL DE SIGUIENTE PAGINA
        urls_publicaciones = crawler.get_publications_url()
        url_paginacion = crawler.get_pagination_url()
        print("Cantidad de pubs:", len(urls_publicaciones))

        # POR CADA PUBLICACION DE UNA PAGINA (tipicamente 1 pagina tiene 50 a 55 publicaciones)
        for url_publicacion in urls_publicaciones:
            print("Publicacion numero:", len(historico_paginas), ". URL:", url_publicacion)  # imprimo nro de pub y url

            pagina_extraida = 0  # A priori, asumo que no pude extraer datos de la publicacion (param de corte 1)

            # CLICKEO EN LA PUBLICACION
            crawler.driver.get(url_publicacion)
            sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))  # Intentando humanizar mis acciones...

            # OBTENGO SU IDENTIFICADOR DE PUBLICACION ("id_publicacion")
            id_publicacion = crawler.get_publication_id(url_publicacion)

            # BUSCO EL BOTON "VER TODAS LAS OPINIONES" DENTRO DE LA PUBLICACION
            url_ver_todas_las_opiniones = crawler.get_ver_todas_las_opiniones_url()

            # SI EXISTE EL BOTON (en ese caso, la publicacion tiene opiniones)
            if url_ver_todas_las_opiniones is not None:

                # CLICKEO EN BOTON "VER TODAS LAS OPINIONES"
                crawler.driver.get(url_ver_todas_las_opiniones)
                sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))  # Intentando humanizar mis acciones...

                # SI LAS OPINIONES SON NUEVAS (pues ≠ publicaciones pueden tener = opiniones)
                if crawler.verification_new_opinions(l_prim_opiniones):

                    pagina_extraida = 1  # Cambio su valor a 1 pues pude extraer datos de la pub (param de corte 1)

                    # HAGO SCROLL DOWN PARA CARGAR TODAS LAS OPINIONES
                    sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))  # Intentando humanizar mis acciones...
                    crawler.ScrollDown()

                    # EXTRAIGO OPINIONES Y LAS GUARDO EN UN DATAFRAME ("df_opiniones")
                    d_opiniones_publicacion = crawler.get_publication_opinions_data(id_publicacion)
                    l_prim_opiniones.append(d_opiniones_publicacion['content'][0])  # Guardo la primera opinion de la
                    # publicacion para poder hacer la verificacion de opiniones nuevas
                    df_opiniones = df_creator.add_lines_to_dataframe(d_opiniones_publicacion, df_opiniones)
                    # print(df_opiniones)

                    # CLICKEO EN BOTON "VOLVER" PARA SALIR DE SECCION "VER TODAS LAS OPINIONES"
                    crawler.driver.back()
                    sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))  # Intentando humanizar mis acciones...

                    # EXTRAIGO DATOS DE LA PUBLICACION Y LAS GUARDO EN UN DATAFRAME ("df_modelos")
                    d_data_modelos = crawler.get_modelo_data(id_publicacion, crawler.producto.atributos)
                    df_modelos = df_creator.add_lines_to_dataframe(d_data_modelos, df_modelos)
                    # print(df_modelos)

                # SI LAS OPINIONES NO SON NUEVAS (ES DECIR, SE REPITEN), ENTONCES NO EXTRAIGO NADA.
                else:
                    print("OPINIONES REPETIDAS")

                    # CLICKEO EN BOTON "VOLVER" PARA SALIR DE SECCION "VER TODAS LAS OPINIONES"
                    crawler.driver.back()

            # SI NO EXISTE EL BOTON "VER TODAS LAS OPINIONES" (pub sin opiniones), ENTONCES NO EXTRAIGO NADA
            else:
                print("PUBLICACION SIN OPINIONES")
                url_sin_opi.append(url_publicacion)

            # CLICKEO EN BOTON "VOLVER" PARA SALIR DE LA PAGINA DE LA PUBLICACION
            crawler.driver.back()
            sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))  # Intentando humanizar mis acciones...

            # VERIFICO PARAMETRO DE CORTE 1 (corta si las ultimas publicaciones no tienen datos)
            historico_paginas.append(pagina_extraida)  # Agrego un boolean segun si extraje o no la publicacion

            # Si las ultimas publicaciones tienen muy pocos datos
            if corte_extraccion_datos.ultimas_pub_sin_data(historico_paginas, PORC_MIN_ULT_PUB_EXTRAIDAS, CANT_ULT_PUB):

                # corto la extraccion de datos (parametro de corte 1)
                ult_pub_sin_data = True
                break

        # SI ENCONTRE URL DE SIGUIENTE PAGINA
        print("Proxima pagina a relevar: ", url_paginacion)
        if url_paginacion is not None:

            # HAGO CLICK EN LA "SIGUIENTE PAGINA"
            crawler.driver.get(url_paginacion)
            sleep(random.uniform(8, 10))  # Intentando humanizar mis acciones y tambien esperar a carga de nueva pagina
            pag_num += 1  # variable que si llega a <PAG_MAX>, hace cortar la extraccion de datos (parametro de corte 2)

        # SI NO ENCONTRE LA URL DE LA SIGUIENTE PAGINA
        else:
            # CORTO LA EXTRACCION DE DATOS (PARAMETRO DE CORTE 3)
            no_mas_paginas = True

        print("++++++++++++++++++++++++++++++++++++ CAMBIO DE PAGINA ++++++++++++++++++++++++++++++++++++")

    # FINALIZADA LA EXTRACCION, CIERRO EL WEB BROWSER AUTOMATICO
    crawler.driver.close()

    # EXPLICO POR QUE CORTO LA EXTRACCION DE DATOS
    corte_extraccion_datos.explicacion_corte(pag_num, PAG_MAX, ult_pub_sin_data)

    print(url_sin_opi)

    return df_opiniones, df_modelos

'''
def main():
    # Pedido al usuario de producto a buscar y, con el, creo objeto de clase Product
    # producto = Product(str(input("Ingrese producto a buscar: ")))
    producto = Product("auriculares")  # despues lo saco

    # Valido el producto buscado tal que no sea una busqueda tan amplia
    producto.search_validation()

    # Obtengo atributos o caracteristicas mas relevantes del producto
    producto.atributos = producto.get_product_attributes()

    # En base al producto a buscar, creo los data
    df_opiniones = df_creator.create_opinions_dataframe()
    df_modelos = df_creator.create_models_dataframe(producto.atributos)

    # Carga de datos a data
    df_opiniones, df_modelos = data_extractor(producto, df_opiniones, df_modelos)

    # Exporto data
    df_opiniones.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_opiniones_{}.xlsx'.format(producto.nombre), 'Hoja de datos', index=False)
    df_modelos.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_modelos_{}.xlsx'.format(producto.nombre), 'Hoja de datos', index=False)


main()
'''
