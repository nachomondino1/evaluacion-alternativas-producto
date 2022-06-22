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
    :return: Producto y pagina principal de Mercado Libre
    """
    # Pido producto a relevar al administrador
    producto = str(input("Ingrese producto a relevar: "))

    # Obtengo URL de pagina principal del producto en Mercado Libre
    home_page_url = get_home_page_url(producto)
    print("Validando producto ingresado...".center(120))

    # Si el producto es valido
    if not is_product_valid(home_page_url):
        print('Busqueda muy amplia, por favor sea mas especifico.', end=' ')
        return select_product()  # El return asegura que a la primera carga valida, salga
    return producto, home_page_url

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
    res = False if tag_nombre_subcat is None else True
    return res

def get_home_page_url(producto):
    """
    Busca URL de la Pagina principal de un producto en Mercado Libre
    :return: String con URL de la pagina principal del producto en Mercado Libre
    """
    # DEFINO REGLAS QUE SIGUE LA URL DE LA PAGINA PRINCIPAL DE UN PRODUCTO EN MERCADO LIBRE
    reg1 = producto.replace(" ", "-")  # si el producto tiene mas de una palabra, reemplazo espacios en blanco por guiones
    reg2 = producto.replace(" ", "%20")  # si el producto tiene mas de una palabra, reemplazo espacios en blanco por string "%20"

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
    l_atributos = collect_data.get_product_attributes(home_page_url)

    print(" b) Creando dataframes del producto...".center(120))
    df_alt = pd.DataFrame(columns=['id_alternativa', 'precio'] + l_atributos)
    df_opi = pd.DataFrame(columns=['id_alternativa', 'opinion'])
    print("Se han creado con exito los dataframes \n")

    print(" c) Extrayendo datos del producto...".center(120))
    df_alt, df_opi = collect_data.data_extractor(df_alt, df_opi, home_page_url)

    # Exporto data
    #df_alt.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/{}/df_alt.xlsx'.format(producto), index=False)
    #df_opi.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/{}/df_opi.xlsx'.format(producto), index=False)

    # PRUEBA
    # df_alt.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/prueba/df_alt.xlsx'.format(producto), index=False)
    # df_opi.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/prueba/df_opi.xlsx'.format(producto), index=False)

    '''

    # Levanto df para hacer 2 y 3 independientemente
    producto = 'prueba_cel(sin_param y cond nuevo)'
    df_alt = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/{}/df_alt.xlsx'.format(producto))
    df_opi = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/{}/df_opi.xlsx'.format(producto))
    df_alt_cleaned_to_client = df_alt.copy()  # parece boludo el copy() pero sino el nuevo df sufre los mismos cambios que df_alt por mas que lo cambie de nombre a df_alt_cleaned...

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

    """
    # Exporto data
    df_alt.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/{}/df_alt.xlsx'.format(producto), index=False)
    df_opi.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/{}/df_opi.xlsx'.format(producto), index=False)
    """


    print(" (3) DATA PREPARATION ".center(120, "#"))
    # Adentro de construct_data.filter_most_frequent_words ojo que lo uso en sentiment atrib.to_cust_needs tmb
    # INICIALIZO DICCIONARIO DE PALABRAS RELACIONADAS (lo tengo que inicializar antes de construct data... (pues lo uso) ?)
    # d_rel_words = diccionario_palabras_relacionadas.get_dict_related_words(producto)


    # df_cust_needs = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/tv/df_cust_needs.xlsx',index_col=0)
    '''
    print("3.1. CUSTOMER NEEDS")  # La eleccion de customer needs en independiente de la eleccion de atributos. Toda customer need sera tenida en cuenta independientemente de si tiene o no al menos un atributo con el cual relacionarse
    print(" # CLEAN DATA: Limpieza de opiniones  ")
    print("## Elimino opiniones repetidas y opiniones NaN")  # Elimino opiniones repetidas y NaN
    df_opi = df_opi.dropna(subset='opinion')  # no documentado... creia que no habia opiniones nan
    df_opi = df_opi.drop_duplicates(subset='opinion', ignore_index=True).reset_index(drop=True)  # elimino duplicados teniendo en cuenta solo la columna content que es la que contiene opiniones propiamente
    print("## Stop word removal, puntuaction, tokenization")  # Limpio opiniones
    df_opi = clean_data.delete_date_of_issue_from_opinion(df_opi)  # Elimino fecha de emision al final de la opinion (por ej, "Hace x meses")
    df_opi.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_opi_without_date.xlsx'.format(producto))
    df_opi_tokenizado = clean_data.clean_opinions(df_opi)  # Preparo las opiniones

    print("# CONSTRUCT DATA: Selecciono customer needs del producto")
    print("## Obtengo palabras mas frecuentes en opiniones")  # Obtengo palabras mas frecuentes en opiniones
    l_most_freq_words = construct_data.most_frequent_ngrams(df_opi_tokenizado=df_opi_tokenizado, n_ngram=1, QUANT_NGRAMS=200)

    print("### Filtro palabras mas frecuentes")  # Obtengo palabras mas frecuentes en opiniones
    l_most_freq_words_filt = construct_data.filter_most_frequent_words(l_most_freq_words, d_rel_words)  # NUEVO!

    print("## Obtengo frases de 3 palabras mas frecuentes en opiniones")  # Obtengo frases mas frecuentes en opiniones
    l_possible_customer_needs = construct_data.most_frequent_ngrams(df_opi_tokenizado=df_opi_tokenizado, n_ngram=3, QUANT_NGRAMS=4000)

    print("## Selecciono customer needs del producto propiamente")  # Selecciono frases mas frecuentes como customer needs
    df_cust_needs = construct_data.select_customer_needs(l_most_freq_words_filt, l_possible_customer_needs)
    '''

    print("3.2. ATRIBUTOS")
    print("# FORMAT DATA: Convierto columnas de strings con numeros a columnas numericas")  # Convierto columnas inherentemente numericas a numericas
    df_alt_cleaned = format_data.string_column_to_numeric_column(df_alt)
    print("# FORMAT DATA: Desagrego columnas cuyos valores son listas")
    # df_alt_cleaned = clean_data.disaggregate_columns_with_lists(df_alt_cleaned)  # dsp de convert no num porque el "/" a veces es parte de la unidad. Las columnas generadas no requieren de quitar ninguna unidad pues son 1-0
    print("# FORMAT DATA: Convierto columnas SI-NO a 1-0")  # Columnas si-no a 1-0
    df_alt_cleaned = format_data.yes_no_column_to_one_zero_column(df_alt_cleaned)
    print(" # CLEAN DATA: Descarto atributos extriados exclusivamente para ser mostrados a cliente")
    df_alt_cleaned = clean_data.select_attributes(df_alt_cleaned)  # debo desagregar columnas antes...
    print(" # CLEAN DATA: Limpieza de alternativas")
    print(" ## Por precio=NaN")
    df_alt_cleaned = df_alt_cleaned.dropna(subset=['precio']).reset_index(drop=True)  # Incluir 'Modelo' luego lo quito
    print(df_alt_cleaned.shape)
    print("## Por repeticion de modelos")  # Por repeticion
    df_alt_cleaned = clean_data.drop_alt_duplicates(df_alt_cleaned, df_opi).reset_index(drop=True)    # FALTARIA DOC ahpra si es necesaria pues elimine atributos... al haber menos hay mas posib de filas repetidas
    print(df_alt_cleaned.shape)
    print("## Por cantidad de NaN values")  # Por tener muchos valores NaN
    df_alt_cleaned = clean_data.drop_alternatives_with_most_na(df_alt_cleaned, df_opi)
    print(df_alt_cleaned.shape)

    # Borro alternativas que elimine de analisis (ademas de no usarlas en analisis tampoco seran mostradas al cliente)
    ids_cleaned = df_alt_cleaned["id_alternativa"].unique()
    df_alt_cleaned_to_client = df_alt_cleaned_to_client[df_alt_cleaned_to_client.id_alternativa.isin(ids_cleaned)].reset_index(drop=True)  # Elimino alternativas

    print("## Por valores erroneos en publicaciones")  # Por tener valores erroneos
    # df_alt_cleaned = clean_data.drop_alternatives_with_wrong_values(df_alt_cleaned, df_opi)  # debe ser despues de convertir a numerica las columnas
    df_alt_cleaned, df_alt_cleaned_to_client  = clean_data.drop_alternatives_with_wrong_values(df_alt_cleaned, df_alt_cleaned_to_client, df_opi)  # debe ser despues de convertir a numerica las columnas
    df_alt_cleaned_to_client.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_alt_cleaned_to_client.xlsx'.format("prueba"), index=False)  # cuando corra tod@ junto pongo product.nombre
    print(df_alt_cleaned)
    print(df_alt_cleaned_to_client)  # Deberia tener menos alternativas pues elimina tmb las alt que tienen opis y al menos un valor mal cargado (en cambio en analisis la dejo pues me da opiniones)

    print(" # CLEAN DATA: Limpieza de atributos de alternativas")
    print(" ## Descarto atributos con un solo valor unico")
    df_alt_cleaned = clean_data.delete_attr_x_values(df_alt_cleaned) # despues de la eliminacion de alternativas tal vez quedo un solo valor
    print("## Categorizo columnas numericas continuas")  # CATEGORIZO COLUMNAS NUMERICAS CONTINUAS EN DATAFRAME ALTERNATIVAS
    df_alt_cleaned.iloc[:, 1:] = clean_data.categorize_numeric_columns(df_alt_cleaned.iloc[:, 1:])  # categorizo columnas numericas con valores continuos, no le paso columna id pues la categorizaria.
    # Debo eliminar alt antes...


    print(" 3.3. MATRIZ DE RELACIONES".center(120))
    print("# Obtengo matriz de relaciones") # 3. RELACIONO CUSTOMER NEEDS Y ATRIBUTOS MEDIANTE 'MATRIZ DE RELACIONES'
    df_relation_matrix = construct_data.create_relation_matrix(list(df_alt_cleaned.columns[1:]), list(df_cust_needs.index))
    # Agrego customer needs sin relaciones como atributos del producto --> al crear la matriz, si temrina con relacion 0, agregar columna...


    # EXPORTO DATAFRAMES
    # Exporto dataframes alternativas cleaned y opiniones cleaned
    # df_alt_cleaned.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_alt_cleaned.xlsx'.format(producto), index=False)  # cuando corra tod@ junto pongo product.nombre
    # df_opi_tokenizado.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_opi_cleaned.xlsx'.format(producto))
    # Exporto dataframe de customer needs del producto
    #df_cust_needs.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_cust_needs.xlsx'.format(producto))  # cuando corra tod@ junto pongo product.nombre
    #df_relation_matrix.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_relation_matrix.xlsx'.format(producto), index_label="customer_need")

    # df_alt_cleaned.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_alt_cleaned.xlsx'.format("prueba"), index=False)  # cuando corra tod@ junto pongo product.nombre
    # Exporto dataframe de customer needs del producto
    # df_cust_needs.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_cust_needs.xlsx'.format("prueba"))  # cuando corra tod@ junto pongo product.nombre
    # df_relation_matrix.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_relation_matrix.xlsx'.format("prueba"), index_label="customer_need")


    '''
    # Levanto df para hacer modelling independientemente
    producto = 'prueba'
    df_alt_cleaned = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_alt_cleaned.xlsx'.format(producto))
    df_opi = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_opi_without_date.xlsx'.format(producto), index_col=0)
    df_relation_matrix = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_relation_matrix.xlsx'.format(producto), index_col=0)
    print(df_alt_cleaned, df_opi, df_relation_matrix)
    df_cust_needs = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_cust_needs.xlsx'.format(producto), index_col=0)  # cuando corra tod@ junto pongo product.nombre

    d_rel_words = diccionario_palabras_relacionadas.get_dict_related_words("tv")
    d_avoid_fp = diccionario_palabras_relacionadas.get_dict_avoid('tv')
    
    """
    # Exporto diccionario
    with open("d_rel_words.pkl", "wb") as tf:
        pickle.dump(d_rel_words, tf)
    """
    
    l_cust_needs_one_word = list(df_cust_needs.index)
    print(l_cust_needs_one_word)


    print(" (4) MODELLING ".center(120, "#"))
    print(" (4.1) ATRIBUCION ".center(120))
    print("a) Atribuyo sentiment a customer needs...".center(120))
    df_cust_need_sent = sentiment_atribution.to_customer_needs(df_opi, l_cust_needs_one_word, d_rel_words, d_avoid_fp)  # df_opi falta eliminar acentos...

    print("b) Atribuyo sentiment a valores de los atributos del producto...".center(120))
    df_attr_values_sent, df_attr_alt_sent = sentiment_atribution.to_attribute(df_alt_cleaned, df_cust_need_sent, df_relation_matrix)

    # Exporto resultado de atribucion
    df_cust_need_sent.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/atribucion/{}/df_cust_need_sent.xlsx'.format(producto), index=False)  # cuando corra tod@ junto pongo product.nombre
    df_attr_values_sent.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/atribucion/{}/df_attr_values_sent.xlsx'.format(producto), index=False)  # cuando corra tod@ junto pongo product.nombre
    df_attr_alt_sent.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/atribucion/{}/df_attr_alt_sent.xlsx'.format(producto), index=False)  # cuando corra tod@ junto pongo product.nombre
    
    
    """
    # Levanto df para hacer modelling independientemente
    producto = 'celulares'
    df_alt_to_client = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_alt_cleaned_to_client.xlsx'.format(producto))
    df_alt_cleaned = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_alt_cleaned.xlsx'.format(producto))
    df_attr_values_sent = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/atribucion/{}/df_attr_values_sent.xlsx'.format(producto))
    # print(df_alt_correct_price)
    


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
    # df_alt_correct_price_clust = clustering.drop_alternatives_unwanted(df_alt_correct_price, df_alt_cleaned_cluster)  # Elimino alternativas desechadas durante procesamiento y agrego columna label a dataframe alternativas
    df_alt_to_client_clust = clustering.add_clust_label(df_alt_to_client, df_alt_cleaned_cluster)  # Elimino alternativas desechadas durante procesamiento y agrego columna label a dataframe alternativas

    print(" e) Obteniendo tabla de numero de alternativas por cluster...")
    df_alt_per_clust = clustering.create_table_num_alt_per_cluster(df_alt_cleaned_cluster)
    print(df_alt_per_clust)

    print(" f) Obteniendo tabla de centroides segun valores de atributos...")
    df_centroids_values = clustering.create_table_cluster_centroids_values(df_alt_to_client, df_alt_cleaned_cluster)
    print(df_centroids_values)

    print(" g) Obteniendo tabla de numero de marcas por cluster...")
    df_brand_per_cluster = clustering.create_table_brand_per_cluster(df_alt_to_client, df_alt_cleaned_cluster)
    print(df_brand_per_cluster)

    # Exporto resultados de clustering
    df_alt_to_client_clust.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/clustering/{}/df_alt_to_client_clust.xlsx'.format(producto))
    df_alt_per_clust.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/clustering/{}/df_alt_per_clust.xlsx'.format(producto))
    df_centroids_values.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/clustering/{}/df_centroids_values.xlsx'.format(producto))
    df_brand_per_cluster.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/clustering/{}/df_brand_per_cluster.xlsx'.format(producto))
    """
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







'''

 print(" (3) DATA PREPARATION ".center(120, "#"))
    print(" 1. FORMAT DATA (Dataframe alternativas)".center(120))
    print("# Convierto columnas de strings con numeros a columnas numericas")  # Convierto columnas inherentemente numericas a numericas
    df_alt_cleaned = format_data.string_column_to_numeric_column(df_alt)
    print("# Desagrego columnas cuyos valores son listas")
    df_alt_cleaned = clean_data.disaggregate_columns_with_lists(df_alt_cleaned)  # dsp de convert no num porque el "/" a veces es parte de la unidad. Las columnas generadas no requieren de quitar ninguna unidad pues son 1-0
    print("# Convierto columnas SI-NO a 1-0")  # Columnas si-no a 1-0
    df_alt_cleaned = format_data.yes_no_column_to_one_zero_column(df_alt_cleaned)


    print(" 2. CLEAN DATA ".center(120))
    print(" # Dataframe alternativas  ".center(120)) #     print(" 2. ELIMINO ALTERNATIVAS ".center(120))  # 4. ELIMINO ALTERNATIVAS
    print(" ## Descarto atributos extriados exclusivamente para ser mostrados a cliente")
    df_alt_cleaned = clean_data.select_attributes(df_alt_cleaned)  # debo desagregar columnas antes...
    print(" ## Elimino alternativas")
    print(" ### Por precio= NaN")
    df_alt_cleaned = clean_data.drop_alternatives_without_price(df_alt_cleaned)  # Incluir 'Modelo' luego lo quito
    print("### Por repeticion")  # Por repeticion
    # df_alt_cleaned_with_mod = pd.concat([df_alt_cleaned, df_alt['Modelo']])
    df_alt_cleaned = clean_data.drop_alt_duplicates(df_alt_cleaned, df_opi)   # NO DEBERIA SER NECESARIA PERO FALLA LA EXTRACCION EN EVITAR DUPLICADOS... FALTARIA DOC ahpra si es necesaria pues elimine atributos... al haber menos hay mas posib de filas repetidas
    print("### Por NaN values")  # Por tener muchos valores NaN
    df_alt_cleaned = clean_data.drop_alternatives_with_most_na(df_alt_cleaned, df_opi)
    print("### Por valores erroneos en publicaciones")  # Por tener valores erroneos
    df_alt_cleaned = clean_data.drop_alternatives_with_wrong_values(df_alt_cleaned, df_opi)  # debe ser despues de convertir a numerica las columnas
    print(" ## Descarto atributos con un solo valor unico")
    df_alt_cleaned = clean_data.delete_attr_x_values(df_alt_cleaned) # despues de la eliminacion de alternativas tal vez quedo un solo valor
    print("## Categorizo columnas numericas continuas")  # CATEGORIZO COLUMNAS NUMERICAS CONTINUAS EN DATAFRAME ALTERNATIVAS
    df_alt_cleaned.iloc[:, 1:] = clean_data.categorize_numeric_columns(df_alt_cleaned.iloc[:, 1:])  # categorizo columnas numericas con valores continuos, no le paso columna id pues la categorizaria.
    # Debo eliminar alt antes...

    print(" # Dataframe opiniones  ".center(120)) #     print(" 2. ELIMINO ALTERNATIVAS ".center(120))  # 4. ELIMINO ALTERNATIVAS
    print("## Elimino opinion=NaN y opiniones repetidas")  # Elimino opiniones repetidas y NaN
    df_opi = df_opi.dropna(subset='opinion')  # no documentado... creia que no habia opiniones nan
    df_opi = df_opi.drop_duplicates(subset='opinion', ignore_index=True).reset_index(drop=True)  # elimino duplicados teniendo en cuenta solo la columna content que es la que contiene opiniones propiamente
    print("## Limpieza opiniones")  # Limpio opiniones
    df_opi = clean_data.delete_date_of_issue_from_opinion(df_opi)  # Elimino fecha de emision al final de la opinion (por ej, "Hace x meses")
    df_opi.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_opi_without_date.xlsx'.format(producto))
    df_opi_tokenizado = clean_data.clean_opinions(df_opi)  # Preparo las opiniones


    # Adentro de construct_data.filter_most_frequent_words ojo que lo uso en sentiment atrib.to_cust_needs tmb
    # INICIALIZO DICCIONARIO DE PALABRAS RELACIONADAS (lo tengo que inicializar antes de construct data... (pues lo uso) ?)
    d_rel_words = diccionario_palabras_relacionadas.get_dict_related_words(producto)



    
    print(" 3. CONSTRUCT DATA".center(120))  # 1. OBTENGO CUSTOMER NEEDS DE OPINIONES
      print("# Selecciono customer needs del producto")
    print("## Obtengo palabras mas frecuentes en opiniones")  # Obtengo palabras mas frecuentes en opiniones
    l_most_freq_words = construct_data.most_frequent_ngrams(df_opi_tokenizado=df_opi_tokenizado, n_ngram=1,
                                                            QUANT_NGRAMS=200)

    print("### Filtro palabras relacionadas")  # Obtengo palabras mas frecuentes en opiniones
    l_most_freq_words_filt = construct_data.filter_most_frequent_words(l_most_freq_words, d_rel_words)  # NUEVO!

    print("## Obtengo frases de 3 palabras mas frecuentes en opiniones")  # Obtengo frases mas frecuentes en opiniones
    l_possible_customer_needs = construct_data.most_frequent_ngrams(df_opi_tokenizado=df_opi_tokenizado, n_ngram=3,
                                                                    QUANT_NGRAMS=4000)

    print(
        "## Selecciono customer needs del producto propiamente")  # Selecciono frases mas frecuentes como customer needs
    df_cust_needs = construct_data.select_customer_needs(l_most_freq_words_filt, l_possible_customer_needs)

    print("# Obtengo matriz de relaciones") # 3. RELACIONO CUSTOMER NEEDS Y ATRIBUTOS MEDIANTE 'MATRIZ DE RELACIONES'
    df_relation_matrix = construct_data.create_relation_matrix(list(df_alt_cleaned.columns[1:]), list(df_cust_needs.index))

    # Agrego customer needs sin relaciones como atributos del producto --> al crear la matriz, si temrina con relacion 0, agregar columna...
    


    # EXPORTO DATAFRAMES
    # Exporto dataframes alternativas cleaned y opiniones cleaned
    df_alt_cleaned.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_alt_cleaned.xlsx'.format(producto), index=False)  # cuando corra tod@ junto pongo product.nombre
    df_opi_tokenizado.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_opi_cleaned.xlsx'.format(producto))
    # Exporto dataframe de customer needs del producto
    # df_cust_needs.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_cust_needs.xlsx'.format(producto))  # cuando corra tod@ junto pongo product.nombre
    # df_relation_matrix.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_relation_matrix.xlsx'.format(producto), index_label="customer_need")


'''