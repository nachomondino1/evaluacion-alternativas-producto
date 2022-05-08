# Importo librerias
import pandas as pd
from p2_data_preparation.utils import preparacion_texto


def delete_date_of_issue_from_opinion(df_opiniones):
    """
    Elimina fecha de emision de cada opinion
    :param df_opiniones: Dataframe opiniones
    :return: Dataframe opiniones cuyas opiniones ya no tienen fecha de emision
    """
    # Defino variable
    idx_opi = df_opiniones.columns.get_loc("opinion")  # indice de columna "opinion"

    # POR OPINION
    for i in df_opiniones.index:
        opinion = df_opiniones.iloc[i, idx_opi]  # Busco una opinion

        # BUSCO EL INDICE DEL ULTIMO PUNTO DE ESTA (despues del punto esta la fecha de emision)
        idx = opinion.rfind('.')  # rfind() (r de reverse?) busca desde atras en cambio find() desde adelante

        # REEMPLAZO OPINION POR ELLA MISMA PERO HASTA ANTES DEL ULTIMO PUNTO
        df_opiniones.iloc[i, idx_opi] = opinion[:idx]

    print("Se ha quitado con exito la fecha de emision de cada opinion")
    # df_opiniones['opinion'].to_csv('/Users/nachomondino/Desktop/df_opiniones.csv', index=False)
    return df_opiniones

def clean_opinions(df_opiniones):  # creo que la voy a sacar y desde el main llamo a cada funcion directo de preparacion_texto.py
    """
    Procesa opiniones: convierto a miniscula, elimino acentos, elimino puntuacion, tokenizo y elimino palabras vacias
    :param opiniones: Dataframe opiniones
    :return: Dataframe opiniones con opiniones procesadas
    """
    # Creo objeto de clase TextPreparation para tener disponible herramientas de procesamiento de texto
    tp = preparacion_texto.TextPreparation(df_opiniones['opinion'])

    print("Originalmente el dataframe luce como sigue")
    print(df_opiniones.head(5))

    print("Convierto opiniones a miniscula")
    df_opiniones['opinion'] = tp.to_lower()
    print(df_opiniones.head(5))

    print("Remuevo acentos de opiniones")
    df_opiniones['opinion'] = tp.delete_accent()
    print(df_opiniones.head(5))

    print("Quito puntuacion de opiniones")  # a priori creo que no lo removeria peus necesito los puntos para obtener cada frase de la opinion y
    df_opiniones['opinion'] = tp.delete_punctuation()
    print(df_opiniones.head(5))

    print("Tokenizo opiniones")
    df_opiniones['opinion'] = tp.tokenize()
    print(df_opiniones.head(5))

    print("Remuevo palabras vacias")
    df_opiniones['opinion'] = tp.stop_word_removal()
    print(df_opiniones.head(5))

    return df_opiniones

def categorize_numeric_columns(df):
    """
    Dado un dataframe, categoriza sus columnas numericas (las no numericas no porque al no haber una "distancia" entre
    strings, no puedo determinar cual se asemeja con cual) continuas (las discretas no pues ya estan categorizadas)
    :param df: Dataframe
    :return: Dataframe con todas sus columnas numericas discretas
    """
    # DEFINO VARIABLES
    PERCENTILES = 1 / 6
    CANT_CLASES = int(1 / PERCENTILES)  # cantidad de clases con ≠ amplitud (basado en percentiles)

    # POR COLUMNA DEL DATAFRAME
    for columna in df.columns:

        # SI LA COLUMNA ES NUMERICA
        if (df[columna].dtype == 'float64') or (df[columna].dtype == 'int64'):

            # Defino variables
            cant_valores_unicos = len(df[columna].value_counts())
            cant_opt_valores_unicos = len(df[columna]) ** 0.5  # cant clases ideales = raiz(nro datos)

            # SI LA COLUMNA ES CONTINUA (toma muchos valores distintos, especificamente, mas que la cantidad optima)
            if cant_valores_unicos > cant_opt_valores_unicos:  # Aqui se podria aplicar "factor de holgura"
                print("La columna '{}' sera categorizada...".format(columna))

                # CREO CLASES QUE TENDRA LA VARIABLE
                # Defino variables
                d = {}  # diccionario con valores maixmos y medios de cada clase
                valores = list(df[columna]) # lista de valores de la columna
                valores_unicos = sorted(list(df[columna].dropna().unique()))
                print("Valores unicos", valores_unicos)

                # Creo cada clase
                for i in range(CANT_CLASES):
                    # Obtengo indices de valor min y max para la clase
                    idx_valor_min_clase = int(len(valores_unicos) * PERCENTILES * i) # valor min para estar en clase i
                    idx_valor_max_clase = int(len(valores_unicos) * PERCENTILES * (i + 1)) - 1 # valor min para estar en clase i. El -1 seria porque el idx de la lista arranca en 0

                    # Obtengo valores min y max de la clase a partir de los indices
                    valor_min_clase = valores_unicos[idx_valor_min_clase]
                    valor_max_clase = valores_unicos[idx_valor_max_clase]
                    valor_med_clase = (valor_max_clase + valor_min_clase) / 2  # valor medio de clase i

                    # guardo valor maximo y medio de la clase
                    d[valor_max_clase] = valor_med_clase
                    print("Clase Nº{}: Valor min = {} ; Valor med = {} ; Valor max = {}".format(i, valor_min_clase, valor_med_clase, valor_max_clase))

                # REEMPLAZO VALORES CONTINUOS POR LA MEDIA DE LA CLASE A LA QUE PERTENECE
                # Por valor del atributo
                for i in range(len(valores)):

                    # Por valor maximo de las clases
                    for valor_limite in list(d.keys()):

                        # Si el valor es menor al valor maximo de la clase
                        if df[columna].iloc[i] <= valor_limite:

                            # reemplazo valor por el valor medio de la clase
                            df.loc[i, columna] = d[valor_limite]

                            # dejo de comparar el valor con los valores maximos de las clases pues ya encontre su clase
                            break

            # SI LA COLUMNA ES DISCRETA (toma pocos valores distintos)
            else:
                # imprimo mensaje
                print("La columna '{}' es numerica pero toma valores discretos".format(columna))

        # SI LA COLUMNA NO ES NUMERICA
        else:
            # imprimo mensaje
            print("La columna '{}' no es numerica!".format(columna))

    return df

def delete_attr_x_values(df):
    """
    Elimino columnas del dataframe que toman un solo valor constante, o bien, toma muchos valores
    :param df: Dataframe
    :return: Dataframe sin columnas que tomen un solo valor o, por el contrario, muchos
    """
    # Defino variables
    PORC_MUCHOS_VAL = 0.5
    col_excepciones = ["id_alternativa", "Marca", "Línea", "Modelo"]  # columnas que no eliminar a pesar de que toman muchos valores

    # POR COLUMNA DEL DATAFRAME
    for columna in df.columns:

        # SI COLUMNA NO ES DE LAS COLUMNAS EXCEPCIONES
        if columna not in col_excepciones:

            # Obtengo lista de frecuencia de sus valores
            unique_values = list(df[columna].dropna().unique())  # dropna para evitar que NaN sea una valor unico
            cant_unique_values = len(unique_values)
            cant_posible_values = len(df[columna])

            # SI LA COLUMNA ES CONSTANTE (TOMA UN UNICO VALOR)
            if cant_unique_values == 1:

                # Elimino el atributo
                print("Elimino columna {} por tomar 1 solo valor".format(columna))
                df = df.drop([columna], axis=1)

            # SI LA COLUMNA ES CONTINUA (TOMA MUCHOS VALORES DISTINTOS)
            elif cant_unique_values > PORC_MUCHOS_VAL * cant_posible_values:

                # Elimino el atributo
                print("Elimino columna {} por tomar muchos valores distintos".format(columna))
                df = df.drop([columna], axis=1)

            # SI LA COLUMNA ES DISCRETA (no toma ni 1 valor ni muchos)
            else:
                # No hacer nada
                print("La columna {} toma valores discretos! (ni 1 ni muchos)".format(columna))

    return df

'''
def main para hacer pruebas en este archivo independientemente de main.py
def main():  # esto lo implemento en main.py, dsp de terminar el archivo, la paso...
    # Levanto el dataframe
    df_modelos = pd.read_excel('/Users/nachomondino/Desktop/df_modelos_formateado.xlsx')
    # df_modelos = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_modelos_celulares.xlsx')
    df_opiniones = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_opiniones_celulares.xlsx')

    # 1) ELIMINO NONE VALUES
    print("+++ (1) ELIMINO NONE VALUES +++")
    # df_opiniones.dropna()  # borra las pocas filas que no tienen title

    # 2) ELIMINO FILAS REPETIDAS --> ojo que tiene que ser sin id...
    print("+++ (2) ELIMINO FILAS REPETIDAS +++")
    # df_opiniones = df_opiniones.drop(delete_repeated_rows(df_opiniones['content']))  # elimino duplicados teniendo en cuenta solo la columna content que es la que contiene opiniones propiamente
    # print(df_opiniones.shape)

    # 3) CATEGORIZO VARIABLES NUMERICAS
    print("+++ (3) CATEGORIZO CAMPOS NUMERICOS CONTINUOS +++")
    # df_modelos.iloc[:, 1:] = categorize_numeric_columns(df_modelos.iloc[:, 1:])  # categorizo columnas numericas con valores continuos, no le paso columna id pues la categorizaria.
    # df_modelos.to_excel('/Users/nachomondino/Desktop/df_categorizado.xlsx', 'Hoja de datos', index=False)

    # 4) ELIMINO CAMPOS ESPECIFICOS SEGUN CANTIDAD DE VALORES Y CANTIDAD DE OPINIONES POR VALOR
    print("+++ (4) ELIMINO CAMPOS CONSTANTES, O BIEN, CONTINUOS +++")
    # ESTA NO df_modelos.iloc[:, 2:] = delete_attr_x_values(df_modelos.iloc[:, 2:])  # elimino columnas que toman 1 o muchos valores # IndexError: single positional indexer is out-of-bounds (creo que era porque el df que devolvia la funcion tenia un largo distinto?)
    # df_modelos = delete_attr_x_values(df_modelos)  # elimino columnas que toman 1 o muchos valores # IndexError: single positional indexer is out-of-bounds
    # df_modelos.to_excel('/Users/nachomondino/Desktop/df_modelos_cleaned.xlsx', 'Hoja de datos', index=False)

    # 5) PREPARACION DE OPINIONES
    print("+++ (5) PREPARACION DE OPINIONES +++")
    # Elimino fecha de emision al final de la opinion (por ej, "Hace x meses")
    df_opiniones = correct_opinion_column(df_opiniones)

    # Limpio las opiniones
    df_opiniones_tokenizado, df_cleaned_opinions = text_preparation(df_opiniones['content'])  # Alternativa 2
    print(df_cleaned_opinions)

    # tal vez cleaned() que devuelva solo el df_cleaned y customeerr needs lo tokeniza y obtiene las customer needs... OJO que las funciones de prep_texto las hice con token...
    # si el df_cleaned no lo uso para los modelos pues no mejoran el sentiment, entonces no lo uso...


main()
'''