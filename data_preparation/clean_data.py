# Importo librerias
import pandas as pd
from data_preparation.utils import preparacion_texto


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
    :param opiniones: Columna "opinion" de dataframe opiniones
    :return: Dataframe con columna "tokens" cuyos valores son las opiniones procesadas
    """
    # Creo objeto de clase TextPreparation para tener disponible herramientas de procesamiento de texto
    tp = preparacion_texto.TextPreparation(df_opiniones['opinion'])

    print("Convierto opiniones a miniscula")
    df_opiniones['opinion'] = tp.to_lower()
    print(df_opiniones.head(5))

    print("Remuevo acentos de opiniones")
    df_opiniones['opinion'] = tp.delete_accent()
    print(df_opiniones.head(5))

    print("Quito puntuacion de opiniones")
    df_opiniones['opinion'] = tp.delete_punctuation()
    print(df_opiniones.head(5))

    print("Tokenizo opiniones")
    df_opiniones['opinion'] = tp.tokenize()
    print(df_opiniones.head(5))

    print("Remuevo palabras vacias")
    df_opiniones['opinion'] = tp.stop_word_removal()
    print(df_opiniones.head(5))

    '''
    # POR OPINION
    for opinion in opiniones:

        # CONVIERTO A MINÚSCULAS
        opinion = opinion.lower()

        # Correccion de repeticiones 'largooo' en vez de 'largo'
        # Correccion de palabras (mala escritura) 'espectativas' en vez de 'expectativas'
        # Correccion de abreviaturas 'q' en vez de 'que'

        # ELIMINO ACENTOS
        opinion = tp.delete_accent(opinion)
        # print(opinion)

        # ELIMINO PUNTUACION
        opinion = tp.delete_punctuation(opinion)
        # print(opinion)

        # (1) TOKENIZATION: SEPARO SUS PALABRAS POR ESPACIOS EN BLANCO
        tokens = opinion.split()

        # (2) STOP WORD REMOVAL: ELIMINO PALABRAS VACIAS COMO POR EJEMPLO ARTICULOS
        tokens = tp.stop_word_removal(tokens)  #pruebo a no implementar stop word removal

        # GUARDO OPINION PROCESADA
        df_tokenizado.loc[len(df_tokenizado)] = [tokens]  # df_tokenizado = df_tokenizado.append({"tokens": tokens}, ignore_index=True)
        # untoken = ' '.join(tokens)
        # df_cleaned.loc[len(df_cleaned)] = untoken
    
    '''

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

    # POR COLUMNA DEL DATAFRAME
    for columna in df.columns:

        # SI LA COLUMNA ES NUMERICA
        if (df[columna].dtype == 'float64') or (df[columna].dtype == 'int64'):

            # Y SI ES CONTINUA, ES DECIR, TOMA MUCHO VALORES DISTINTOS (NO ES DISCRETA)
            # Defino variables
            cant_valores_unicos = len(df[columna].value_counts())
            cant_opt_valores_unicos = len(df[columna]) ** 0.5  # cant clases ideales = raiz(nro datos)

            # Si toma mas valores que la cantidad optima
            if cant_valores_unicos > cant_opt_valores_unicos:  # Aqui se podria aplicar "factor de holgura"
                print("La columna '{}' sera categorizada...".format(columna))

                # DEFINO CLASES (con ≠ amplitud (basado en percentiles)
                # Defino variables
                cant_clases = int(1 / PERCENTILES)
                valores = list(df[columna]) # lista de valores de la columna
                valores_unicos = sorted(list(df[columna].dropna().unique()))
                print(valores_unicos)
                valores_limite_max = []  # lista con valores maximos
                d = {}

                # Por clase
                for i in range(cant_clases):
                    idx_valor_min_clase = int(len(valores_unicos) * PERCENTILES * i) # valor min para estar en clase i
                    idx_valor_max_clase = int(len(valores_unicos) * PERCENTILES * (i + 1)) - 1 # valor min para estar en clase i
                    # el -1 seria porque el idx de la lista arranca en 0

                    valor_min_clase = valores_unicos[idx_valor_min_clase]
                    valor_max_clase = valores_unicos[idx_valor_max_clase]
                    valor_med_clase = (valor_max_clase + valor_min_clase) / 2  # valor medio de clase i

                    # guardo valor maximo de la clase
                    valores_limite_max.append(valor_max_clase)
                    d[valor_max_clase] = valor_med_clase

                    print("Clase Nº{}: Valor min = {} ; Valor med = {} ; Valor max = {}".format(i, valor_min_clase, valor_med_clase, valor_max_clase))

                # REEMPLAZO VALORES POR LA MEDIA DE LA CLASE A LA QUE PERTENECE
                # Por valor del atributo
                for i in range(len(valores)):

                    # Por valor maximo de las clases
                    for valor_limite in valores_limite_max:

                        # Si el valor es menor al valor maximo de la clase
                        if df[columna].iloc[i] <= valor_limite:

                            # reemplazo valor por el valor medio de la clase
                            df.loc[i, columna] = d[valor_limite]

                            # dejo de comparar el valor con los valores maximos de las clases pues ya encontre su clase
                            break

            # la columna es numerica pero discreta (toma pocos valores distintos)
            else:
                print("La columna '{}' es numerica pero toma valores discretos".format(columna))

        # la columna no es numerica
        else:
            print("La columna '{}' no es numerica!".format(columna))

    return df

def delete_attr_x_values(df):
    # Defino variables
    PORC_MUCHOS_VAL = 0.5
    # columnas_no_eliminar = ["Marca", "Línea", "Modelo"]  # columnas que no eliminar a pesar de que toman muchos valores
    columnas_no_eliminar = ["id_alternativa", "precio", "Marca", "Línea", "Modelo"]  # columnas que no eliminar a pesar de que toman muchos valores

    # Por cada atributo
    for columna in df.columns:

        # Obtengo lista de frecuencia de sus valores
        unique_values = list(df[columna].value_counts())
        cant_unique_values = len(unique_values)
        cant_posible_values = len(df[columna])

        if columna not in columnas_no_eliminar:

            # SI LA COLUMNA ES CONSTANTE (ES DECIR, UN UNICO VALOR)
            if cant_unique_values == 1:

                # Elimino el atributo
                print("Elimino columna {} por tomar 1 solo valor".format(columna))
                df = df.drop([columna], axis=1)

            # SI LA COLUMNA TOMA MUCHOS VALORES DISTINTOS
            elif cant_unique_values > PORC_MUCHOS_VAL * cant_posible_values:

                # Elimino el atributo
                print("Elimino columna {} por tomar muchos valores distintos".format(columna))
                df = df.drop([columna], axis=1)

            # SI LA COLUMNA TOMA VALORES DISCRETOS (ni 1 ni muchos)
            else:
                # NO HACER NADA
                print("La columna {} toma valores discretos! (ni 1 ni muchos)".format(columna))
                pass

    return df

''' Prueba
df_opiniones = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_opiniones_celulares.xlsx')
pd.set_option("display.max.columns", None)  # para ver todas las columnas del df y no que las colapse
pd.set_option("display.precision", 2)  # mostrar maximo dos decimales
print(df_opiniones['opinion'].head(5))
df = clean_text(df_opiniones['opinion'])
print(df.head(5))
'''



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


'''
def delete_repeated_rows(df):
    """
     La funcion debe obtener los indices de las filas a borrar
    :param df: Dataframe
    :return: Lista de indices de las filas del dataframe a borrar
    """
    # Defino lista donde guardar los indices de las filas a borrar
    idx = []

    # Defino cantidad de filas
    cant_filas = df.shape[0]
    print("Originalmente el dataframe tenia {} filas.".format(cant_filas), end=" ")

    # Elimino filas duplicadas
    df = df.drop_duplicates()

    for i in range(len(df)):
        if i not in df.index:
            idx.append(i)

    # Defino nueva cantidad de filas
    cant_filas = df.shape[0]
    print("Tras eliminar las filas duplicadas, el dataframe tiene {} filas".format(cant_filas))

    return idx
'''
