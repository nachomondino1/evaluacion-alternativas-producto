# Importo librerias
import pandas as pd
import operator
from p3_modelling.sentiment_atribution import contains_word_type

################################################ FUNCIONES PRINCIPALES ################################################
def most_frequent_ngrams(df_opi_tokenizado, n_ngram, QUANT_NGRAMS): # acordate que no se puede probar individualmente porque se levanta mal el df_opi_tokenizado (en vez de lista lo entinede como string)
    """
    Obtiene lista de los ngrams mas frecuentes utilizados en las opiniones de un producto
    :param QUANT_NGRAMS: Integer. Numero de ngrams frecuentes que extraer
    :param df_opi_tokenizado: Dataframe. Unidad de analisis: opinion de un producto. Columnas: id_alternativa y opinion.
     Los valores de la columna opinion debe estar tokenizados, es decir, cada opinion debe ser una lista cuyos elementos
     son sus palabras
    :return: Lista. N-grams mas frecuentes en opiniones ordenados por frecuencia de mayor a menor.
    """
    # DEFINO VARIABLES
    d = {}
    idx_token = df_opi_tokenizado.columns.get_loc("opinion")  # agrega flexibilidad pues puedo pasarle el df_opiniones enterro e igual usa solo "opiniones"

    # POR OPINION
    for i in range(len(df_opi_tokenizado)):
        opinion = df_opi_tokenizado.iloc[i, idx_token]

        # OBTENGO NGRAMS (CONJ DE N PALABRAS) DE OPINION (++1 ngram por opinion)
        ngrams = generate_n_grams(opinion, n_ngram)

        # GUARDO NGRAM Y SU FRECUENCIA
        # Por cada ngram
        for ngram in ngrams:
            # Sumo 1 a su frecuencia
            d[ngram] = d[ngram]+1 if ngram in d.keys() else 1

    # OBTENGO LISTA DE LOS N-GRAMS MAS FRECUENTES
    l_freq_ngrams = most_frequent_dict_key(d, QUANT_NGRAMS)
    print("{} frases de {} palabra mas frecuentes: {}".format(QUANT_NGRAMS, n_ngram, l_freq_ngrams))

    # Exporto dataframe de palabras mas frecuentes (momentaneamente lo pongo aca)
    #if n_ngram == 1:
    #    df = pd.DataFrame(data=d.values(), columns=['frecuencia'], index=d.keys())
    #    df = df.sort_values(by='frecuencia', ascending=False)  # sorted() no es para dataframes
    #    df.to_excel('/Users/nachomondino/Desktop/df_most_freq_words.xlsx')
    return l_freq_ngrams

def filter_most_frequent_words(l_freq_words, d_rel_words):  # ES BASTANTE MEJORABLE..
    """
    Filtra palabras mas frecuentes segun relevancia, tipo de palabra y palabra relacionadas
    :param l_freq_words: Lista. Palabras mas frecuentes en opiniones ordenadas por frecuencia de mayor a menor.
    :param d_rel_words: Diccionario. Keys: Palabra. Values: Palabras relacionadas a key.
    :return: Lista. Palabras mas frecuentes en opiniones ordenadas por frecuencia de mayor a menor. Solo palabras
    relevantes, sustantivos y evitando repeticion de palabras relacionadas
    """
    # DEFINO VARIABLES
    l_freq_words_filt = []
    l_pal_irrel = ['android', 'año', 'años', 'amazon', 'aparato',
                   'band', 'baja',
                   'calidad', 'conforme', 'compra', 'cosas', 'color', 'compu', 'cosa', 'caso', 'cuidado', 'camaras', 'celulares',
                   'descripcion', 'disney', 'diferencia',
                   'equipo', 'expectativas', 'encanto', 'estrellas', 'espectativas',
                   'funcion', 'flow', 'falta',
                   'gama', 'gusto', 'gracias', 'general', 'google', 'gb', 'gente',
                    'hora', 'horas', 'hs',
                   'iphone',
                   'luz',
                    'mano', 'mes', 'meses', 'momento', 'maquina', 'modelo', 'motorola', 'moto', 'mercado',
                    'netflix', 'nota',
                    'preciocalidad', 'persona', 'personas', 'prestaciones', 'producto', 'problema', 'problemas', 'punto', 'puntos', 'publicacion', 'poder', 'pena', 'pulsera',
                    'redes', 'relacion', 'rendimiento', 'resto', 'regalo', 'respecto', 'reloj', 'relojes',
                    'tiempo', 'tipo', 'tv', 'tele', 'televisor', 'trabajo', 'telefono',
                    'uso',
                    'verdad', 'videos',
                    'semana', 'super', 'samsung', 'smart', 'smartwatch',
                    'youtube',
                    'xiaomi',
                    'whatsapp', 'windows', 'watch']

    # Por palabra frecuente
    for palabra in l_freq_words:
        print("PALABRA: {}".format(palabra))

        # Si la palabra es relevante
        if palabra not in l_pal_irrel:

            # Si es sustantivo
            if contains_word_type(text=palabra, word_type=['NOUN']): # En smartband: or palabra == 'facil' or palabra=='conecta':  # hacer que reciban lista y la filtren...

                # La guardo
                l_freq_words_filt.append(palabra)
                print("\t Se guardo la palabra {}".format(palabra))

    l_freq_words_filt_copy = l_freq_words_filt
    # ELIMINO PALABRAS RELACIONADAS
    # Por palabra
    for palabra in l_freq_words_filt:

        # SI TIENE, ELIMINO SUS PALABRAS RELACIONADAS DE LISTA
        if palabra in d_rel_words.keys():

            # Obtengo sus palabras relacionadas
            l_related_words = d_rel_words[palabra][1:]  # siempre la primera palabra relacionada es la propia palabra

            # Por palabra relacionada
            for word in l_related_words:  # sin incluir palabra propiamente

                word = word.replace(" ","")  # Elimino espacios agregados para identificar cust needs en opiniones y evitar confusion

                # Si esta en lista de palabras
                if word in l_freq_words_filt:

                    # La remuevo
                    l_freq_words_filt_copy.remove(word)  # La eliminacion afecta el ciclo for? Sí
                    print("\t Se removio palabra '{}' dado que ya esta '{}'".format(word, palabra))

    print("{} palabras restantes: {}".format(len(l_freq_words_filt), l_freq_words_filt))
    return l_freq_words_filt

def select_possible_customer_needs(l_most_freq_words, l_possible_customer_needs):
    """
    Selecciona las customer needs de un producto a partir de las frases mas frecuentes en las opiniones del producto
    :param l_most_freq_words: Lista. Palabras mas frecuentes en opiniones y relevantes
    :param l_possible_customer_needs: Lista. Frases de 3 palabras mas frecuentes en opiniones
    :return: Dataframe. Unidad de analisis: customer need del producto. Columnas: Customer needs de 1 palabra (index)
    y customer needs de 3 palabras
    """
    # Defino variables
    df_cust_needs = pd.DataFrame(columns=["cust_needs_three_words"])  # Dataframe a retornar
    i = 0
    print("{:^40s}\t{:^40}\t{:^40}".format("Palabra frecuente", "Posible customer need", "Posicion en frecuencia "))

    # POR POSIBLE CUSTOMER NEED
    for possible_customer_need in l_possible_customer_needs:
        i += 1

        # Obtengo palabras mas frecuentes en posible customer need
        l_freq_word_in_cust_need = freq_word_in_cust_need(possible_customer_need, l_most_freq_words)

        # Si tiene una sola de las palabras mas frecuentes (evitar cust needs con mas de 1 caracteristica)
        if len(l_freq_word_in_cust_need) == 1:

            # Defino variable
            freq_word = l_freq_word_in_cust_need[0]  # palabra frecuente en posible customer need

            # y si aun no extraje una customer need para dicha palabra
            if freq_word not in df_cust_needs.index:

                # Guardo customer need
                df_cust_needs.loc[freq_word] = possible_customer_need
                print("{:^40s}\t{:^40}\t{:^40}".format(freq_word, possible_customer_need, i))
    return df_cust_needs

def manually_select_customer_needs(df_cust_needs):
    """
    Permite seleccionar manualmente las necesidades del cliente dentro de las posibles.
    :param df_cust_needs: Dataframe. Unidad de analisis: posible customer need del producto. Columnas: Customer needs
    de 1 palabra (index) y customer needs de 3 palabras
    :return: Dataframe. Unidad de analisis: customer need del producto. Columnas: Customer needs de 1 palabra (index)
    y customer needs de 3 palabras.
    """
    # POR POSIBLE CUSTOMER NEED
    for word in df_cust_needs.index:

        # Defino variable
        possible_customer_need = df_cust_needs.loc[word, 'cust_needs_three_words']  # Frase posible customer need

        # Pregunto a administrador
        # Mientras la carga sea invalida
        try:
            # Solicito 0 o 1 para determinar si customer need sera considerada o no
            bool = input("Ingrese 'd' para eliminar, 'c' para cambiar el nombre u otra letra para guardar sin cambiar el nombre'{}': ".format(possible_customer_need.upper()))

            if bool == "c":
                # Guardo customer need
                cust_need_rename = input('\t Renombre la customer need:')
                df_cust_needs.loc[word, 'cust_needs_three_words'] = cust_need_rename
                print("\t Se cambio el nombre de la frase '{}'".format(possible_customer_need))

            elif bool == "d":
                # Guardo customer need
                df_cust_needs = df_cust_needs.drop([word])
                print("\t Se elimino la frase '{}'".format(possible_customer_need))

        except ValueError:  # si el input no es un numero entero
            pass
    print(df_cust_needs)
    return df_cust_needs

def create_relation_matrix(l_atributos, l_cust_needs):
    """
    Crea matriz de relaciones entre customer needs y atributos del producto. Para ello, pide al usuario por terminal
    la relacion entre cada uno.
    :param l_atributos: Lista. Atributos o campos especificos de un producto (solo los utiles para el analisis)
    :param l_cust_needs: Lista. Customer needs (las de 1 sola palabra) de un producto
    :return: Dataframe. Filas: customer need de producto. Columnas: atributos o campos especificos del producto. Celdas:
    indica relacion entre customer need  i y atributo j
    """
    # DEFINO VARIABLES
    print("Los atributos son: ", l_atributos)
    print("Las customer needs son: ", l_cust_needs)
    df_relation_matrix = pd.DataFrame(columns=l_atributos, index=l_cust_needs)  # Dataframe a retornar

    # POR ATRIBUTO O CAMPO ESPECIFICO DEL PRODUCTO
    for atributo in l_atributos:

        # POR CUSTOMER NEED DEL PRODUCTO
        for customer_need in l_cust_needs:

            # SOLICITO RELACION ENTRE ATRIBUTO Y CUSTOMER NEED POR TERMINAL
            # Validacion de ingreso de datos, solicito relacion hasta que el input sea 0, 1, 3 o 9
            while True:
                try:
                    input_admin = int(input("Ingrese relacion entre atributo '{}' y customer need '{}'(0, 1, 3 o 9 ptos): ".format(atributo.upper(), customer_need.upper())))

                    # Si el input del admin es 0, 1, 3 o 9
                    if input_admin in [0, 1, 3, 9]:

                        # Administrador cargo relacion correctamente
                        df_relation_matrix.loc[customer_need, atributo] = input_admin
                        break

                    # Si el input del admin no es 0, 1, 3 o 9
                    else:
                        print("Ingreso no valido. El ingreso debe ser un numero, en particular, 0, 1, 3 o 9. ")

                # Si el input no es un numero
                except ValueError:
                    # sigo en el ciclo while hasta que cargue la relacion correctamente
                    print("Ingreso no valido. El ingreso debe ser un numero, en particular, 0, 1, 3 o 9. ")

        # Imprimo resumen de cuantos ptos tiene cada customer need
        print("{:^40s}\t{:^40}".format("Customer need", "Suma de ptos de relaciones"))
        for cust_need in df_relation_matrix.index:
            print("{:^40s}\t{:^40}".format(cust_need, sum(df_relation_matrix.loc[cust_need].dropna())))

    # SI LA CUSTOMER NEED NO TIENE RELACION CON NINGUN ATRIBUTO
    # Por customer need
    for customer_need in l_cust_needs:

        # Si no tiene relacion con ningun atributo
        if sum(df_relation_matrix.loc[customer_need]) == 0:

            # Creo atributo con el cual relacionarla
            df_relation_matrix[customer_need] = 0

            # Asigno relacion de 1 con atributo creado
            df_relation_matrix.loc[customer_need, customer_need] = 1

    return df_relation_matrix

################################################ FUNCIONES SECUNDARIAS ################################################
# UTILIZADA EN MOST_FREQUENT_NGRAMS()
def most_frequent_dict_key(dict, quantity_freq):
    """
    De un diccionario de frecuencias (value es numerico, en particular, la frecuencia de la key), selecciona las keys
    mas frecuentes
    :param dict:  Diccionario cuyos values deben ser numeros, especficamente, frecuencias tal que puedo ordenar las keys
    (según frecuencia)
    :param quantity_freq: Cantidad de keys a seleccionar de las mas frecuentes
    :return: Lista de keys mas frecuentes (de largo quantity_freq)
    """
    # Defino variable
    l_freq = []

    # Ordeno diccionario por frecuencia (value)
    sorted_dict = sorted(dict.items(), key=operator.itemgetter(1))  # Lista con pares key-value ordenados crecientemente segun el value
    sorted_dict = sorted_dict[::-1]  # invierto lista, ahora ordenados descendientemnete

    # Selecciono las keys del dict de mayor frecuencia
    for item in sorted_dict[:quantity_freq]:  # hasta los primeros x
        key = item[0]
        l_freq.append(key)

    return l_freq

def generate_n_grams(text, ngram):
    """
    Obtiene lista de los n-grams de un texto
    :param text: Lista. Texto tokenizado, es decir, como lista de palabras
    :param ngram: Largo de frases a buscar
    :return: Lista de frases de largo <ngrams> en <texto>
    """
    # words = [word for word in text.split(" ") if word not in set(stopwords.words('english'))]
    # print("Sentence after removing stopwords:", text)
    temp = zip(*[text[i:] for i in range(0, ngram)])
    ans = [' '.join(ngram) for ngram in temp]
    return ans

# UTILIZADA EN SELECT_CUSTOMER_NEEDS()
def freq_word_in_cust_need(possible_customer_need, l_most_freq_words):
    """
    Obtengo lista de palabras mas frecuentes (si hay) en posible customer need.
    :param l_most_freq_words: Lista. Palabras mas frecuentes en opiniones y relevantes
    :param possible_customer_needs: String. Frase de 3 palabras que puede ser customer need.
    :return: Lista. Palabras mas frecuentes en posible customer need
    """
    # Defino variables
    l_freq_words_in_cust_need = []

    # POR CADA PALABRA DE ESTA
    for palabra in possible_customer_need.split():

        # SI LA PALABRA ES DE LA MAS FRECUENTES
        if palabra in l_most_freq_words:
            l_freq_words_in_cust_need.append(palabra)
    return l_freq_words_in_cust_need

'''
# para correr pruebas en archivo independientemente de main.py
df_alt_cleaned = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/celulares/df_alt_cleaned.xlsx')
df_opi_tokenizado = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/celulares/df_opi_cleaned.xlsx', index_col=0)
print(df_alt_cleaned)
print(df_opi_tokenizado)
main(df_alt_cleaned, df_opi_tokenizado)
'''
