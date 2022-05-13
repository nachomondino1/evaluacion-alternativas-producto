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
    :param df_attr_values: Dataframe cuya unidad de analisis son los valores de los atributos del producto. Sus columnas
    son valor, atributo al que perenece y su sentiment
    :param df_alt: Dataframe cuya unidad de analisis es cada una de las alternativas del producto, sus columnas
    son los atributos del producto y las celdas el valor que toma el atributo en una alternativa
    :return: Dataframe cuya unidad de análisis es cada una de las alternativas del producto, sus columnas son los
    atributos del producto y las celdas, a diferencia del df_attr_values, son los sentiment que toma el valor del
    atributo
    """
    # Creo dataframe a retornar vacio con los nombres de las columnas correspondientes
    df = pd.DataFrame(columns=['id_alternativa'] + list(df_attr_values['atributo'].unique()))

    # POR ALTERNATIVA
    for i in range(len(df_alt)):
        print("++++ Nº MODELO: {} ++++ ".format(i))

        fila_alternativa = [df_alt.iloc[i, 0]]  # la reinicio para cada modelo, agrego el id_pub

        # POR ATRIBUTO
        for atributo in df.columns[1:]:  # tengo que evitar id_pub, linea y modelo
            print("ATRIBUTO: ", atributo)

            # Obtengo valor del atributo para el modelo
            idx_atrib = df_alt.columns.get_loc(atributo)
            valor = df_alt.iloc[i, idx_atrib]

            # SI EL VALOR DEL ATRIBUTO DE LA ALTERNATIVA NO ES NAN
            if str(valor) != 'nan':  # isnan?

                # BUSCO SENTIMENT DEL VALOR
                prom_sent = float(df_attr_values[(df_attr_values['atributo'] == atributo) & (df_attr_values['valor'] == valor)]['sent'])
                print("Valor {} toma sentiment {}".format(valor, prom_sent))

            # SI EL VALOR DEL ATRIBUTO DE LA ALTERNATIVA ES NAN
            else:
                # Busco min prom_sent
                prom_sent = df_attr_values[df_attr_values['atributo'] == atributo]['sent'].min()
                print("Valor {} es NaN. Busco peor sentiment, en este caso, {}".format(valor, prom_sent))

            # GUARDO SENTIMENT
            fila_alternativa.append(prom_sent)

        # Guardo fila de modelo
        print("Fila de sentiment de la alternativa: ", fila_alternativa)
        # print("Cantidad de seentiments", len(l_prom_sent))
        # print("Cantidad de columnas", len(df.columns))
        df.loc[len(df)] = fila_alternativa

    # df.to_excel('/Users/nachomondino/Desktop/df_clustering.xlsx', 'Hoja de datos')
    # Reemplazo valores Nan por valores medios de cada columna
    df.iloc[:,1:] = replace_nan(df.iloc[:,1:])
    # df.to_excel('/Users/nachomondino/Desktop/df_clustering_sin_nan.xlsx', 'Hoja de datos')
    # df = df.dropna()  # elimina alternativas con NaN

    return df

def replace_nan(df):
    """
    Por columna del dataframe, reemplaza valores NaN (valores que no tienen sentiment asociado) por la media de dicha
    columna
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
        print("Atributo:", column, "valor promedio:", valor_promedio)

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
    print("columnas a clusterizar:", df_clustering.columns, len(df_clustering.columns))
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
    results = pd.DataFrame(ans, columns=['k', 'Scaled Inertia']).set_index('k')
    print(results)

    # Elijo el mejor k (minimiza scaled inertia)
    best_k = results.idxmin()[0]

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

def create_table_0(df_clust):

    table0 = pd.DataFrame(columns=df_clust.columns)

    # POR CLUSTER
    for cluster in df_clust['label'].unique():

        # Defino variable
        fila = []  # donde guardare scores para un cluster

        # Selecciono alternativas de un solo cluster
        df_grupo = df_clust[df_clust['label'] == cluster]

        # POR ATRIBUTO
        for atributo in df_clust:  # salvo el id_pub

            # OBTENGO PROMEDIO DE SCORES promedio de scores
            score_prom = df_grupo[atributo].mean()

            # GUARDO SCORE
            fila.append(score_prom)

        # GUARDO FILA DEL CLUSTER
        table0.loc[len(table0)] = fila

    # ORDENO LA TABLA POR Nº DE CLUSTER
    table1 = table0.sort_values(by=['label'])
    return table1

def create_table_2(df_alt, df_clust):

    # seguro necesite df_modelos_formateado pues las numericas las promedio.. y las string pongo el mas freecueente......!
    table2 = pd.DataFrame(columns=df_alt.columns[1:], index=df_clust['label'].unique())

    # POR CLUSTER
    for cluster in df_clust['label'].unique():
        print("CLUSTER LABEL: ", cluster)

        # Defino variable
        fila = []  # donde guardare scores para un cluster

        # SELECCIONO ALTERNATIVAS DE CLUSTER EN DATAFRAME ALTERNATIVAS
        # Selecciono ids de alternativas de un cluster
        ids_cluster = df_clust[df_clust['label'] == cluster]['id_alternativa']
        # Selecciono alternativas en dataframe alternativas segun ids
        df_alt_filt_cluster = df_alt[df_alt.id_alternativa.isin(ids_cluster)]

        # POR ATRIBUTO
        for atributo in df_alt.columns[1:]:  #excluyo id
            print("Atributo: ", atributo, df_alt_filt_cluster[atributo].dtype)
            # print(df_alt_cluster[atributo])

            # Si es numerica
            if df_alt_filt_cluster[atributo].dtype == 'int64' or df_alt_filt_cluster[atributo].dtype == 'float64':
                # Obtengo promedio de la columna
                valor = df_alt_filt_cluster[atributo].mean()

            # Si no es numerica
            else:
                # Obtengo valor mas frecuente de la columna
                print(df_alt_filt_cluster[atributo].value_counts())
                valor = df_alt_filt_cluster[atributo].value_counts().index[0]

            print("Valor atributo: ", valor)
            fila.append(valor)

        # Guardo fila por grupo
        print("Fila: ", fila)
        table2.loc[cluster] = fila
        # table2.loc[len(table2)] = fila

    return table2

def create_table_4(df_alt, df_clust):

    table4 = pd.DataFrame(index=df_clust['label'].unique(), columns=df_alt['Marca'].dropna().unique())

    # POR CLUSTER
    for cluster in df_clust['label'].unique():
        print("CLUSTER LABEL: ", cluster)

        # SELECCIONO ALTERNATIVAS DE CLUSTER EN DATAFRAME ALTERNATIVAS
        # Selecciono ids de alternativas de un cluster
        ids_cluster = df_clust[df_clust['label'] == cluster]['id_alternativa']
        # Selecciono alternativas en dataframe alternativas segun ids
        df_alt_filt_cluster = df_alt[df_alt.id_alternativa.isin(ids_cluster)]

        # OBTENGO FRECUENCIA DE MARCAS EN CLUSTER
        marcas = df_alt_filt_cluster['Marca'].value_counts()
        print(marcas)
        print(marcas.index)
        print(marcas.values)

        # GUARDO MARCAS Y SUS FRECUENCIAS
        for i in range(len(marcas)):

            marca, frec = marcas.index[i], marcas.values[i]
            table4.loc[cluster, marca] = frec

            # print(marcas.index[i])
            # print(marcas.values[i])

        # for marca in list(marcas.index), marcas.values:
        #    print(marca)
            # table4.loc[cluster, marca] = frec_marca

    return table4

def cluster_names(df_clust):
    d = {}

    for cluster in df_clust['label'].unique():
        print("CLUSTER LABEL: ", cluster)

        nombre_cluster = input(str("Ingrese nombre del cluster: "))

        d[cluster] = nombre_cluster

    print("Label de clusters y su nombre: ", d)
    return d

def replace_labels_with_names(df_clust, d):

    df_copia = pd.DataFrame(columns=df_clust.columns)

    for label in df_clust['label'].unique():

        # Selecciono alternativas de un cluster
        df_clust_filt_cluster = df_clust[df_clust['label'] == label]

        # Reemplazo label por nombre del label
        df_clust_filt_cluster = df_clust_filt_cluster.drop(['label'], axis=1)  # borro columna label
        df_clust_filt_cluster = df_clust_filt_cluster.assign(label=d[label])
        # df_clust_filt_cluster['label'] = d[label]  # creo nueva columna label con nombre de label

        # Guardo
        df_copia = pd.concat([df_copia, df_clust_filt_cluster])

    return df_copia

def create_table_1(df_clust):

    table1 = pd.DataFrame(columns=['Cantidad de alternativas'], index=df_clust['label'].unique())
    table1.index.name = 'Nombre de cluster'

    # Por cluster
    for cluster in df_clust['label'].unique():

        # Selecciono alternativas de un cluster
        df_clust_filt_cluster = df_clust[df_clust['label'] == cluster]

        table1.loc[cluster] = len(df_clust_filt_cluster)

    return table1

def show_results(df_alt, df_clust):  #despues veo si la pongo en pagina_web.py o si la dejo

    table0 = create_table_0(df_clust)  # tabla 0 pues el cliente no la ve, es solo para mi y asi poder definir nombres de clusters

    # Obtengo nombre de clusters
    d = cluster_names(df_clust)

    # Reemplazo labels por nombre de labels
    df_clust = replace_labels_with_names(df_clust, d)
    df_clust.to_excel('/Users/nachomondino/Desktop/AAAAAA.xlsx')

    table1 = create_table_1(df_clust)

    table2 = create_table_2(df_alt, df_clust)

    table4 = create_table_4(df_alt, df_clust)

    return table0, table1, table2, table4


def main():

    # Creo el dataframe para clustering
    df_alt = pd.read_excel('/Users/nachomondino/Desktop/df_alt_celulares_cleaned.xlsx')  #index_col=0
    df_alt_orig = pd.read_excel('/Users/nachomondino/Desktop/df_alt_celulares.xlsx')  #index_col=0
    df_attr_values = pd.read_excel('/Users/nachomondino/Desktop/df_attr_value_sent.xlsx', 'Hoja de datos',index_col=0)
    print(df_alt)
    print(df_attr_values)
    df_input_clustering = create_clustering_dataframe(df_alt, df_attr_values)
    print(df_input_clustering)
    # df_clustering = pd.read_excel('/Users/nachomondino/Desktop/df_clustering.xlsx', 'Hoja de datos',index_col=0)

    # df_modelos = pd.read_excel('/Users/nachomondino/Desktop/df_modelos_cleaned.xlsx', 'Hoja de datos')

    # Proceso los datos
    # df_clustering = pd.read_excel('/Users/nachomondino/Desktop/df_clustering.xlsx', index_col=0)
    df_clustering = pd.concat([df_input_clustering['id_alternativa'], k_means(df_input_clustering.iloc[:, 1:])], axis=1)
    # print("FINAL: ", df_clustering)

    df_clustering.to_excel('/Users/nachomondino/Desktop/df_clustering_labels.xlsx')


    """ Table 3
    ids_cleaned = df_clustering["id_alternativa"]
    print(ids_cleaned, len(ids_cleaned))
    # selecciono ids que no fueron eliminados
    print(df_alt_orig.shape)
    df_alt_orig = df_alt_orig[df_alt_orig.id_alternativa.isin(ids_cleaned)]
    print(df_alt_orig.shape)
    table3 = pd.concat([df_alt_orig, df_clustering['label']])
    print(table3)
    table3.to_excel('/Users/nachomondino/Desktop/df_clustering_table3.xlsx')
    """

    df0, df1, df2, df4 = show_results(df_alt, df_clustering)
    df1.to_excel('/Users/nachomondino/Desktop/df_clustering_table_1.xlsx')
    df2.to_excel('/Users/nachomondino/Desktop/df_clustering_table_2.xlsx')
    df4.to_excel('/Users/nachomondino/Desktop/df_clustering_table_4.xlsx')

main()
