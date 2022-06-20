# Importo librerias
import pandas as pd
import statistics as st


################################################ FUNCIONES PRINCIPALES ################################################
def correct_price_column(df_alt):
    """
    Corrige columna precio dado que el punto es entendido como una coma (Por ejemplo, 20.000 los entiende como 20)
    :param df_alt: Dataframe alternativas
    :return: Columna precio corregida
    """
    # Defino variables
    l_precios = []
    cont = 0

    # POR PRECIO
    for i in range(len(df_alt)):
        precio = df_alt.loc[i, 'precio']
        print('Precio: {}'.format(precio))
        print(type(precio))

        # DEFINO VARIABLE DE PRECIO EN FORMATO STRING Y CUENTO CANTIDAD DE PUNTOS
        str_precio = str(precio)  # precio en formato string
        cant_puntos = str_precio.count(".")  # Cantidad de puntos de precio
        miles = int("1" + ("000" * cant_puntos))

        # CORRIJO PRECIO SEGUN CANTIDAD DE PUNTOS
        # correct_precio = int(precio * miles)
        if len(l_precios) > 3:
            # l_precios.append(correct_precio) # el punto lo entiende como coma. SettingWithCopyWarning: A value is trying to be set on a copy of a slice from a DataFrame

            # Calculo media y desvio
            media, desv = st.mean(l_precios), st.stdev(l_precios)
            lim_inf, lim_sup = media - 11 * desv, media + 11 * desv  # Limites lo suficientemente flexibles
            print("\t Limite inf: {:.0f} \t Limite sup: {:.0f} ".format(lim_inf, lim_sup))

            correct_precio = int(precio * miles)

            if correct_precio < lim_inf or correct_precio > lim_sup:
                cont += 1
                correct_precio = int(precio)
                # print("\t Se guardo el precio original dado que la correcion debe estar mal"

            l_precios.append(correct_precio)
            print('\t Precio corregido: {}'.format(correct_precio))
        else:
            correct_precio = int(precio * miles)
            l_precios.append(correct_precio)
            print('\t Precio corregido: {}'.format(correct_precio))


    df_alt['precio'] = l_precios
    print("Se dejaron {} precios sin corregir".format(cont))
    print("Se corrigio el precio correctamente")
    return df_alt

def string_column_to_numeric_column(df):
    """
    Dado un dataframe, revisa cada columna de este y, aquellas que sean inherentemente numéricas pero que sean
    interpretadas como strings (pues llevan la unidad del valor numerico), son convertidas a numericas.
    :param df: Dataframe al cual hacer la conversion
    :return: Dataframe convertido
    """
    # DEFINO PASAJE DE UNIDADES
    # unidades de memoria a GB, unidades de superficie a m2, unidades de peso a kg, unidad de longitud a mm, unidad
    # densidad de imagen a ppi, unidades de carga ekectrica a mah, unidades de cant de pixeles a mpx
    # https://convertlive.com/es/c/convertir/peso (link para convertir unidades)
    d = {"kb": 1/1048576, 'mb': 1/1024, "gb": 1, "tb": 1024,  # UNIDADES DE MEMORIA (verificado)
         'mg': 0.000001, "g": 1/1000, 'lb': 0.453592, 'kg': 1, 'tn': 1000,  # UNIDADES DE PESO  (verificado)
         'mm': 1, '"': 25.4, 'pulgadas': 25.4, 'in': 25.4, 'cm': 10, 'ft': 304.8, 'm': 1000,  # UNIDADES DE LONGITUD (verificado)
         'm2': 1, 'ha': 10000,  # UNIDADES DE LONGITUD (verificado)
         'ppi': 1, 'dpi': 1,  # UNIDADES DE DENSIDAD DE IMAGEN (verificado)
         'mah': 1, 'ah': 1000, # UNIDADES DE CARGA ELECTRICA (verificado)
         'px': 1/1000000, 'mpx': 1,  # CANTIDAD DE PIXELES
         'ms': 1/3.6*10**6, 'h': 1, 'días': 24, 'semanas': 24*7,  # UNIDAD DE TIEMPO (verificado)
         'ω': 1, 'mo': 1, 'o': 1,  # UNIDAD DE IMPEDANCIA (verificado)
         'db': 1,  # UNIDAD DE RELACION ENTRE DOS VALORES DE PRESION SONORA, O TEENSION Y POTENCIA ELECTRICA (verificado)
         'hz': 1/10**(9), 'mhz': 1/1000, 'ghz': 1,  # UNIDAD DE FRECUENCIA
         'cd/m²': 1,  # UNIDAD DE BRILLO (verificado)
         'w': 1  # UNIDAD DE POTENCIA ELECTRICA (verificado)
         }

    # POR COLUMNA DEL DATAFRAME
    for columna in df.columns:
        print("{}".format(columna.upper()))

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
                                print("\t WARNING! La unidad {} no esta en el diccionario de unidades. "
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
                    print("\t AVISO! Originalmente habia mas de una unidad, por lo que, algunos valores sufrieron"
                          " una conversion de unidades. Unidades: {}".format(unidades))
                # si la columna tenia una unidad
                else:
                    # Imprimo aviso de que no hice conversion de unidades
                    print("\t Originalmente habia una sola unidad, por lo que, no se hizo conversion de unidades. Unidad: "
                          "{}".format(unidades))

                # Verificacion de columna datatype
                if (df[columna].dtype != "float64") and (df[columna].dtype != 'int64'):
                    print('\t ERROR! Algo no salio bien y no se realizo correctamente el cambio de dtype de la columna {}'.format(columna))

    return df

def yes_no_column_to_one_zero_column(df):
    """
    Convierte todas las columnas si-no de un dataframe a columnas de 1-0
    :param df: Dataframe
    :return: Dataframe pasado por parametro con columnas si-no reemplazadas por columnas 1-0
    """
    # Defino variables
    valores_buscados = {"si": 1, "sí": 1, "no": 0}  # Defino lista con los valores buscados
    columnas_si_no = []
    PORC_MIN_CARAC_DIF = 0.15

    # POR COLUMNA DEL DATAFRAME
    for columna in df.columns:

        is_carac_dif = False

        # SI LA COLUMNA CONTIENE STRINGS
        if df[columna].dtype == 'object':

            # A priori supongo que la columna es del tipo si no
            columna_si_no = True

            # POR VALOR UNICO
            for valor in df[columna].dropna().unique():  # Alternativamente, df[columna].value_counts().index

                # SI EL VALOR ES SI O NO
                if str(valor).lower() in valores_buscados.keys():
                    # CONTINUAR REVISANDO VALORES UNICOS
                    pass

                # SI EL VALOR NO ES SI O NO
                else:
                    # DEJO DE RECORRER VALORES UNICOS DE LA COLUMNA PUES NO ES DEL TIPO SI-NO
                    columna_si_no = False
                    break

            # Si LA COLUMNA ES DEL TIPO SI-NO
            if columna_si_no:
                print("La columna {} es SI-NO".format(columna))

                # SI ES UNA CARACTERISTICA DIFERNCIADORA (mayoria de "Sí" frente a "No")
                cant_no, cant_si = len(df[df[columna] == "No"]), len(df[df[columna] == "Sí"])
                try:
                    if cant_no/cant_si < PORC_MIN_CARAC_DIF:
                        is_carac_dif = True
                        print("\t Ademas, es una caracteristica diferenciadora!")
                        print("\t Cantidad de si: {}, Cantidad de No: {}".format(cant_si, cant_no))
                except ZeroDivisionError:  # si no hay valor si
                    pass

                # REEMPLAZO SI Y NO POR 1 Y 0 RESPECTIVAMENTE
                # Por valor
                for i in range(len(df[columna])):
                    # Si el valor no es nan
                    try:
                        # Reemplazo valor "Si" o "no" por 1 o 0 respectivamente
                        valor_si_no = df[columna].iloc[i].lower()
                        df.loc[i, columna] = valores_buscados[valor_si_no]

                    # Si el valor es nan
                    except:
                        # Si el atributo es una caracteristica diferenciadora
                        if is_carac_dif:
                            # Reemplazo NaN por 0
                            df.loc[i, columna] = 0
                        # Si el atributo no es una caracteristica diferenciadora
                        else:
                            # Dejo el NaN
                            pass
                columnas_si_no.append(columna)

    print("Columnas convertidas: {}".format(columnas_si_no))
    return df


################################################ FUNCIONES SECUNDARIAS ################################################
# UTILIZADA EN STRING_COLUMN_TO_NUMERIC_COLUMN
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
                print("\t Es numerica pero no es posible extraer un numero pues hay mas de uno. Valor que fallo: {}".format(valor))
                return False

            # Si no encontre numeros
            elif cant_num == 0:
                # Retorno false pues la columna no es numerica
                print("\t No es numerica. Valor que fallo: {}".format(valor))
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
    print("\t Es inherentemente numerica!")
    return True

def main(df_alt):
    print("3.1.1 Dataframe Alternativas: Corrigiendo columna precio...".center(120))
    df_alt['precio'] = correct_price_column(df_alt['precio'])  # DOCUMENTAR QUE LO HAGO PRIMERO...
    print()

    # Guardo Dataframe alternativas pues sera el que le mostrare al cliente
    df_alt_correct_price = df_alt.copy()

    print("3.1.2 Dataframe Alternativas: Convirtiendo columnas de strings con numeros a columnas numericas...".center(120))
    df_alt = string_column_to_numeric_column(df_alt)
    print()

    print("3.1.3 Dataframe Alternativas: Convirtiendo columnas si-no a columnas 1-0... ".center(120))
    df_alt = yes_no_column_to_one_zero_column(df_alt)
    print()
    return df_alt_correct_price, df_alt

# main()  # Para correr pruebas en archivo independientemente de main.py


'''
def correct_price_column(col_precio):
    """
    Corrige columna precio dado que el punto es entendido como una coma (Por ejemplo, 20.000 los entiende como 20)
    :param col_precio: Columna precio
    :return: Columna precio corregida
    """
    # Defino variables
    # l_precio_sin_nan = []
    l_precios = []
    i = 0

    # POR PRECIO
    for precio in col_precio:
        # print('Precio: {}'.format(precio))

        # DEFINO VARIABLE DE PRECIO EN FORMATO STRING Y CUENTO CANTIDAD DE PUNTOS
        str_precio = str(precio)  # precio en formato string
        cant_puntos = str_precio.count(".")  # Cantidad de puntos de precio
        miles = int("1" + ("000" * cant_puntos))

        # SI EL PRECIO NO ES NAN
        # if str_precio != 'nan':

        # CORRIJO PRECIO SEGUN CANTIDAD DE PUNTOS
        correct_precio = int(precio * miles)

        if len(l_precios) < 3:
            l_precios.append(correct_precio) # el punto lo entiende como coma. SettingWithCopyWarning: A value is trying to be set on a copy of a slice from a DataFrame

        else:
            # Calculo media y desvio
            media, desv = st.mean(l_precios), st.stdev(l_precios)
            lim_inf, lim_sup = media - 11 * desv, media + 11 * desv  # Limites lo suficientemente flexibles
            # print("\t Limite inf: {:.0f} \t Limite sup: {:.0f} ".format(lim_inf, lim_sup))

            if correct_precio < lim_inf or correct_precio > lim_sup:
                i += 1
                correct_precio = int(precio)
                # print("\t Se guardo el precio original dado que la correcion debe estar mal")

            # print('\t Precio corregido: {}'.format(correct_precio))
            l_precios.append(correct_precio) # el punto lo entiende como coma. SettingWithCopyWarning: A value is trying to be set on a copy of a slice from a DataFrame


        # SI EL PRECIO ES NAN
        #else:  # cannot convert float NaN to integer  # si elimino precios = nan, sacaria el try-except
            # NO CORRIJO NADA
            #l_precios.append(None)

    print("Se dejaron {} precios sin corregir".format(i))

    # GUARDO COLUMNA PRECIO CORREGIDA
    new_col_precio = pd.Series(l_precios)  #si o si sera dtype float64 pues el NaN es un float64
    print("Se corrigio el precio correctamente")
    return new_col_precio
'''