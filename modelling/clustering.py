# Importo librerias
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min
from mpl_toolkits.mplot3d import Axes3D

def dataframe_clustering(df_modelos, df_attr_values):
    # df = pd.DataFrame(columns=df_modelos.columns)
    df = pd.DataFrame(columns=df_attr_values['campo_especifico'].unique())

    # Por modelo
    for i in range(len(df_modelos)):
        print("++++ Nº MODELO: {} ++++ ".format(i))

        l_prom_sent = []  # la reinicio para cada modelo

        valores_nan = 0  # la reinicio para cada modelo

        # Por atributo
        # for atributo in df_modelos.columns:  # tengo que evitar id_pub, linea y modelo
        for atributo in df.columns:  # tengo que evitar id_pub, linea y modelo
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

                # No encontre el atributo pues este no tiene relacion con ninguna customer need
                # except:
                #    prom_sent = None
                #    print("Valor {} no se encontro sentiment".format(valor))


            # si el valor es NaN
            else:
                # Busco min prom_sent
                prom_sent = df_attr_values[df_attr_values['campo_especifico'] == atributo]['prom_sent'].min()
                print("Valor {} es NaN. Busco peor sentiment, en este caso, {}".format(valor ,prom_sent))

            # Guardo prom_sent
            l_prom_sent.append(prom_sent)

        # Guardo fila de modelo
        print("Fila de sentiment del modelo: ", l_prom_sent)
        print("Cantidad de seentiments", len(l_prom_sent))
        print("Cantidad de columnas", len(df.columns))
        df.loc[len(df)] = l_prom_sent

    return df

def clustering(df_clustering):
    plt.rcParams['figure.figsize'] = (16, 9)
    plt.style.use('ggplot')

    # Defino datos
    X = np.array(df_clustering[df_clustering.columns])  #por ahi teenga que sacar algunas columnas..

    # Obtener el valor de K
    Nc = range(1, 20)
    kmeans = [KMeans(n_clusters=i) for i in Nc]
    score = [kmeans[i].fit(X).score(X) for i in range(len(kmeans))]
    plt.plot(Nc, score)
    plt.xlabel('Number of Clusters')
    plt.ylabel('Score')
    plt.title('Elbow Curve')
    plt.show()

    # Ejecutamos K-means
    kmeans = KMeans(n_clusters=5).fit(X)
    centroids = kmeans.cluster_centers_
    print(centroids)


def main():
    '''
    df_modelos = pd.read_excel('/Users/nachomondino/Desktop/df_modelos_cleaned.xlsx', 'Hoja de datos')
    df_attr_values = pd.read_excel('/Users/nachomondino/Desktop/df_attr_value_sent.xlsx', 'Hoja de datos',index_col=0)
    print(df_modelos)
    print(df_attr_values)
    df_clustering = dataframe_clustering(df_modelos, df_attr_values)
    # df_clustering.to_excel('/Users/nachomondino/Desktop/df_clustering.xlsx', 'Hoja de datos')
    '''
    df_clustering = pd.read_excel('/Users/nachomondino/Desktop/df_clustering.xlsx', 'Hoja de datos')
    clustering(df_clustering)


main()
