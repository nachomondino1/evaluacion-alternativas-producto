import pandas as pd

def check_if_numeric_column(columna):
    """
    Determina si una columna con valores string puede ser convertida a una columna con valores numericos. Esto se podra
    solo si todos los valores strings contienen un numero, tipicamente son de la forma <numero + espacio en blanco +
    unidad>
    :param columna: Columna de valores string
    :return: True si la columna puede ser convertida a numerica, o bien, False en caso contrario.
    """

    # Por valor de la columna
    for valor in columna:

        try:
            # Intento separar el valor, por un lado, la parte numerica y por otro los strings
            value_words = valor.split()
            cant_num = 0

            # Por cada palabra del valor
            for word in value_words:

                # Si la palabra es un numero
                try:
                    float(word)
                    cant_num += 1  # suma 1 solo si la palabra es numero

                # Si la palabra no es un numero
                except ValueError:
                    pass

            # Al terminar de revisar palabras de un valor, veo cuantos numeros encontre
            # Si encontre un numero
            if cant_num > 1:
                # Retorno false pues la columna es numerica pero no es de la forma <nro + blank space + unidad>
                print("'{}' es numerica pero no es posible extraer un numero pues hay mas de uno. Valor que fallo: {}".format(columna.name, valor))
                return False

            # Si no encontre numeros
            elif cant_num == 0:
                # Retorno false pues la columna no es numerica
                print("'{}' no es numerica. Valor que fallo: {}".format(columna.name, valor))
                return False

            # Si encontre un numero
            else:
                # print('EL VALOR {} CONTIENE NUMERO'.format(valor))
                # Sigo recorriendo valores para verificar que todos contengan un numero
                pass

        # Excepto si el valor es un none value
        except AttributeError:
            # print("Deberia ser nan:", valor)
            pass

    print("'{}' es numerica!".format(columna.name))
    return True

def string_column_to_numeric_column(df):
    """
    Dado un dataframe, convierte sus columnas con valores string que guardan numeros en valores numericos para poder
    hacer moperaciones matematicas.
    :param df: Dataframe al cual hacer la conversion
    :return: Dataframe convertido
    """
    # unidades de memoria a GB, unidades de superficie a m2, unidades de peso a kg, unidad de longitud a metro, unidad
    # densidad de imagen a ppi, unidades de carga ekectrica a mah, unidades de cant de pixeles a mpx
    d = {"kb": 1/1048576, 'mb': 1/1024, "gb": 1, "tb": 1024,  # UNIDADES DE MEMORIA
         "g": 1/1000, 'kg': 1, 'tn': 1000,  # UNIDADES DE PESO
         'mm': 1/1000, 'cm': 1/100, 'm': 1,  # UNIDADES DE LONGITUD
         'm2': 1, 'ha': 10000,  # UNIDADES DE LONGITUD
         'ppi': 1,  # UNIDADES DE DENSIDAD DE IMAGEN
         'mah': 1, 'a': 1000, # UNIDADES DE CARGA ELECTRICA
         'mpx': 1, # CANTIDAD DE PIXELES
         }

    # Por cada columna de las columnas del df
    for columna in df.columns:

        # Si la columna contiene strings
        if df[columna].dtype == "object":

            # y si los strings contienen valores numericos
            if check_if_numeric_column(df[columna]):

                # Defino variables
                valores = list(df[columna])  # lista con valores (de forma <nro + blank space + unidad>) de la columna
                nuevos_valores = []  # lista con los nuevos valores numericos (<nro>) de la columna
                unidades = set()  # lista de unidades (<unidad>) de la columna

                # OBTENGO VALORES NUMERICOS POR UN LADO Y UNIDADES POR OTRO
                for value in df[columna]:

                    # Separo value en substrings
                    try:
                        value_substrings = value.split()  # separo en [<nro>,<unidad>]

                        # Si el valor es <numero + espacio en blanco + unidad>
                        if len(value_substrings) == 2:

                            # obtengo valor numerico por un lado y unidad por otro
                            valor_numerico, unidad = float(value_substrings[0]), value_substrings[1].lower()

                            # si hay que hacer cambio de unidad
                            if unidad in d.keys():
                                valor_numerico *= d[unidad]
                            else:
                                print("CUIDADO! La unidad {} no esta en el diccionario de unidades. "
                                      "No se podran hacer conversiones para esta columna".format(unidad))

                            # Guardo valor numerico y unidad
                            nuevos_valores.append(valor_numerico)
                            unidades.add(unidad)

                        else:
                            print("La funcion no pudo hacer la conversion pues esta preparada para convertir strings "
                                  "que sean de la forma <numero + espacio en blanco + unidad>")

                    # Excepto si el valor es 'nan'
                    except AttributeError:
                        # Guardo valor 'nan'
                        nuevos_valores.append(value)
                        # print("Deberia ser nan:", valor)

                # Imprimo aviso si hice o no conversion de unidades
                if len(unidades) > 1:
                    print("CUIDADO! Verificar conversiones de unidad. Unidades: {}".format(unidades))
                else:
                    print("No se hicieron cambios de conversion. Unidad: {}".format(unidades))

                # REEMPLAZO VALORES POR VALORES NUMERICOS
                df[columna] = df[columna].replace(valores, nuevos_valores)
                print('Verificar cambio de dtype:', df[columna].dtype)

    return df

def yes_no_column_to_ones_ceros_column(df):
    # Defino lista con los valores buscados
    valores_buscados = {"si": 1, "sí": 1, "no": 0}

    # POR COLUMNA DE LAS COLUMNAS DEL DATAFRAME
    for columna in df.columns:

        # SI LA COLUMNA ES DEE STRINGS
        if df[columna].dtype == 'object':

            # OBTENGO VALORES UNICOS DE LA COLUMNA
            valores_unicos = df[columna].value_counts()  # el nan no es considerado un valor. Los valores son el index

            # A priori supongo que la columna es del tipo si no
            columna_si_no = True

            # POR CADA VALOR UNICO
            for valor in valores_unicos.index:

                # SI EL VALOR ES UNO DE LOS VALORES BUSCADOS
                if valor.lower() in valores_buscados.keys():
                    # CONTINUAR REVISANDO VALORES
                    pass

                # NO ES UN VALOR DE LOS BUSCADOS
                else:
                    # DEJO DE RECORRER VALORES UNICOS DE LA COLUMNA PUES NO ES DEL TIPO "SI" O "NO"
                    columna_si_no = False
                    break

            if columna_si_no:
                print('Columna {} es convertida a 1 y 0'.format(columna))

                for i in range(len(df[columna])):

                    try:
                        # Reemplazo valor "Si" o "no" por 1 o 0 respectivamente
                        valor_si_no = df[columna].iloc[i].lower()
                        df[columna].iloc[i] = valores_buscados[valor_si_no]  # SettingWithCopyWarning: A value is trying to be set on a copy of a slice from a DataFrame

                    # El valor es un nan
                    except:
                        pass

    return df

def correct_price_column(col_precio):
    """
    Corrige columna precio dado que el punto es entendido como una coma (Por ejemplo, 20.000 los entiende como 20)
    :param col_precio: Columna precio
    :return: Columna precio corregida
    """

    # Por cada valor de columna precio
    for i in range(len(col_precio)):

         # Intento corregir el valor
        try:
            # Convierto valor a string
            string_value = str(col_precio.iloc[i])  # numpy.float64 no tiene method replace()

            # Saco el punto
            correct_string_value = string_value.replace(".", "")

            # Lo convierto a numero entero y lo reemplazo en la columna
            col_precio.iloc[i] = int(correct_string_value)  # el punto lo entiende como coma. SettingWithCopyWarning: A value is trying to be set on a copy of a slice from a DataFrame

        # Excepto que es nan
        except ValueError:  # cannot convert float NaN to integer

            # No corrigo nada
            pass

    print("Se corrigio el precio correctamente ")
    return col_precio



'''
def main para hacer pruebas en este archivo independientemente de main.py
def main():
    # Levanto el dataframe
    df_modelos = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_modelos_celulares.xlsx')

    # 1) NUMERIC COLUMNS NOT IDENTIFIED
    print("+++ (1) CONVERSION DE COLUMNAS STRING CON NUMEROS A COLUMNAS NUMERICAS +++")
    df_modelos = string_column_to_numeric_column(df_modelos)
    # df_modelos.to_excel('/Users/nachomondino/Desktop/df1.xlsx', 'Hoja de datos', index=False)

    # 2) "YES" AND "NO" COLUMNS TO 1 AND 0 COLUMNS
    print("+++ (2) COLUMNAS SI-NO A COLUMNA 1-0 +++")
    df_modelos = yes_no_column_to_ones_ceros_column(df_modelos)
    # df_modelos.to_excel('/Users/nachomondino/Desktop/df2.xlsx', 'Hoja de datos', index=False)

    # 3) CORRECTION OF PRICE COLUMN
    print("+++ (3) CORRECCION COLUMNA PRECIO +++")
    df_modelos['precio'] = correct_price_column(df_modelos['precio'])
    df_modelos.to_excel('/Users/nachomondino/Desktop/df_modelos_formateado.xlsx', 'Hoja de datos', index=False)


main()

'''