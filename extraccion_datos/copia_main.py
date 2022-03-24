# Importo librerias
from selenium import webdriver
from MercadoLibreCrawler import MercadoLibreCrawler
import DataFrameCreator
from product import Product


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
    pag_num, pag_max = 1, 10                                    # param 1: Hasta pagina 10 de Mercado libre
    no_mas_paginas = 0                                          # param 2: Hasta ultima pagina (cuando hay menos de 10)
    corte_pub_sin_opi, pub_sin_opi, pub_sin_opi_max = 0, 0, 15  # param 3: Hasta 15 publicaciones consec sin opiniones
    corte_pub_opi_rep, pub_opi_rep, pub_opi_rep_max = 0, 0, 15  # param 4: Hasta 15 publicaciones consec con opiniones repetidas

    # Defino lista en la que incluire las primeras opiniones de cada publicacion. Ayudara a no extraer opiniones repetidas
    l_prim_opiniones = []
    l_l_publicaciones = set() # sacar luego de correr pruebas

    # Ingreso a pagina principal del producto en Mercado Libre
    driver.get(producto.home_page_url)

    # Mientras que no se cumpla alguno de los cuatro parametro de corte
    while (pag_num < pag_max) and (no_mas_paginas == 0) and (corte_pub_sin_opi == 0) and (corte_pub_opi_rep == 0):

        # Extraigo URLs de cada una de las publicaciones de una pagina de Mercado Libre. Tambien de la paginacion.
        url_publicaciones = crawler.getPublicationsUrl()
        url_paginacion = crawler.getPaginacionUrl() #probe a ponerlo a bajo pero corto por no haberr mas paginas en la 5, para mi fallo la carga de  la pagina.

        # Recorro cada publicacion
        for url_publicacion in url_publicaciones:
            l_l_publicaciones.add(url_publicacion) #es para ver si el crawler ingresa a un link repetido o siempre es nueevo. Su largo deberia ser 50, 100, 150, y asi
            print("Publicacion numero:", len(l_l_publicaciones), url_publicacion)

            # Clickeo en una publicacion
            driver.get(url_publicacion)

            # Obtengo id de la publicacion (que identifica como unica a cada publicacion)
            id_publicacion = crawler.getIdPublicacion(url_publicacion)

            if id_publicacion != None: # estoy probando si falla mucho la extraccion del id (solo lo implemento en la copia del main)

                # Obtengo el URL del boton "Ver todas las opiniones"
                url_ver_todas_las_opiniones = crawler.getVerTodasLasOpinionesUrl()

                # Si existe el boton "Ver todas las opiniones" y extraje el id
                if url_ver_todas_las_opiniones != None:

                    # Clickeo en boton "Ver todas las opiniones"
                    driver.get(url_ver_todas_las_opiniones)

                    # Si las opiniones son nuevas (En meli, ≠ publicaciones pueden tener = opiniones)
                    if crawler.verificationNewOpinions(l_prim_opiniones) == True:

                        # Reinicio parametros de corte por publiaciones consecutivas sin opiniones o opiniones repetidas
                        pub_sin_opi, pub_opi_rep = 0, 0

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
                        # Sumo 1 al parametro de corte de opiniones repetidas
                        pub_opi_rep += 1
                        print("OPINIONES REPETIDAS", pub_opi_rep)

                        # Si llego al maximo de publicaciones seguidas con opiniones repetidas
                        if pub_opi_rep == pub_opi_rep_max:

                            # Corto la extraccion de datos
                            corte_pub_opi_rep = 1

                        # Clikeo en Volver saliendo de "Ver todas las opiniones"
                        driver.back()

                # No existe el boton "Ver todas las opiniones" (pub con  menos de 3 opiniones, o bien, no hay)
                else:
                    # Sumo 1 al parametro de corte de publicaciones sin opiniones
                    pub_sin_opi += 1
                    print("PUBLICACION SIN OPINIONES", pub_sin_opi)

                    # Si llego al maximo de publicaciones seguidas sin opiniones
                    if pub_sin_opi == pub_sin_opi_max:

                        # Corto la extraccion de datos
                        corte_pub_sin_opi = 1

                # Clikeo en Volver saliendo de la pagina de la publicacion y volviendo a la pagina principal
                driver.back()

            else:
                print("FALLO EXTRACCION DE ID")
                driver.back()


        # Si existe siguiente pagina
        if url_paginacion != None:

            # Clikeo en "Siguiente pagina" tras haber visitado todas las publicaciones de una pagina
            driver.get(url_paginacion)
            print("Cambio de pagina", url_paginacion, pag_num)

            # Sumo 1 a parametro de corte de cantidad de paginas visitadas
            pag_num += 1

        # Si no existe siguiente pagina
        else:
            # Corto la extraccion de datos
            no_mas_paginas = 1
            print("No hay mas paginas")

    # Cierro el Web Browser Automatico dando por finalizada la extraccion de datos
    driver.close()

    # Explico por que razon finalizo la extraccion de datos
    if corte_pub_sin_opi == 1:
        print("Corto por {} publicaciones seguidas sin opiniones".format(pub_sin_opi_max))
    elif corte_pub_opi_rep == 1:
        print("Corto por {} publicaciones seguidas con opiniones repetidas".format(pub_opi_rep_max))
    elif no_mas_paginas == 1:
        print("Corto por no haber mas paginas. Se recorrieron {} paginas".format(pag_num))
    else:
        print("Corto porque se visitaron las {} primeras paginas".format(pag_max))

    return df_opiniones, df_modelos


def main():
    # Pedido al usuario de producto a buscar y, con el, creo objeto de clase Product
    # producto = Product(str(input("Ingrese producto a buscar: ")))
    producto = Product("notebook") # despues lo saco
    # producto = Product("mancuernas") # despues lo saco

    # Valido el producto buscado tal que no sea una busqueda tan amplia
    producto.nombre_subcat = producto.validacionBusqueda()

    # Obtengo atributos o caracteristicas mas relevantes del producto
    producto.atributos = producto.getAtributos()
    print(producto.atributos)

    # En base al producto a buscar, creo los dataframes
    df_opiniones = DataFrameCreator.CrearOpinionsDataFrame()
    df_modelos = DataFrameCreator.CrearModelosDataFrame(producto.atributos)

    # Carga de datos a dataframes
    df_opiniones, df_modelos = ExtractorDatos(producto, df_opiniones, df_modelos)

    # Exporto dataframes
    df_opiniones.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/extraccion_datos/df_opiniones_{}.xlsx'.format(producto.nombre), 'Hoja de datos', index=False)
    df_modelos.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/extraccion_datos/df_modelos_{}.xlsx'.format(producto.nombre), 'Hoja de datos', index=False)

main()