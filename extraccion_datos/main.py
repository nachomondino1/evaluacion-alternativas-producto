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
opts.add_argument("USER_AGENT=Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543a Safari/419.3")
driver = webdriver.Chrome('/Users/nachomondino/Desktop/chromedriver', chrome_options=opts)


def AgregarFilasAlDataFrame(d_data_publicacion, df):
    """
    Agrega datos en un DataFrame existente
    :param d_data_publicacion: diccionario con datos. Los value pueden ser un solo valor o una lista de valores
    :param df: DataFrame existente
    :return: DataFrame existente con nuevos datos agregados
    """

    # Convierto diccionario a DataFrame para poder concatenarlos luego
    try:
        new_df = pd.DataFrame(data=d_data_publicacion) #index=[0]
    except:
        new_df = pd.DataFrame(data=d_data_publicacion, index=[0])

    # Concateno los dataframe agregando la nueva publicacion a ya extraidas.
    df = pd.concat([df, new_df])

    return df


def CrearPublicationsDataFrame(campos_especificos):
    """
    Crea DataFrame (vacio, sin datos aun) de publicaciones con los nombres de las columnas de aquellos campos que
    deseo extraer de una publicacion
    :param campos_especificos: Lista de campos especificos de una subcategoria de productos de Mercado Libre que
    deseo extraer. Por ejemplo, "tamano de pantalla" para la subcategoria "Celulares y Smartphones". Su largo dependera
    de cada subcategoria, por lo que, la cantidad de columnas del df tambien variara de una subcategoria a otra.
    :return: DataFrame para guardar informacion de publicaciones de una subcategoria en particular
    """
    # A priori, extraigo de cada publicacion los campos generales a todas las subcategorias de productos
    campos_a_extraer = ['id_publicacion', 'nombre_publicacion', 'estado', 'precio', 'envio', 'devolucion', 'compra_protegida']

    # Agrego los campos especificos de la subcategoria
    for campos_especifico in campos_especificos:
        campos_a_extraer.append(campos_especifico)

    # Creo el DataFrame con los campos a extraer como columnas de este
    df = pd.DataFrame(columns=campos_a_extraer)

    return df


def BuscaSubcategoriaID(df_categorias, subcategoria_producto):
    '''
    A partir del nombre de la subcategoria de un prodcuto, encuentra el id de esta.
    :param df_categorias: DataFrame con informacion sobre las categorias y subcategorias de los productos de Mercado
    Libre. En particular 4 columnas: id de categoria, nombre de categoria, id de subcategoria y nombre de subcategoria
    :param subcategoria_producto: Nombre de la subcategoria de un producto
    :return: id de la subcategoria de dicho producto
    '''
    # Extraigo fila del df de la subcategoria del producto
    datos_subcategoria = df_categorias[df_categorias.subcategoria == subcategoria_producto]

    # De dicha fila me interesa solo la columna del id de la subcategoria (numero 2)
    id = datos_subcategoria.iloc[0, 2]

    return id


def main():
    # luego implementare que busqueda = 20/30 prod mas demandados.
    # producto = str(input("Ingrese producto: "))
    # producto = "Mancuernas"
    producto = "celulares"

    # Creo objetos crawler y api para tener disponible todos los metodos de ambas formas de extraccion
    crawler = MercadoLibreCrawler(driver, producto)
    api = MercadoLibreApi()

    # Valido el producto buscado tal que no sea una busqueda tan amplia
    '''
    while crawler.validacionBusqueda(busqueda) == None:
        print("Por favor sea mas especifico en su busqueda")
        busqueda = str(input("Ingrese busqueda: "))
    '''

    # Ingreso a HomePage de Mercado Libre del producto buscado
    home_page_url = crawler.getHomePageUrl(producto)
    driver.get(home_page_url)

    # Busco informacion de subcategorias y, a partir del nombre de la subcategoria del producto, encuentro su id.
    df_categorias = api.getCategoriasID()
    nombre_subcategoria_producto = crawler.getSubcategoriaProducto(home_page_url)
    id_subcategoria_producto = BuscaSubcategoriaID(df_categorias, nombre_subcategoria_producto)
    # print(id_subcategoria_producto)

    # Busco atributos de una subcategoria de productos a partir de su id
    atributos = api.getAtributosSubcategoria(id_subcategoria_producto)
    # print('atributos:', atributos)

    # Creo dataframes en los que guardare la informacion extraida # VERE DE SACARLO LUEGO
    df_opiniones = pd.DataFrame(columns=['id_publicacion','title', 'content', 'rate', 'likes', 'dislikes'])
    df_publicaciones = CrearPublicationsDataFrame(atributos)

    # Defino parametros para que que corte el web scraping
    paginacion_num, paginacion_max = 1, 10
    pub_consec_sinopi, pub_consec_sinopi_max = 0, 5

    # Extraer info hasta que entre 5 veces consecutivas a publicaciones sin opiniones o que haya visitado mas de 10 paginas
    while (pub_consec_sinopi < pub_consec_sinopi_max) or (paginacion_num < paginacion_max):

        # Extraigo links de la pagina principal de Mercado Libre. De cada publicacion y para cambiar de pagina
        links_publicaciones = crawler.getPublicationsUrl(driver)
        link_paginacion = crawler.getPaginacionUrl(driver)

        # Recorro cada publicacion
        for publicacion in links_publicaciones[:3]:

            # Ingreso a una publicacion
            driver.get(publicacion)

            # Obtengo id de la publicacion (que identifica como unica a cada publicacion)
            id_publicacion = crawler.getIdPublicacion(driver)

            # Click en "Ver todas las opiniones" --> Si no puede hacer click es por dos razones: 1) o no hay opiniones 2) hay menos de 3 opiniones. En cualquier caso me conviene no obtenerlas
            if crawler.ClickVerTodasLasOpiniones(driver) == True:

                # Verifico que las Opiniones sean nuevas
                if crawler.verificationNewOpinions(driver, df_opiniones) == True:
                    pub_consec_sinopi = 0

                    # Hago Scroll down para cargar todas las opiniones (pues son nuevas y las quiero extraer)
                    crawler.ScrollDown(driver)

                    # Extraigo opiniones y las guardo en df_opiniones
                    d_opiniones_publicacion = crawler.getPublicacionOpinions(driver, id_publicacion)
                    # df_opiniones = storing_data.OpinionsDataFrame(id_publicacion, l_opiniones_publicacion, df_opiniones)
                    df_opiniones = AgregarFilasAlDataFrame(d_opiniones_publicacion, df_opiniones)
                    print(df_opiniones)

                    # Salgo de "Ver todas las opiniones"
                    driver.back()

                    # Extraigo datos de la publicacion (notar que solo lo extraigo si las opiniones son nuevas) y
                    # los guardo en df_publicaciones
                    d_data_publicacion = crawler.PublicationExtractor(driver, id_publicacion, atributos)
                    df_publicaciones = AgregarFilasAlDataFrame(d_data_publicacion, df_publicaciones)
                    print(df_publicaciones)

                else:
                    # Vuelvo a pagina de publicacion
                    driver.back()

            else:
                pub_consec_sinopi += 1

            # Vuelvo a Home Page
            driver.back()  # Puede que no haga falta

        # Hago click en Siguiente pagina (guardo paginas visitadas?)
        driver.get(link_paginacion)
        print("Cambio de pagina", link_paginacion)
        paginacion_num += 1

    # Explico por que razon finalizo el web scraping...
    if pub_consec_sinopi == pub_consec_sinopi_max:
        print("Corto por 5 publicaciones seguidas sin opiniones ")
    else:
        print("Corto porque se visitaron las 10 primeras paginas")

    driver.close()

    # Exporto dataframes
    # tendre que implementar una forma de guardar el archivo para ≠ productos..
    # df_opiniones.to_excel('/Users/nachomondino/Desktop/df_opiniones.xlsx', 'Hoja de datos', index=False)
    # df_datos_publicaciones.to_excel('/Users/nachomondino/Desktop/df_publications.xlsx', 'Hoja de datos', index=False)

main()

