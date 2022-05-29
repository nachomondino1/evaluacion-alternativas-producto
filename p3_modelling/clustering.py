# Importo librerias
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
# import matplotlib.pyplot as plt


def create_clustering_dataframe(df_alt, df_attr_values):
    """
    Agrega informacion de distintos dataframes para crear el dataframe con todos valores numericos y sin NaN y asi poder
    hacer clustering
    :param df_alt: Dataframe cuya unidad de analisis es cada una de las alternativas del producto, sus columnas
    son los atributos del producto y las celdas el valor que toma el atributo en una alternativa
    :param df_attr_values: Dataframe cuya unidad de analisis son los valores de los atributos del producto. Sus columnas
    son valor, atributo al que perenece y su sentiment
    :return: Dataframe cuya unidad de análisis es cada una de las alternativas del producto, sus columnas son los
    atributos del producto y las celdas, a diferencia del df_attr_values, son los sentiment que toma el valor del
    atributo
    """
    # Creo dataframe a retornar vacio con los nombres de las columnas correspondientes
    df_input_clust = pd.DataFrame(columns=['id_alternativa'] + list(df_attr_values['atributo'].unique()))  # el id_alt no sera utilizado pero igual lo necesito

    # POR ALTERNATIVA
    for i in range(len(df_alt)):
        # print("++++ Nº MODELO: {} ++++ ".format(i))

        # fila_alternativa = [df_alt.iloc[i, 0]]  # la reinicio para cada modelo, aunque la inicializo con el id_alt
        df_input_clust.loc[i, "id_alternativa"] = df_alt.iloc[i, 0]

        # POR ATRIBUTO
        for atributo in df_input_clust.columns[1:]:
            # print("ATRIBUTO: ", atributo)

            # Obtengo valor del atributo para el modelo
            idx_atrib = df_alt.columns.get_loc(atributo)
            valor = df_alt.iloc[i, idx_atrib]

            # SI EL VALOR DEL ATRIBUTO DE LA ALTERNATIVA NO ES NAN
            if str(valor) != 'nan':  # isnan() no lo pude implementar print(str(valor)!= 'nan', np.isnan(valor))

                # BUSCO SENTIMENT DEL VALOR
                prom_sent = float(df_attr_values[(df_attr_values['atributo'] == atributo) & (df_attr_values['valor'] == valor)]['sent'])
                # print("Valor {} toma sentiment {}".format(valor, prom_sent))

            # SI EL VALOR DEL ATRIBUTO DE LA ALTERNATIVA ES NAN
            else:
                # Busco min prom_sent
                prom_sent = df_attr_values[df_attr_values['atributo'] == atributo]['sent'].min()
                # print("Valor {} es NaN. Busco peor sentiment, en este caso, {}".format(valor, prom_sent))

            df_input_clust.loc[i, atributo] = prom_sent
            # GUARDO SENTIMENT
            # fila_alternativa.append(prom_sent)

        # Guardo fila de modelo
        # print("Fila de sentiment de la alternativa: ", fila_alternativa)
        # df.loc[len(df)] = fila_alternativa

    print(df_input_clust)
    # Reemplazo valores Nan por valores medios de cada columna
    df_input_clust.iloc[:, 1:] = replace_nan(df_input_clust.iloc[:, 1:])  # no incluyo id_alt? al pedo total no lo va a reemplazar...
    print(df_input_clust)

    return df_input_clust

def replace_nan(df):
    """
    Reeemplaza valores NaN de cada columna del dataframe por la media de la respectiva columna
    :param df: Dataframe cuya unidad de análisis es cada una de las alternativas del producto, sus columnas son los
    atributos del producto y las celdas son los sentiment que toma el valor del atributo pero contiene NaN values
    :return: Dataframe cuya unidad de análisis es cada una de las alternativas del producto, sus columnas son los
    atributos del producto y las celdas son los sentiment que toma el valor del atributo sin NaN values
    """
    # Hago copia del dataframe para evitar warning al reemplazar un valor por otro nuevo
    df_copia = df.copy()

    # Por columna
    for column in df.columns:

        # Obtengo promedio de valores de columna
        valor_promedio = df[column].mean()

        # Por valor
        for i in range(len(df[column])):

            # Si el valor es NaN (el valor no tiene sentiment)
            if str(df[column].iloc[i]) == 'nan':

                # Reemplazo valor NaN por valor promedio de la columna
                df_copia[column].iloc[i] = valor_promedio  # esta linea arroja warning si no usaria copia

    return df_copia

def k_means(df_clustering):
    """
    Aplica modelo de K-means a los datos pasados por parametro. Previamente, selecciono automaticamente el k ideal.
    :param df_clustering: Dataframe cuya unidad de análisis es cada una de las alternativas del producto, sus columnas
    son los atributos del producto y las celdas son los sentiment que toma el valor del atributo
    :return: Dataframe cuya unidad de análisis es cada una de las alternativas del producto, sus columnas
    son los atributos del producto y la columna "label" con el cluster al que pertenece y las celdas son los sentiment
    que toma el valor del atributo
    """
    print("Las {} columnas a clusterizar: {}".format(len(df_clustering.columns), list(df_clustering.columns)))
    # Defino datos
    X = np.array(df_clustering[df_clustering.columns])  #por ahi teenga que sacar algunas columnas..

    # escalo datos para determinar k  # estoy en duda si hay que hacerlo pero por los rdos diria que si
    sc_X = StandardScaler()
    scaled_data = sc_X.fit_transform(X)
    # print("Scaled data")
    # print(scaled_data)
    # print('---')
    # Eleccion automatica de k
    k = chooseBestKforKMeans(scaled_data, range(2,20))

    # Ejecutamos K-means
    kmeans = KMeans(n_clusters=k).fit(X)
    print(kmeans)

    # Agrego columna de cluster al que pertenece cada alternativa
    df_clustering["label"] = kmeans.labels_
    return df_clustering

def chooseBestKforKMeans(scaled_data, k_range):
    """
    Choose best k for some data
    :param scaled_data: Data que debe estar normalizada (?)
    :param k_range: Rango de valores que puede tomar k
    :return: best k
    """
    ans = []
    # Por k
    for k in k_range:

        # Creo modelo de K-means
        scaled_inertia = kMeansRes(scaled_data, k)

        # Guardo resultados del modelo
        ans.append((k, scaled_inertia))

    # Creo dataframe para mostrar los resultados
    df = pd.DataFrame(ans, columns=['k', 'Scaled Inertia']).set_index('k')
    print(df)

    # Elijo el mejor k (minimiza scaled inertia)
    best_k = df.idxmin()[0]

    return best_k

def kMeansRes(scaled_data, k, alpha_k=0.04):  #lo subi de 0.02 a 0.06 para tener menos clusters...
    '''
    Parameters
    ----------
    scaled_data: matrix
        scaled data. rows are samples and columns are features for clustering
    k: int
        current k for applying KMeans
    alpha_k: float
        manually tuned factor that gives penalty to the number of clusters
    Returns
    -------
    scaled_inertia: float
        scaled inertia value for current k
    '''

    # Calculo inertia para k=1 donde todos los datos pertenecen a un solo grupo
    inertia_o = np.square((scaled_data - scaled_data.mean(axis=0))).sum()

    # Entreno Modelo de K-means buscando k clusters
    kmeans = KMeans(n_clusters=k, random_state=0).fit(scaled_data)

    # Evaluo el modelo con metrica "scaled inertia" (formula de scaled inertia)
    scaled_inertia = kmeans.inertia_ / inertia_o + alpha_k * k

    return scaled_inertia

def create_table_cluster_centroids_sent(df_alt_clust):
    """
    Obtiene centroides de cada cluster. Cada cluster tiene un sentiment promedio para cada atributo del producto
    :param df_alt_clust: Dataframe cuya unidad de analisis son las alternativas. Las columnas son los atributos del
    producto, quienes toman un sentiment en particular, y una columna adicional "label" con el cluster al que corresponde
    cada alternativa
    :return: Dataframe cuya unidad de analisis son los clusters. Las columnas son los atributos del producto quienes
    toman el sentiment promedio de todas las alternativas que pertenecen al respectivo cluster.
    """
    # Defino variable
    labels = df_alt_clust['label'].unique()
    df_centroids_sent = pd.DataFrame(columns=df_alt_clust.columns[1:len(df_alt_clust.columns)-1], index=labels)  # no incluyo id_pub ni label

    # POR CLUSTER
    for cluster in labels:

        # Selecciono alternativas de un solo cluster
        df_alt_one_cluster = df_alt_clust[df_alt_clust['label'] == cluster]

        # POR ATRIBUTO
        for atributo in df_alt_clust.iloc[:, 1:len(df_alt_clust.columns)-1]:  # salvo el id_pub y el label

            # OBTENGO PROMEDIO DE SCORES
            score_prom = df_alt_one_cluster[atributo].mean()

            df_centroids_sent.loc[cluster, atributo] = score_prom

    print("Se exporto Dataframe con los centroides de cada cluster para poder darle nombre a clusters")
    df_centroids_sent.to_excel('/Users/nachomondino/Desktop/df_centroids_sent.xlsx')
    return df_centroids_sent

def cluster_names(df_clust):
    """
    Asigna un nombre a cada cluster
    :param df_clust:
    :return:
    """
    # Defino variable
    d = {}

    # Por cluster
    for cluster in df_clust['label'].unique():
        print("CLUSTER LABEL: ", cluster)

        # Solicito nombre del cluster por terminal
        nombre_cluster = input(str("Ingrese nombre del cluster: "))

        # Guardo relacion entre label y nombre
        d[cluster] = nombre_cluster

    print("Label de clusters y su nombre: ", d)
    return d

def replace_labels_with_names(df_alt_clust, d):
    """
    Reemplaza label del cluster de cada alternativa del producto por el nombre del cluster correspondiente
    :param df_alt_clust:
    :param d: Diccionario cuyas keys... y cuyos values..
    :return:
    """
    # Defino variable
    df_copia = pd.DataFrame(columns=df_alt_clust.columns)

    # Por cluster
    for label in df_alt_clust['label'].unique():

        # Selecciono alternativas de un cluster
        df_clust_filt_cluster = df_alt_clust[df_alt_clust['label'] == label]

        # Reemplazo label por nombre del label
        df_clust_filt_cluster = df_clust_filt_cluster.drop(['label'], axis=1)  # borro columna label
        df_clust_filt_cluster = df_clust_filt_cluster.assign(label=d[label])  # creo nueva columna label con nombre de label

        # Guardo
        df_copia = pd.concat([df_copia, df_clust_filt_cluster])

    return df_copia

def create_table_num_alt_per_cluster(df_alt_clust):
    """
    Obtiene el numero de alternativas por cada cluster
    :param df_alt_clust: Dataframe
    :return:
    """
    # Defino variables
    df_alt_per_clust = pd.DataFrame(columns=['Cantidad de alternativas'], index=df_alt_clust['label'].unique())
    df_alt_per_clust.index.name = 'Nombre de cluster'

    # OBTENGO Nº DE ALTERNATIVAS POR CLUSTER
    # Por cluster
    for cluster in df_alt_clust['label'].unique():

        # Selecciono alternativas de un cluster
        df_clust_filt_cluster = df_alt_clust[df_alt_clust['label'] == cluster]

        # Cuento cantidad de alternativas
        df_alt_per_clust.loc[cluster] = len(df_clust_filt_cluster)

    return df_alt_per_clust

def create_table_cluster_centroids_values(df_alt, df_alt_cleaned_clust):
    """
    Obtiene centroides de clusters. Cada cluster toma el valor mas frecuente para cada atributo del producto
    :param df_alt:
    :param df_alt_cleaned_clust: Dataframe cuya unidad de analisis son las alternativas. Las columnas son los atributos del
    producto, quienes toman un sentiment en particular, y una columna adicional "label" con el cluster al que corresponde
    cada alternativa
    :return:
    """
    # Defino variable
    # seguro necesite df_modelos_formateado pues las numericas las promedio.. y las string pongo el mas freecueente......!
    labels = df_alt_cleaned_clust['label'].unique()  # podria haber obtenido los nombres de la primera tabla (?)
    df_centroids_values = pd.DataFrame(columns=df_alt.columns[1:len(df_alt.columns)-1], index=labels)  # excluyo id_alt y label

    print("Labels (deberian ser 5):", labels)

    # POR CLUSTER
    for cluster in labels:
        print("CLUSTER LABEL: ", cluster)

        # SELECCIONO ALTERNATIVAS DE CLUSTER EN DATAFRAME ALTERNATIVAS
        ids_cluster = df_alt_cleaned_clust[df_alt_cleaned_clust['label'] == cluster]['id_alternativa']  # ids de un cluster
        print("IDS de cluster (deberian ser la cant que dice la tabla 4.2.5):", len(ids_cluster))
        df_alt_one_clust = df_alt[df_alt.id_alternativa.isin(ids_cluster)]  # alternativas de un cluster
        print("Dataframe de alternartivas de un cluster:")
        print(df_alt_one_clust)

        # POR ATRIBUTO
        for atributo in df_alt.columns[1:len(df_alt.columns)-1]:  #excluyo id y label
            print("Atributo: ", atributo)
            # print(df_alt_cluster[atributo])

            # Si es una variable numerica y continua
            if df_alt_one_clust[atributo].dtype in ['int64', 'float64'] and len(df_alt_one_clust[atributo].dropna().unique()) > len(df_alt_one_clust) ** 0.5:
                # Obtengo promedio de la columna
                valor = round(df_alt_one_clust[atributo].mean(), 0)

            # Si es numerica y discreta, o bien, no es numerica
            else:
                # Obtengo valor mas frecuente de la columna
                try:
                    print(df_alt_one_clust[atributo].value_counts())
                    valor = df_alt_one_clust[atributo].value_counts().index[0]

                except IndexError:  # si no hay valores para ese atributo en ese cluster
                    valor = None

            print("Valor mas frecuente del atributo:", valor)
            df_centroids_values.loc[cluster, atributo] = valor

    return df_centroids_values

def create_table_brand_per_cluster(df_alt, df_alt_cleaned_cluster):
    """
    :param df_alt:
    :param df_alt_cleaned_cluster:
    :return:
    """
    # Si el atributo se llama "Marca"
    if 'Marca' in list(df_alt.columns):
        atrib_marca = 'Marca'
    else:
        for atributo in list(df_alt.columns):
            if 'marca' in atributo.lower():
                atrib_marca = atributo
                break

    # Defino variable
    l_marcas = list(df_alt[atrib_marca].dropna().unique())
    df_brand_per_cluster = pd.DataFrame(index=df_alt_cleaned_cluster['label'].unique(), columns=l_marcas)
    print(l_marcas)

    # POR CLUSTER
    for cluster in df_alt_cleaned_cluster['label'].unique():
        # print("CLUSTER LABEL: ", cluster)

        # SELECCIONO ALTERNATIVAS DE CLUSTER EN DATAFRAME ALTERNATIVAS
        ids_cluster = df_alt_cleaned_cluster[df_alt_cleaned_cluster['label'] == cluster]['id_alternativa']  # ids de alternativa en un cluster
        df_alt_cleaned_one_cluster = df_alt[df_alt.id_alternativa.isin(ids_cluster)]  # alternativas de un cluster

        # GUARDO MARCAS Y SUS FRECUENCIAS
        for marca in l_marcas:
            frec = len(df_alt_cleaned_one_cluster[df_alt_cleaned_one_cluster[atrib_marca] == marca])
            df_brand_per_cluster.loc[cluster, marca] = frec

    return df_brand_per_cluster

def drop_alternatives_unwanted(df_alt, df_alt_cleaned_clust):
    """
    Selecciono alternativas que no han sido eliminadas durante data preparation y agrego columna label
    :param df_alt:
    :param df_alt_cleaned_clust:
    :return:
    """
    # Selecciono ids de alternativas que no han sido borradas
    ids_alt_cleaned = df_alt_cleaned_clust["id_alternativa"]

    # Filtro dataframe alternativas por ids
    df_alt = df_alt[df_alt.id_alternativa.isin(ids_alt_cleaned)]

    # Agrego columna de label
    df_alt_with_label = df_alt.copy()
    df_alt_with_label['label'] = list(df_alt_cleaned_clust['label'])

    return df_alt_with_label

def main(df_alt, df_alt_cleaned, df_attr_values_sent):

    # (1) CREO EL DATAFRAME PARA CLUSTERING
    print(" 4.2.1 Creando el dataframe para clustering...")
    df_input_clustering = create_clustering_dataframe(df_alt_cleaned, df_attr_values_sent)
    print(df_input_clustering)

    # (2) APLICO CLUSTERING
    print(" 4.2.2 Aplicando clustering...")
    df_alt_cleaned_cluster = pd.concat([df_input_clustering['id_alternativa'], k_means(df_input_clustering.iloc[:, 1:])], axis=1)

    # (3) DEFINO NOMBRES DE CLUSTERS
    print(" 4.2.3 Definiendo nombre de clusters...")
    # Creo tabla de centroides de clusters de alternativas segun sentiment
    df_centroids_sent = create_table_cluster_centroids_sent(df_alt_cleaned_cluster)  # tabla 0 pues el cliente no la ve, es solo para mi y asi poder definir nombres de clusters
    df_centroids_sent.to_excel('/Users/nachomondino/Desktop/df_centroids_sent.xlsx')
    print("Se exporto Dataframe con los centroides de cada cluster para poder darle nombre a clusters")
    # Obtengo nombre de clusters
    d_labels_names = cluster_names(df_alt_cleaned_cluster)
    # Reemplazo labels por nombre de labels
    df_alt_cleaned_cluster = replace_labels_with_names(df_alt_cleaned_cluster, d_labels_names)

    # (4) OBTENGO DATAFRAME ALTERNATIVAS CON CLUSTER
    print(" 4.2.4 Obteniendo dataframe alternativas para mostrar al cliente con los nombres de clusters correspondientes...")
    # Elimino alternativas desechadas durante procesamiento y agrego columna label a dataframe alternativas
    print(df_alt)
    df_alt = drop_alternatives_unwanted(df_alt, df_alt_cleaned_cluster)
    print(df_alt)

    # (5) CREO TABLA DE NUMERO DE ALTERNATIVAS POR CLUSTER
    print(" 4.2.5 Obteniendo tabla de numero de alternativas por cluster...")
    df_alt_per_clust = create_table_num_alt_per_cluster(df_alt_cleaned_cluster)
    print(df_alt_per_clust)

    # (6) CREO TABLA DE CENTROIDES DE CLUSTERS SEGUN VALORES DE ATRIBUTOS
    print(" 4.2.6 Obteniendo tabla de centroides segun valores de atributos...")
    df_centroids_values = create_table_cluster_centroids_values(df_alt, df_alt_cleaned_cluster)
    print(df_centroids_values)

    # (7) CREO TABLA DE NUMERO DE MARCAS POR CLUSTER
    print(" 4.2.7 Obteniendo tabla de numero de marcas por cluster...")
    df_brand_per_cluster = create_table_brand_per_cluster(df_alt, df_alt_cleaned_cluster)
    print(df_brand_per_cluster)

    return df_alt, df_alt_per_clust, df_centroids_values, df_brand_per_cluster

''' # Para correr prueba independiente de main.py. IMPORTO ARCHIVOS
df_alt = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_alt_formated.xlsx'.format("celulares")  #index_col=0
df_alt_cleaned = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_alt_cleaned.xlsx'.format("celulares"))  #index_col=0
df_attr_values_sent = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/atribucion/{}/df_attr_values_sent.xlsx'.format("celulares"), index_col=0)
print(df_alt), print(df_alt_cleaned), print(df_attr_values)
main(df_alt, df_alt_cleaned, df_attr_values_sent)
'''
