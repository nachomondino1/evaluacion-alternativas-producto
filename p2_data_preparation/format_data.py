import pandas as pd

def is_inherently_numerical(columna):
    """
    Determina si una columna con valores string puede ser convertida a una columna con valores numericos. Esto se podra
    solo si todos los valores strings contienen un numero, tipicamente son de la forma <numero + espacio en blanco +
    unidad>
    :param columna: Columna de valores string
    :return: True si la columna puede ser convertida a numerica, o en caso contrario, False
    """
    # POR VALOR DE LA COLUMNA
    for valor in columna:

        # SI EL VALOR NO ES NAN
        try:
            # ME FIJO CANTIDAD DE NUMEROS QUE CONTIENE
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

            # DEPENDIENDO DE CANTIDAD DE NUMEROS, SIGO ITERANDO O CORTO
            # Si encontre mas de un numero
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

        # SI EL VALOR ES NAN
        except AttributeError:
            # print("Deberia ser nan:", valor)
            pass

    # IMPRIMO MENSAJE DE QUE LA COLUMNA ES NUMERICA
    print("'{}' es inherentemente numerica!".format(columna.name))
    return True

def string_column_to_numeric_column(df):
    """
    Dado un dataframe, revisa cada columna de este y, aquellas que sean inherentemente numéricas pero que sean
    interpretadas como strings (pues llevan la unidad del valor numerico), son convertidas a numericas.
    :param df: Dataframe al cual hacer la conversion
    :return: Dataframe convertido
    """
    # DEFINO PASAJE DE UNIDADES
    # unidades de memoria a GB, unidades de superficie a m2, unidades de peso a kg, unidad de longitud a metro, unidad
    # densidad de imagen a ppi, unidades de carga ekectrica a mah, unidades de cant de pixeles a mpx
    d = {"kb": 1/1048576, 'mb': 1/1024, "gb": 1, "tb": 1024,  # UNIDADES DE MEMORIA
         "g": 1/1000, 'kg': 1, 'tn': 1000,  # UNIDADES DE PESO
         'mm': 1/1000, 'cm': 1/100, 'm': 1,  # UNIDADES DE LONGITUD
         'pulgadas': 1 , '"': 1,  # UNIDADES DE LONGITUD (sistema ingles)
         'm2': 1, 'ha': 10000,  # UNIDADES DE LONGITUD
         'ppi': 1,  # UNIDADES DE DENSIDAD DE IMAGEN
         'mah': 1, 'a': 1000, # UNIDADES DE CARGA ELECTRICA
         'mpx': 1, # CANTIDAD DE PIXELES
         }

    # POR COLUMNA DEL DATAFRAME
    for columna in df.columns:

        # SI LA COLUMNA CONTIENE STRINGS
        if df[columna].dtype == "object":

            # Y ESTOS CONTIENEN VALORES NUMERICOS
            if is_inherently_numerical(df[columna]):

                # Defino variables
                valores = list(df[columna])  # lista con valores (de forma <nro + blank space + unidad>) de la columna
                nuevos_valores = []  # lista con los nuevos valores numericos (<nro>) de la columna
                unidades = set()  # lista de unidades (<unidad>) de la columna

                # POR VALOR DE LA COLUMNA
                for valor in valores:

                    # SI EL VALOR NO ES NAN
                    try:
                        # OBTENGO SU VALOR NUMERICO
                        # Separo valor en substrings
                        valor_substrings = valor.split()  # separo en [<nro>,<unidad>]

                        # Si el valor es de la forma <numero + espacio en blanco + unidad>
                        if len(valor_substrings) == 2:

                            # Obtengo valor numerico por un lado y unidad por otro
                            valor_numerico, unidad = float(valor_substrings[0]), valor_substrings[1].lower()

                            # Hago pasaje de unidades
                            if unidad in d.keys():
                                valor_numerico *= d[unidad]
                            else:
                                print("CUIDADO! La unidad {} no esta en el diccionario de unidades. "
                                      "No se podran hacer conversiones para esta columna".format(unidad))

                            # Guardo valor numerico y unidad
                            nuevos_valores.append(valor_numerico)
                            unidades.add(unidad)

                        # Si el valor no es de la forma <numero + espacio en blanco + unidad>
                        else:
                            print("La funcion no pudo hacer la conversion pues esta preparada para convertir strings "
                                  "que sean de la forma <numero + espacio en blanco + unidad>")

                    # SI EL VALOR ES NAN
                    except AttributeError:
                        # Guardo valor 'nan'
                        nuevos_valores.append(valor)
                        # print("Deberia ser nan:", valor)

                # REEMPLAZO VALORES POR SUS VALORES NUMERICOS
                df[columna] = df[columna].replace(valores, nuevos_valores)

                # IMPRIMO WARNINGS EN CASO NECESARIO
                # si la columna tenia mas de una unidad
                if len(unidades) > 1:
                    # Imprimo aviso de que hice conversion de unidades
                    print("CUIDADO! Originalmente habia mas de una unidad, por lo que, algunos valores sufrieron"
                          " una conversion de unidades. Unidades: {}".format(unidades))
                # si la columna tenia una unidad
                else:
                    # Imprimo aviso de que no hice conversion de unidades
                    print("Originalmente habia una sola unidad, por lo que, no se hizo conversion de unidades. Unidad: "
                          "{}".format(unidades))

                # Verificacion de columna datatype
                if (df[columna].dtype != "float64") and (df[columna].dtype != 'int64'):
                    print('ATENCION! Algo no salio bien y no se realizo correctamente el cambio de dtype de la columna {}'.format(columna))

    return df

def yes_no_column_to_one_zero_column(df):
    """
    Convierte todas las columnas si-no de un dataframe a columnas de 1-0
    :param df: Dataframe
    :return: Dataframe pasado por parametro con columnas si-no reemplazadas por columnas 1-0
    """
    # Defino variables
    valores_buscados = {"si": 1, "sí": 1, "no": 0}  # Defino lista con los valores buscados

    # POR COLUMNA DEL DATAFRAME
    for columna in df.columns:

        # SI LA COLUMNA CONTIENE STRINGS
        if df[columna].dtype == 'object':

            # A priori supongo que la columna es del tipo si no
            columna_si_no = True

            # POR VALOR UNICO
            for valor in df[columna].dropna().unique():  # Alternativamente, df[columna].value_counts().index

                # SI EL VALOR ES SI O NO
                if valor.lower() in valores_buscados.keys():
                    # CONTINUAR REVISANDO VALORES UNICOS
                    pass

                # SI EL VALOR NO ES SI O NO
                else:
                    # DEJO DE RECORRER VALORES UNICOS DE LA COLUMNA PUES NO ES DEL TIPO SI-NO
                    columna_si_no = False
                    break

            # Si LA COLUMNA ES DEL TIPO SI-NO
            if columna_si_no:
                print('Columna {} es convertida a 1 y 0'.format(columna))

                # Por valor
                for i in range(len(df[columna])):
                    # Si el valor no es nan
                    try:
                        # Reemplazo valor "Si" o "no" por 1 o 0 respectivamente
                        valor_si_no = df[columna].iloc[i].lower()
                        df.loc[i, columna] = valores_buscados[valor_si_no]

                    # Si el valor es nan
                    except:
                        pass

    return df

def correct_price_column(col_precio):  #tal vez no la aplique...
    """
    Corrige columna precio dado que el punto es entendido como una coma (Por ejemplo, 20.000 los entiende como 20)
    :param col_precio: Columna precio
    :return: Columna precio corregida
    """
    # Defino variables
    l_precios = []

    # POR VALOR DE COLUMNA "PRECIO"
    for i in range(len(col_precio)):

         # SI EL VALOR NO ES NAN
        try:
            # ARREGLO EL VALOR
            # Convierto valor a string
            string_value = str(col_precio.iloc[i])  # numpy.float64 no tiene method replace()

            # Saco el punto
            correct_string_value = string_value.replace(".", "")  #siempre use espacio en blanco

            # Lo convierto a numero entero y lo reemplazo en la columna
            l_precios.append(int(correct_string_value)) # el punto lo entiende como coma. SettingWithCopyWarning: A value is trying to be set on a copy of a slice from a DataFrame

        # SI EL VALOR ES NAN
        except ValueError:  # cannot convert float NaN to integer  # si elimino precios = nan, sacaria el try-except
            # NO CORRIJO NADA
            l_precios.append(None)

    # GUARDO COLUMNA PRECIO CORREGIDA
    new_col_precio = pd.Series(l_precios)  #si o si sera dtype float64 pues el NaN es un float64
    print("Se corrigio el precio correctamente ")
    return new_col_precio

'''
# def main para hacer pruebas en este archivo independientemente de main.py
def main():
    # Levanto el dataframe
    df_modelos = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/df_modelos_celulares.xlsx')

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
    # df_modelos.to_excel('/Users/nachomondino/Desktop/df_modelos_formateado.xlsx', 'Hoja de datos', index=False)
    df_modelos.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/df_modelos_formateado.xlsx', 'Hoja de datos', index=False)


main()
'''
