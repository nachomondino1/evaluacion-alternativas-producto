# Importo librerias
import pandas as pd
import data_preparation.preparacion_texto as tp


def delete_repeated_rows(df):
    """
     La funcion debe obtener los indices de las filas a borrar

    :param df: Dataframe al cual revisar valores duplicados
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

def categorize_numeric_columns(df):
    """
    Dado un dataframe, categoriza sus columnas numericas (las no numericas no porque al no haber una "distancia" entre
    strings, no puedo determinar cual se asemeja con cual) continuas (las discretas no pues ya estan categorizadas)
    :param df: Dataframe
    :return: Dataframe con todas sus columnas numericas discretas
    """
    # POR COLUMNA DEL DATAFRAME
    for columna in df.columns:

        # SI LA COLUMNA ES NUMERICA
        if (df[columna].dtype == 'float64') or (df[columna].dtype == 'int64'):

            # Y SI ES CONTINUA, ES DECIR, TOMA MUCHO VALORES DISTINTOS (NO ES DISCRETA)
            cant_valores_unicos = len(df[columna].value_counts())
            cant_opt_valores_unicos = len(df[columna])**0.5  # cant clases ideales = raiz(nro datos)
            FACTOR_HOLGURA = 1.5  # al ser mayor de 1, me aseguro que la columna realmente tome muchos valores
            if cant_valores_unicos > FACTOR_HOLGURA * cant_opt_valores_unicos:

                print("La columna '{}' sera categorizada...".format(columna))

                # Defino variables
                valores = list(df[columna])  # lista de valores de la columna
                valores_limite_max = []  # lista con valores maximos
                valor_min = min(valores)  # valor maximo de la columna
                valor_max = max(valores)  # valor minimo de la columna
                rango = valor_max - valor_min  # valor maximo - valor minimo
                amplitud_clase = rango / cant_opt_valores_unicos  # amplitud de una clase

                # CREO INTERVALOS DE CADA CLASE
                # por cada clase
                for i in range(int(cant_opt_valores_unicos)):
                    # determino valores minimo, medio y maximo de la clase
                    valor_min_clase = round(valor_min + amplitud_clase * i, 2)  # valor min para estar en clase i
                    valor_max_clase = round(valor_min + amplitud_clase * (i+1), 2)  # valor max para estar en clase i
                    valor_med_clase = round((valor_max_clase + valor_min_clase) / 2, 2)  # valor medio de clase i
                    print("Clase Nº{}: Valor min = {} ; Valor med = {} ; Valor max = {}".format(i, valor_min_clase, valor_med_clase, valor_max_clase))

                    # guardo valor maximo de la clase
                    valores_limite_max.append(valor_max_clase)

                # REEMPLAZO VALORES POR LA MEDIA DE LA CLASE A LA QUE PERTENECE
                # por cada valor
                for i in range(len(valores)):

                    # por cada valor maximo de las clases
                    for valor_limite in valores_limite_max:

                        # si el valor es menor al valor maximo de la clase
                        if df[columna].iloc[i] < valor_limite:

                            # reemplazo valor por el valor medio de la clase
                            df[columna].iloc[i] = round(valor_limite - (amplitud_clase / 2), 1)

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
    columnas_no_eliminar = ["id_publicacion", "precio", "Marca", "Línea", "Modelo"]  # columnas que no eliminar a pesar de que toman muchos valores

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

def correct_opinion_column(df):
    # Recorrer cada fila, en part, la columna de opiniones y quitar hasta el punt
    idx_opi = df.columns.get_loc("content")  # es una idea aplicable a varias funciones que ya hice

    # Por el largo del dataframe
    for i in range(len(df)):

        # Busco una opinion
        opinion = df.iloc[i, idx_opi]

        # Busco el ultimo punto.... se hace con rfind(), r debe ser de reverse
        idx = opinion.rfind('.')

        # Reemplazo opinion por ella misma pero sin la fecha de emision
        df.iloc[i, idx_opi] = opinion[:idx]

    # df['content'].to_csv('/Users/nachomondino/Desktop/df_opiniones.csv', index=False)
    return df


def text_preparation(textos):
    # df = pd.DataFrame(columns=["col"])
    df_tokenizado = pd.DataFrame(columns=['tokens'])
    df_cleaned = pd.DataFrame(columns=['content'])
    # df_steamed = pd.DataFrame(columns=['tokens'])

    # POR OPINION
    for opinion in textos:

        # Lo convierto en miniscula
        opinion = opinion.lower()

        # Correccion de repeticiones 'largooo' en vez de 'largo'
        # Correccion de palabras (mala escritura) 'espectativas' en vez de 'expectativas'
        # Correccion de abreviaturas 'q' en vez de 'que'

        # Elimino acentos
        opinion = tp.delete_accent(opinion)
        # print(opinion)

        # Elimino puntuacion
        opinion = tp.delete_punctuation(opinion)
        # print(opinion)

        # (1) TOKENIZATION: SEPARO SUS PALABRAS POR ESPACIOS EN BLANCO
        tokens = opinion.split()

        # (2) STOP WORD REMOVAL
        tokens = tp.stop_word_removal(tokens)
        df_tokenizado = df_tokenizado.append({"tokens": tokens}, ignore_index=True)
        untoken = ' '.join(tokens)
        df_cleaned = df_cleaned.append({"content": untoken}, ignore_index=True)

        '''
        # (3) STEAM
        tokens = tp.steamming(tokens)
        df_steamed = df_steamed.append({"tokens": tokens}, ignore_index=True)

        for token in tokens:
            df = df.append({"col": token}, ignore_index=True)
        '''

    return df_tokenizado, df_cleaned


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







"""
Verificar unicidad de filas desde marca en adelante
Contar None values. 
    1.- Si una FILA tiene menos del x% de atrib entonces la sacaria. 
    2.- Si una columna tiene menos del x% de atrib la sacaria

Contar valores unicos de columnas.
    1.- Si tiene muchos valores unicos (mas de x por ej): --> (no incluir id_pub, precio, marca ni modelo)
        1.1.- Si la variable es numerica, convertirla en categorica (por ej, capacidad de la bateria, en cambio, modelo del procesador no puedo)
        1.2.- Si no es numerica, (Por ej, "Modelo del procesador" quien toma muchos valores ≠ y con poca frec cada uno)
            Si el mas frecuente, tiene una frec muy chica, entonces eliminar.
            Si el mas frecuente tiene una frec aceptable, no eliminar
            
    2.- Si tiene muy pocos valores unicos:
        2.1.- y predomina uno por mucho, entonces no tener en cuenta el atributo. Por ej, atrib "Con camara" hay 71 Si y 2 No. Es practicamente cte en los modelos y encima el "No" se basa en pocas opiniones..
    Pero que hago con los modelos que son el caso particular que no lo tiene? 
        2.2.- 
    
    3.- Si tiene un solo valor, eliminar atributo. No hay diferencial entre modelos. Por ej, atributo "Con teclado QWERTY físico" que solo toma el valor "No".


Ver si precio lo entiende como int o como str. 
"""


''' ANTES DE DECIDIR QUE NO IBA A BORRAR FILAS DEL DF_MODELOS
def delete_none_values(df):
    # ELIMINO FILAS CON MUCHOS NONE VALUES
    df_copia = df.copy()  #tuve que haceer copia porque quedaba out of bounds

    porc_max_none = 0.20
    cant_col = len(df.columns)

    # Recorro cada fila del df
    for i in range(len(df)):
        none_values_fila = 0
        print("Nueva fila, numero {}".format(i))

        # Recorro cada columna del df
        for j in range(cant_col):

            # si la celda tiene el valor None
            if str(df.iloc[i, j]) == 'nan':
                print(df.iloc[i, j])  # se deberian imprimir los nan

                # Sumo 1 al contador de None
                none_values_fila += 1

        # Terminado de recorrer las columnas de una fila, defino porcentaje de None de dicha fila
        porc_none = none_values_fila / cant_col

        # Si hay mas None de los tolerados
        if porc_none > porc_max_none:
            # Elimino fila
            print("Elimino fila numero {} pues tienen el {:.0f}% de sus valores None".format(i, porc_none*100))
            df_copia = df_copia.drop(i, axis=0)
            print(df_copia.shape)

    # ELIMINO COLUMNAS CON MUCHOS NONE VALUES
    # falta implementar
    return df


'''



'''
def find_numeric_columns(df):

    # Deberia ver si una columna es dtype int64 o float64 y luego analizar cuantos valores tiene
    # si la columna es dtype float64 o int64 y es una variable discreta
    # entonces categorizarla, reemplazar valores anterior por los nuevos.


    print("+++ INICIALIZO REVISION DE COLUMNAS NUMERICAS +++")

    # Devuelve lista de columnas numericas?
    l_columnas_numericas = []

    # Por cada columna (campo especifico) de las columnas del df
    for columna in df.columns:
        print("COLUMNA: ", columna)

        valores = list(df[columna])
        nuevos_valores = []

        columna_numerica = True
        unidades = set()

        # Por cada valor de la columna
        for valor in df[columna]:

            try:
                # separo el valor segun espacios (requiero que numero y string esten separados)
                lista_palabras_valor = valor.split()
                cant_num = 0

                # por cada palabra
                for palabra in lista_palabras_valor:

                    # Si la palabra es un numero
                    try:
                        valor_numerico = float(palabra)
                        cant_num += 1

                    # Si la palabra no es un numero
                    except ValueError:
                        unidades.add(palabra)
                        pass

                # Al terminar de revisar palabras del valor, veo cuantos numeros encontre
                if cant_num > 1:
                    print("No es numerica. Valor que contiene dos o mas numeros:", valor)
                    columna_numerica = False
                    break

                elif cant_num == 0:
                    print("No es numerica. Valor que no contiene numeros:", valor)
                    columna_numerica = False
                    break

                else:
                    # print('EL VALOR {} CONTIENE NUMERO'.format(valor))
                    nuevos_valores.append(valor_numerico)
                    pass

            # Excepto si el valor es un none value
            except AttributeError:
                nuevos_valores.append(valor)
                # print("Deberia ser nan:", valor)

        if columna_numerica:
            l_columnas_numericas.append(columna_numerica)
            print("Es numerica!")
            print("Unidades:", unidades)

            # OJO TENGO QUE PONER CONDICION DE QUE TENGA MUCHOS VALORES UNICOS
            if len(df[columna].value_counts()) > len(df[columna])**0.5:

                # Si tiene una sola unidad
                if len(unidades) == 0:
                    columna_discretizada = categorize_numeric_column(columna=df[columna])
                    df[columna] = columna_discretizada

                elif len(unidades) == 1:
                    # reeemplazo columna
                    df[columna] = df[columna].replace(valores, nuevos_valores)

                    # Discretizo columna
                    columna_discretizada = categorize_numeric_column(columna=df[columna])
                    df[columna] = columna_discretizada

                # Si tiene mas de una unidad
                else:
                    print("No la puedo discretizar pues tiene mas de una unidad")

            else:
                print("La columna ya toma valores discretos, por lo que, no hace falta discretizar")

        print()

    print("Las columnas numericas son: {}".format(l_columnas_numericas))
    return df



'''