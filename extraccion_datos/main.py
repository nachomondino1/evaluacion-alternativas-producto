# Importo librerias
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from MercadoLibreCrawler import MercadoLibreCrawler
from MercadoLibreCrawler import Product
from MercadoLibreApi import MercadoLibreApi
from selenium.webdriver.common.by import By
from time import sleep # despues la saco e implemento implicit wait
from bs4 import BeautifulSoup
from urllib.request import urlopen
import DataFrameCreator



def Extractor(crawler):
    # Obtengo url de Pagina principal del producto e ingreso
    HomePageUrl = crawler.producto.HomePageUrl
    driver = crawler.driver

    # Ingreso a pagina principal del producto en Mercado Libre
    crawler.driver.get(HomePageUrl)

    # Creo dataframes
    df_opiniones = pd.DataFrame(columns=['id_publicacion','title', 'content', 'rate', 'likes', 'dislikes'])
    atributos = crawler.producto.getAtributos()
    df_modelos = DataFrameCreator.CrearModelosDataFrame(atributos)

    # Defino parametros para que que corte el web scraping
    paginacion_num, paginacion_max = 1, 10
    pub_consec_sinopi, pub_consec_sinopi_max = 0, 5
    no_mas_paginas = 0

    # Extraer info hasta que entre 5 veces consecutivas a publicaciones sin opiniones o que haya visitado mas de 10 paginas
    while (paginacion_num < paginacion_max) and (no_mas_paginas == 0):
        print(pub_consec_sinopi < pub_consec_sinopi_max) #no lo puedo poner aca porque solo chequea en cada cambio de pagina
        print(paginacion_num < paginacion_max)
        print(no_mas_paginas == 0)

        # Extraigo links de la pagina principal de Mercado Libre. De cada publicacion y para cambiar de pagina
        links_publicaciones = crawler.getPublicationsUrl(driver)

        # Recorro cada publicacion
        for publicacion in links_publicaciones[:3]:

            # Ingreso a una publicacion
            driver.get(publicacion)

            # Obtengo id de la publicacion (que identifica como unica a cada publicacion)
            id_publicacion = crawler.getIdPublicacion(driver) #no lo esta extrayendo
            print(id_publicacion)

            # Click en "Ver todas las opiniones" --> Si no puede hacer click es por dos razones: 1) o no hay opiniones 2) hay menos de 3 opiniones. En cualquier caso me conviene no obtenerlas
            if crawler.ClickVerTodasLasOpiniones(driver) == True:

                # Verifico que las Opiniones sean nuevas
                if crawler.verificationNewOpinions(driver, df_opiniones) == True:
                    # Reinicio parametro de corte por publiaciones consecutivas sin opiniones pues encontro nuevas opiniones
                    pub_consec_sinopi = 0

                    # Hago Scroll down para cargar todas las opiniones (pues son nuevas y las quiero extraer)
                    crawler.ScrollDown(driver)

                    # Extraigo opiniones y las guardo en df_opiniones
                    d_opiniones_publicacion = crawler.getPublicationOpinionsData(driver, id_publicacion)
                    df_opiniones = DataFrameCreator.AgregarFilasAlDataFrame(d_opiniones_publicacion, df_opiniones)
                    print(df_opiniones)

                    # Salgo de "Ver todas las opiniones"
                    driver.back()

                    # Extraigo datos de la publicacion (notar que solo lo extraigo si las opiniones son nuevas) y
                    # los guardo en df_publicaciones
                    d_data_modelos = crawler.getModeloData(driver, id_publicacion, atributos)
                    df_modelos = DataFrameCreator.AgregarFilasAlDataFrame(d_data_modelos, df_modelos)
                    print(df_modelos)

                else:
                    # Vuelvo a pagina de publicacion
                    print("OPINIONES REPETIDAS")
                    driver.back()

            else:
                print("PUBLICACION SIN OPINIONES")
                pub_consec_sinopi += 1

                if pub_consec_sinopi == pub_consec_sinopi_max:
                    break # no funciona creo
                print(pub_consec_sinopi)

            # Vuelvo a Home Page
            driver.back()  # Puede que no haga falta

        # Hago click en Siguiente pagina (guardo paginas visitadas?)
        link_paginacion = crawler.getPaginacionUrl(driver)

        # Puede que no haya mas paginas...
        if link_paginacion != None:
            driver.get(link_paginacion)
            print("Cambio de pagina", link_paginacion)
            paginacion_num += 1
        else:
            no_mas_paginas = 1

    # Explico por que razon finalizo el web scraping...
    if pub_consec_sinopi == pub_consec_sinopi_max:
        print("Corto por 5 publicaciones seguidas sin opiniones ")
    else:
        print("Corto porque se visitaron las 10 primeras paginas")

    driver.close()

    # Exporto dataframes --> implementarlo en DataFrameCreator.py
    # tendre que implementar una forma de guardar el archivo para ≠ productos..
    df_opiniones.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/extraccion_datos/df_opiniones_{}.xlsx'.format(producto), 'Hoja de datos', index=False)
    df_modelos.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/extraccion_datos/df_modelos_{}.xlsx'.format(producto), 'Hoja de datos', index=False)


def main():
    # Creo objetos crawler para tener disponible todos los metodos para hacer web scraping
    crawler = MercadoLibreCrawler()

    # Defino driver y producto a buscar
    # Defino a Chrome como Web Browser
    opts = Options()
    opts.add_argument(
        "USER_AGENT=Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543a Safari/419.3")
    crawler.driver = webdriver.Chrome('/Users/nachomondino/PycharmProjects/Utils/web_scraping_browsers/chromedriver',
                              chrome_options=opts)
    # crawler.producto = str(input("Ingrese producto a buscar: "))
    crawler.producto = "banco de pesas"

    # Valido el producto buscado tal que no sea una busqueda tan amplia
    crawler.validacionBusqueda()

    # Extraigo datos del producto buscado usando el driver
    Extractor(crawler)

main()


'''
    # Solicito producto al cliente
    # busqueda = str(input("Ingrese producto a buscar: ")) # luego implementare que busqueda = 20/30 prod mas demandados.
    # busqueda = "Mancuernas"
    busqueda = "celulares"
    busqueda = "banco de pesas"
        
    # Defino a Chrome como Web Browser
    opts = Options()
    opts.add_argument(
        "USER_AGENT=Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543a Safari/419.3")
    driver = webdriver.Chrome('/Users/nachomondino/PycharmProjects/Utils/web_scraping_browsers/chromedriver',
                              chrome_options=opts)
'''