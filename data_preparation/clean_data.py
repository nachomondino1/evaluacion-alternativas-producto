# Importo librerias
import pandas as pd


def delete_repeated_rows(df):
    """
     La funcion debe obteneer los indices de las filas a borrar

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

def categorize_numeric_columns(df): # esta funcion deberia recibir una columna y discretizarla (teniendo en cuentas las unidades)

    # ver si agrego lista negra = [id_pub]
    # Por columna del dataframe
    for columna in df.columns:

        # Si la columna es numerica
        if (df[columna].dtype == 'float64') or (df[columna].dtype == 'int64'):

            # y si tiene muchos valores (no es discreta)
            if len(df[columna].value_counts()) > 1.5 * len(df[columna])**0.5:

                print("La columna {} sera categorizada".format(columna))

                valores = list(df[columna])
                valores_limite_max = []
                valor_min = min(valores)

                num_clases = round(len(valores)**0.5)  # raiz cuadrada de la cantidad de datos
                rango = max(valores) - min(valores)  # valor maximo - valor minimo
                amplitud_clase = rango / num_clases

                # CREO INTERVALOS DE CADA CLASE
                for i in range(num_clases):
                    valor_min_intervalo = round(valor_min + amplitud_clase * i, 2)
                    valor_max_intervalo = round(valor_min + amplitud_clase * (i+1), 2)
                    valor_med_intervalo = round((valor_max_intervalo + valor_min_intervalo) / 2, 2)

                    valores_limite_max.append(valor_max_intervalo)
                    print("Clase Nº{}: Valor min = {} ; Valor med = {} ; Valor max = {}".format(i, valor_min_intervalo, valor_med_intervalo, valor_max_intervalo))

                # REEMPLAZO VALORES POR LA MEDIA DE LA CLASE
                for i in range(len(df[columna])):
                    for valor_limite in valores_limite_max:
                        if df[columna].iloc[i] < valor_limite:
                            df[columna].iloc[i] = round(valor_limite - (amplitud_clase / 2), 1)
                            # columna = columna.replace(valor, valor_limite - int(amplitud_clase / 2)) # COMO VERGA SABE EL INDEX? No se
                            break

            else:
                print("La columna '{}' es numerica pero toma valores discretos".format(columna))
        else:
            print("La columna '{}' no es numerica!".format(columna))

    return df

def delete_attr_x_values(df):

    df_copia = df.copy()

    cant_atributos = len(df.columns)
    cant_valores_posibles = len(df)

    # Defino parametros:
    porc_pocos_val = 0.2
    porc_muchos_val = 0.75

    # Por cada atributo
    for atributo in df.columns:

        # Obtengo lista de frecuencia de sus valores
        val_col = list(df[atributo].value_counts())
        # print("Campo al cual ver valores unicos:", atributo)
        # print(val_col)

        # Si el atributo tiene un unico valor para todos los modelos
        if len(val_col) < 3:

            # Recorro cada frecuencia
            for valor in val_col:

                # si alguna frecuencia es predominante
                if valor > 0.9 * sum(val_col):

                    # Elimino el atributo
                    print("Elimino atributo {} por tener muy pocos valores y uno muy predominante".format(atributo))
                    df_copia = df_copia.drop([atributo], axis=1)

        # Si el atributo tiene muchos valores
        elif len(val_col) > porc_muchos_val * cant_valores_posibles:

            # Intento convertir la variable a numerica
            try:
                # Pruebo con el primer elemento
                int(df[atributo][0])
                print("Entendio el atributo {} como numero".format(atributo))


            except:

                # Si el valor mas frecuente tiene una frecuencia aceptable
                if val_col[0] > 0.1 * cant_valores_posibles:
                    pass

                else:
                    # Elimino el atributo
                    print("Elimino atributo {} por tener muchos valores y de frecuencia baja".format(atributo))
                    df_copia = df_copia.drop([atributo], axis=1)

        else:
            pass

    print(df_copia)
    return df_copia


def main(): # esto lo implemento en main.py, dsp de terminar el archivo, la paso...
    # Levanto el dataframe
    df_modelos = pd.read_excel('/Users/nachomondino/Desktop/df.xlsx')
    df_opiniones = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_opiniones_celulares.xlsx')

    # 1) ELIMINO NONE VALUES
    df_opiniones.dropna()  # borra las pocas filas que no tienen title

    # 2) ELIMINO FILAS REPETIDAS --> ojo que tiene que ser sin id...
    df_opiniones = df_opiniones.drop(delete_repeated_rows(df_opiniones['content']))  # elimino duplicados teniendo en cuenta solo la columna content que es la que contiene opiniones propiamente
    # df_modelos = df_modelos.drop(delete_repeated_rows(df_modelos.iloc[:, 2:]))  # elimino duplicados sin tener en cuenta las columna de id y precio, DECIDI NO HACERLO
    print(df_opiniones.shape)

    # 3) CATEGORIZO VARIABLES NUMERICAS
    # categorize_numeric()
    df_modelos.iloc[:, 1:] = categorize_numeric_columns(df_modelos.iloc[:, 1:])  # categorizo columnas numericas con valores continuos, no le paso columna id pues la categorizaria.
    df_modelos.to_excel('/Users/nachomondino/Desktop/df_categorizado.xlsx', 'Hoja de datos', index=False)

    # 4) ELIMINO CAMPOS ESPECIFICOS SEGUN CANTIDAD DE VALORES Y CANTIDAD DE OPINIONES POR VALOR
    # delete_attr_x_values(df_modelos.iloc[:, 3:])
    # df_modelos.to_excel('/Users/nachomondino/Desktop/df_modelos_cleaned.xlsx', 'Hoja de datos', index=False)

    # 5) PREPARACION DEL TEXTO


main()







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