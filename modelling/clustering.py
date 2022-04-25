# Importo librerias
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
# import matplotlib.pyplot as plt


def create_clustering_dataframe(df_modelos, df_attr_values):
    """
    Agrega informacion de distintos dataframes para crear el dataframe con todos valores numericos y sin NaN y asi poder
    hacer clustering
    :param df_modelos: Dataframe cuya unidad de analisis son los valores de los atributos del producto. Sus columnas son
    valor, atributo al que perenece y su sentiment
    :param df_attr_values: Dataframe cuya unidad de analisis es cada una de las alternativas del producto, sus columnas
    son los atributos del producto y las celdas el valor que toma el atributo en una alternativa
    :return: Dataframe cuya unidad de análisis es cada una de las alternativas del producto, sus columnas son los
    atributos del producto y las celdas, a diferencia del df_attr_values, son los sentiment que toma el valor del
    atributo
    """
    # Creo dataframe a retornar vacio con los nombres de las columnas correspondientes
    df = pd.DataFrame(columns=['id_publicacion'] + list(df_attr_values['campo_especifico'].unique()))

    # Por modelo
    for i in range(len(df_modelos)):
        print("++++ Nº MODELO: {} ++++ ".format(i))

        l_prom_sent = [df_modelos.iloc[i, 0]]  # la reinicio para cada modelo, agrego el id_pub

        # Por atributo
        for atributo in df.columns[1:]:  # tengo que evitar id_pub, linea y modelo
            print("ATRIBUTO: ", atributo)

            # Obtengo valor del atributo para el modelo
            idx_atrib = df_modelos.columns.get_loc(atributo)
            valor = df_modelos.iloc[i, idx_atrib]

            # Si el valor no es NaN
            if str(valor) != 'nan':

                #try:
                # Busco prom_sent para ese valor
                prom_sent = float(df_attr_values[
                    (df_attr_values['campo_especifico'] == atributo) & (df_attr_values['valor'] == valor)][
                    'prom_sent'])
                print("Valor {} toma sentiment {}".format(valor,prom_sent))

            # si el valor es NaN
            else:
                # Busco min prom_sent
                prom_sent = df_attr_values[df_attr_values['campo_especifico'] == atributo]['prom_sent'].min()
                print("Valor {} es NaN. Busco peor sentiment, en este caso, {}".format(valor, prom_sent))

            # Guardo prom_sent
            l_prom_sent.append(prom_sent)

        # Guardo fila de modelo
        print("Fila de sentiment del modelo: ", l_prom_sent)
        # print("Cantidad de seentiments", len(l_prom_sent))
        # print("Cantidad de columnas", len(df.columns))
        df.loc[len(df)] = l_prom_sent

    # Reemplazo valores Nan por valores medios de cada columna
    df = replace_nan(df)
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
    # k = chooseBestKforKMeans(X, range(2, 40))

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
    results = pd.DataFrame(ans, columns = ['k','Scaled Inertia']).set_index('k')
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

def show_results(df_mod, df_clust):  #despues veo si la pongo en pagina_web.py o si la dejo

    table1 = pd.DataFrame(columns=df_clust.columns)

    # Tabla 1
    # Por grupo
    for cluster in df_clust['label'].unique():

        # Defino variable donde guardar scores para un grupo
        fila = []

        # filtro dataframe
        df_grupo = df_clust[df_clust['label'] == cluster]

        # Por atributo
        for atributo in df_clust:  #salvo el id_pub

            # Obtengo promedio de scores
            score_prom = df_grupo[atributo].mean()

            # Guardo score
            fila.append(score_prom)

        # Guardo fila del grupo en tabla 1
        table1.loc[len(table1)] = fila

    # Ordeno la tabla por grupo
    table1 = table1.sort_values(by=['label'])
    '''
    # table 2
    # seguro necesite df_modelos_formateado pues las numericas las promedio..
    table2 = pd.DataFrame()
    # Por grupo
    for grupo in df_clust['label'].unique():
        # Defino variable donde guardar scores para un grupo
        fila = []

        # filtro dataframe
        df_grupo = df_clust[df_clust['label'] == grupo]

        # Obtengo ids del grupo
        ids = df_grupo['id_publicacion']

        # Filtro df_modelos por id
        df_mod_grupo = pd.DataFrame(columns=df_mod.columns)
        for id in ids:
            df_aux = df_mod[df_mod['id_publicacion'] == id]
            df_mod_grupo = pd.concat([df_mod_grupo, df_aux])

        # Por columna
        for column in df_mod.columns:

            # Si es numerica
            if type(column) == 'int64' or type(column) == 'float64':

                # Obtengo promedio de la columna
                value_prom = df_mod_grupo[column].mean()

                # Guardo promedio
                fila.append(value_prom)

        # Guardo fila por grupo
        table2.loc[len(table2)] = fila

    # table 3
    # table 4
    '''

    return table1 #, table2

def main():

    # Creo el dataframe para clustering
    df_modelos = pd.read_excel('/Users/nachomondino/Desktop/df_modelos_cleaned_2.xlsx', index_col=0)
    df_attr_values = pd.read_excel('/Users/nachomondino/Desktop/df_attrr_values_sent_11.xlsx', 'Hoja de datos',index_col=0)
    print(df_modelos)
    print(df_attr_values)
    df_clustering = create_clustering_dataframe(df_modelos, df_attr_values)
    df_clustering.to_excel('/Users/nachomondino/Desktop/df_clustering.xlsx', 'Hoja de datos')

    # df_clustering = pd.read_excel('/Users/nachomondino/Desktop/df_clustering.xlsx', 'Hoja de datos',index_col=0)

    # df_modelos = pd.read_excel('/Users/nachomondino/Desktop/df_modelos_cleaned.xlsx', 'Hoja de datos')

    # Proceso los datos
    # df_clustering = pd.read_excel('/Users/nachomondino/Desktop/df_clustering.xlsx', index_col=0)
    df = k_means(df_clustering.iloc[:, 1:])  # no le mando id de pub
    df.to_excel('/Users/nachomondino/Desktop/df_clustering_labels.xlsx')

    df2 = show_results(df_modelos, df)
    df2.to_excel('/Users/nachomondino/Desktop/df_clustering_prueba.xlsx')


main()
