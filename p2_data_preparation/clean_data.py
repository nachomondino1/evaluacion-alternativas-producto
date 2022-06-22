# Importo librerias
import pandas as pd
from p2_data_preparation.utils import preparacion_texto
import statistics as st
import numpy as np
import re


################################################ FUNCIONES PRINCIPALES ################################################
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

    print("Se ha quitado con exito la fecha de emision de cada opinion \n")
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
    print(df_opiniones.head(5), '\n')
    return df_opiniones

def drop_alternatives_with_most_na(df_alt, df_opi):
    """
    Elimina alternativas con mayoria de valores NaN en atributos del producto
    :param df_alt: Dataframe alternativas
    :param df_opi: Dataframe opiniones
    :return: Dataframe alternativas sin alternativas con mayoria de NaN values
    """
    # Defino variables
    l_idx_a_borrar = []
    n_valores_posibles = len(df_alt.columns[1:])  # excluyo id
    ids_con_opi = df_opi['id_alternativa'].unique()
    PORC_MIN_NO_NAN = 0.5

    # Por alternativa del dataframe
    for i in range(len(df_alt)):

        # Defino variables
        valores_alt = list(df_alt.iloc[i, 1:])  # valores de la alternativa (excluyo id)
        n_valores_nan = 0  # reinicio variable de cantidad de nan de alternativa
        id_alt = df_alt.loc[i, "id_alternativa"]  # id de la alternativa

        # Por valor de la alternativa
        for valor in valores_alt:

            # Si el valor es NaN
            if str(valor) == 'nan':

                # Sumo 1 a cantidad de valores nan de la alternativa
                n_valores_nan += 1

        # Si la alternativa tiene mas del 50% de valores NaN y no tiene opiniones asociadas
        if (n_valores_nan / n_valores_posibles > PORC_MIN_NO_NAN) and (id_alt not in ids_con_opi):

            # Guardo el indice de la alternativa
            l_idx_a_borrar.append(i)

    # Borro alternativas segun indices
    for idx in l_idx_a_borrar:
        df_alt = df_alt.drop([idx], axis=0)

    print("Cantidad de alternativas borradas: {}".format(len(l_idx_a_borrar)))
    print("Cantidad de alterantivas restantes: {}\n".format(df_alt.shape[0]))

    # Reinicio indice de alternativas
    df_alt = df_alt.reset_index(drop=True)  # el dropna me borra una fila y los indices quedan mal...
    return df_alt

def drop_alt_duplicates(df_alt, df_opi):  # temporal hasta que entienda porque falla is_alt_new() de collect_initial_data --> ya no ese temporal pues aqui borro por modelo y no tan general como por fila (sin id y precio)
    """
    Borra las alternativas repetidas (las que se le escapan al collect_initial_data.py)
    :param df_alt: Dataframe alternativas con columna 'Modelo'
    :param df_opi: Dataframe opiniones
    :return: Dataframe alternativas con alternativas unicas
    """
    l_idx = []

    # Por modelo
    for modelo in df_alt["Modelo"].dropna().unique():
        # print("Modelo: {}".format(modelo))

        # Busco alternativas del modelo
        df_alt_mismo_mod = df_alt[df_alt['Modelo'] == modelo]
        df_alt_mismo_mod = df_alt_mismo_mod.dropna(axis=1)  #.drop_duplicates(subset=list(df_alt_mismo_mod.columns)[2:])
        df_alt_mismo_mod_filt = pd.DataFrame(columns=list(df_alt_mismo_mod.columns))
        l_ind_a_rev = []

        # print("Alternativas del mismo modelo: \n", df_alt_mismo_mod)

        # Por alternativa
        for i in df_alt_mismo_mod.index:

            id_alt = df_alt_mismo_mod.loc[i, 'id_alternativa']  # Id de alternativa

            # Si tiene opiniones
            if id_alt in df_opi['id_alternativa'].values:

                # Agrego fila
                df_alt_mismo_mod_filt.loc[i] = df_alt_mismo_mod.loc[i]

            # Si no tiene opiniones
            else:
                # Guargdo esa info para revisar la alternativa luego
                l_ind_a_rev.append(i)

        # print("Alternativas del mismo modelo con opiniones: \n", df_alt_mismo_mod_filt)

        # Por alternativa sin opiniones
        for idx in l_ind_a_rev:

            # La elimino si se repite
            df_alt_mismo_mod_filt.loc[idx] = df_alt_mismo_mod.loc[idx]
            # print(df_alt_mismo_mod_filt)
            df_alt_mismo_mod_filt = df_alt_mismo_mod_filt.drop_duplicates(subset=list(df_alt_mismo_mod.columns)[2:])
            # print(df_alt_mismo_mod_filt)

        # Guardo indices de alternativas filtradas
        for idx in df_alt_mismo_mod_filt.index:
            l_idx.append(idx)
        # l_idx += df_alt_mismo_mod_filt.index # ValueError: operands could not be broadcast together with shapes (0,) (2,)

    # Guardo modelos unicos
    df_alt = df_alt.loc[l_idx]
    # print(df_alt)
    return df_alt

'''
def drop_alt_duplicates(df_alt, df_opi): # temporal hasta que entienda porque falla is_alt_new() de collect_initial_data --> ya no ese temporal pues aqui borro por modelo y no tan general como por fila (sin id y precio)
    """
    Borra las alternativas repetidas (las que se le escapan al collect_initial_data.py)
    :param df_alt: Dataframe alternativas con columna 'Modelo'
    :param df_opi: Dataframe opiniones
    :return: Dataframe alternativas con alternativas unicas
    """
    # Defino variables
    ids_con_opi = list(df_opi['id_alternativa'].unique())  # ids con opiniones
    df_alt_dropped = pd.DataFrame()
    
    # ELIMINO ALTERNATIVAS DUPLICADAS
    # Por modelo
    for modelo in df_alt["Modelo"].dropna().unique():

        # Busco alternativas del modelo
        df_alt_mismo_mod = df_alt[df_alt['Modelo']==modelo]
        n_mismo_mod = len(df_alt_mismo_mod)



        # PRUEBA
        # ORDENO ALTERNATIVAS SEGUN SI TIENEN O NO OPINIONES
        df_alt_mismo_mod['with opis'] = 0  # Agrego columna 'with opis' al df  # assign() e insert() no me funcionaron

        # Agrego colunna "with opis"
        for i in df_alt_mismo_mod.index:

            id_alt = df_alt_mismo_mod.loc[i, 'id_alternativa']

            # Si tiene opiniones
            if id_alt in ids_con_opi:
                df_alt_mismo_mod.loc[i,'with opis'] = 1

        # Ordeno alternativas por columna "with opis"
        df_alt_mismo_mod = df_alt_mismo_mod.sort_values(by='with opis', ascending=False)
        df_alt_mismo_mod = df_alt_mismo_mod.drop(['with opis'], axis=1)


        # Elimino duplicados
        df_alt_mismo_mod_sin_reps = df_alt_mismo_mod.dropna(axis=1) # Elimino columnas que tengan NaN (la mayoria de repeticiones de modelos tienen tod@ igual salvo que una tiene NaN en algunas col y la otra no)
        df_alt_mismo_mod_sin_reps = df_alt_mismo_mod_sin_reps.drop_duplicates(subset=list(df_alt_mismo_mod_sin_reps.columns[2:]))  # Elimino duplicados
        n_mismo_mod_sin_rep = len(df_alt_mismo_mod_sin_reps)

        # Si los modelos son iguales
        if n_mismo_mod != n_mismo_mod_sin_rep:

            # Borrar las alt que no tengan opiniones... (pues de las alt duplicadas puedo estar eliminando aquella que tienee las opis asociadas y no quiero eso)
            # Me quedo con primera fila de las repetidas (asegurandome que tenga opiniones pues esta ordenado por si tiene o no opis)
            df_aux = df_alt_mismo_mod[df_alt_mismo_mod.index.isin(df_alt_mismo_mod_sin_reps.index)]
            df_alt_dropped = pd.concat([df_alt_dropped, df_aux])
            print("Se descubieron {} modelos repetidos".format(n_mismo_mod-n_mismo_mod_sin_rep))

        # Si los modelos son distintos
        else:
            df_alt_dropped = pd.concat([df_alt_dropped, df_alt_mismo_mod])

    # VERIFICO QUE LAS ALTERNATIVAS BORRADAS NO TENGAN OPINIONES
    n_alt_with_opis_filt = len(df_alt_dropped[df_alt_dropped.id_alternativa.isin(ids_con_opi)])
    print("Se elimino {} alternativa/s por ser repetidas. De ellas, {} tenian al menos una opinion".format(len(df_alt)-len(df_alt_dropped), len(ids_con_opi) - n_alt_with_opis_filt))
    print("Cantidad de alterantivas restantes: {}\n".format(df_alt_dropped.shape[0]))

    df_alt_dropped = df_alt_dropped.drop(['Modelo'], axis=1)  # Pues sino dejaria columna 'Modelo' en df_alt_cleaned
    df_alt_dropped = df_alt_dropped.reset_index(drop=True)  # reseteo index al eliminar filas
    return df_alt_dropped
'''

def drop_alternatives_with_wrong_values(df_alt, df_alt_to_client, df_opi):
    """
    Elimina alternativas que tengan al menos un valor cargado incorrectamente en la publicacion de Mercado Libre. Solo
    tiene en cuenta valores de atributos numericos.
    :param df_alt: Dataframe alternativas
    :param df_alt_to_client: Dataframe alternativas con las alternativas que seran mostradas al cliente
    :param df_opi: Dataframe opiniones
    :return: Dataframe alternativas sin alternativas con valores mal cargados
    """
    # DEFINO VARIABLE
    l_idx_alt_a_borrar = set()  # set de indices de alternativas a borrar (una alternativa puede tener mas de un outlier)
    l_idx_alt_to_client_a_borrar = set()  # set de indices de alternativas a borrar (una alternativa puede tener mas de un outlier)

    # POR COLUMNA DEL DATAFRAME
    for columna in df_alt.columns[1:]:  #excluyo id

        # Defino variables
        l_unique_values = df_alt[columna].dropna().unique()
        print(columna.upper())

        # SI LA COLUMNA ES NUMERICA Y TIENE MAS DE DOS VALORES UNICOS (evita columnas 1-0)
        if df_alt[columna].dtype in ['float64', 'int64'] and len(l_unique_values) > 2:

            # Calculo cuantiles y rango
            l_values_sort = sorted(list(df_alt[columna].dropna()))  # sino los valores nan se acumulan en extremo de lista...
            q1, q3 = l_values_sort[int(0.25 * len(l_values_sort))], l_values_sort[int(0.75 * len(l_values_sort))]  # percentiles 25 y 75
            IQR = q3 - q1  # Rango intercuartil (resta de percentil 75 y 25)
            lim_inf, lim_sup = q1 - 1.5 * IQR, q3 + 1.5 * IQR  # Limites superior e inferior. Fuera son outliers.
            lim_inf_valor_mal_cargado, lim_sup_valor_mal_cargado = q1 - 5 * IQR, q3 + 5 * IQR  # 10 no, es mucho
            print("\t Q1: {:.1f} \t Q3: {:.1f} \t IQR: {:.1f}".format(q1, q3, IQR))
            print("\t LIMITES: \t outlier_inf = {:.1f}  outlier_sup = {:.1f} \t mal_cargado_inf = {:.1f} mal_cargado_sup = {:.1f}".format(lim_inf, lim_sup, lim_inf_valor_mal_cargado, lim_sup_valor_mal_cargado))

            # Defino variables
            l_val_erroneos = [valor for valor in l_unique_values if valor > lim_sup or valor < lim_inf]

            # POR VALOR ERRONEO (FUERA DEL RANGO INTERCUARTIL)
            for valor in l_val_erroneos:

                # Defino variables
                frec_val = len(df_alt[df_alt[columna] == valor])  # Frecuencia del valor
                idxs = [i for i in range(len(df_alt[columna])) if df_alt.loc[i, columna] == valor]  # Indices de alternativas cuyo atributo toma el valor outlier # no es el mismo index que en df_alt_to_client
                ids = [df_alt.loc[i, "id_alternativa"] for i in range(len(df_alt[columna])) if df_alt.loc[i, columna] == valor]  #Ids de alternativas cuyo atributo toma el valor outlier # son los mismos que en df_alt_to_client
                print("\tValor: {} \tFrecuencia: {}.".format(valor, frec_val), end=" ")

                # SI EL VALOR ERRONEO ES UN VALOR "MAL CARGADO"
                if valor > lim_sup_valor_mal_cargado or valor < lim_inf_valor_mal_cargado:
                    print("El valor {} es un valor MAL CARGADO".format(valor))

                    # POR CADA ALTERNATIVA CUYO VALOR ES UN DATO MAL CARGADO (MAL CARGADO POR EL VENDEDOR)
                    for i in range(frec_val):

                        idx = idxs[i]
                        id_alt = ids[i]
                        print("\t\t Alternativa Nº{}: ".format(i + 1), end=" ")

                        # SI LA ALTERNATIVA A LA QUE PERTENECE EL VALOR TIENE OPINIONES
                        if id_alt in list(df_opi['id_alternativa'].unique()):

                            # REEMPLAZO OUTLIER POR NAN
                            df_alt.loc[idx, columna] = None
                            print("Dado que la alternativa tiene opiniones asociadas, reemplazo el valor por NaN")

                        # SI LA ALTERNATIVA A LA QUE PERTENECE EL VALOR NO TIENE OPINIONES
                        else:
                            # GUARDO INDICE ALTERNATIVA QUE TIENE VALOR MAL CARGADO
                            l_idx_alt_a_borrar.add(idx)
                            print("Dado que la alternativa no tiene opiniones asociadas, elimino la alternativa")

                        # GUARDO INDICE ALTERNATIVA QUE TIENE VALOR MAL CARGADO
                        # eliminar directamente segun ids_to_client o ids pues son iguales
                        idx_client = df_alt_to_client[df_alt_to_client['id_alternativa'] == id_alt].index[0]
                        l_idx_alt_to_client_a_borrar.add(idx_client)  # el idx es ≠ y borra otra alternativa...
                        print("\t\t Elimino alternativa del dataframe que le mostrare al cliente. No le puedo mostrar "
                              "una alternativa con este valor mal cargado")

                # SI EL VALOR ERRONEO ES UN VALOR "OUTLIER" (ESTA BIEN CARGADO)
                else:
                    print("El valor {} es un valor OUTLIER")

                    # POR CADA ALTERNATIVA CUYO VALOR ES UN OUTLIER
                    for i in range(frec_val):

                        # INDEPENDIENTEMENTE DE SI TIENE OPINIONES, REEMPLAZO OUTLIER POR NAN
                        df_alt.loc[idxs[i], columna] = None
                        print("\t\t Alternativa Nº{}: ".format(i + 1), end=" ")
                        print("Dado que la alternativa no tiene un valor mal cargado, reemplazo el outlier por NaN")

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
    for idx_1 in l_idx_alt_a_borrar:
        df_alt = df_alt.drop([idx_1], axis=0)

    for idx_2 in l_idx_alt_to_client_a_borrar:
        df_alt_to_client = df_alt_to_client.drop([idx_2], axis=0)

    # Reinicio indices
    df_alt = df_alt.reset_index(drop=True)  # el dropna me borra una fila y los indices quedan mal...
    df_alt_to_client = df_alt_to_client.reset_index(drop=True)

    print("Cantidad de alternativas eliminadas: {}".format(len(l_idx_alt_a_borrar)))
    print("Cantidad de alterantivas restantes: {}\n".format(df_alt.shape[0]))
    return df_alt, df_alt_to_client

def disaggregate_columns_with_lists(df_alt):  # terminar de codear nombres
    """
    Desagrega columnas cuyos valores son listas. Cada elemento de la lista contendra su columna.
    :param df_alt: Dataframe alternativas
    :return: Dataframe alternativas reemplazando cada columna cuyos valores son listas por multiples columnas, una por
    cada elemento de la lista (soloe elementos mas frecuentes)
    """
    # Defino variable
    df_alt_res = df_alt.copy()  # Dataframe a retornar
    PORC_MIN_NO_NAN = 0.1

    # Por columna
    for columna in df_alt.columns:
        print("Columna: ", columna)

        # Si los valores de la columna son listas
        if is_column_with_list(df_alt[columna]):

            # Defino variables
            df = pd.DataFrame(index=list(df_alt.index))  # Dataframe con columnas desagregadas de columna con listas
            elemento_drop = []

            # Por valor (cada uno es una lista en formato string)
            for i in range(len(df_alt)):
                valor = df_alt.loc[i, columna]
                # print("Valor: ", valor)

                # Si el valor no es nan
                if str(valor) != 'nan':

                    # valor = valor.replace(" ", "")  # quito espacios en blanco entre elementos'
                    valor = valor.rstrip().lstrip() # quito espacios en blanco iniciales y finales '
                    # print("Valor strip:", valor)

                    # Obtengo elementos de lista
                    # l_elementos = valor.split(',')
                    l_elementos = re.split(', |,', valor)  # Funcionar funciona|. Puedo agregar mas sep / |/| x | - '
                    # print("Elementos del valor:", l_elementos)

                    # INICIALIZO COLUMNAS NUEVAS
                    # Por elemento del valor
                    for elemento in l_elementos:

                        # Si el elemento aun no tiene columna
                        # print(elemento, list(df.columns), elemento in list(df.columns))
                        col_name = columna + "_" + elemento
                        if col_name not in list(df.columns):
                            # Creo columna
                            df[col_name] = 0 # None
                            # print("\t Creo columna para el elemento {}".format(elemento))

                        # Guardo presencia de elemento
                        df.loc[i, col_name] = 1

            # ELIMINO COLUMNAS QUE TENGAN MAS DEL 80% DE NAN
            # Por columna
            df_copia = df.copy()
            for col in df.columns:

                # Defino variables
                n_valores = len(df[df[col] == 1])  # n_valores = len(df[col].dropna()) --> uso 0 en veez de NaN pq sino me trae problemas que la col tiene un solo valor
                porc_no_nan = n_valores / len(df)

                # Si tiene mas del 80% de NaN
                if porc_no_nan < PORC_MIN_NO_NAN:
                    # Elimino columna
                    df = df.drop([col], axis=1)
                    elemento_drop.append(col)

            # Agrego columnas a desechar en una sola columna "Otros"
            l = []
            if len(elemento_drop) > 1:

                # Determino valores de columna "Otros" para cada alternativa
                # Por valor
                for i in range(len(df_copia)):

                    # Veo si tiene otros o no
                    suma = sum(df_copia.loc[i, elemento_drop])  # 0 si no tiene otros, de lo contrario, 1 o mas

                    if suma == 0:
                        l.append(0)
                    else:
                        l.append(1)

                # Agrego columna "Otros"
                col_name = columna + "_" + 'otros'
                df[col_name] = l

            print(df)
            print("Elementos no tenidos en cuenta por tener mas de {}% de NaN: {}".format((1-PORC_MIN_NO_NAN)*100, elemento_drop))

            # REEMPLAZO COLUMNA POR COLUMNAS MULTIPLES
            df_alt_res = df_alt_res.drop([columna], axis=1)  # elimino columna original con listas
            df_alt_res = pd.concat([df_alt_res, df], axis=1) # agrego columnas multiples

    df_alt_res.to_excel('/Users/nachomondino/Desktop/prueba.xlsx', index=False)
    return df_alt_res

def is_column_with_list(columna):
    """
    Verifica que los valores de una columna sean listas
    :param columna: Series de pandas. Columna.
    :return: True si sus valores son listas, de lo contrario, False
    """
    columna = columna.dropna()
    n_valores = len(columna)
    i = 0

    # Si contiene strings
    if columna.dtype == 'object':
        print("\t Contiene strings", end=" ")

        # Si los valores son lista
        for valor in columna:

            if valor.count(',') > 0:  # or valor.count("/") > 0 or valor.count(" x ") > 0 or valor.count(" - ") > 0:
                i += 1

        # Si la mayoria de valores enumera elementos
        if i > 0.3 * n_valores:
            print("y sus valores son listas!")
            return True
        else:
            print("pero sus valores no son listas")
            return False

def categorize_numeric_columns(df):
    """
    Dado un dataframe, categoriza sus columnas numericas (las no numericas no porque al no haber una "distancia" entre
    strings, no puedo determinar cual se asemeja con cual) continuas (las discretas no pues ya estan categorizadas)
    :param df: Dataframe
    :return: Dataframe con todas sus columnas numericas discretas
    """
    # POR COLUMNA DEL DATAFRAME
    for columna in df.columns:
        print(columna.upper().center(120))

        # SI LA COLUMNA ES NUMERICA
        if (df[columna].dtype == 'float64') or (df[columna].dtype == 'int64'):

            # Defino variables
            n_clases = len(df[columna].dropna().unique())  # cant_valores_unicos = len(df[columna].value_counts())
            n_clases_opt = int(len(df[columna].dropna()) ** 0.5)  # cant clases ideales = raiz(nro datos)  # borror nan de posibles valores pues son mentira

            # SI LA COLUMNA ES CONTINUA (toma muchos valores distintos, especificamente, mas que la cantidad optima)
            if n_clases > n_clases_opt:  # Aqui se podria aplicar "factor de holgura"
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

def select_attributes(df_alt):  # FALTA DOC
    """
    Selecciono los atributos
    :param df_alt:
    :return:
    """
    # SELECCIONO ATRIBUTOS
    # Defino variable
    l_attr_remove = []

    # Por elemento
    for atributo in df_alt.columns:
        print(atributo.center(120))

        # Obtengo lista de frecuencia de sus valores
        unique_values = list(df_alt[atributo].dropna().unique())  # dropna para evitar que NaN sea una valor unico
        n_possible_unique_values = len(df_alt[atributo].dropna())
        n_unique_values = len(unique_values)
        n_opt_unique_values = int(len(df_alt[atributo].dropna()) ** 0.5)
        n_nan_values = (len(df_alt) - n_possible_unique_values) / len(df_alt)

        # Si toma muchos valores distintos
        if n_unique_values > n_opt_unique_values:
            print("CUIDADO! Tiene mas valores unicos que lo recomendado que es {}".format(n_opt_unique_values))
            print("Nºvalores: {} ; Nºvalores unicos: {}".format(n_possible_unique_values, n_unique_values))

        # Si tiene muchos valores NaN
        if n_nan_values > 0.5:
            print("CUIDADO! Toma muchos valores NaN, un {:1f}%".format(n_nan_values*100))

        # Mientras la carga sea invalida
        while True:
            try:
                # Solicito 0 o 1 para determinar si el atributo sera considerado o no
                bool = int(input("Tendra en cuenta el elemento '{}' (0 o 1): ".format(atributo.upper())))

                if bool == 0 or bool == 1:

                    # si el atribuo sera considerado
                    if bool == 0:
                        l_attr_remove.append(atributo)
                    break

            except ValueError:  # si el input no es un numero entero
                pass

    # ELIMINO ATRIBUTOS NO RELEVANTES DE DATAFRAME ALTERNATIVAS
    df_alt = df_alt.drop(l_attr_remove, axis=1)
    return df_alt

def delete_attr_x_values(df):
    """
    Elimino columnas del dataframe que toman un solo valor constante
    :param df: Dataframe
    :return: Dataframe sin columnas que tomen un solo valor
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
    PORC_MIN_CLASES_CON_VALOR, PORC_MAX_CLASES_CON_VALOR = 0.4, 0.72  # porcentajes min y max de clases con valores (es decir, no vacias)

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


''' no tiene sentido una funcion para dos lineas que se pueden hacer 1 sola..
def drop_alternatives_without_price(df_alt):
    """
    :param df_alt:
    :return:
    """
    # Elimino alternativas sin precio
    df_alt_filt = df_alt.dropna(subset=['precio'])  # en vez de df_alternativas['precio'].dropna() o df_alt.dropna(how='any', subset=['precio'], inplace=True)

    # Reseteo index
    df_alt_filt = df_alt_filt.reset_index(drop=True)  # el dropna me borra una fila y los indices quedan mal...
    print("Se elimino {} alternativa/s por tener precio=NaN.".format(df_alt.shape[0]- df_alt_filt.shape[0]))
    return df_alt_filt
'''