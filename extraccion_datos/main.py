# Importo librerias
import random
from time import sleep
from selenium import webdriver
import DataFrameCreator
from MercadoLibreCrawler import MercadoLibreCrawler
from MercadoLibreCrawler import Product
import corte_extraccion_datos as corte


def data_extractor(producto, df_opiniones, df_modelos):
    """
    Extrae datos de opiniones y de las publicaciones de un producto mediante web scraping y la API de Mercado Libre
    y los almacena en los DataFrames pasados como parametro. Representa toda la logica de extraccion.

    :param producto: producto pasado por el usuario para el cual extraer informacion
    :param df_opiniones: DataFrame solo con los nombres de las columnas para ser llenado con opiniones
    :param df_modelos: DataFrame solo con los nombres de las columnas para ser llenado con datos de publicaciones
    :return: Ambos Datafranes cargados con todos los datos extraidos
    """

    # Defino a Chrome como Web Browser
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Hace que no se abra un web browser en tu compu
    driver = webdriver.Chrome(executable_path='./chromedriver', options=options)

    # Creo objeto de clase MercadoLibreCrawler para tener disponible todos los metodos para hacer web scraping
    crawler = MercadoLibreCrawler(driver, producto)

    # Defino parametros de corte de la extraccion
    pag_num, PAG_MAX = 0, 25                                                 # param 1: Hasta pagina 10 de Mercado libre
    no_mas_paginas = 0                                                       # param 2: Hasta ultima pagina
    PORC_MIN_ULT_PUB_EXTRAIDAS, CANT_ULT_PUB, ult_pub_sin_data = 0.1, 30, 0  # param 3: De las ultimas <CANT_ULT_PUB> paginas, pido extraer datos en al menos <porc_min_ult_pub> de ellas


    # Defino lista en la que incluire las primeras opiniones de cada publicacion. Ayudara a no extraer opiniones repetidas
    l_prim_opiniones = []
    historico_paginas = []
    SLEEP_MIN, SLEEP_MAX = 2, 4

    # Ingreso a pagina principal del producto en Mercado Libre
    crawler.driver.get(producto.home_page_url)  # hasta que no se carga toda la pagina, no sigue...

    # Mientras que los parametros de corte no lo indiquen
    while (pag_num < PAG_MAX) and (no_mas_paginas == 0) and (ult_pub_sin_data == 0):

        # Extraigo URLs de cada una de las publicaciones de una pagina de Mercado Libre.
        sleep(random.uniform(8, 10))  # Intentando humanizar mis acciones y en parte esperar a carga de nueva pagina
        urls_publicaciones = crawler.get_publications_url()
        url_paginacion = crawler.get_pagination_url()
        print("Cantidad de pubs:", len(urls_publicaciones))

        # Recorro cada publicacion
        for url_publicacion in urls_publicaciones:
            print("Publicacion numero:", len(historico_paginas), ". URL:", url_publicacion) # Por lo menos para las pruebas es util, saber el nro de publicacion y el link

            pagina_extraida = 0  # A priori, asumo que no pude extraer datos de la publicacion

            # Clickeo en una publicacion
            crawler.driver.get(url_publicacion) # driver.get(url_publicacion)

            # Obtengo id de la publicacion (que identifica como unica a cada publicacion)
            id_publicacion = crawler.get_publication_id(url_publicacion)

            # Obtengo el URL del boton "Ver todas las opiniones"
            url_ver_todas_las_opiniones = crawler.get_ver_todas_las_opiniones_url()

            # Si existe el boton "Ver todas las opiniones" y extraje el id
            if url_ver_todas_las_opiniones is not None:

                # Clickeo en boton "Ver todas las opiniones"
                sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))  # Intentando humanizar mis acciones...
                crawler.driver.get(url_ver_todas_las_opiniones) # driver.get(url_ver_todas_las_opiniones)

                # Si las opiniones son nuevas (En meli, ≠ publicaciones pueden tener = opiniones)
                if crawler.verification_new_opinions(l_prim_opiniones):

                    # Seteo a 1 pagina extraida
                    pagina_extraida = 1

                    # Hago Scroll down para cargar todas las opiniones (pues son nuevas y las quiero extraer)
                    sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))  # Intentando humanizar mis acciones...
                    crawler.ScrollDown()

                    # Extraigo opiniones y las guardo en df_opiniones
                    sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))  # Intentando humanizar mis acciones...
                    d_opiniones_publicacion = crawler.get_publication_opinions_data(id_publicacion)
                    df_opiniones = DataFrameCreator.AgregarFilasAlDataFrame(d_opiniones_publicacion, df_opiniones)
                    print(df_opiniones)

                    # Guardo la primera opinion de la publicacion para poder hacer la verificacion de opiniones nuevas
                    l_prim_opiniones.append(d_opiniones_publicacion['content'][0])

                    # Clikeo en Volver saliendo de "Ver todas las opiniones"
                    crawler.driver.back()

                    # Extraigo datos de la publicacion (notar que solo lo extraigo si las opiniones son nuevas) y
                    # los guardo en df_modelos
                    sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))  # Intentando humanizar mis acciones...
                    d_data_modelos = crawler.get_modelo_data(id_publicacion, crawler.producto.atributos)
                    df_modelos = DataFrameCreator.AgregarFilasAlDataFrame(d_data_modelos, df_modelos)
                    print(df_modelos)

                # Las opiniones se repiten con las de otra publicacion, por lo que, no extraigo nada
                else:
                    print("OPINIONES REPETIDAS")

                    # Clikeo en Volver saliendo de "Ver todas las opiniones"
                    crawler.driver.back()

            # No existe el boton "Ver todas las opiniones" (pub con  menos de 3 opiniones, o bien, no hay)
            else:
                print("PUBLICACION SIN OPINIONES")

            # Clikeo en Volver saliendo de la pagina de la publicacion y volviendo a la pagina principal
            crawler.driver.back()

            #  Verifico parametro de corte 3, en el que corto si las ultimas publicaciones no tienen datos
            historico_paginas.append(pagina_extraida) # Agrego un boolean segun si extraje o no la publicacion

            if corte.ultimas_pub_sin_data(historico_paginas, PORC_MIN_ULT_PUB_EXTRAIDAS, CANT_ULT_PUB):
                ult_pub_sin_data = True
                break

        print("Proxima pagina a relevar: ", url_paginacion)
        # HAGO CLICK EN "SIGUIENTE PAGINA"
        if url_paginacion is not None:
            sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))  # Intentando humanizar mis acciones...
            crawler.driver.get(url_paginacion)
            pag_num += 1
        else:
            no_mas_paginas = 1

        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

    # Cierro el Web Browser Automatico dando por finalizada la extraccion de datos
    crawler.driver.close()

    # Explico la razon por la que corto la extraccion de datos
    corte.explicacion_corte(pag_num, PAG_MAX, no_mas_paginas, ult_pub_sin_data)

    return df_opiniones, df_modelos


def main():
    # Pedido al usuario de producto a buscar y, con el, creo objeto de clase Product
    # producto = Product(str(input("Ingrese producto a buscar: ")))
    producto = Product("celulares") # despues lo saco

    # Valido el producto buscado tal que no sea una busqueda tan amplia
    producto.search_validation()

    # Obtengo atributos o caracteristicas mas relevantes del producto
    producto.atributos = producto.get_atributos()

    # En base al producto a buscar, creo los data
    df_opiniones = DataFrameCreator.CrearOpinionsDataFrame()
    df_modelos = DataFrameCreator.CrearModelosDataFrame(producto.atributos)

    # Carga de datos a data
    df_opiniones, df_modelos = data_extractor(producto, df_opiniones, df_modelos)

    # Exporto data
    df_opiniones.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_opiniones_{}.xlsx'.format(producto.nombre), 'Hoja de datos', index=False)
    df_modelos.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_modelos_{}.xlsx'.format(producto.nombre), 'Hoja de datos', index=False)


main()