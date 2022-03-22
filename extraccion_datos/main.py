# Importo librerias
from selenium import webdriver
from MercadoLibreCrawler import MercadoLibreCrawler
import DataFrameCreator
from product import Product


def ExtractorDatos(producto, df_opiniones, df_modelos):
    """
    Extrae datos de opiniones y de las publicaciones de un producto mediante web scraping y la API de Mercado Libre
    y los almacena en los DataFrames pasados como parametro. Representa toda la logica de extraccion.

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

    # Simplemente para que el codigo quede mas simple
    HomePageUrl = crawler.producto.HomePageUrl
    driver = crawler.driver

    # Defino parametros de corte de la extraccion
    # Parametro 1: Extraer datos hasta pagina 10 de Mercado libre
    paginacion_num, paginacion_max = 1, 10
    # Parametro 2: Extraer datos hasta ultima pagina (si hay menos de 10 paginas para ese producto)
    no_mas_paginas = 0
    # Parametro 3: Extraer datos a menos que no extraiga datos de 10 publicaciones consecutivas por no tener opiniones
    corte_pub_consec_sinopi, pub_consec_sinopi, pub_consec_sinopi_max = 0, 0, 15

    # Ingreso a pagina principal del producto en Mercado Libre
    driver.get(HomePageUrl)

    # Mientras que no se cumpla alguno de los tres parametro de corte
    while (paginacion_num < paginacion_max) and (no_mas_paginas == 0) and (corte_pub_consec_sinopi == 0):

        # Extraigo links de la pagina principal de Mercado Libre. De cada publicacion y para cambiar de pagina
        links_publicaciones = crawler.getPublicationsUrl()
        link_paginacion = crawler.getPaginacionUrl()

        # Recorro cada publicacion
        for publicacion in links_publicaciones[:3]:

            # Ingreso a una publicacion
            driver.get(publicacion)

            # Obtengo id de la publicacion (que identifica como unica a cada publicacion)
            id_publicacion = crawler.getIdPublicacion()
            if len(id_publicacion) == 0: #solo para ver cual es el error
                print("FALLO LA EXTRACCION DEL ID", publicacion)
            print("Nueva publicacion a extraer datos:", publicacion)

            # Clickeo, si existe en la publicacion, en "Ver todas las opiniones"
            if crawler.ClickVerTodasLasOpiniones() == True:

                # Si las opiniones son nuevas (En meli, ≠ publicaciones pueden tener = opiniones)
                if crawler.verificationNewOpinions(df_opiniones) == True:

                    # Reinicio parametro de corte por publiaciones consecutivas sin opiniones pues encontro nuevas opiniones
                    pub_consec_sinopi = 0

                    # Hago Scroll down para cargar todas las opiniones (pues son nuevas y las quiero extraer)
                    crawler.ScrollDown()

                    # Procedo a extraccion de datos
                    # Extraigo opiniones y las guardo en df_opiniones
                    d_opiniones_publicacion = crawler.getPublicationOpinionsData(id_publicacion)
                    df_opiniones = DataFrameCreator.AgregarFilasAlDataFrame(d_opiniones_publicacion, df_opiniones)
                    print(df_opiniones)

                    # Salgo de "Ver todas las opiniones"
                    driver.back()

                    # Extraigo datos de la publicacion (notar que solo lo extraigo si las opiniones son nuevas) y
                    # los guardo en df_modelos
                    d_data_modelos = crawler.getModeloData(id_publicacion, crawler.producto.atributos)
                    df_modelos = DataFrameCreator.AgregarFilasAlDataFrame(d_data_modelos, df_modelos)
                    print(df_modelos)

                # Las opiniones se repiten con las de otra publicacion, por lo que, no extraigo nada
                else:
                    print("OPINIONES REPETIDAS")
                    # Vuelvo a pagina de publicacion para luego poder volver a la pagina principal
                    driver.back()

            # La publicacion no tiene boton "Ver todas las opiniones" porque hay menos de 3 opiniones, o bien, no hay
            else:
                print("PUBLICACION SIN OPINIONES")
                # Sumo 1 a la variable "publicaciones consecutivas sin opiniones"
                pub_consec_sinopi += 1
                print("VERIFICAR QUE NO TIENE OPINIONES", publicacion) #para verificar que no tenga opiniones

                # Si llegue al maximo de "publicaciones consecutivas sin opiniones", dejar de extraer
                if pub_consec_sinopi == pub_consec_sinopi_max:
                    corte_pub_consec_sinopi = 1

            # Habiendo extraido datos de la publicacion o no segun corresponda, vuelvo a Home Page para continuar con
            # otra publicacion
            driver.back()

        # Terminado de extraer datos de las publicaciones de una pagina, clicke en "siguiente pagina" si existe
        if link_paginacion != None:
            driver.get(link_paginacion)
            print("Cambio de pagina", link_paginacion)
            paginacion_num += 1
        # No hay "siguiente pagina", por lo que, dejo de extraer datos
        else:
            no_mas_paginas = 1
            print("No hay mas paginas")

    # Cierro el Web Browser Automatico dando por finalizada la extraccion de datos
    driver.close()

    # Explico por que razon finalizo la extraccion de datos
    if corte_pub_consec_sinopi == 1:
        print("Corto por 10 publicaciones seguidas sin opiniones ")
    elif no_mas_paginas == 1:
        print("Corto por no haber mas paginas")
    else:
        print("Corto porque se visitaron las 10 primeras paginas")

    return df_opiniones, df_modelos


def main():
    # Pedido al usuario de producto a buscar y, con el, creo objeto de clase Product
    # producto = Product(str(input("Ingrese producto a buscar: ")))
    producto = Product("celulares") # despues lo saco
    # producto = Product("mancuernas") # despues lo saco

    # Valido el producto buscado tal que no sea una busqueda tan amplia
    producto.nombre_subcat = producto.validacionBusqueda()

    # Obtengo atributos o caracteristicas mas relevantes del producto
    producto.atributos = producto.getAtributos()

    # Creo dataframes
    df_opiniones = DataFrameCreator.CrearOpinionsDataFrame()
    df_modelos = DataFrameCreator.CrearModelosDataFrame(producto.atributos) #ver si puede llamar a producto.atributos dentro

    # Carga de datos a dataframes usando el crawler
    df_opiniones, df_modelos = ExtractorDatos(producto, df_opiniones, df_modelos)

    # Exporto dataframes --> implementarlo en DataFrameCreator.py
    df_opiniones.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/extraccion_datos/df_opiniones_{}.xlsx'.format(producto.nombre), 'Hoja de datos', index=False)
    df_modelos.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/extraccion_datos/df_modelos_{}.xlsx'.format(producto.nombre), 'Hoja de datos', index=False)

main()