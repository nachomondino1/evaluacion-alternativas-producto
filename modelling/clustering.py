# Importo librerias
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min
from mpl_toolkits.mplot3d import Axes3D


def create_clustering_dataframe(df_modelos, df_attr_values):

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
    replace_nan(df)

    return df

def replace_nan(df):

    # https://stackoverflow.com/questions/10368721/running-kmeans-function-on-matrix-with-nan
    # Replace NaNs in column with mean of the column

    # Por columna
    for column in df.columns:

        # Obtengo promedio de
        valor_promedio = df[column].mean()

        # Por valor
        for i in range(len(df[column])):

            valor = df[column].iloc[i]

            # Si el valor es NaN
            if str(valor) == 'nan':

                # Reemplazo valor NaN por valor promedio de la columna
                df[column].iloc[i] = valor_promedio

    return df

def clustering(df_clustering):
    # https://www.aprendemachinelearning.com/k-means-en-python-paso-a-paso/

    plt.rcParams['figure.figsize'] = (16, 9)
    plt.style.use('ggplot')

    # Defino datos
    X = np.array(df_clustering[df_clustering.columns])  #por ahi teenga que sacar algunas columnas..

    '''
    # Obtener el valor de K
    Nc = range(1, 20)
    kmeans = [KMeans(n_clusters=i) for i in Nc]
    score = [kmeans[i].fit(X).score(X) for i in range(len(kmeans))]
    plt.plot(Nc, score)
    plt.xlabel('Number of Clusters')
    plt.ylabel('Score')
    plt.title('Elbow Curve')
    plt.show()
    '''

    # Ejecutamos K-means
    kmeans = KMeans(n_clusters=5).fit(X)
    print(kmeans)
    centroids = kmeans.cluster_centers_
    print(centroids)

    df_clustering["label"] = kmeans.labels_
    return df_clustering

def show_results(df_mod, df_clust):  #despues veo si la pongo en pagina_web.py o si la dejo

    table1 = pd.DataFrame(columns=df_clust.columns[1:])

    # Tabla 1
    # Por grupo
    for grupo in df_clust['label'].unique():

        # Defino variable donde guardar scores para un grupo
        fila = []

        # filtro dataframe
        df_grupo = df_clust[df_clust['label']==grupo]

        # Por atributo
        for atributo in df_clust.columns[1:]:  #salvo el id_pub

            # Obtengo promedio de scores
            score_prom = df_grupo[atributo].mean()

            # Guardo score
            fila.append(score_prom)

        # Guardo fila del grupo en tabla 1
        table1.loc[len(table1)] = fila

    # Ordeno la tabla por grupo
    table1 = table1.sort_values(by=['label'])

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

    return table1, table2

def main():

    '''
    # Armo el dataframe
    df_modelos = pd.read_excel('/Users/nachomondino/Desktop/df_modelos_cleaned.xlsx', 'Hoja de datos')
    df_attr_values = pd.read_excel('/Users/nachomondino/Desktop/df_attr_value_sent.xlsx', 'Hoja de datos',index_col=0)
    print(df_modelos)
    print(df_attr_values)
    df_clustering = create_clustering_dataframe(df_modelos, df_attr_values)
    df_clustering.to_excel('/Users/nachomondino/Desktop/df_clustering.xlsx', 'Hoja de datos')
    '''

    '''
    df_clustering = pd.read_excel('/Users/nachomondino/Desktop/df_clustering.xlsx', 'Hoja de datos',index_col=0)

    # Retiro Nan para poder usar Kmeans que no puede tener NaN values... igual son pocos los valores que les pasa esto. 84 de 121 modelos tiene todos los valores.
    df_clustering = replace_nan(df_clustering)
    print(df_clustering)
    # df_clustering.to_excel('/Users/nachomondino/Desktop/df_clustering_sin_nan.xlsx')
    '''

    df_modelos = pd.read_excel('/Users/nachomondino/Desktop/df_modelos_cleaned.xlsx', 'Hoja de datos')

    # Proceso los datos
    df_clustering = pd.read_excel('/Users/nachomondino/Desktop/df_clustering.xlsx', index_col=0)
    df = clustering(df_clustering)
    df.to_excel('/Users/nachomondino/Desktop/df_clustering_labels.xlsx')

    df2 = show_results(df_modelos, df)
    df2.to_excel('/Users/nachomondino/Desktop/df_clustering_prueba.xlsx')


main()
