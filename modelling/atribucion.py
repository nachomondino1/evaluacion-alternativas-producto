# 4.2 Atribucion de sentiment de opinion a cada valor de cada campo especifico
import pandas as pd

def create_relation_matrix(atributos, customer_needs):
    df = pd.DataFrame(columns=atributos)
    d = {}

    for customer_need in customer_needs:

        for atributo in atributos:

            # Pido al administrador relacion entre customer_need y atributo
            d[atributo] = int(input("Ingrese relacion entre {} y {} (0, 1, 3 o 9 ptos): ").format(atributo, customer_need))

        # Agregar fila al dataframe
        df = df.append(d, ignore_index=True)

    return df


# le paso df_opiniones con opinion y rate
def temp(df_opiniones, relevant_words):  #pasar df entero

    # df_sent = pd.DataFrame(columns=[relevant_words])  #tendre que agregarr id_pub
    df_sent = pd.DataFrame()  #tendre que agregarr id_pub

    idx_opi = df_opiniones.columns.get_loc("content")  # agrega flexibilidad pues puedo pasarle el df_opiniones enterro e igual usa solo "opiniones"
    idx_rate = df_opiniones.columns.get_loc("rate")  # agrega flexibilidad pues puedo pasarle el df_opiniones enterro e igual usa solo "opiniones"

    # Por opinion  --> tendre que guardar un sentiment a cada atrib y eso esta basado en una deteerminada cant de opis
    for i in range(len(df_opiniones)):

        # inicializo diccionarios donde guardare datos por opinion
        d_sent = {'id_publicacion': df_opiniones.iloc[i, 0]}  # no se si inicializarlo asi o vacio..

        opinion = df_opiniones.iloc[i, idx_opi]
        rate = df_opiniones.iloc[i, idx_rate]

        for word in relevant_words:

            # Si la opinion menciona el atributo
            if word in opinion:

                d_sent[word] = rate

            # Si la opinion no menciona el atributo
            else:
                # el atributo no toma sentiment
                pass

        # Termino de ver si una opinion menciona a los atributos, guardo fila en df
        df_sent = df_sent.append(d_sent, ignore_index=True)

    print(df_sent)
    df_sent.to_excel('/Users/nachomondino/Desktop/BBBBB.xlsx', 'Hoja de datos', index=False)

    return df_sent


def conglomerar_id(df_sent):
    # Deberia ver que id tiene una opinion, y asignarlelos sentiment de cada atrib al valor que corresponda

    # TENGO QUE PENSAR COMO IMPLEMENTAR...
    for id in df_sent['id_publicacion'].unique():

        df_filtrado = df_sent[df_sent['id_publicacion'] == id]

        for columna in df_sent.columns:

            pass

# Levanto el dataset --> en la vida real le paso df_cleanded
df_opiniones = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_opiniones_celulares.xlsx')
relevant_words = ['precio', 'bateria', 'camara', 'memoria', 'ram', 'tamaño', 'pantalla']
df_sent = temp(df_opiniones, relevant_words)
df_sent_x_modelo = conglomerar_id(df_sent)



