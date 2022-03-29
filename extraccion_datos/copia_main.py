# Importo librerias
from selenium import webdriver
import DataFrameCreator
from MercadoLibreCrawler import MercadoLibreCrawler
from MercadoLibreCrawler import Product
import corte_extraccion_datos as corte


def ExtractorDatos(producto, df_opiniones, df_modelos):
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
    options.add_argument('--headless') # Hace que no se abra un web browser en tu compu
    driver = webdriver.Chrome(
        executable_path='/Users/nachomondino/PycharmProjects/Utils/web_scraping_browsers/chromedriver', options=options)

    # Creo objeto de clase MercadoLibreCrawler para tener disponible todos los metodos para hacer web scraping
    crawler = MercadoLibreCrawler(driver, producto)
    driver = crawler.driver

    # Defino parametros de corte de la extraccion
    pag_num, pag_max = 0, 11                                                # param 1: Hasta pagina 10 de Mercado libre
    porc_min_ult_pub_extraidas, cant_ult_pub, ult_pub_sin_data = 0.3, 30, 0 # param 2: De las ultimas <cant_ult_pub> paginas, pido extraer datos en al menos <porc_min_ult_pub> de ellas
    historico_paginas = []
    urls_sin_opiniones = [] # lo saco cdo deje de probar el get_URL_vertodaslasopi

    # Defino lista en la que incluire las primeras opiniones de cada publicacion. Ayudara a no extraer opiniones repetidas
    l_prim_opiniones = []

    # Ingreso a pagina principal del producto en Mercado Libre
    driver.get(producto.home_page_url)     # driver.get(producto.home_page_url)

    # Obtengo URL de las paginas a visitar teniendo en cuenta solo el parametro de corte 1
    urls_paginacion, urls_publicaciones = crawler.get_URL_paginacion(pag_max)

    # Recorro cada pagina
    for url_paginacion in urls_paginacion:

        # Extraigo URLs de cada una de las publicaciones de una pagina de Mercado Libre. Tambien de la paginacion.
        # url_publicaciones = crawler.get_URL_publicaciones() #Pruebo a extraerlo afuera

        # url_paginacion = crawler.get_URL_paginacion() # probe a ponerlo abajo pero corto por no haber mas paginas en la 5, para mi fallo la carga de la pagina.
        print("Pagina a relevar: ", url_paginacion)

        # Recorro cada publicacion
        for url_publicacion in urls_publicaciones:
            print("Publicacion numero:", len(historico_paginas), ". URL:", url_publicacion) # Por lo menos para las pruebas es util, saber el nro de publicacion y el link

            pagina_extraida = 0 #  A priori, asumo que no pude extraer datos de la publicacion --> si funciona lambda, no hace falta...

            # Clickeo en una publicacion
            driver.get(url_publicacion) # driver.get(url_publicacion)

            # Obtengo id de la publicacion (que identifica como unica a cada publicacion)
            id_publicacion = crawler.get_IdPublicacion(url_publicacion)

            # Obtengo el URL del boton "Ver todas las opiniones"
            url_ver_todas_las_opiniones = crawler.get_URL_VerTodasLasOpiniones()

            # Si existe el boton "Ver todas las opiniones" y extraje el id
            if url_ver_todas_las_opiniones is not None:

                # Clickeo en boton "Ver todas las opiniones"
                driver.get(url_ver_todas_las_opiniones) # driver.get(url_ver_todas_las_opiniones)

                # Si las opiniones son nuevas (En meli, ≠ publicaciones pueden tener = opiniones)
                if crawler.verificacion_opiniones_nuevas(l_prim_opiniones):

                    # Seteo a 1 pagina extraida
                    pagina_extraida = 1

                    # Hago Scroll down para cargar todas las opiniones (pues son nuevas y las quiero extraer)
                    # crawler.ScrollDown()

                    # Extraigo opiniones y las guardo en df_opiniones
                    d_opiniones_publicacion = crawler.get_Data_OpinionesPub(id_publicacion)
                    df_opiniones = DataFrameCreator.AgregarFilasAlDataFrame(d_opiniones_publicacion, df_opiniones)
                    print(df_opiniones)

                    # Guardo la primera opinion de la publicacion para poder hacer la verificacion de opiniones nuevas
                    l_prim_opiniones.append(d_opiniones_publicacion['content'][0])

                    # Clikeo en Volver saliendo de "Ver todas las opiniones"
                    driver.back()

                    # Extraigo datos de la publicacion (notar que solo lo extraigo si las opiniones son nuevas) y
                    # los guardo en df_modelos
                    d_data_modelos = crawler.get_Data_Modelos(id_publicacion, crawler.producto.atributos)
                    df_modelos = DataFrameCreator.AgregarFilasAlDataFrame(d_data_modelos, df_modelos)
                    print(df_modelos)

                # Las opiniones se repiten con las de otra publicacion, por lo que, no extraigo nada
                else:
                    print("OPINIONES REPETIDAS")

                    # Clikeo en Volver saliendo de "Ver todas las opiniones"
                    driver.back()

            # No existe el boton "Ver todas las opiniones" (pub con  menos de 3 opiniones, o bien, no hay)
            else:
                urls_sin_opiniones.append(url_publicacion) # lo saco cdo deje de probar el get_URL_vertodaslasopi
                print("PUBLICACION SIN OPINIONES")

            # Clikeo en Volver saliendo de la pagina de la publicacion y volviendo a la pagina principal
            driver.back()

            #  Verifico parametro de corte 3, en el que corto si las ultimas publicaciones no tienen datos
            historico_paginas.append(pagina_extraida) # Agrego un boolean segun si extraje o no la publicacion

            if corte.ultimas_pub_sin_data(historico_paginas, porc_min_ult_pub_extraidas, cant_ult_pub):
                ult_pub_sin_data = True

        # Verifico parametros de corte 2
        if ult_pub_sin_data:
            break

        # HAGO CLICK EN "SIGUIENTE PAGINA"
        driver.get(url_paginacion)
        pag_num += 1

        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

    # Cierro el Web Browser Automatico dando por finalizada la extraccion de datos
    driver.close()
    print(urls_sin_opiniones) # lo saco cdo deje de probar el get_URL_vertodaslasopi

    # Explico la razon por la que corto la extraccion de datos
    corte.explicacion_corte(pag_num, pag_max, ult_pub_sin_data)

    return df_opiniones, df_modelos


def main():
    # Pedido al usuario de producto a buscar y, con el, creo objeto de clase Product
    # producto = Product(str(input("Ingrese producto a buscar: ")))
    producto = Product("auriculares") # despues lo saco

    # Valido el producto buscado tal que no sea una busqueda tan amplia
    producto.nombre_subcat = producto.validacion_busqueda()

    # Obtengo atributos o caracteristicas mas relevantes del producto
    # producto.atributos = producto.getAtributos()

    # celulares
    # producto.atributos = ['Marca', 'Modelo', 'Color', 'Resolución de la cámara trasera principal', 'Resolución de la cámara frontal principal', 'Con cámara', 'Cantidad de cámaras traseras', 'Con teclado QWERTY físico', 'Modelo del procesador', 'Es Dual SIM', 'Cantidad de ranuras para tarjeta SIM', 'Memoria interna', 'Memoria RAM', 'Tamaño de la pantalla', 'Tipo de resolución de la pantalla ', 'Resolución de la pantalla', 'Tecnología de la pantalla', 'Con pantalla táctil', 'Capacidad de la batería', 'Altura x Ancho x Profundidad', 'Red', 'Con conector USB', 'Con Wi-Fi', 'Con GPS', 'Con Bluetooth']

    # auriculares
    producto.atributos = ['Marca', 'Modelo', 'Color', 'Con micrófono', 'Con micrófono desmontable', 'Con micrófono flexible', 'Formato del auricular', 'Es inalámbrico', 'Con Bluetooth']

    # En base al producto a buscar, creo los data
    df_opiniones = DataFrameCreator.CrearOpinionsDataFrame()
    df_modelos = DataFrameCreator.CrearModelosDataFrame(producto.atributos)

    # Carga de datos a data
    df_opiniones, df_modelos = ExtractorDatos(producto, df_opiniones, df_modelos)

    # Exporto data
    df_opiniones.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_opiniones_{}.xlsx'.format(producto.nombre), 'Hoja de datos', index=False)
    df_modelos.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_modelos_{}.xlsx'.format(producto.nombre), 'Hoja de datos', index=False)


main()