# Creo que implementare un modelo por archivo
# Importo librerias
import pandas as pd
from pysentimiento import create_analyzer


def modelo1(df_opiniones):
    # Uso funcion create_analyzer
    analyzer = create_analyzer(task="sentiment", lang="es")

    l_predict = []
    idx_opi = df_opiniones.columns.get_loc("content")  # agrega flexibilidad pues puedo pasarle el df_opiniones enterro e igual usa solo "opiniones"
    # df_opiniones = df_opiniones['opinion']  # salta el mismo error que antes con los otros df. Se pone el nombre la columna...

    # Por opinion
    for i in range(len(df_opiniones)):

        opinion = df_opiniones.iloc[i, idx_opi]
        # print('Nº',i, opinion)

        # Predigo sentiment
        pred = analyzer.predict(opinion)
        # print(pred)

        # Guardo en lista
        l_predict.append(pred.output)

    # Guardo las columnas del dataframe en diccionario
    d = {'content': df_opiniones['content'], 'y_pred': l_predict}

    return pd.DataFrame(data=d, columns=['content', 'y_pred'])

'''
# Levanto el dataset --> en la vida real le paso df_cleanded
df_opiniones = pd.read_excel('/Users/nachomondino/Desktop/AAAAA.xlsx')
print(modelo1(df_opiniones))
'''

# Podria pasarle el df_opiniones entero y localizar la columna opinion. Luego agregarrle una columna a ese df o haceer uno nuevo

