# Importo librerias
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from MercadoLibreCrawler import MercadoLibreCrawler


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


def getIdentificadorProducto(url):
    # los dos df tienen que tener el id pero no creo que este bien pasarlo como parametro en los get()
    # es mejor llamar a esta funcion dentro de las funciones get()
    # esta hecha muy wachiturro --> no creo que sea la version final

    try:
        idx_ini = url.index('MLA-')
        idx_fin = url.index('-')
        id = url[idx_ini+4:idx_fin]

    except:
        idx_ini = url.index('p/MLA')
        idx_fin = url.index('?')
        id = url[idx_ini+5:idx_fin]

    return id


def main():
    df_opiniones_publicaciones = pd.DataFrame(columns=['id','title', 'content', 'rate', 'likes', 'dislikes'])
    paginacion_num, paginacion_max = 1, 10

    # luego implementare que busqueda = 20/30 prod mas demandados
    # busqueda = str(input("Ingrese producto: "))
    busqueda = "celulares"

    # Creo objeto crawler para tener disponible todos los metodos
    crawler = MercadoLibreCrawler(driver, busqueda)

    # Valido la busqueda (para que no sea tan amplia)
    while crawler.validacionBusqueda(driver,busqueda) == None:
        print("Por favor sea mas especifico en su busqueda")
        busqueda = str(input("Ingrese busqueda: "))

    # Ingreso a HomePage
    driver.get(crawler.getHomePageUrl(busqueda))

    # IMPLEMENTAR BUSQUEDA DE ID_CATEGORIA


    # IMPLEMENTAR BUSQUEDA DE ATRIBUTOS SEGUN LA CATEGORIA DEL PRODUCTO

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

                    # Obtengo id del producto
                    id_publicacion = getIdentificadorProducto(publicacion)

                    # Hago Scroll down para cargar todas las opiniones (pues son nuevas y las quiero extraer)
                    crawler.ScrollDown(driver) #TEMPORALMENTE LO LLAMO ASI, LUEGO TENDRE QUE IMPORTARLO DE OTRO ARCHIVO

                    # Extraigo opiniones
                    opiniones_publicacion = crawler.getPublicacionOpinions(driver)
                    df_opiniones_publicaciones = OpinionsDataFrame(id_publicacion, opiniones_publicacion, df_opiniones_publicaciones)
                    #print(df_opiniones_publicaciones)
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

