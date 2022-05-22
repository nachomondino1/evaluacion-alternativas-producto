# Importo Librerias
import pandas as pd
from p1_data_understanding.collect_data import collect_data
from p1_data_understanding import describe_data, explore_data
from p2_data_preparation import format_data, clean_data, construct_data
from p3_modelling import sentiment_atribution, clustering
from bs4 import BeautifulSoup
from urllib.request import urlopen

def choose_product():
    # Pido producto a relevar al administrador
    producto = str(input("Ingrese producto a relevar: "))

    print("Validando producto ingresado...".center(120))
    # Valido el producto buscado tal que no sea una busqueda tan amplia
    producto, home_page_url = search_validation(producto)

    return producto, home_page_url

def search_validation(producto):
    """
    Valida la busqueda, es decir, verifica que sea lo suficientemente acotada tal que se refiere a un solo producto
    en particular (Mercado Libre le debe encontrar una subcategoria de producto). Si es invalido, pide productos
    hasta el primer producto valido
    :return: Funcion sin retorno
    """
    # Obtengo home page de producto
    home_page_url = get_home_page_url(producto)

    # ACCEDO AL CODIGO HTML DE LA PAGINA PRINCIPAL DEL PRODUCTO
    html = urlopen(home_page_url)
    bs = BeautifulSoup(html, 'html.parser')

    # BUSCO TAG DONDE ESTA LA SUBCATEGORIA DEL PRODUCTO
    tag_nombre_subcat = bs.find('div', {'class': "ui-search-breadcrumb"}).find("meta", {
        "content": "2"})  # Antes buscaba solo si habia hasta el tag "ol" pero habia BUSQUEDAS QUE SON DE UNA SUBCATEGORIA Y EN LA HOMEPAGE SOLO APARECE SU CATEGORIA ppal y no la subcategoria... POR EJ:'comida preparada'  Lo podria solucionar en validacionBusqueda() buscando no solo el tag ol sino buscando el segundo tag li

    # SI NO ENCONTRE EL TAG DE LA SUBCATEGORIA (PRODUCTO NO VALIDO)
    if tag_nombre_subcat is None:
        print('Busqueda muy amplia, por favor sea mas especifico.', end=' ')

        # PIDO NUEVO PRODUCTO
        producto = str(input("Ingrese producto a buscar: "))

        # VALIDA NUEVO PRODUCTO (FUNCION RECURSIVA)
        search_validation(producto)

    # SI ENCONTRE EL TAG DE LA SUBCATEGORIA (PRODUCTO VALIDO)
    else:
        # DEFINO EL NOMBRE DE LA SUBCATEGORIA A LA QUE PERTENECE EL PRODUCTO
        print("El producto ha sido validado con exito")
        return producto, home_page_url

def get_home_page_url(producto):
    """
    Busca URL de la Pagina principal de un producto en Mercado Libre
    :return: String con URL de la pagina principal del producto en Mercado Libre
    """
    # DEFINO REGLAS QUE SIGUE LA URL DE LA PAGINA PRINCIPAL DE UN PRODUCTO EN MERCADO LIBRE
    # si el producto tiene mas de una palabra, reemplazo espacios en blanco por guiones
    reg1 = producto.replace(" ", "-")

    # si el producto tiene mas de una palabra, reemplazo espacios en blanco por string "%20"
    reg2 = producto.replace(" ", "%20")

    # APLICO REGLAS A URL Y LA RETORNO
    return 'https://listado.mercadolibre.com.ar/{}#D[A:{}]'.format(reg1, reg2)

def main():
    # Escogo producto
    print(" (1) ELECCION DE PRODUCTO ".center(120, '#'))
    producto, home_page_url = choose_product()
    print("Pagina principal de mercado libre: ", home_page_url), print()

    print(" (2) DATA UNDERSTANDING ".center(120, '#'))
    print(" (2.1) COLLECT INITIAL DATA ".center(120))
    df_alt, df_opi = collect_data.main(home_page_url)

    # Exporto data
    df_alt.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/{}/df_alt.xlsx'.format(producto), index=False)
    df_opi.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/{}/df_opi.xlsx'.format(producto), index=False)
    '''
    
    # Levanto el dataframe ES PRUEBA DE (3)
    producto = 'tv'
    df_alt = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/{}/df_alt.xlsx'.format(producto))
    df_opi = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/{}/df_opi.xlsx'.format(producto))


    print(" (2.2) DESCRIBE DATA ".center(120))
    describe_data.main(df_alt, df_opi)

    print(" (2.3) EXPLORE DATA ".center(120))
    explore_data.main(df_alt, df_opi)

    # Exporto data
    # df_alt.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/{}/df_alt.xlsx'.format(producto), index=False)
    # df_opi.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/{}/df_opi.xlsx'.format(producto), index=False)


    print(" (3) DATA PREPARATION ".center(120, "#"))
    print(" (3.1) FORMAT DATA ".center(120))
    df_alt_correct_price, df_alt_formated = format_data.main(df_alt)
    print("Exporto Dataframe alternativas con precio corregido pues sera utilizado para ser presentado al cliente")
    df_alt_correct_price.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_alt_formated.xlsx'.format(producto), index=False)  # cuando corra tod@ junto pongo product.nombre

    print(" (3.2) CLEAN DATA ".center(120))
    df_alt_cleaned, df_opi_tokenizado = clean_data.main(df_alt_formated, df_opi)

    print(" (3.3) CONSTRUCT DATA ".center(120))
    df_alt_cleaned, df_cust_needs = construct_data.main(df_alt_cleaned, df_opi_tokenizado)
    l_cust_needs_one_word = df_cust_needs['cust_needs_one_word']  # customer needs de una palabra

    # EXPORTO DATAFRAMES
    # Exporto dataframes alternativas cleaned y opiniones cleaned
    df_alt_cleaned.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_alt_cleaned.xlsx'.format(producto), index=False)  # cuando corra tod@ junto pongo product.nombre
    df_opi_tokenizado.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_opi_cleaned.xlsx'.format(producto))
    # Exporto dataframe de customer needs del producto
    df_cust_needs.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_cust_needs.xlsx'.format(producto))  # cuando corra tod@ junto pongo product.nombre


    print(" (4) MODELLING ".center(120, "#"))
    print(" (4.1) ATRIBUCION ".center(120))
    df_cust_need_sent, df_relation_matrix, df_attr_values_sent = sentiment_atribution.main(df_alt_cleaned, df_opi, l_cust_needs_one_word)

    # Exporto resultado de atribucion
    df_cust_need_sent.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/atribucion/{}/df_cust_need_sent.xlsx'.format(producto), index=False)  # cuando corra tod@ junto pongo product.nombre
    df_relation_matrix.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/atribucion/{}/df_relation_matrix.xlsx'.format(producto), index_label="customer_need")
    df_attr_values_sent.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/{}/df_attr_values_sent.xlsx'.format(producto), index=False)  # cuando corra tod@ junto pongo product.nombre

    print(" (4.2) CLUSTERING ".center(120))
    df_alt,df_alt_per_clust, df_alt_per_clust, df_brand_per_cluster =  clustering.main(df_alt, df_alt_cleaned, df_attr_values_sent)

    # Exporto resultados de clustering
    df_alt.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/clustering/{}/df_alt_clust.xlsx'.format(producto))
    df_alt_per_clust.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/clustering/{}/df_alt_per_clust.xlsx'.format(producto))
    df_alt_per_clust.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/clustering/{}/df_centroids_values.xlsx'.format(producto))
    df_brand_per_cluster.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/clustering/{}/df_brand_per_cluster.xlsx'.format(producto))
    '''

if __name__ == '__main__':
    main()
