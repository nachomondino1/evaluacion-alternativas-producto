# Importo librerias
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from MercadoLibreCrawler import MercadoLibreCrawler
from MercadoLibreApi import MercadoLibreApi
from selenium.webdriver.common.by import By
from time import sleep # despues la saco e implemento implicit wait


# Defino a Chrome como Web Browser
opts = Options()
opts.add_argument(
    "USER_AGENT=Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543a Safari/419.3")
driver = webdriver.Chrome('/Users/nachomondino/Desktop/chromedriver', chrome_options=opts)


def OpinionsDataFrame(id_publicacion, new_opinions, df):
    """
    Mi idea es hacer una funcion que cree el dataframe
    CRASHEA...
    :return:
    TENGO QUE VER SI LA DEJO ACA...
    """
    idx, l_id_publicacion, d = 0, [], {}
    l = ['id','title','content','rate', 'likes', 'dislikes']

    # Creo lista del id pues muchas opiniones pertenecen al mismo id
    for i in range(len(new_opinions)):
        l_id_publicacion.append(id_publicacion)

    # Inserto la lista de id en la primera posicion
    new_opinions.insert(0, l_id_publicacion)

    # Creo diccionario con nuevas opiniones y luego lo convierto a dataFrame
    for columna in new_opinions:
        d[l[idx]] = columna
        idx += 1
    new_df = pd.DataFrame(data=d)

    # Concateno los dataframe de opiniones juntando las viejas y las nuevas
    df = pd.concat([df, new_df])
    print(df)
    return df


# def PublicacionesDataFrame(id_publicacion, new_publications, df):
    # Sera una funcion practicamente igual a OpinionsDataFrame()


def getIdentificadorProducto(driver):
    # los dos df tienen que tener el id pero no creo que este bien pasarlo como parametro en los get()
    # es mejor llamar a esta funcion dentro de las funciones get()
    # esta hecha muy wachiturro --> no creo que sea la version final

    url = driver.find_element(By.XPATH, '//meta[@property="og:url"]').get_attribute('content')
    print(url)

    try:
        idx_ini = url.index('p/MLA')
        id = url[idx_ini + 5:]

    except:
        idx_ini = url.index('MLA-')
        idx_fin = url.index('-')
        id = url[idx_ini + 4:idx_fin]

    return id


def BuscaCategoriaID(id_categorias,categoria_busqueda):
    datos_categoria = id_categorias[id_categorias.subcategoria == categoria_busqueda]
    id = datos_categoria.iloc[0,2]
    return id


def main():
    df_opiniones_publicaciones = pd.DataFrame(columns=['id','title', 'content', 'rate', 'likes', 'dislikes'])
    paginacion_num, paginacion_max = 1, 10

    # luego implementare que busqueda = 20/30 prod mas demandados. Creo que cambiaria "busqueda" por "producto"
    # busqueda = str(input("Ingrese producto: "))
    # busqueda = "Mancuernas"
    busqueda = "celulares"


    # Creo objetos crawler y api para tener disponible todos los metodos de ambas formas de extraccion
    crawler = MercadoLibreCrawler(driver, busqueda)
    api = MercadoLibreApi()

    # Valido la busqueda (para que no sea tan amplia)
    '''
    while crawler.validacionBusqueda(busqueda) == None:
        print("Por favor sea mas especifico en su busqueda")
        busqueda = str(input("Ingrese busqueda: "))
    '''

    # Ingreso a HomePage
    home_page_url = crawler.getHomePageUrl(busqueda)
    driver.get(home_page_url)

    # IMPLEMENTAR BUSQUEDA DE ID_CATEGORIA
    categoria_busqueda = crawler.getCategoriaBusqueda(home_page_url)
    id_categorias = api.getCategoriasID()
    id_categoria_busqueda = BuscaCategoriaID(id_categorias,categoria_busqueda)
    print(id_categoria_busqueda)

    #  BUSQUEDA DE ATRIBUTOS SEGUN LA CATEGORIA DEL PRODUCTO
    atributos = api.getAtributosCategoria(id_categoria_busqueda)
    print('atributos:', atributos)
    # api.getAtributosCategoria("MLA1055") #Ejemplo de categoria de producto

    while paginacion_num < paginacion_max:

        # Extraigo links
        links_publicaciones = crawler.getPublicationsUrl(driver)
        link_paginacion = crawler.getPaginacionUrl(driver)

        for publicacion in links_publicaciones[:3]:
            # Ingreso a publicacion
            driver.get(publicacion)
            print(publicacion)

            # Obtengo id del producto
            # GETPUBLICATIONSURL() obtiene urls que son de la forma "https://click1.mercadolibre.com.ar..." que no siguen las reglas...
            # Y cuando hago el driver.get(url) no falla pues ese link raro te termina mandando a la url para la cual hice la funcion getIdentificadorProducto()
            # id_publicacion = getIdentificadorProducto(driver)

            # Click en "Ver todas las opiniones" --> Si no puede hacer click es por dos razones: 1) o no hay opiniones 2) hay menos de 3 opiniones. En cualquier caso me conviene no obtenerlas
            if crawler.ClickVerTodasLasOpiniones(driver) == True:

                # Verifico Opiniones Repetidas
                if crawler.verificationNewOpinions(driver, df_opiniones_publicaciones) == True:

                    # Hago Scroll down para cargar todas las opiniones (pues son nuevas y las quiero extraer)
                    # crawler.ScrollDown() # TENDRE QUE VER COMO LLAMAR EL METODO DE LA CLASE PADRE CRAWLER

                    # Extraigo opiniones
                    # opiniones_publicacion = crawler.getPublicacionOpinions(driver)
                    # df_opiniones_publicaciones = OpinionsDataFrame(id_publicacion, opiniones_publicacion, df_opiniones_publicaciones)
                    driver.back()  # salgo de "ver todas las opiniones"

                    # Extraigo descripcion del producto (notar que solo lo extraigo si las opiniones son nuevas)
                    sleep(3)
                    datos_publicaciones = crawler.PublicationExtractor(driver, atributos)
                    # print(datos_publicaciones)

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

