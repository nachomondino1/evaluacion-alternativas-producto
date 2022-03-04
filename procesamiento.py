"""
Pseudocodigo de lo que quisiera que haga:
# Para una búsqueda de muchas búsquedas: # que busquedas? Podria guardar una lista de los 20/30 productos mas demandados por los clientes y tener esos datos ya preparados. El resto de las busquedas se podrian hacer en el momento llamando a procesamiento.py y le podria mostrar un relojito al cliente porque va a tardar.
    1.- Extrae los datos mediante web scraping para esa busqueda (uso directorio de web scraping)
    2.- Limpio el texto (uso directorio de text mining)
        2.1 Extrae Customer needs (a partir de analisis de opiniones)
    3. Busca atributos
    4. Me pide matriz de relaciones
    5. Sentiment Analysis
    (necesito matriz de relaciones si o si para linkear el sentiment de las customer needs a cada valor de cada atributo).
    Por ej, si una opinion dice que el celular le dura
    todo el dia entonces se relacion con la bateria y el tamaño de pantalla del celular (en menor medida) y le debere
    asignar ese sentiment al valor en particular que toma la bateria y el que toma el tamaño de pantalla. Si por ejemplo,
    “el celular le dura todo el dia” tiene un sentiment de 4.3, y el celularr tiene bateria de 4500 mAh y tamaño de pantalla de 5’’
    entonces le asigno 4.3 a bateria = 4500 mAh y 4.3 a tamaño de pantalla = 5’’ (tendria que ver de agregar la influencia de la relacion entre customer need y
    atributo pues tamaño de pantalla tiene menos relacion con  “el celular le dura todo el dia” que el atributo bateria por lo que, no deberian tener 4,3 los dos..)
"""

# Importo librerias
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from MercadoLibreCrawler import MercadoLibreCrawler

# Faltaria importar browser_crawler para scroll down


# Defino a Chrome como Web Browser
opts = Options()
opts.add_argument(
    "USER_AGENT=Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543a Safari/419.3")
driver = webdriver.Chrome('/Users/nachomondino/Desktop/chromedriver', chrome_options=opts)

"""
def unirDataFrames(df1,df2):
    df = pd.concat([df1, df2])
    return df
"""

def OpinionsDataFrame(new_opinions, df):
    """
    Mi idea es hacer una funcion que cree el dataframe
    :return:
    """
    # Creo diccionario con nuevas opiniones y luego lo convierto a dataFrame
    d = {'title':new_opinions[0], 'content':new_opinions[1], 'rate':new_opinions[2], 'likes':new_opinions[3], 'dislikes':new_opinions[4]}
    new_df = pd.DataFrame(data=d)

    # Concateno los dataframe de opiniones juntando las viejas y las nuevas
    df = pd.concat([df, new_df])
    return df


def main():
    df_opiniones_publicaciones = pd.DataFrame(columns=['title', 'content', 'rate', 'likes', 'dislikes'])
    paginacion_num, paginacion_max = 1, 10

    # luego implementare que busqueda = 20/30 prod mas demandados
    # busqueda = str(input("Ingrese producto: "))
    busqueda = "celulares"

    crawler = MercadoLibreCrawler(driver, busqueda)

    # Valido la busqueda (para que no sea tan amplia)
    while crawler.validacionBusqueda(driver,busqueda) == None:
        print("Por favor sea mas especifico en su busqueda")
        busqueda = str(input("Ingrese busqueda: "))


    # Ingreso a HomePage
    driver.get(crawler.getHomePageUrl(busqueda))

    while paginacion_num < paginacion_max:

        # Extraigo links
        links_publicaciones = crawler.getPublicationsUrl(driver)
        link_paginacion = crawler.getPaginacionUrl(driver)

        for publicacion in links_publicaciones[:3]:

            # Ingreso a publicacion
            driver.get(publicacion)

            # Click en "Ver todas las opiniones" --> Si no puede hacer click es por dos razones: 1) o no hay opiniones 2) hay menos de 5 opiniones. En cualquier caso me conviene no obtenerlas
            if crawler.ClickVerTodasLasOpiniones(driver) == True:

                # Verifico Opiniones Repetidas
                if crawler.verificationNewOpinions(driver, df_opiniones_publicaciones) == True:
                    # Hago Scroll down para cargar todas las opiniones (pues son nuevas y las quiero extraer)
                    # WebScrapingActions.ScrollDown(driver)

                    # Extraigo opiniones
                    opiniones_publicacion = crawler.getPublicacionOpinions(driver)
                    df_opiniones_publicaciones = OpinionsDataFrame(opiniones_publicacion, df_opiniones_publicaciones)
                    print(df_opiniones_publicaciones)
                    # Extraigo descripcion del producto (notar que solo lo extraigo si las opiniones son nuevas)
                    driver.back()  # salgo de "ver todas las opiniones"

                    # implementar extraccion

                else:
                    # Vuelvo a pagina de publicacion
                    driver.back()

            else:
                pass

            # Vuelvo a Home Page
            driver.back()  # Puede que no haga falta

        # Hago click en Siguiente pagina  (guardo paginas visitadas?)
        driver.get(link_paginacion)
        print("Cambio de pagina", link_paginacion)
        paginacion_num += 1

    driver.close()

main()

