def string_column_to_numeric_column(df):
    """
    Dado un dataframe, revisa cada columna de este y, aquellas que sean inherentemente numéricas (contienen valores
    numericos pero son interpretadas como string por llevar la unidad), son convertidas a numericas.
    :param df: Dataframe (cualquiera sea)
    :return: Dataframe pasado como parametro con columnas string inherentemente numericas convertidas a numericas
    """
    # DEFINO DICCIONARIO DE PASAJE DE UNIDADES # https://convertlive.com/es/c/convertir/peso (link para convertir unidades)
    d = {"kb": 1/1048576, 'mb': 1/1024, "gb": 1, "tb": 1024,  # UNIDADES DE MEMORIA (TO GB) (verificado)
         'oz': 0.0283495,'mg': 0.000001, "g": 1/1000, 'lb': 0.453592, 'kg': 1, 'tn': 1000,  # UNIDADES DE PESO (TO KG) (verificado)
         'mm': 1, '"': 25.4, 'pulgadas': 25.4, 'in': 25.4, 'cm': 10, 'ft': 304.8, 'm': 1000,  # UNIDADES DE LONGITUD (TO MM) (verificado)
         'm2': 1, 'ha': 10000,  # UNIDADES DE SUPERFICIE (TO M2) (verificado)
         'ppi': 1, 'dpi': 1,  # UNIDADES DE DENSIDAD DE IMAGEN (TO PPI) (verificado)
         'mah': 1, 'ah': 1000, # UNIDADES DE CARGA ELECTRICA (TO mAh) (verificado)
         'px': 1/1000000, 'mpx': 1,  # CANTIDAD DE PIXELES (TO mpx)
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

            # Defino variables
            l_unidades = set()  # Lista de las distintas unidades de la columna
            is_num_col = False

            # POR VALOR (evito NaN)
            for i in df.dropna(subset=columna).index:   # Evito valor=NaN para evitar try-except o if-else (total los NaN se quedan)

                # SI LA COLUMNA ES INHERENTEMENTE NUMERICA
                try:
                    # OBTENGO VALOR NUMERICO POR UN LADO Y UNIDAD POR OTRO
                    numero, unidad = df.loc[i, columna].split()

                    # REEMPLAZO VALOR STRING POR NUMERO
                    df.loc[i, columna] = float(numero) * d[unidad.lower()]
                    l_unidades.add(unidad)
                    is_num_col = True

                # SI LA COLUMNA NO ES INHERENTEMENTE NUMERICA
                except:
                    print("\t La columna no es inherentemente numerica. Valor que fallo: {}".format(df.loc[i, columna]))
                    break

            # SI LA COLUMNA ES INHERENTEMENTE NUMERICA
            if is_num_col:

                # Imprimo aviso de que la columna es inherentemene numerica
                print("\t La columna es inherentemente numerica!")

                # Imprimo aviso por cantidad de unidades de columna
                print("\t Unidades de la columna: {}".format(l_unidades))

                # Convierto dtype de columna a numerica
                try:
                    df = df.astype({columna: 'float64'})
                except:
                    print('\t ERROR! Algo no salio bien y no se realizo correctamente el cambio de dtype de la columna {}'.format(columna))
        else:
            print("\t La columna ya es numerica!")
    return df

def yes_no_column_to_one_zero_column(df):
    """
    Convierte todas las columnas si-no de un dataframe a columnas de 1-0
    :param df: Dataframe (cualquiera sea)
    :return: Dataframe pasado por parametro con columnas si-no reemplazadas por columnas 1-0
    """
    # Defino variables
    PORC_MIN_CARAC_DIF = 0.15  # Porcentaje minimo para definir si es una caracteristica diferenciadora o no

    # POR COLUMNA
    for columna in df.columns:
        print("{}".format(columna.upper()))

        # SI LA COLUMNA ES DEL TIPO SI-NO
        if 'Sí' in df[columna].unique() and 'No' in df[columna].unique():  # FutureWarning: elementwise comparison failed; returning scalar instead, but in the future will perform elementwise comparison
            print("\t LA COLUMNA ES DEL TIPO SI-NO!")

            # Defino variables
            df_si = df[df[columna] == 'Sí']  # Alternativas con columnas que toma valor "Sí"
            df_no = df[df[columna] == 'No']  # Alternativas con columnas que toma valor "No"
            df_nan = df[df[columna].isna()]  # Alternativas con columnas que toma valor "NaN"

            # REEMPLAZO VALOR "Sí" POR 1 Y "No' POR 0
            df.loc[df_si.index, columna] = 1
            df.loc[df_no.index, columna] = 0

            # SI ES UNA CARACTERISTICA DIFERENCIADORA
            if PORC_MIN_CARAC_DIF * len(df_si) > len(df_no):
                # REEMPLAZO VALOR 'nan' POR 0
                df.loc[df_nan.index, columna] = 0  # Asi valor 0 tendra mas opis (si no tendra un sent poco robusto)
                print("\t Ademas es una caracteristica diferenciadora!")

        # SI LA COLUMNA NO ES DEL TIPO SI-NO
        else:
            print("\t La columna no es del tipo Si-No")
    return df

