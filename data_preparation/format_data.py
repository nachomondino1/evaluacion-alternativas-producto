import pandas as pd

def check_if_numeric_column(columna):
    # Chequee si una columna de strings puede ser convertida a numerica. retorna true or false.

    for valor in columna:

        try:
            # separo el valor segun espacios (requiero que numero y string esten separados)
            value_words = valor.split()
            cant_num = 0

            # por cada palabra
            for word in value_words:

                # Si la palabra es un numero
                try:
                    float(word)
                    cant_num += 1  # suma 1 solo si la palabra es numero

                # Si la palabra no es un numero
                except ValueError:
                    pass

            # Al terminar de revisar palabras del valor, veo cuantos numeros encontre
            if cant_num > 1:
                print("'{}' es numerica pero no es posible extraer un numero pues hay mas de uno. Valor que fallo: {}".format(columna.name, valor))
                return False

            elif cant_num == 0:
                print("'{}' no es numerica. Valor que fallo: {}".format(columna.name, valor))
                return False

            else:
                # print('EL VALOR {} CONTIENE NUMERO'.format(valor))
                pass

        # Excepto si el valor es un none value
        except AttributeError:
            # print("Deberia ser nan:", valor)
            pass

    print("'{}' es numerica!".format(columna.name))
    return True

def string_column_to_numeric_column(df):
    print("+++ INICIALIZO REVISION DE COLUMNAS NUMERICAS +++")

    # unidades de memoria a GB, unidades de superficie a m2, unidades de peso a kg, unidad de longitud a metro, unidad
    # densidad de imagen a ppi
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

        # Defino variables
        valores = list(df[columna])
        nuevos_valores = []
        unidades = set()

        # Si la columna contiene strings
        if df[columna].dtype == "object":

            # y si los strings contienen valores numericos
            if check_if_numeric_column(df[columna]):

                # OBTENGO VALORES NUMERICOS POR UN LADO Y UNIDADES POR OTRO
                for value in df[columna]:

                    # Separo value en substrings
                    try:
                        value_substrings = value.split()

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

                # Imprimo aviso si hice conversion de unidades
                if len(unidades) > 1:
                    print("CUIDADO! Verificar conversiones de unidad. Unidades: {}".format(unidades))
                else:
                    print("No se hicieron cambios de conversion. Unidad: {}".format(unidades))

                # REEMPLAZO VALORES
                df[columna] = df[columna].replace(valores, nuevos_valores)
                print('Verificar cambio de dtype:', df[columna].dtype)

    return df

def precio(col_precio):
    # voy a tener que contar cuantos puntos y en base a eso multiplicar por 1000 o lo que sea.

    for i in range(len(col_precio)):
        try:
            col_precio.iloc[i] = int(col_precio.iloc[i])  # el punto lo entiende como coma
            print(col_precio.iloc[i])

        except ValueError:  # cannot convert float NaN to integer
            pass

    return col_precio


def main(): # esto lo implemento en main.py, dsp de terminar el archivo, la paso...
    # Levanto el dataframe
    df_modelos = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_modelos_celulares.xlsx')

    df = string_column_to_numeric_column(df_modelos)
    # df.to_excel('/Users/nachomondino/Desktop/df.xlsx', 'Hoja de datos', index=False)

    df['precio'] = precio(df['precio'])
    df.to_excel('/Users/nachomondino/Desktop/df2.xlsx', 'Hoja de datos', index=False)


main()
