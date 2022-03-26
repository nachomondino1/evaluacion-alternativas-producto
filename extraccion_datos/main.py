# Importo librerias
from selenium import webdriver
import DataFrameCreator
from MercadoLibreCrawler import MercadoLibreCrawler
from MercadoLibreCrawler import Product


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
    no_mas_paginas = 0                                                      # param 2: Hasta ultima pagina (cuando hay menos de 10)
    porc_min_ult_pag_extraidas, cant_ult_pag, ult_pag_sin_data = 0.1, 30, 0 # param 3: De las ultimas <cant_ult_pag> paginas, pido extraer datos en al menos <porc_min_ult_pag> de ellas
    historico_paginas = []

    # Defino lista en la que incluire las primeras opiniones de cada publicacion. Ayudara a no extraer opiniones repetidas
    l_prim_opiniones = []

    # Ingreso a pagina principal del producto en Mercado Libre
    driver.get(producto.home_page_url)

    # Mientras que no se cumpla alguno de los tres parametro de corte
    while (pag_num < pag_max) and (no_mas_paginas == 0) and (ult_pag_sin_data == 0):

        # Extraigo URLs de cada una de las publicaciones de una pagina de Mercado Libre. Tambien de la paginacion.
        url_publicaciones = crawler.getPublicationsUrl()
        url_paginacion = crawler.getPaginacionUrl() #probe a ponerlo abajo pero corto por no haber mas paginas en la 5, para mi fallo la carga de la pagina.

        # Recorro cada publicacion
        for url_publicacion in url_publicaciones:
            print("Publicacion numero:", len(historico_paginas), url_publicacion) # Por lo menos para las pruebas es util, saber el nro de publicacion y el link

            # A priori, asumo que no pude extraer datos de la publicacion
            pagina_extraida = False

            # Clickeo en una publicacion
            driver.get(url_publicacion)

            # Obtengo id de la publicacion (que identifica como unica a cada publicacion)
            id_publicacion = crawler.getIdPublicacion(url_publicacion)

            # Obtengo el URL del boton "Ver todas las opiniones"
            url_ver_todas_las_opiniones = crawler.getVerTodasLasOpinionesUrl()

            # Si existe el boton "Ver todas las opiniones" y extraje el id
            if url_ver_todas_las_opiniones != None:

                # Clickeo en boton "Ver todas las opiniones"
                driver.get(url_ver_todas_las_opiniones)

                # Si las opiniones son nuevas (En meli, ≠ publicaciones pueden tener = opiniones)
                if crawler.verificationNewOpinions(l_prim_opiniones) == True:

                    # Seteo a 1 pagina extraida
                    pagina_extraida = True

                    # Hago Scroll down para cargar todas las opiniones (pues son nuevas y las quiero extraer)
                    # crawler.ScrollDown()

                    # Extraigo opiniones y las guardo en df_opiniones
                    d_opiniones_publicacion = crawler.getPublicationOpinionsData(id_publicacion)
                    df_opiniones = DataFrameCreator.AgregarFilasAlDataFrame(d_opiniones_publicacion, df_opiniones)
                    print(df_opiniones)

                    # Guardo la primera opinion de la publicacion para poder hacer la verificacion de opiniones nuevas
                    l_prim_opiniones.append(d_opiniones_publicacion['content'][0])

                    # Clikeo en Volver saliendo de "Ver todas las opiniones"
                    driver.back()

                    # Extraigo datos de la publicacion (notar que solo lo extraigo si las opiniones son nuevas) y
                    # los guardo en df_modelos
                    d_data_modelos = crawler.getModeloData(id_publicacion, crawler.producto.atributos)
                    df_modelos = DataFrameCreator.AgregarFilasAlDataFrame(d_data_modelos, df_modelos)
                    print(df_modelos)

                # Las opiniones se repiten con las de otra publicacion, por lo que, no extraigo nada
                else:
                    print("OPINIONES REPETIDAS")

                    # Clikeo en Volver saliendo de "Ver todas las opiniones"
                    driver.back()

            # No existe el boton "Ver todas las opiniones" (pub con  menos de 3 opiniones, o bien, no hay)
            else:
                print("PUBLICACION SIN OPINIONES")

            # Clikeo en Volver saliendo de la pagina de la publicacion y volviendo a la pagina principal
            driver.back()

            #  VERIFICO QUE TENGA SENTIDO SEGUIR EXTRAYENDO DATOS
            # Agrego un boolean segun si extraje o no la publicacion
            historico_paginas.append(pagina_extraida)

            # Si no es la primera pagina (pues en la primera pagina, podria ser que las primeras publicaciones falle la extraccion y el porcentaje seria 0 y por ende cortarria)
            if pag_num > 1:

                # Selecciono los boolean de las ultimas x paginas
                ultimas_paginas = historico_paginas[-cant_ult_pag:]
                # print("Ultimas {}:".format(cant_ult_pag), ultimas_paginas)

                # Cantidad de ultimas paginas que logre extraer datos
                cant_ult_pag_extraidas = sum(ultimas_paginas)

                # Defino porcentaje de las ultimas paginas que logre extraer datos
                porc_ult_pag_extraidas =  cant_ult_pag_extraidas / cant_ult_pag
                # print("Porcentaje de extraidas de ultimas", porc_ult_pag_extraidas)

                # Si el porcentaje de ultimas paginas extraidas es menor al porcentaje minimo
                if porc_ult_pag_extraidas < porc_min_ult_pag_extraidas:

                    # Dejo de extraer datos
                    ult_pag_sin_data = 1
                    break

        # HAGO CLICK EN "SIGUIENTE PAGINA"
        try:
            # Clikeo en "Siguiente pagina" tras haber visitado todas las publicaciones de una pagina
            driver.get(url_paginacion)
            print("Cambio de pagina", url_paginacion, pag_num)

            # Sumo 1 a parametro de corte de cantidad de paginas visitadas
            pag_num += 1

        except:
            # Corto la extraccion de datos
            print("Intento descubrir por que falla esto (deberia ser None):", url_paginacion)
            no_mas_paginas = 1
            print("No hay mas paginas")

    # Cierro el Web Browser Automatico dando por finalizada la extraccion de datos
    driver.close()

    # Explico razon por la que finalizo la extraccion de datos
    if ult_pag_sin_data == 1:
        print("Corto pues el Crawler ingreso al {} de las ultimas {} paginas".format(porc_ult_pag_extraidas, cant_ult_pag))
    elif no_mas_paginas == 1:
        print("Corto por no haber mas paginas. Se recorrieron {} paginas".format(pag_num))
    else:
        print("Corto porque se visitaron las {} primeras paginas".format(pag_max))

    return df_opiniones, df_modelos


def main():
    # Pedido al usuario de producto a buscar y, con el, creo objeto de clase Product
    # producto = Product(str(input("Ingrese producto a buscar: ")))
    producto = Product("celulares") # despues lo saco

    # Valido el producto buscado tal que no sea una busqueda tan amplia
    producto.nombre_subcat = producto.validacionBusqueda()

    # Obtengo atributos o caracteristicas mas relevantes del producto
    # producto.atributos = producto.getAtributos()
    producto.atributos = ['Marca', 'Modelo', 'Color', 'Resolución de la cámara trasera principal', 'Resolución de la cámara frontal principal', 'Con cámara', 'Cantidad de cámaras traseras', 'Con teclado QWERTY físico', 'Modelo del procesador', 'Es Dual SIM', 'Cantidad de ranuras para tarjeta SIM', 'Memoria interna', 'Memoria RAM', 'Tamaño de la pantalla', 'Tipo de resolución de la pantalla ', 'Resolución de la pantalla', 'Tecnología de la pantalla', 'Con pantalla táctil', 'Capacidad de la batería', 'Altura x Ancho x Profundidad', 'Red', 'Con conector USB', 'Con Wi-Fi', 'Con GPS', 'Con Bluetooth']

    # En base al producto a buscar, creo los dataframes
    df_opiniones = DataFrameCreator.CrearOpinionsDataFrame()
    df_modelos = DataFrameCreator.CrearModelosDataFrame(producto.atributos)

    # Carga de datos a dataframes
    df_opiniones, df_modelos = ExtractorDatos(producto, df_opiniones, df_modelos)

    # Exporto dataframes
    df_opiniones.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/extraccion_datos/df_opiniones_{}.xlsx'.format(producto.nombre), 'Hoja de datos', index=False)
    df_modelos.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/extraccion_datos/df_modelos_{}.xlsx'.format(producto.nombre), 'Hoja de datos', index=False)

main()