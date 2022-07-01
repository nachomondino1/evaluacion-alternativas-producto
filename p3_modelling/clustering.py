# Importo librerias
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import statistics as st
# import matplotlib.pyplot as plt


def create_clustering_dataframe(df_alt, df_sent_alt, df_sent_attr_values):
    """
    Agrega informacion de distintos dataframes para crear el dataframe con todos valores numericos y sin NaN y asi poder
    hacer clustering
    :param df_alt: Dataframe. Unidad de analisis: alternativa del producto. Columnas: id_alternativa y atributos del
    producto. Celdas: valor que toma el atributo en una alternativa
    :param: df_sent_alt: Dataframe. Unidad de analisis: alternativa del producto. Columnas: id_alternativa, atributo,
    numero de opiniones en que basa su sentiment y su sentiment
    :param df_sent_attr_values: Dataframe. Unidad de analisis: valor de un atributo del producto. Columnas: valor, atributo
    al que perenece, numero de opiniones en que basa su sentiment y su sentiment
    :return: Dataframe. Unidad de análisis: alternativa del producto. Columnas: id_alternativa y atributos del producto.
    Celdas: sentiment que toma el atributo
    """
    # Creo dataframe a retornar vacio con los nombres de las columnas correspondientes
    l_atributos = list(df_sent_attr_values['atributo'].unique()) + list(df_sent_alt['atributo'].unique())
    df_input_clust = pd.DataFrame(columns=['id_alternativa'] + l_atributos)  # el id_alt no sera utilizado pero igual lo necesito

    # POR ALTERNATIVA
    for i in range(len(df_alt)):

        # Guardo id_alternativa
        id_alt = df_alt.loc[i, 'id_alternativa']  # id_alt =  df_alt.iloc[i, 0]
        df_input_clust.loc[i, "id_alternativa"] = id_alt
        # print("\t Nº ALTERNATIVA: {}".format(i))

        # POR ATRIBUTO
        for atributo in l_atributos:
            # print("ATRIBUTO: ", atributo)

            # SI EL ATRIBUTO TIENE SENTIMENT POR CADA UNO DE SUS VALORES (ATRIBUCION POR VALORES)
            if atributo in list(df_sent_attr_values['atributo'].unique()):

                # Defino variable
                valor = df_alt.loc[i, atributo]  # Valor del atributo en alternativa

                # SI EL VALOR DEL ATRIBUTO DE LA ALTERNATIVA NO ES NAN
                try:
                # if str(valor) != 'nan':  # isnan() no lo pude implementar print(str(valor)!= 'nan', np.isnan(valor))
                    # BUSCO SENTIMENT DEL VALOR
                    # sent = float(df_sent_attr_values[(df_sent_attr_values['atributo'] == atributo) & (df_sent_attr_values['valor'] == valor)]['sent'])  # podria probar sent = df_sent_attr_values[(df_sent_attr_values['atributo'] == atributo) & (df_sent_attr_values['valor'] == valor)]['sent'].values
                    sent = float(df_sent_attr_values[(df_sent_attr_values['atributo'] == atributo) & (df_sent_attr_values['valor'] == valor)]['sent'].values)
                    print("Valor '{}' toma sentiment {}".format(valor, sent))

                # SI EL VALOR DEL ATRIBUTO DE LA ALTERNATIVA ES NAN
                except TypeError:
                # else:
                    # BUSCO SENTIMENT MINIMO DEL ATRIBUTO
                    sent = df_sent_attr_values[df_sent_attr_values['atributo'] == atributo]['sent'].min()
                    print("Valor {} es NaN. Busco peor sentiment, en este caso, {}".format(valor, sent))

            # SI EL ATRIBUTO ("FICTICIO") TIENE SENTIMENT POR CADA ALTERNATIVA (ATRIBUCION POR ALTERNATIVA)
            else:
                # SI TIENE SENTIMENT
                try:
                    # Obtengo sentiment de alternativa para el atributo
                    sent = float(df_sent_alt[(df_sent_alt['id_alternativa']==id_alt) & (df_sent_alt['atributo']==atributo)]['sent'])
                # SI NO TIENE SENTIMENT (NAN)
                except TypeError:
                    sent = None  # total luego lo reemplazo al nan
                # print("Sentiment: ",sent)

            # GUARDO SENTIMENT
            df_input_clust.loc[i, atributo] = sent

    # REEMPLAZO VALORES NAN POR VALORES MEDIOS DE CADA COLUMNA
    df_input_clust.iloc[:, 1:] = replace_nan(df_input_clust.iloc[:, 1:])  # no incluyo id_alt? al pedo total no lo va a reemplazar...
    return df_input_clust

def replace_nan(df):
    """
    Reeemplaza valores NaN de cada columna del dataframe por la media de la respectiva columna
    :param df: Dataframe. Cualquiera.
    :return: Dataframe pasado por parametro habiendo reemplazo NaN values de sus columnas por la media de cada una
    """
    # Hago copia del dataframe para evitar warning al reemplazar un valor por otro nuevo
    df_copia = df.copy()

    # Por columna
    for column in df.columns:

        # Obtengo promedio de sus valores
        valor_promedio = df[column].mean()  # es lo mismo que st.mean(df[column].dropna())

        # Selecciono valores NaN del atributo
        df_nan = df[df[column].isna()]

        # Reemplazo valores NaN por valor promedio del atributo
        df_copia.loc[df_nan.index, column] = valor_promedio
    return df_copia

def k_means(df_clustering):
    """
    Aplica modelo de K-means a los datos pasados por parametro. Previamente, selecciono automaticamente el k ideal.
    :param df_clustering: Dataframe. Unidad de análisis: alternativa del producto. Columnas: id_alternativa y atributos
    del producto. Celdas: sentiment que toma el atributo (sin NaN)
    :return: Dataframe. Unidad de análisis: alternativa del producto. Columnas: id_alternativa, una por atributo del
    producto y la columna "label" con el cluster al que pertenece. Celdas: sentiment que toma el atributo
    """
    # Defino variables
    X = np.array(df_clustering[df_clustering.columns])  #por ahi teenga que sacar algunas columnas..
    sc_X = StandardScaler() # inicializo objeto de clase StandardScaler()
    print("Las {} columnas a clusterizar: {}".format(len(df_clustering.columns), list(df_clustering.columns)))

    # Escalo datos para determinar k  # estoy en duda si hay que hacerlo pero por los rdos diria que si
    scaled_data = sc_X.fit_transform(X)

    # Eleccion automatica de k
    k = chooseBestKforKMeans(scaled_data, range(2,20))

    # Ejecutamos K-means
    kmeans = KMeans(n_clusters=k).fit(X)

    # Agrego columna de cluster al que pertenece cada alternativa
    df_clustering["label"] = kmeans.labels_
    return df_clustering

def chooseBestKforKMeans(scaled_data, k_range):
    """
    Choose best k for some data
    :param scaled_data: Data que debe estar normalizada
    :param k_range: Slice. Rango de valores que puede tomar k
    :return: Integer. Best k
    """
    # Defino variable
    ans = []

    # Por posible valor de k
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

def kMeansRes(scaled_data, k, alpha_k=0.06):  #lo subi de 0.02 a 0.06 para tener menos clusters...
    """
    Entrena modelo de K-means con k pasada como parametro y calcula metrica "scaled inertia"
    :param scaled_data: rows are samples and columns are features for clustering
    :param k: Integer. Current k for applying KMeans
    :param alpha_k: Float. Manually tuned factor that gives penalty to the number of clusters
    :return: Float. Scaled inertia value for current k
    """
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
    :param df_alt_clust: Dataframe. Unidad de analisis: alternativa del producto. Columnas: id_alternativa, una por
    atributo del producto y label (cluster de alternativa). Celdas: sentiment de atributo en alternativa
    :return: Dataframe. Unidad de analisis: cluster de alternativas. Columnas: una por atributo del producto y label
    (en index). Celdas: sentiment promedio de todas las alternativas que pertenecen al respectivo cluster en un atributo
    """
    # Defino variable
    l_labels = df_alt_clust['label'].unique()
    df_centroids_sent = pd.DataFrame(columns=df_alt_clust.columns[1:len(df_alt_clust.columns)-1], index=l_labels)  # no incluyo id_pub ni label

    # POR CLUSTER
    for label in l_labels:

        # Selecciono alternativas de un solo cluster
        df_alt_one_cluster = df_alt_clust[df_alt_clust['label'] == label]

        # POR ATRIBUTO
        for atributo in df_alt_clust.iloc[:, 1:len(df_alt_clust.columns)-1]:  # salvo el id_pub y el label

            # OBTENGO PROMEDIO DE SENTIMENTS Y LO GUARDO
            prom_sent = df_alt_one_cluster[atributo].mean()
            df_centroids_sent.loc[label, atributo] = prom_sent

    print("Se exporto Dataframe con los centroides de cada cluster para poder darle nombre a clusters")
    df_centroids_sent.to_excel('/Users/nachomondino/Desktop/df_centroids_sent.xlsx')
    return df_centroids_sent

def replace_labels_with_names(df_alt_clust):
    """
    Reemplaza label del cluster de cada alternativa del producto por el nombre del cluster correspondiente
    :param df_alt_clust: Dataframe. Unidad de análisis: alternativa del producto. Columnas: id_alternativa, una por
    atributo del producto y la columna "label" con el label del cluster al que pertenece. Celdas: sentiment que toma el
    atributo
    :return: Dataframe. Unidad de análisis: alternativa del producto. Columnas: id_alternativa, una por atributo
    del producto y la columna "label" con el nombre del cluster al que pertenece. Celdas: sentiment que toma el atributo
    """
    # Defino variable
    df_alt_clust_copy = df_alt_clust.copy()

    # POR CLUSTER
    for cluster in df_alt_clust['label'].unique():
        print("CLUSTER LABEL: {}".format(cluster))

        # Selecciono alternativas del cluster
        df_alt_one_clust = df_alt_clust[df_alt_clust['label'] == cluster]

        # SOLICITO NOMBRE DEL CLUSTER POR TERMINAL
        nombre_cluster = input(str("Ingrese nombre del cluster: "))

        # REEMPLAZO LABEL POR EL NOMBRE DEL CLUSTER
        df_alt_clust_copy.loc[df_alt_one_clust.index, 'label'] = nombre_cluster
    return df_alt_clust_copy

def add_clust_label(df_alt_to_client, df_alt_clust):
    """
    Agrega columna label a Dataframe alternativas que sera mostrado al cliente
    :param df_alt_to_client: Dataframe. Unidad de analisis: alternativa del producto (solo las que seran mostradas al
    cliente). Columnas: id_alternativa y una por atributo del producto.
    :param df_alt_clust: Dataframe. Unidad de análisis: alternativa del producto. Columnas: id_alternativa, una por
    atributo del producto y la columna "label" con el nombre del cluster al que pertenece. Celdas: sentiment que toma el
    atributo
    :return: Dataframe. Unidad de analisis: alternativa del producto (solo las que seran mostradas al cliente).
    Columnas: id_alternativa, una por atributo del producto y label con el nombre del cluster al que pertenece
    """
    # Creo columna label
    df_alt_to_client['label'] = None

    # Por alternativa
    for i in range(len(df_alt_to_client)):

        # Obtengo su id
        id_alt = df_alt_to_client.loc[i, 'id_alternativa']

        # Busco su label
        label = df_alt_clust[df_alt_clust['id_alternativa']==id_alt]['label'].values[0]

        # Agrego label a alternativa
        df_alt_to_client.loc[i, 'label'] = label

    return df_alt_to_client

def create_table_num_alt_per_cluster(df_alt_clust):
    """
    Obtiene el numero de alternativas por cada cluster
    :param df_alt_clust: Dataframe. Unidad de análisis: alternativa del producto. Columnas: id_alternativa, una por
    atributo del producto y la columna "label" con el nombre del cluster al que pertenece. Celdas: sentiment que toma
    el atributo
    :return: Dataframe. Unidad de analisis: cluster de alternativas (index). Columnas: Numero de alternativas. Celdas:
    Numero de alternativas por cluster
    """
    # Defino variables
    df_alt_per_clust = pd.DataFrame(columns=['Cantidad de alternativas'], index=df_alt_clust['label'].unique())  # Dataframe a retornar
    df_alt_per_clust.index.name = 'Nombre de cluster'  # Nombre de indice en dataframe a retornar

    # POR CLUSTER
    for cluster in df_alt_clust['label'].unique():

        # SELECCIONO ALTERNATIVAS DE CLUSTER
        df_clust_filt_cluster = df_alt_clust[df_alt_clust['label'] == cluster]

        # CUENTO CANTIDAD DE ALTERNATIVAS Y LO GUARDO
        df_alt_per_clust.loc[cluster] = len(df_clust_filt_cluster)

    return df_alt_per_clust

def create_table_cluster_centroids_values(df_alt, df_alt_cleaned_clust):
    """
    Obtiene centroides de clusters. Cada cluster toma el valor mas frecuente para cada atributo del producto
    :param df_alt: Dataframe. Unidad de analisis: alternativa del producto (solo las que seran mostradas al cliente).
    Columnas: id_alternativa, una por atributo del producto y label con el nombre del cluster al que pertenece
    :param df_alt_cleaned_clust: Dataframe. Unidad de análisis: alternativa del producto. Columnas: id_alternativa, una por
    atributo del producto y la columna "label" con el nombre del cluster al que pertenece. Celdas: sentiment que toma
    el atributo
    :return: Dataframe. Unidad de analisis: cluster de alternativas (en index). Columnas: una por atributo del producto.
    Celdas: valor mas frecuente del atributo en cluster
    """
    # Defino variables
    l_labels = df_alt_cleaned_clust['label'].unique()  # podria haber obtenido los nombres de la primera tabla (?)
    df_centroids_values = pd.DataFrame(columns=df_alt.columns[1:len(df_alt.columns)-1], index=l_labels)  # Dataframe a retornar (excluyo id_alt y label)
    print("Labels (deberian ser 5):", l_labels)

    # POR CLUSTER
    for cluster in l_labels:
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
                    valor = df_alt_one_clust[atributo].value_counts().index[0]

                except IndexError:  # si no hay valores para ese atributo en ese cluster
                    valor = None

            df_centroids_values.loc[cluster, atributo] = valor
            print("Valor mas frecuente del atributo:", valor)
    return df_centroids_values

def create_table_brand_per_cluster(df_alt, df_alt_cleaned_cluster):
    """
    Obtiene distribucion de las marcas en los diferentes clusters
    :param df_alt: Dataframe. Unidad de analisis: alternativa del producto (solo las que seran mostradas al cliente).
    Columnas: id_alternativa, una por atributo del producto y label con el nombre del cluster al que pertenece
    :param df_alt_cleaned_cluster: Dataframe. Unidad de análisis: alternativa del producto. Columnas: id_alternativa,
    una por atributo del producto y la columna "label" con el nombre del cluster al que pertenece. Celdas: sentiment que
    toma el atributo
    :return: Dataframe. Unidad de analisis: cluster de alternativas (index). Columnas: una por Marca del producto.
    Celdas: Numero de modelos de marca en cluster.
    """
    # Defino variable
    df_brand_per_cluster = pd.DataFrame(index=df_alt_cleaned_cluster['label'].unique())  # Dataframe a retornar

    # SI EL PRODUCTO TIENE EL ATRIBUTO 'MARCA'
    try:
        # Defino variable
        l_marcas = df_alt['Marca'].unique()  # Lista de todas las marcas del produto

        # POR MARCA
        for marca in l_marcas:

            # SI LA MARCA TIENE MAS DE X MODELOS
            if len(df_alt[df_alt['Marca'] == marca]) > 3: # En smartband lo uso en 3

                # POR CLUSTER
                for cluster in df_alt_cleaned_cluster['label'].unique():
                    # print("CLUSTER LABEL: ", cluster)

                    # SELECCIONO ALTERNATIVAS DEL CLUSTER CON LA MARCA Y LAS CUENTO
                    ids_cluster = df_alt_cleaned_cluster[df_alt_cleaned_cluster['label'] == cluster]['id_alternativa']  # ids de alternativa en un cluster
                    df_alt_cleaned_one_cluster = df_alt[df_alt.id_alternativa.isin(ids_cluster)]  # alternativas de un cluster
                    frec = len(df_alt_cleaned_one_cluster[df_alt_cleaned_one_cluster['Marca'] == marca])

                    # GUARDO MARCA Y SU FRECUENCIA
                    df_brand_per_cluster.loc[cluster, marca] = frec

    # SI EL PRODUCTO NO TIENE EL ATRIBUTO 'MARCA'
    except:
        print("El producto no tiene atributo 'Marca'")
    return df_brand_per_cluster


def create_table_best_clusters_per_customer_need(df_centroids_sent, df_relation_matrix, df_alt_clust):  # Temporalmente recibe nombre de clusters de df_alt_clust
    """
    :param df_centroids_sent:
    :param df_relation_matrix:
    :return:
    """
    # Defino varibles
    df_centroids_sent.index = df_alt_clust['label'].unique()
    df_brand_per_cust = pd.DataFrame(index=df_centroids_sent.index, columns=df_relation_matrix.index)

    # POR CUSTOMER NEED
    for customer_need in df_relation_matrix.index:
        print('Customer need: ', customer_need)

        # Defino variables
        sum_relaciones = sum(df_relation_matrix.loc[customer_need].values)  # BUSCO ATRIBUTOS CON QUE TIENE RELACION

        # POR GRUPO
        for grupo in df_centroids_sent.index:
            print('\t Grupo: ', grupo)

            # Defino variable
            sent_grupo_cust_need = 0  # Sentiment de grupo en customer need

            # POR ATRIBUTO
            for atributo in df_relation_matrix.columns:

                # Defino variable
                relacion = df_relation_matrix.loc[customer_need, atributo]  # Peso de relacion entre atributo y customer need

                # SI TIENE RELACION CON CUSTOMER NEED:
                if relacion > 0:
                    print('\t\t Atributo: ', atributo)

                    # Obtengo sentiment del atributo en el grupo
                    sent_grupo_atrib = df_centroids_sent.loc[grupo, atributo]
                    print("\t\t\t Sentiment {}".format(sent_grupo_atrib))

                    sent_grupo_cust_need += relacion * sent_grupo_atrib / sum_relaciones

            # GUARDO SENTIMENT DEL GRUPO EN LA CUSTOMER NEED
            df_brand_per_cust.loc[grupo, customer_need] = sent_grupo_cust_need
            print(df_brand_per_cust)

        # Traducir sentiments en una posicion
        df_brand_per_cust_copia = df_brand_per_cust.copy()
        l_grupos_left = list(df_brand_per_cust.index)
        # Por cantidad de grupos
        for i in range(len(df_centroids_sent.index)):

            # Defino variable
            sent_max = -10  # Mejor sentiment de los grupos en customer need

            # Por grupo
            for grupo in df_brand_per_cust_copia.index:

                # Defino variables
                sent = df_brand_per_cust.loc[grupo, customer_need]  # Sentiment de grupo en customer need

                # Si su sentiment es el mejor
                if sent > sent_max:

                    # Guardo grupo del mejor sentiment
                    grupo_max = grupo
                    sent_max = sent

            # Elimino grupo con mejor sentiment
            print(df_brand_per_cust_copia)
            print(grupo_max)
            l_grupos_left.remove(grupo_max)
            print(l_grupos_left)
            df_brand_per_cust_copia = df_brand_per_cust.loc[l_grupos_left]  # df_brand_per_cust_copia.drop([grupo_max], axis=0)

            # Reemplazo sentiment por posicion
            df_brand_per_cust.loc[grupo_max, customer_need] = i + 1
        print(df_brand_per_cust)
    return df_brand_per_cust

''' Hice al reves el df_brand_per_cust en columnas y filas
def create_table_best_clusters_per_customer_need(df_centroids_sent, df_relation_matrix):
    """
    :param df_centroids_sent:
    :param df_relation_matrix:
    :return:
    """
    # Defino varibles
    df_brand_per_cust = pd.DataFrame(index=df_relation_matrix.index)

    # POR CUSTOMER NEED
    for customer_need in df_relation_matrix.index:
        print('Customer need: ', customer_need)

        # Defino variables
        sum_relaciones = sum(df_relation_matrix.loc[customer_need].values)  #   # BUSCO ATRIBUTOS CON QUE TIENE RELACION

        # POR GRUPO
        for grupo in df_centroids_sent.index:
            print('\t Grupo: ', grupo)

            # Defino variable
            sent_grupo_cust_need = 0  # Sentiment de grupo en customer need

            # POR ATRIBUTO
            for atributo in df_relation_matrix.columns:

                # Defino variable
                relacion = df_relation_matrix.loc[customer_need, atributo]  # Peso de relacion entre atributo y customer need

                # SI TIENE RELACION CON CUSTOMER NEED:
                if relacion > 0:
                    print('\t\t Atributo: ', atributo)

                    # Obtengo sentiment del atributo en el grupo
                    sent_grupo_atrib = df_centroids_sent.loc[grupo, atributo]
                    print("\t\t\t Sentiment {}".format(sent_grupo_atrib))

                    sent_grupo_cust_need += relacion * sent_grupo_atrib / sum_relaciones

            # GUARDO SENTIMENT DEL GRUPO EN LA CUSTOMER NEED
            df_brand_per_cust.loc[customer_need, grupo] = sent_grupo_cust_need
            print(df_brand_per_cust)

        # Traducir sentiments en una posicion
        df_brand_per_cust_copia = df_brand_per_cust.copy()
        # Por cantidad de grupos
        for i in range(len(df_centroids_sent.index)):

            # Defino variable
            sent_max = int()  # Mejor sentiment de los grupos en customer need

            # Por grupo
            for grupo in df_brand_per_cust_copia.columns:

                # Defino variables
                sent = df_brand_per_cust_copia.loc[customer_need, grupo]  # Sentiment de grupo en customer need

                # Si su sentiment es el mejor
                if sent > sent_max:

                    # Guardo grupo del mejor sentiment
                    grupo_max = grupo
                    sent_max = sent

            # Elimino grupo con mejor sentiment
            df_brand_per_cust_copia = df_brand_per_cust_copia.drop([grupo_max], axis=0)

            # Reemplazo sentiment por posicion
            df_brand_per_cust.loc[customer_need, grupo_max] = i + 1
        print(df_brand_per_cust)

    return df_brand_per_cust
'''


'''  # en desuso pues es por marca y no por cluster. No tiene porque estar en clustering pues no usa nada de la informacion de los clusters.
La reemplazo por create_table_best_clusters_per_customer_need()
def create_table_best_brands_per_customer_need(df_alt, df_input_clustering, df_relation_matrix):
    # Defino varibles
    l_marcas = df_alt['Marca'].unique()
    df_brand_per_cust = pd.DataFrame(index=df_relation_matrix.index, columns=['Marca Nº1','Marca Nº2', 'Marca Nº3'])

    # POR CUSTOMER NEED
    for customer_need in df_relation_matrix.index:
        print('Customer need: ', customer_need)

        # BUSCO ATRIBUTOS CON QUE TIENE RELACION
        sum_relaciones = sum(df_relation_matrix.loc[customer_need].values)
        df = pd.DataFrame(index=l_marcas, columns=['sent'])

        # POR ATRIBUTO
        for atributo in df_relation_matrix.columns:

            # Defino variable
            relacion = df_relation_matrix.loc[customer_need, atributo]  # Peso de relacion entre atributo y customer need

            # SI TIENE RELACION CON CUSTOMER NEED:
            if relacion > 0:
                print('\t Atributo: ', atributo)

                # POR MARCA
                for marca in l_marcas:

                    # Obtengo alternativas de la marca
                    l_idxs = df_alt[df_alt['Marca'] == marca].index  # Lista de indices de alternativas de la marca
                    l_ids = df_alt.loc[l_idxs, 'id_alternativa']  # Lista de id de alternativas de la marca
                    df_clust_marca = df_input_clustering[df_input_clustering.id_alternativa.isin(l_ids)]

                    # Obtengo sentiment promedio de la marca en customer need
                    sent_prom_marca = df_clust_marca[atributo].mean()
                    print("\t\t Marca: {} \t Sentiment {}".format(marca, sent_prom_marca))

                    # Si la marca tiene mas de 3 alternativas (sino por tener una sola alternativa de bueen valor, terminas siendo el mejor)
                    if len(l_idxs) > 3:
                        # Guardo sentiment
                        df.loc[marca, atributo] = relacion * sent_prom_marca / sum_relaciones

        # SELECCIONO MARCA CON MEJOR SENTIMENT PARA LA CUSTOMER NEED
        # Obtengo sentiment promedio (gralmente las cust needs tienen mas de una relacion)
        for marca in l_marcas:
            sent = sum(df.loc[marca].dropna())  # si no hago dropna() la sum es nan
            df.loc[marca, 'sent'] = sent

        # Selecciono las 3 marcas con mejor sentiment para la customer need
        df = df.sort_values(by='sent', ascending=False)
        l_marcas_selected = df.iloc[:3].index

        # Guardo las marcas y la customer need
        df_brand_per_cust.loc[customer_need, ['Marca Nº1','Marca Nº2', 'Marca Nº3']] = l_marcas_selected
        print(df_brand_per_cust)
    return df_brand_per_cust
'''

''' # Para correr prueba independiente de main.py. IMPORTO ARCHIVOS
df_alt = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_alt_formated.xlsx'.format("celulares")  #index_col=0
df_alt_cleaned = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_alt_cleaned.xlsx'.format("celulares"))  #index_col=0
df_attr_values_sent = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/atribucion/{}/df_attr_values_sent.xlsx'.format("celulares"), index_col=0)
print(df_alt), print(df_alt_cleaned), print(df_attr_values)
main(df_alt, df_alt_cleaned, df_attr_values_sent)
'''
