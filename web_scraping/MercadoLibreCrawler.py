# Implementacion con Selenium
"""
Pensar en la implementacion de codigo valido en general para muchos links y no solo para celulares --> a lo mejor puedo hacer un input al cliente, buscar eso en meli y extraer la categoria y asi obtener la pagina principal
Hacer todo con funciones
Pensar en el handle de excepciones
Page loads son una mierda (perdida de tiempo para asegurarse que cargue, o bien, extraes antes de que termine de cargar y crashea). En cambio, conviene usar WebDriverWait and expected_conditions. This script has several new imports, most notably WebDriverWait and expected_conditions, both of which are combined here to form what Selenium calls an implicit wait.
"""

# Importo librerias
import pandas as pd
import random
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import OpinionsExtractor as oe
import LinksExtractor as le
import WebScrapingActions


# Defino a Chrome como Web Browser
opts = Options()
opts.add_argument(
    "USER_AGENT=Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543a Safari/419.3")
driver = webdriver.Chrome('/Users/nachomondino/Desktop/chromedriver', chrome_options=opts)


def unirDataFrames(df1,df2):
    df = pd.concat([df1, df2])
    return df


def main():
    df_opiniones_publicaciones = pd.DataFrame(columns=['title', 'content', 'rate', 'likes', 'dislikes'])
    paginacion_num, paginacion_max = 1, 10

    # Pedido al usuario de producto a buscar
    busqueda = str(input("Ingrese busqueda: "))

    # Valido la busqueda (para que no sea tan amplia)
    while WebScrapingActions.validacionBusqueda(driver, busqueda) == False:
        print("Por favor sea mas especifico en su busqueda")
        busqueda = str(input("Ingrese busqueda: "))

    # Ingreso a HomePage
    driver.get(le.getHomePageUrl(busqueda))

    while paginacion_num < paginacion_max:

        # Extraigo links
        links_publicaciones = le.getPublicationsUrl(driver)
        link_paginacion = le.getPaginacionUrl(driver)

        for publicacion in links_publicaciones[:3]:

            # Ingreso a publicacion
            driver.get(publicacion)

            # Click en "Ver todas las opiniones" --> Si no puede hacer click es por dos razones: 1) o no hay opiniones 2) hay menos de 5 opiniones. En cualquier caso me conviene no obtenerlas
            if oe.ClickVerTodasLasOpiniones(driver) == True:

                # Verifico Opiniones Repetidas
                if oe.verificationNewOpinions(driver, df_opiniones_publicaciones) == True:
                    # Hago Scroll down para cargar todas las opiniones (pues son nuevas y las quiero extraer)
                    WebScrapingActions.ScrollDown(driver)

                    # Extraigo opiniones
                    df_opiniones_publicacion = oe.getPublicacionOpinions(driver)
                    print(df_opiniones_publicacion)
                    df_opiniones_publicaciones = unirDataFrames(df_opiniones_publicaciones, df_opiniones_publicacion)

                    # Extraigo descripcion del producto (notar que solo lo extraigo si las opiniones son nuevas)
                    driver.back()  # salgo de "ver todas las opiniones"

                    # implementar extraccion
                    
                else:
                    # Vuelvo a pagina de publicacion
                    driver.back()

            else:
                pass

            # Vuelvo a Home Page
            driver.back() # Puede que no haga falta

        # Hago click en Siguiente pagina  (guardo paginas visitadas?)
        driver.get(link_paginacion)
        print("Cambio de pagina", link_paginacion)
        paginacion_num += 1

    driver.close()

main()


"""
Implementacion con BeautifulSoup

# Importo librerias
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re

def getLinks(url):
    '''
    Obtiene links de la pagina web a partir de su URL pasada como parametro.

    :return:
    Lista de links de la pagina web
    '''

    i = 1
    # Cargo en variable el codigo HTML de la pagina
    html = urlopen(url)

    # Creo objeto de BeautifulSoup que permite operar el codigo html
    bs = BeautifulSoup(html.read(), "html.parser")

    # Extraigo links dentro del codigo html
    links = bs.find_all("div",{"class","ui-search-result__image"}).a
    # find_all("div",{"class":"ui-search-result__image"})

    #links = bs.find_all("a",{"href":re.compile('(/MLA)+')})

    for link in links:
        # algunos tags "a" no tienen atributo "href"
        if "href" in link.attrs:
            print(link.attrs["href"])
            print(i)
            i += 1



# Pruebo pagina principal
getLinks("https://celulares.mercadolibre.com.ar/#menu=categories")

# Pruebo una publicacion
#getLinks("https://www.mercadolibre.com.ar/lg-k62-128-gb-sky-blue-4-gb-ram/p/MLA16998061?pdp_filters=item_id:MLA1110271363#searchVariation=MLA16998061&position=1&search_layout=stack&type=pad&tracking_id=eb724177-656c-4fc1-b719-907784f8b18b")


Si extriago todos los links de la pagina, me extrae links que no requiero.

Que tienen en comun los links de las publicaciones?
- Tienen el termino "MLA" en su url
- estan en tag div class="ui-search-result__image" --> porque en el otro div hay dos links
Ojo! cada publicacion posee dos veces su link, una vez en la imagen y otra vez en el titulo.



Alternativa a getRate con BautifulSoup --> funciona medio mal:
  pageSource = driver.page_source
    bs = BeautifulSoup(pageSource, 'html.parser')
    print(bs.find_all("svg"))

"""
