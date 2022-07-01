# Importo librerias
import pandas as pd
from p2_data_preparation.utils import preparacion_texto
import statistics as st


################################################ FUNCIONES PRINCIPALES ################################################
def delete_date_of_issue_from_opinion(df_opiniones):
    """
    Elimina fecha de emision de cada opinion
    :param df_opiniones: Dataframe. Unidad de analisis: opinion del producto. Columnas: id_alternativa y opinion.
    :return: Dataframe. Unidad de analisis: opinion del producto. Columnas: id_alternativa y opinion. Filas: misma
    cantidad pero sin fecha de emision en valores de columna opinion.
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

    print("Se ha quitado con exito la fecha de emision de cada opinion \n")
    return df_opiniones

def clean_opinions(df_opiniones):  # creo que la voy a sacar y desde el main llamo a cada funcion directo de preparacion_texto.py
    """
    Procesa opiniones: convierto a miniscula, elimino acentos, elimino puntuacion, tokenizo y elimino palabras vacias
    :param df_opiniones: Dataframe. Unidad de analisis: opinion del producto. Columnas: id_alternativa y opinion.
    :return: Dataframe. Unidad de analisis: opinion del producto. Columnas: id_alternativa y opinion. Filas: misma
    cantidad pero valores de columna opinion en minuscula, sin acentos ni puntuacion y como lista de palabras.
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
    print(df_opiniones.head(5), '\n')
    return df_opiniones

def drop_alternatives_with_most_na(df_alt, df_opi):
    """
    Elimino alternativas con mas muchos NaN values y sin opiniones.
    :param df_alt: Dataframe. Unidad de analisis: alternativa del producto. Columnas: id_alternativa, precio y campos
    especificos segun el producto.
    :param df_opi: Dataframe. Unidad de analisis: opinion del producto. Columnas: id_alternativa y opinion
    :return: Dataframe. Unidad de analisis: alternativa del producto. Columnas: id_alternativa, precio y campos
    especificos segun el producto. Sin alternativas con mas del x% de NaN y sin opiniones.
    """
    # Defino variables
    N_MAX_NAN = 0.5 * len(df_alt.columns)  # Cuanto mayor es, mas tolerable soy.
    ids_with_opi = df_opi['id_alternativa'].unique()
    n_alts_inicial = len(df_alt)

    # POR ALTERNATIVA
    for i in range(len(df_alt)):

        # Defino variables
        id_alt = df_alt.loc[i, 'id_alternativa']  # Id de alternativa
        n_nan = sum(df_alt.loc[i].isna())

        # SI NO TIENE OPINIONES ASOCIADAS Y TIENE MAS DEL X% DE NAN
        if id_alt not in ids_with_opi and n_nan > N_MAX_NAN:

            # Elimino alternativa
            df_alt = df_alt.drop([i])

    # Imprimo resultados
    print("Cantidad de alternativas borradas: {}".format(n_alts_inicial - len(df_alt)))
    print("Cantidad de alterantivas restantes: {}\n".format(df_alt.shape[0]))

    # Reinicio indice de alternativas
    df_alt = df_alt.reset_index(drop=True)  # el dropna me borra una fila y los indices quedan mal...
    return df_alt

def drop_alternatives_with_wrong_values(df_alt, df_alt_to_client, df_opi):
    """
    Elimina alternativas que tengan al menos un valor cargado incorrectamente en la publicacion de Mercado Libre. Solo
    tiene en cuenta valores de atributos numericos.
    :param df_alt: Dataframe. Unidad de analisis: alternativa del producto.  Columnas: id_alternativa, precio y campos
    especificos segun el producto. Filas: Alternativas que seran tenidas en cuenta en el analisis
    :param df_alt_to_client: Dataframe. Unidad de analisis: alternativa del producto. Columnas: id_alternativa, precio
    y camposespecificos segun el producto. Filas: Alternativas que seran mostradas al cliente
    :param df_opi: Dataframe. Unidad de analisis: opinion del producto. Columnas: id_alternativa y opinion.
    :return: Dataframes pasados como parametro (cuya unidad de analisis es la alternativa) sin alternativas con valores
    erroneos
    """
    # DEFINO VARIABLE
    l_idx_alt_a_borrar = set()  # set de indices de alternativas a borrar (una alternativa puede tener mas de un outlier)
    FACTOR_HOLGURA = 1.3  # Evitar que las que son efectivamente discretas pero que tienen valores unicos infrecuentes pasen como continuas

    # POR COLUMNA DEL DATAFRAME
    for columna in df_alt.columns[1:]:  #excluyo id

        # Defino variables
        valores = df_alt[columna].dropna()
        l_unique_values = valores.unique()
        corte = FACTOR_HOLGURA * len(df_alt[columna].dropna()) ** 0.5
        print(columna.upper())

        # SI LA COLUMNA ES NUMERICA Y TIENE MAS DE DOS VALORES UNICOS (evita columnas 1-0)
        if df_alt[columna].dtype in ['float64', 'int64'] and len(l_unique_values) > 2:

            # SI LA VARIABLE ES DISCRETA
            if len(l_unique_values) < corte:
                # OBTENGO MEDIA Y DESVIO
                media, desv = st.mean(valores), st.stdev(valores)
                lim_inf, lim_sup = media - 3 * desv, media + 3 * desv
                lim_inf_mala_carga, lim_sup_mala_carga = media - 6 * desv, media + 6 * desv

                # Si el desvio es 'estirado' por un valor mal cargado
                if desv > 2 * media:
                    # Recalculo limites siendo mas estricto
                    lim_inf, lim_sup = media - 0.7 * desv, media + 0.7 * desv
                    lim_inf_mala_carga, lim_sup_mala_carga = media - 1 * desv, media + 1 * desv
                    print("\t WARNING! Reduzco los limites pues el desvio es muchisimo mayor a la media, es posible que "
                          "haya sido 'estirado' por algun valor mal cargado.")
                print("\t Media: {:.1f} \t Desvio: {:.1f}".format(media, desv))
                print("\t LIMITES: \t outlier_inf = {:.1f}  outlier_sup = {:.1f} \t mal_cargado_inf = {:.1f} mal_cargado_sup = {:.1f}".format(lim_inf, lim_sup, lim_inf_mala_carga, lim_sup_mala_carga))

            # SI LA VARIABLE ES CONTINUA
            else:
                # OBTENGO RANGO INTERCUARTILICO
                l_values_sort = sorted(list(df_alt[columna].dropna()))  # sino los valores nan se acumulan en extremo de lista...
                q1, q3 = l_values_sort[int(0.25 * len(l_values_sort))], l_values_sort[int(0.75 * len(l_values_sort))]  # percentiles 25 y 75
                IQR = q3 - q1  # Rango intercuartil (resta de percentil 75 y 25)
                lim_inf, lim_sup = q1 - 1.5 * IQR, q3 + 1.5 * IQR  # Limites superior e inferior. Fuera son outliers.
                lim_inf_mala_carga, lim_sup_mala_carga = q1 - 5 * IQR, q3 + 5 * IQR  # 10 no, es mucho
                print("\t Q1: {:.1f} \t Q3: {:.1f} \t IQR: {:.1f}".format(q1, q3, IQR))
                print("\t LIMITES: \t outlier_inf = {:.1f}  outlier_sup = {:.1f} \t mal_cargado_inf = {:.1f} mal_cargado_sup = {:.1f}".format(lim_inf, lim_sup, lim_inf_mala_carga, lim_sup_mala_carga))

            # Defino variables
            l_val_erroneos = [valor for valor in l_unique_values if valor > lim_sup or valor < lim_inf]

            # POR VALOR ERRONEO
            for valor in l_val_erroneos:

                # Defino variables
                l_idxs = [i for i in range(len(df_alt[columna])) if df_alt.loc[i, columna] == valor]  # Indices de alternativas cuyo atributo toma el valor outlier # no es el mismo index que en df_alt_to_client
                print("\tValor: {} \tFrecuencia: {}.".format(valor, len(l_idxs)), end=" ")

                # SI EL VALOR ERRONEO ES UN VALOR "MAL CARGADO"
                if valor > lim_sup_mala_carga or valor < lim_inf_mala_carga:
                    print("El valor {} es un valor MAL CARGADO".format(valor))

                    # POR CADA ALTERNATIVA CUYO VALOR ES UN DATO MAL CARGADO (MAL CARGADO POR EL VENDEDOR)
                    for idx in l_idxs:
                        # print("\t\t Alternativa Nº{}: ".format(i + 1), end=" ")
                        id_alt = df_alt.loc[idx, 'id_alternativa']  # Id de alternativa

                        # SI LA ALTERNATIVA A LA QUE PERTENECE EL VALOR TIENE OPINIONES
                        if id_alt in list(df_opi['id_alternativa'].unique()):

                            # REEMPLAZO OUTLIER POR NAN
                            df_alt.loc[idx, columna] = None
                            print("\t\t Dado que la alternativa tiene opiniones asociadas, reemplazo el valor por NaN")

                        # SI LA ALTERNATIVA A LA QUE PERTENECE EL VALOR NO TIENE OPINIONES
                        else:
                            # GUARDO INDICE ALTERNATIVA QUE TIENE VALOR MAL CARGADO
                            l_idx_alt_a_borrar.add(idx)
                            print("\t\t Dado que la alternativa no tiene opiniones asociadas, elimino la alternativa")

                        # ELIMINO ALTERNATIVA DE DF_ALT_TO_CLIENT (VALOR MAL CARGADO
                        # eliminar directamente segun ids_to_client o ids pues son iguales
                        try:
                            idx_client = df_alt_to_client[df_alt_to_client['id_alternativa'] == id_alt].index[0]
                            df_alt_to_client = df_alt_to_client.drop([idx_client], axis=0)
                            print("\t\t Elimino alternativa del dataframe que le mostrare al cliente. No le puedo mostrar "
                              "una alternativa con este valor mal cargado")
                        except:  # Si ya borre la alternativa por un valor erroneo en otra columna
                            pass

                # SI EL VALOR ERRONEO ES UN VALOR "OUTLIER" (ESTA BIEN CARGADO)
                else:
                    print("Es un valor OUTLIER")

                    # POR CADA ALTERNATIVA CUYO VALOR ES UN OUTLIER
                    for idx in l_idxs:

                        # INDEPENDIENTEMENTE DE SI TIENE OPINIONES, REEMPLAZO OUTLIER POR NAN
                        df_alt.loc[idx, columna] = None
                        # print("\t\t Alternativa Nº{}: ".format( + 1), end=" ")
                        print("\t\t Dado que la alternativa no tiene un valor mal cargado, reemplazo el outlier por NaN")

        '''
        else:  # columnas no numericas, PODRIA IMPLEMENTAR ELIMINACION DE VALORES ERRONEOS... PRIMERRO DECIDIR SI CONVIENE, QUE GANO? QUE PIERDO?

            l_unique_values = df_alt[columna].dropna().unique()

            # POR VALOR UNICO DE LA COLUMNA
            for valor in l_unique_values:  # sortear de mayor a menor... Al primer mayor que no borra por frec, deja el resto que esta por debajo...

                # Defino variables
                frec_val = len(df_alt[df_alt[columna] == valor])

                if frec_val == 1:

                    print("\tValor: {} \tFrecuencia: {}.".format(valor, frec_val), end=" ")
                    idxs = [i for i in range(len(df_alt[columna])) if df_alt.loc[i, columna] == valor]
                    # ids = [df_alt.loc[i, "id_alternativa"] for i in range(len(df_alt[columna])) if df_alt.loc[i, columna] == valor]

                    # POR CADA ALTERNATIVA CUYO VALOR ES UN OUTLIER
                    for i in range(frec_val):
                        idx = idxs[i]
                        # id = ids[i]
                        print("\t\t Alternativa Nº{}: ".format(i + 1), end=" ")

                        # REEMPLAZO OUTLIER POR NAN
                        df_alt.loc[idx, columna] = None
                        print("Dado que la alternativa tiene opiniones asociadas, reemplazo el outlier por NaN")
        '''

    # BORRO ALTERNATIVAS QUE TIENEN VALORES MAL CARGADOS
    for idx in l_idx_alt_a_borrar:
        df_alt = df_alt.drop([idx], axis=0)

    # Reinicio indices
    df_alt = df_alt.reset_index(drop=True)  # el dropna me borra una fila y los indices quedan mal...
    df_alt_to_client = df_alt_to_client.reset_index(drop=True)

    print("Cantidad de alternativas eliminadas: {}".format(len(l_idx_alt_a_borrar)))
    print("Cantidad de alterantivas restantes: {}\n".format(df_alt.shape[0]))
    return df_alt, df_alt_to_client

def categorize_numeric_columns(df):
    """
    Dado un dataframe, categoriza sus columnas numericas (las no numericas no porque al no haber una "distancia" entre
    strings, no puedo determinar cual se asemeja con cual) continuas (las discretas no pues ya estan categorizadas)
    :param df: Dataframe. Unidad de analisis: cualquiera. Columnas: cualquiera.
    :return: Dataframe. Unidad de analisis: cualquiera. Columnas: cualquiera. Todas sus columnas numericas continuas
    ahora son numericas discretas
    """
    # Defino variables
    # POR COLUMNA DEL DATAFRAME
    for columna in df.columns:
        print(columna.upper().center(120))

        # SI LA COLUMNA ES NUMERICA
        if (df[columna].dtype == 'float64') or (df[columna].dtype == 'int64'):

            # Defino variables
            n_clases = len(df[columna].dropna().unique())  # cant_valores_unicos = len(df[columna].value_counts())  # n_clases = len(df[columna].value_counts().loc[lambda x: x > 3])  # cant de valores unicos filtrando infrecuentes  --> no es aplicable pues no categoriza ni 'precio' pues no hay dos alt con un mismo precio
            n_clases_opt = int(len(df[columna].dropna()) ** 0.5)  # cant clases ideales = raiz(nro datos)  # borror nan de posibles valores pues son mentira

            # SI LA COLUMNA ES CONTINUA (toma muchos valores distintos, especificamente, mas que la cantidad optima)
            if n_clases > n_clases_opt:  # if n_clases > FACTOR_HOLGURA * n_clases_opt:  # Aqui se podria aplicar "factor de holgura"
                print("Sera categorizada pues tiene {} valores unicos cuando, en este caso, lo recomendado es {}.".format(n_clases, n_clases_opt))

                # OBTENGO VALORES MEDIOS Y MAXIMOS DE CADA CLASE
                d = create_classes(valores=df[columna], cant_clases=n_clases_opt)  # key=valor_max y val=valor_med

                # REEMPLAZO VALORES CONTINUOS POR LA MEDIA DE LA CLASE A LA QUE PERTENECE
                # Por valor del atributo
                for i in range(len(df[columna])):

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
                print("Es numerica pero discreta pues toma {} valores!".format(n_clases))

        # SI LA COLUMNA NO ES NUMERICA
        else:
            # imprimo mensaje
            print("No es numerica!")
    return df

def delete_attr_x_values(df):
    """
    Elimino columnas del dataframe que toman un solo valor constante
    :param df: Dataframe. Unidad de analisis: cualquiera. Columnas: cualquiera
    :return: Dataframe. Unidad de analisis: cualquiera. Columnas: Solo columnas que tomen mas de un solo valor
    """
    # Defino variables
    col_eliminadas = []

    # POR COLUMNA DEL DATAFRAME
    for columna in df.columns:
        print(columna.upper().center(120))

        # Obtengo lista de frecuencia de sus valores
        n_unique_values = len(list(df[columna].dropna().unique()))

        # SI LA COLUMNA ES CONSTANTE (TOMA UN UNICO VALOR)
        if n_unique_values == 1:  #cuando hay muchas alt al menos hay 1 con valor distinto..

            # Elimino atributo
            df = df.drop([columna], axis=1)
            col_eliminadas.append(columna)
            print("Elimino la columna por tomar 1 solo valor")

    print("COLUMNAS ELIMINADAS: ", col_eliminadas)
    return df

################################################ FUNCIONES SECUNDARIAS ################################################
# UTILIZADAS EN CATEGORIZE_NUMERIC_COLUMN()
def create_classes(valores, cant_clases):
    """
    Genera clases o categoria para un conjunto de valores numericos continuos
    :param valores: Lista de valores de una columna numerica continua
    :param cant_clases: Cantidad de clases a generar
    :return: Diccionario con valores maximos de cada clase como key y con valores medios de cada clase como value
    """
    # DEFINO VARIABLES
    # respecto de valores
    valores_unicos = sorted(valores.dropna().unique())
    valor_min, valor_max = min(valores_unicos), max(valores_unicos)
    print("Valores unicos: ", valores_unicos)
    # respecto de clases
    rango = valor_max - valor_min
    amplitud_clase = rango / cant_clases
    cant_clases_perc = int(round(0.65 * cant_clases, 0))  # cantidad de clases utilizando percentiles
    percentiles = 1 / cant_clases_perc  # percentil
    # inicializo variables
    d = {}  # diccionario a retornar (con valores maximos y medios de cada clase)
    PORC_MIN_CLASES_CON_VALOR, PORC_MAX_CLASES_CON_VALOR = 0.3, 0.72  # porcentajes min y max de clases con valores (es decir, no vacias)

    # CREO CLASES CON MISMA AMPLITUD
    print("Creo {} clases con amplitud de {:.2f}".format(cant_clases, amplitud_clase))
    print("{:^10s}\t{:^10s}\t{:^10s}\t{:^10s}".format("Clase Nº","Valor min", "Valor med", "Valor max"))
    # Por clase
    for i in range(cant_clases):
        # Determino valores minimo, medio y maximo de la clase
        valor_min_clase = round(valor_min + amplitud_clase * i, 2)  # valor min para estar en clase i
        valor_max_clase = round(valor_min + amplitud_clase * (i + 1), 2)  # valor max para estar en clase i
        valor_med_clase = round((valor_max_clase + valor_min_clase) / 2, 2)  # valor medio de clase i

        # Guardo valor medio y maximo de la clase
        d[valor_max_clase] = valor_med_clase
        print("{:^10d}\t{:^10.1f}\t{:^10.1f}\t{:^10.1f}".format(i+1, valor_min_clase, valor_med_clase, valor_max_clase))

    # Imprimo resultados de distribucion de valores en clase
    cant_val_por_clase = values_distribution_in_classes(d, valores_unicos)

    # Determino % de clases con al menos un valor
    cant_clases_con_valor = len(cant_val_por_clase) - cant_val_por_clase.count(0)
    porc_clases_con_valor = cant_clases_con_valor / cant_clases

    # SI LA DISTRIBUCION DE VALORES EN CLASES NO ES BUENA
    # Si menos del 50% de las clases tienen valores o mas del 71%
    if (porc_clases_con_valor < PORC_MIN_CLASES_CON_VALOR) or (porc_clases_con_valor > PORC_MAX_CLASES_CON_VALOR):

        # Imprimo razon, por la que, vuelvo a generar clases
        print("No funciono bien la creacion de clases con misma amplitud. Razon: ", end="")
        if porc_clases_con_valor < PORC_MIN_CLASES_CON_VALOR:
            print("Hay pocas clases con valores, es decir, hay una gran concentracion de valores en pocas clases. "
                  "Valores muy distintos tomaran mismo sentiment por estar en misma clase")
        else:
            print("Hay muchas clases con valores. Valores tendran sentiment poco robusto")
        print("Ahora, generare {} clases a partir de tomar percentiles {}".format(cant_clases_perc, percentiles))

        # Defino variables
        d = {}  # reinicio diccionario pues no usare clases de misma amplitud

        # CREO CLASES A PARTIR DE PERCENTILES
        # Por clase
        print("{:^10s}\t{:^10s}\t{:^10s}\t{:^10s}".format("Clase Nº", "Valor min", "Valor med", "Valor max"))
        for i in range(cant_clases_perc):

            # Obtengo indices de valor min y max para la clase
            idx_valor_min_clase = int(len(valores_unicos) * percentiles * i)  # valor min para estar en clase i
            idx_valor_max_clase = int(len(valores_unicos) * percentiles * (i + 1)) - 1  # valor min para estar en clase i. El -1 seria porque el idx de la lista arranca en 0

            # Obtengo valores min y max de la clase a partir de los indices
            valor_min_clase = valores_unicos[idx_valor_min_clase]
            valor_max_clase = valores_unicos[idx_valor_max_clase]
            valor_med_clase = (valor_max_clase + valor_min_clase) / 2  # valor medio de clase i

            # Guardo valor maximo y medio de la clase
            d[valor_max_clase] = valor_med_clase
            print("{:^10d}\t{:^10.1f}\t{:^10.1f}\t{:^10.1f}".format(i + 1, valor_min_clase, valor_med_clase, valor_max_clase))

        # Imprimo resultados de distribucion de valores en clases
        values_distribution_in_classes(d, valores_unicos)

    # SI LA DISTRIBUCION DE VALORES EN CLASES ES BUENA
    else:
        # IMPRIMO MENSAJE
        print("Funciono correctamente la creacion de clases con misma amplitud! ")

    return d

def values_distribution_in_classes(dict, valores_unicos):
    """
    Obtiene la distribucion de los valores unicos en las clases, es decir, la cantidad de valores unicos por clase.
    :param dict: Diccionario con valores maximos de cada clase como key y con valores medios de cada clase como value
    :param valores_unicos: Lista de valores unicos de una columna numerica continua
    :return: Lista de cantidad de valores unicos por clase
    """
    # Inicializo diccionario a retornar
    d = {}
    for key in dict.keys():
        d[key] = 0

    # Por valor unico
    for valor in valores_unicos:

        # Por valor maximo de clase
        for valor_max_clase in list(dict.keys()):

            # si el valor es menor al valor maximo de clase
            if valor <= valor_max_clase:  # si el valor unico estaria en clase

                # sumo 1 a clase a la que pertenece el valor
                d[valor_max_clase] += 1

                break  # para no seguir comparando valor con otros valores maximos de clases

    print("Distribucion de valores unicos en clases: ", list(d.values()))
    return list(d.values())

'''
def main(df_alt, df_opi):

    # Elimino alternativas con precios nan
    print("3.2.1 Dataframe Alternativas: Elimino alternativas con precios nan...".center(120))  # FALTA DOC
    df_alt = drop_alternatives_without_price(df_alt)
    print()

    print("3.2.1 Eliminando None values...".center(120))
    df_opi = df_opi.dropna(subset='opinion')   # no documentado... creia que no habia opiniones nan
    df_alt = drop_alternatives_with_most_na(df_alt=df_alt, df_opi=df_opi)

    print("3.2.2 Eliminando filas repetidas...".center(120))
    df_opi = df_opi.drop_duplicates(subset='opinion', ignore_index=True).reset_index(drop=True)  # elimino duplicados teniendo en cuenta solo la columna content que es la que contiene opiniones propiamente
    # df_opi = df_opi  # reseteo index al eliminar filas
    df_alt = drop_alt_duplicates(df_alt, df_opi) # NO DEBERIA SER NECESARIA PERO FALLA LA EXTRACCION EN EVITAR DUPLICADOS... FALTARIA DOC

    print("3.2.3 Elimino alternativas con datos erroneos (Dataframe Alternativas)...".center(120))
    df_alt = drop_alternatives_with_wrong_values(df_alt, df_opi)

    print("3.2.4 Preparando opiniones (Dataframe Opiniones)...".center(120))
    df_opi = delete_date_of_issue_from_opinion(df_opi)  # Elimino fecha de emision al final de la opinion (por ej, "Hace x meses")
    df_opi_tokenizado = df_opi.copy()
    df_opi_tokenizado = clean_opinions(df_opi_tokenizado)  # Limpio las opiniones

    print("3.2.5 Discretizando campos numericos continuos (Dataframe Alternativas)...".center(120))
    df_alt.iloc[:, 1:] = categorize_numeric_columns(df_alt.iloc[:, 1:])  # categorizo columnas numericas con valores continuos, no le paso columna id pues la categorizaria.
    return df_alt, df_opi, df_opi_tokenizado
'''

'''
ya no es necesaria al eliminar alternativas repetidas por modelo en extraccion.
def drop_duplicate_alternatives(df_alt, df_opi):  # parece funcionar bien pero deberia confirmarlo
    """
    Borra las alternativas repetidas siempre que no tengan opiniones
    :param df_alt: Dataframe. Unidad de analisis: alternativa del producto. Columnas: id_alternativa, precio y campos
    especificos segun el producto.
    :param df_opi: Dataframe. Unidad de analisis: opinion del producto. Columnas: id_alternativa y opinion.
    :return: Dataframe. Unidad de analisis: alternativa del producto. Columnas: id_alternativa, precio y campos
    especificos segun el producto. Menos filas del dataframe al eliminar alternativas repetidas sin opiniones.
    """
    # Ids de alternativas con opiniones
    l_ids_with_opi = df_opi['id_alternativa'].unique()
    l_idx_filt = list(df_alt[df_alt.id_alternativa.isin(l_ids_with_opi)].index)

    # POR ALTERNATIVA
    for idx in df_alt.index:

        # SI NO TIENE OPINIONES
        if idx not in l_idx_filt:

            df_alt_filt = df_alt.loc[l_idx_filt]

            # OBTENGO ALTERNATIVAS CON EL MISMO MODELO
            df_alt_same_mod = df_alt_filt[df_alt_filt['Modelo'] == df_alt.loc[idx, 'Modelo']]

            # COMPARO CONTRA ALTERNATIVAS DEL MISMO MODELO
            # Agrego alternativa sin opiniones
            df_alt_same_mod_with_new_alt = df_alt_same_mod.copy()
            df_alt_same_mod_with_new_alt.loc[idx] = df_alt.loc[idx].values

            # Elimino columnas con NaN para evitar diferencias ficticias y borro modelos duplicados (sin tener en cuenta id y precio)
            df_alt_same_mod_with_new_alt = df_alt_same_mod_with_new_alt.dropna(axis=1)  # .drop_duplicates(subset=list(df_alt_mismo_mod.columns)[2:])
            df_alt_same_mod_with_new_alt = df_alt_same_mod_with_new_alt.drop_duplicates(subset=list(df_alt_same_mod_with_new_alt.columns)[2:])

            # SI LA ALTERNATIVA ES NUEVA
            if len(df_alt_same_mod) != len(df_alt_same_mod_with_new_alt):
                # GUARDO ALTERNATIVA
                l_idx_filt.append(idx)

    print("Cantidad de alterantivas antes de limpieza: {}\n".format(df_alt.shape[0]))
    df_alt = df_alt.loc[l_idx_filt] # Selecciono las alternativas filtradas
    df_alt = df_alt.reset_index(drop=True)  # Reseteo indices
    # df_alt = df_alt.drop(['Modelo'], axis=1)  # Elimino columna "Modelo" utilizada para la eliminacion de alts
    print("Cantidad de alterantivas despues de limpieza: {}\n".format(df_alt.shape[0]))
    df_alt.to_excel('/Users/nachomondino/Desktop/asfad.xlsx')
    return df_alt
'''

