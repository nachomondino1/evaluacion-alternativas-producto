# Importo Librerias
import pandas as pd
from p1_data_understanding.collect_data import collect_data
from p1_data_understanding import describe_data, explore_data
from p2_data_preparation import format_data, clean_data, construct_data
from p3_modelling import sentiment_atribution, clustering
from bs4 import BeautifulSoup
from urllib.request import urlopen
from p3_modelling.utils import diccionario_palabras_relacionadas
import pickle

def select_product():
    """
    Permite seleccionar un producto y verifica que sea valido, es decir, lo suficientemente acotado.
    :return:
    """
    # Pido producto a relevar al administrador
    producto = str(input("Ingrese producto a relevar: "))

    # Obtengo URL de pagina principal del producto en Mercado Libre
    home_page_url = get_home_page_url(producto)

    print("Validando producto ingresado...".center(120))
    # Mientras el producto sea invalido
    while True:
        # Si el producto es valido
        if is_product_valid(home_page_url):
            # Salgo de la funcion con producto validado
            return producto, home_page_url
        # Si el producto no es valido
        else:
            # Vuelvo a pedir producto y busco el URL de su pagina principal en Mercado Libre
            producto = str(input("Ingrese producto a buscar: "))
            home_page_url = get_home_page_url(producto)

def is_product_valid(home_page_url):
    """
    Determina si un producto es valido o no segun si tiene subcategoria en Mercado Libre.
    :param home_page_url:
    :return: True si el producto es valido, de lo contrario, False
    """

    # Accedo a codigo html de home page
    html = urlopen(home_page_url)
    bs = BeautifulSoup(html, 'html.parser')

    # BUSCO TAG DONDE ESTA LA SUBCATEGORIA DEL PRODUCTO
    tag_nombre_subcat = bs.find('div', {'class': "ui-search-breadcrumb"}).find("meta", {"content": "2"})  # Antes buscaba solo si habia hasta el tag "ol" pero habia BUSQUEDAS QUE SON DE UNA SUBCATEGORIA Y EN LA HOMEPAGE SOLO APARECE SU CATEGORIA ppal y no la subcategoria... POR EJ:'comida preparada'  Lo podria solucionar en validacionBusqueda() buscando no solo el tag ol sino buscando el segundo tag li

    # SI NO ENCONTRE EL TAG DE LA SUBCATEGORIA (PRODUCTO NO VALIDO)
    if tag_nombre_subcat is None:
        print('Busqueda muy amplia, por favor sea mas especifico.', end=' ')
        return False
    else:
        return True

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
    '''
    # Escogo producto
    print(" (1) ELECCION DE PRODUCTO ".center(120, '#'))
    producto, home_page_url = select_product()
    print("Producto: ", producto), print("Pagina principal de mercado libre: ", home_page_url), print()


    print(" (2) DATA UNDERSTANDING ".center(120, '#'))
    print(" (2.1) COLLECT INITIAL DATA ".center(120))
    print(" a) Buscando atributos del producto...".center(120))
    atributos = collect_data.get_product_attributes(home_page_url)

    print(" b) Creando dataframes del producto...".center(120))
    df_alt = collect_data.create_dataframe_alternativas(atributos)
    df_opi = pd.DataFrame(columns=['id_alternativa', 'opinion'])
    print("Se han creado con exito los dataframes \n")

    print(" c) Extrayendo datos del producto...".center(120))
    df_alt, df_opi = collect_data.data_extractor(df_alt, df_opi, home_page_url)
    '''
    '''
    # Levanto df para hacer 2 y 3 independientemente
    producto = 'tv'
    df_alt = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/{}/df_alt.xlsx'.format(producto))
    df_opi = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/{}/df_opi.xlsx'.format(producto))

    print(" (2.2) DESCRIBE DATA ".center(120))
    describe_data.getting_to_know_data(df_opi)
    describe_data.getting_to_know_data(df_alt)  #  print("Dataframe alternativas".center(120))

    print(" (2.3) EXPLORE DATA ".center(120))
    print(" a) Analisis de unicidad de ids ".center(120))
    explore_data.check_ids(df_alt, df_opi)

    print(" b) Analisis de filas repetidas ".center(120))
    print("Dataframe opiniones (considerando unicamente opiniones)"), explore_data.check_repeated_rows(df_opi['opinion'])  # filas repetidas sin tener en cuenta el id_pub
    print("Dataframe alternativas (sin considerar id_alternativa ni precio)"), explore_data.check_repeated_rows(df_alt.iloc[:, 2:])  # filas repetidas sin tener en cuenta el id_pub y precio

    print(" c) Analisis de cantidad de opiniones por valor de cada campo especifico ".center(120))
    explore_data.n_opi_by_value(df_alt, df_opi)
    
    # Exporto data
    df_alt.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/{}/df_alt.xlsx'.format(producto), index=False)
    df_opi.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/{}/df_opi.xlsx'.format(producto), index=False)

    print(" (3) DATA PREPARATION ".center(120, "#"))
    print(" INICIALIZO DICCIONARIO DE PALABRAS RELACIONADAS ".center(120))  # 7. INICIALIZO DICCIONARIO DE PALABRAS RELACIONADAS
    d_rel_words = diccionario_palabras_relacionadas.get_dict_related_words(df_alt)
    # Exporto diccionario
    with open("d_rel_words.pkl", "wb") as tf:
        pickle.dump(d_rel_words, tf)

    print(" 1. OBTENGO CUSTOMER NEEDS DE OPINIONES".center(120))  # 1. OBTENGO CUSTOMER NEEDS DE OPINIONES
    print("# Elimino opinion=NaN y opiniones repetidas (CLEAN DATA)")  # Elimino opiniones repetidas y NaN
    df_opi = df_opi.dropna(subset='opinion')  # no documentado... creia que no habia opiniones nan
    df_opi = df_opi.drop_duplicates(subset='opinion', ignore_index=True).reset_index(drop=True)  # elimino duplicados teniendo en cuenta solo la columna content que es la que contiene opiniones propiamente
    print("# Limpieza opiniones (CLEAN DATA)")  # Limpio opiniones
    df_opi = clean_data.delete_date_of_issue_from_opinion(df_opi)  # Elimino fecha de emision al final de la opinion (por ej, "Hace x meses")
    df_opi.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_opi_without_date.xlsx'.format(producto))
    df_opi_tokenizado = clean_data.clean_opinions(df_opi)  # Preparo las opiniones
    print("# Obtengo palabras mas frecuentes en opiniones (CONSTRUCT DATA)")  # Obtengo palabras mas frecuentes en opiniones
    # l_most_freq_words = construct_data.most_frequent_words(df_opi_tokenizado)
    print("# Obtengo frases de 3 palabras mas frecuentes en opiniones (CONSTRUCT DATA)")  # Obtengo frases mas frecuentes en opiniones
    # l_possible_customer_needs = construct_data.most_frequent_phrases(df_opi_tokenizado)
    print("# Selecciono customer needs del producto (CONSTRUCT DATA)")  # Selecciono frases mas frecuentes como customer needs
    # df_cust_needs = construct_data.select_customer_needs(l_most_freq_words, l_possible_customer_needs)

    df_alt_cleaned = clean_data.disaggregate_columns_with_lists(df_alt) # hacerle print()....

    print(" 2. DESCARTO ATRIBUTOS DEL PRODUCTO EXTRAIDOS SOLO PARA SER MOSTRADOS AL CLIENTE".center(120))  # 2. DESCARTO ATRIBUTOS DEL PRODUCTO EXTRAIDOS SOLO PARA SER MOSTRADOS AL CLIENTE (teniendo en cuenta cuales son las cust needs)
    df_alt_cleaned = clean_data.select_attributes(df_alt_cleaned)

    print(" 3. OBTENGO MATRIZ DE RELACION. RELACIONO CUSTOMER NEEDS Y ATRIBUTOS DEL PRODUCTO".center(120)) # 3. RELACIONO (1) CUSTOMER NEEDS Y (2) ATRIBUTOS MEDIANTE 'MATRIZ DE RELACIONES'
    # df_relation_matrix = construct_data.create_relation_matrix(list(df_alt_cleaned.columns[1:]), list(df_cust_needs.index))

    
    # Exporto dataframes en prueba
    df_alt_cleaned.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_alt_cleaned.xlsx'.format(producto), index=False)  # cuando corra tod@ junto pongo product.nombre
    df_opi_tokenizado.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_opi_cleaned.xlsx'.format(producto))
    # Exporto dataframe de customer needs del producto
    df_cust_needs.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_cust_needs.xlsx'.format(producto))  # cuando corra tod@ junto pongo product.nombre
    df_relation_matrix.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_relation_matrix.xlsx'.format(producto), index_label="customer_need")


    # Levanto dfs e identifico el error
    producto = 'tv'
    df_alt_cleaned = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_alt_cleaned.xlsx'.format(producto))  # cuando corra tod@ junto pongo product.nombre
    df_opi = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_opi_without_date.xlsx'.format(producto), index_col=0)
    print(df_alt_cleaned)
    print(df_opi)

    print(" 4. ELIMINO ALTERNATIVAS ".center(120))  # 4. ELIMINO ALTERNATIVAS
    print(" # Por precio= NaN")
    df_alt_cleaned = clean_data.drop_alternatives_without_price(df_alt_cleaned)
    print("# Por repeticion (CLEAN DATA)")  # Por repeticion
    df_alt_cleaned = clean_data.drop_alt_duplicates(df_alt_cleaned, df_opi)   # NO DEBERIA SER NECESARIA PERO FALLA LA EXTRACCION EN EVITAR DUPLICADOS... FALTARIA DOC ahpra si es necesaria pues elimine atributos... al haber menos hay mas posib de filas repetidas
    print("# Por NaN values (CLEAN DATA)")  # Por tener muchos valores NaN
    df_alt_cleaned = clean_data.drop_alternatives_with_most_na(df_alt_cleaned, df_opi)
    print("# Por valores erroneos en publicaciones (CLEAN DATA)")  # Por tener valores erroneos
    df_alt_cleaned = clean_data.drop_alternatives_with_wrong_values(df_alt_cleaned, df_opi)  #falla


    print(" 5. CONVIERTO COLUMNAS A NUMERICAS PARA PODER OPERAR MATEMATICAMENTE ".center(120))
    print("# Convierto columnas SI-NO a 1-0 (FORMAT DATA)")  # Columnas si-no a 1-0
    df_alt_cleaned = format_data.yes_no_column_to_one_zero_column(df_alt_cleaned)
    print("# Convierto columnas de strings con numeros a columnas numericas (FORMAT DATA)")  # Convierto columnas inherentemente numericas a numericas
    df_alt_cleaned = format_data.string_column_to_numeric_column(df_alt_cleaned)

    print("6. CATEGORIZO COLUMNAS NUMERICAS CONTINUAS EN DATAFRAME ALTERNATIVAS".center(120))  # CATEGORIZO COLUMNAS NUMERICAS CONTINUAS EN DATAFRAME ALTERNATIVAS
    df_alt_cleaned.iloc[:, 1:] = clean_data.categorize_numeric_columns(df_alt_cleaned.iloc[:, 1:])  # categorizo columnas numericas con valores continuos, no le paso columna id pues la categorizaria.

    print(" 7. EXPORTO DATAFRAMES ".center(120))  # 7. EXPORTO DATAFRAMES
    # Exporto dataframes alternativas cleaned y opiniones cleaned
    df_alt_cleaned.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_alt_cleaned.xlsx'.format(producto), index=False)  # cuando corra tod@ junto pongo product.nombre
    # df_opi_tokenizado.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_opi_cleaned.xlsx'.format(producto))
    # Exporto dataframe de customer needs del producto
    #df_cust_needs.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_cust_needs.xlsx'.format(producto))  # cuando corra tod@ junto pongo product.nombre
    #df_relation_matrix.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_relation_matrix.xlsx'.format(producto), index_label="customer_need")
    '''

    # Levanto df para hacer modelling independientemente
    producto = 'tv'
    df_alt_cleaned = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_alt_cleaned.xlsx'.format(producto))
    df_opi = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_opi_without_date.xlsx'.format(producto), index_col=0)
    df_relation_matrix = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_relation_matrix.xlsx'.format(producto), index_col=0)
    print(df_alt_cleaned, df_opi, df_relation_matrix)
    df_cust_needs = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_cust_needs.xlsx'.format(producto), index_col=0)  # cuando corra tod@ junto pongo product.nombre

    d_rel_words = diccionario_palabras_relacionadas.get_dict_related_words(df_alt_cleaned)
    # Exporto diccionario
    with open("d_rel_words.pkl", "wb") as tf:
        pickle.dump(d_rel_words, tf)

    l_cust_needs_one_word = list(df_cust_needs.index)
    print(l_cust_needs_one_word)

    print(" (4) MODELLING ".center(120, "#"))
    print(" (4.1) ATRIBUCION ".center(120))
    print("a) Atribuyo sentiment a customer needs...".center(120))
    df_cust_need_sent = sentiment_atribution.to_customer_needs(df_opi, l_cust_needs_one_word)  # df_opi falta eliminar acentos...

    print("b) Atribuyo sentiment a valores de los atributos del producto...".center(120))
    df_attr_values_sent = sentiment_atribution.to_attribute_value(df_alt_cleaned, df_cust_need_sent, df_relation_matrix)

    # Exporto resultado de atribucion
    df_cust_need_sent.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/atribucion/{}/df_cust_need_sent.xlsx'.format(producto), index=False)  # cuando corra tod@ junto pongo product.nombre
    df_attr_values_sent.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/atribucion/{}/df_attr_values_sent.xlsx'.format(producto), index=False)  # cuando corra tod@ junto pongo product.nombre

    '''
    print(" (4.2) CLUSTERING ".center(120))
    print(" a) Creando el dataframe para clustering...")
    df_input_clustering = clustering.create_clustering_dataframe(df_alt_cleaned, df_attr_values_sent)
    print(df_input_clustering)

    print(" b) Aplicando clustering...")
    df_alt_cleaned_cluster = pd.concat([df_input_clustering['id_alternativa'], clustering.k_means(df_input_clustering.iloc[:, 1:])], axis=1)

    print(" c) Definiendo nombre de clusters...")
    # Creo tabla de centroides de clusters de alternativas segun sentiment
    clustering.create_table_cluster_centroids_sent(df_alt_cleaned_cluster)  # tabla 0 pues el cliente no la ve, es solo para mi y asi poder definir nombres de clusters
    # Obtengo nombre de clusters
    d_labels_names = clustering.cluster_names(df_alt_cleaned_cluster)
    # Reemplazo labels por nombre de labels
    df_alt_cleaned_cluster = clustering.replace_labels_with_names(df_alt_cleaned_cluster, d_labels_names)

    print(" d) Obteniendo dataframe alternativas para mostrar al cliente con los nombres de clusters correspondientes...")
    df_alt_correct_price_clust = clustering.drop_alternatives_unwanted(df_alt_correct_price, df_alt_cleaned_cluster)  # Elimino alternativas desechadas durante procesamiento y agrego columna label a dataframe alternativas

    print(" e) Obteniendo tabla de numero de alternativas por cluster...")
    df_alt_per_clust = clustering.create_table_num_alt_per_cluster(df_alt_cleaned_cluster)
    print(df_alt_per_clust)

    print(" f) Obteniendo tabla de centroides segun valores de atributos...")
    df_centroids_values = clustering.create_table_cluster_centroids_values(df_alt_correct_price, df_alt_cleaned_cluster)
    print(df_centroids_values)

    print(" g) Obteniendo tabla de numero de marcas por cluster...")
    df_brand_per_cluster = clustering.create_table_brand_per_cluster(df_alt_correct_price, df_alt_cleaned_cluster)
    print(df_brand_per_cluster)

    # Exporto resultados de clustering
    df_alt.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/clustering/{}/df_alt_clust.xlsx'.format(producto))
    df_alt_per_clust.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/clustering/{}/df_alt_per_clust.xlsx'.format(producto))
    df_centroids_values.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/clustering/{}/df_centroids_values.xlsx'.format(producto))
    df_brand_per_cluster.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/clustering/{}/df_brand_per_cluster.xlsx'.format(producto))
    '''

if __name__ == '__main__':
    main()


'''
# Corrijo columna precio (pues sera categorizada)
print("# Corrijo columna precio (FORMAT DATA)")
df_alt = format_data.correct_price_column(df_alt)
df_alt_correct_price = df_alt.copy()
df_alt_correct_price.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_alt_correct_price.xlsx'.format(producto), index=False)  # print("Exporto Dataframe alternativas con precio corregido pues sera utilizado para ser presentado al cliente \n")
'''

'''
print(" 7. INICIALIZO DICCIONARIO DE PALABRAS RELACIONADAS ".center(120))  # 7. INICIALIZO DICCIONARIO DE PALABRAS RELACIONADAS
#d_rel_words = diccionario_palabras_relacionadas.get_dict_related_words(df_alt_cleaned)
# Exporto diccionario de palabras relacionadas
with open("d_rel_words.pkl", "wb") as tf:
    pickle.dump(d_rel_words, tf)
'''