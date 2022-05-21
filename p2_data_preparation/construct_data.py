# Importo librerias
import pandas as pd
import operator
import stanza
from p3_modelling.sentiment_atribution import find_related_words
pos_tagger = stanza.Pipeline(lang='es', processors='tokenize,pos')  # stanza.download('es') --> This downloads the English models for the neural pipeline

################################################ FUNCIONES PRINCIPALES ################################################
def most_frequent_words(df_tokenizado):
    """
    Obtiene lista de las palabras mas frecuentes utilizadas en las opiniones de un producto
    :param df_tokenizado: Dataframe cuya unidad de analisis es la opinion de un producto. Cada opinion debe estar
    tokenizada, es decir, debe ser una lista cuyos elementos son sus palabras
    :return: Lista de palabras mas frecuentes en opiniones y relevantes
    """
    # Defino variables
    QUANT_WORDS = 150  # parametro de cuantas mas frecuentes frases buscar. dependera del producto?
    d = {}
    idx_token = df_tokenizado.columns.get_loc("opinion")  # agrega flexibilidad pues puedo pasarle el df_opiniones enterro e igual usa solo "opiniones"
    freq_ngrams_filt = []

    # POR OPINION
    for i in range(len(df_tokenizado)):
        opinion = df_tokenizado.iloc[i, idx_token]

        # OBTENGO PALABRAS DE OPINION
        ngrams = generate_n_grams(opinion, ngram=1)

        # GUARDO PALABRA Y SU FRECUENCIA
        # Por cada palabra
        for ngram in ngrams:
            # Por que no filtro por sustantivo aqui? Por costo computacional, entra (cant ngrams de una opi * cant opis) veces...

            # Si su frecuencia es mayor a 1
            if ngram in d.keys():
                # Sumar uno a su frecuencia
                d[ngram] += 1

            # Si aun no tiene frecuencia
            else:
                # lo inicializo
                d[ngram] = 1

    # OBTENGO LAS PALABRAS MAS FRECUENTES
    freq_ngrams = most_frequent_dict_key(d, QUANT_WORDS)
    print("{} palabras mas frecuentes: {}".format(QUANT_WORDS, freq_ngrams))

    # FILTRO LAS PALABRAS MAS FRECUENTES
    print("Filtro palabras mas frecuentes")
    # Por palabra frecuente
    for palabra in freq_ngrams:

        # Si es sustantivo
        if is_noun(palabra):

            # Si no es una palabra irrelevante
            if not is_irrelevant_word(palabra):

                # La guardo
                freq_ngrams_filt.append(palabra)

    print("Elimino palabras relacionadas para evitar repeticion de customer needs")
    freq_ngrams_filt = delete_related_words(freq_ngrams_filt)
    print("{} palabras restantes: {}".format(len(freq_ngrams_filt), freq_ngrams_filt))

    return freq_ngrams_filt

def most_frequent_phrases(df_tokenizado):
    """
    Obtiene lista de frases de 3 palabras mas frecuentes utilizadas en las opiniones de un producto
    :param df_tokenizado: Dataframe cuya unidad de analisis es la opinion de un producto. Cada opinion debe estar
    tokenizada, es decir, debe ser una lista cuyos elementos son sus palabras
    :return: Lista de las <CANT_POSIBLES_CUSTOMER_NEEDS> frases de 3 palabras mas frecuentes
    """
    print("BUSCO POSIBLES CUSTOMER NEEDS")
    # Defino variables
    CANT_POSIBLES_CUSTOMER_NEEDS = 2000  # parametro de cuantas mas frecuentes frases buscar. dependera del producto?
    d = {}
    idx_token = df_tokenizado.columns.get_loc("opinion")  # agrega flexibilidad pues puedo pasarle el df_opiniones enterro e igual usa solo "opiniones"

    # POR OPINION
    for i in range(len(df_tokenizado)):
        opinion = df_tokenizado.iloc[i, idx_token]

        # OBTENGO SUS FRASES DE 3 PALABRAS O "TRIGRAMS" (una opinion estara compuesta de mas de un trigram)
        ngrams = generate_n_grams(opinion, ngram=3)

        # GUARDO FRASE Y SU FRECUENCIA
        # Por cada trigram
        for ngram in ngrams:

            # Si el trigram ya fue cargado
            if ngram in d.keys():
                # Sumar uno a su frecuencia
                d[ngram] += 1

            # Si el trigram no fue cargado
            else:
                # lo inicializo
                d[ngram] = 1

    # OBTENGO LISTA DE LOS 3-GRAMS MAS FRECUENTES
    freq_ngrams = most_frequent_dict_key(d, CANT_POSIBLES_CUSTOMER_NEEDS)
    print("Primeras {} posibles customer needs: {}".format(100, freq_ngrams[:100]))

    return freq_ngrams

def select_customer_needs(l_most_freq_words, l_possible_customer_needs):
    """
    Selecciona las customer needs de un producto a partir de las frases mas frecuentes en las opiniones del producto
    :param most_freq_words: Lista de palabras mas frecuentes en opiniones y relevantes
    :param possible_customer_needs: Lista de frases de 3 palabras mas frecuentes en opiniones
    :return: Lista de customer needs como frases de 3 palabras, lista de customer needs como frase de 1 sola palabra
    """
    # Defino variables
    l_cust_needs, l_cust_needs_one_word = [], []  # Listas donde guardare el output
    copy_most_freq_words = l_most_freq_words.copy()
    i = 0
    print("{:^40s}\t{:^40}".format("Customer need", "Posicion en frecuencia "))

    # POR POSIBLE CUSTOMER NEED
    for possible_customer_need in l_possible_customer_needs:
        i += 1

        # POR CADA PALABRA DE ESTA
        for palabra in possible_customer_need.split():

            # SI LA PALABRA ES DE LA MAS FRECUENTES
            if palabra in l_most_freq_words:

                # SI LA POSIBLE CUSTOMER NEED ES DESEADA
                if is_possible_customer_need_wanted(possible_customer_need, copy_most_freq_words):

                    # Elimino palabra frecuente para no obtener una customer need parecida
                    l_most_freq_words.remove(palabra)

                    # Guardo customer need
                    l_cust_needs_one_word.append(palabra)
                    l_cust_needs.append(possible_customer_need)

                    print("{:^40s}\t{:^40}".format(possible_customer_need, i))
                break

    # podria filtro de frase con sentido...
    print("Customer needs:", l_cust_needs)
    print("Customer need en una palabra:", l_cust_needs_one_word)

    return l_cust_needs_one_word, l_cust_needs

def filter_attr_and_cust_needs(l_atributos, l_cust_needs, l_cust_need_three_words): # FALTA DOC
    """
    Permite filtrar atributos y customer needs a traves de terminal.
    :param l_atributos: Lista de atributos del producto
    :param l_cust_needs: Lista de customer needs del producto de 1 palabra
    :param l_cust_need_three_words: Lista de customer needs del producto de 3 palabras
    :return: Listas pasadas por parametro filtradas
    """
    l_cust_needs_three_words_filt = []

    print("Selecciona atributos que se relacionaran con customer needs:")
    l_atributos_filt = drop_unwanted_elements(l_atributos)  # elimino atributos no deseados
    print("Selecciona customer needs que se relacionaran con atributos:")
    l_cust_needs_filt = drop_unwanted_elements(l_cust_needs)  # elimino atributos no deseados

    # Por customer need de 1 palabra
    for cust_need in l_cust_needs_filt:
        # Selecciono su customer need de tres palabras
        l_cust_needs_three_words_filt.append(customer_needs_translation(l_cust_need_three_words, cust_need))

    return l_atributos_filt, l_cust_needs_filt, l_cust_needs_three_words_filt



################################################ FUNCIONES SECUNDARIAS ################################################
# UTILIZADA EN MOST_FREQUENT_WORDS() Y EN MOST_FREQUENT_PHRASES()
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
    :param text: Texto tokenizado, es decir, como lista de palabras
    :param ngram: Largo de frases a buscar
    :return: Lista de frases de largo <ngrams> en <texto>
    """
    # words = [word for word in text.split(" ") if word not in set(stopwords.words('english'))]
    # print("Sentence after removing stopwords:", text)
    temp = zip(*[text[i:] for i in range(0, ngram)])
    ans = [' '.join(ngram) for ngram in temp]
    return ans


# UTILIZADA EN MOST_FREQUENT_WORDS()
def is_noun(word):
    """
    Identifica si la palabra es un sustantivo o no
    :param word: Palabra
    :return: True si la palabra es sustantivo, o bien, False
    """
    # Proceso palabra
    doc = pos_tagger(word)

    # Obtengo pos (noun, adj, adv, verb, etc) de la palabra
    pos = doc.sentences[0].words[0].pos  # nlp esta preparada para procesar un documento en lugar de una palabra

    # Si palabra es sustantivo
    if pos == "NOUN":
        return True  # retorno True

    # si palabra no es sustantivo
    else:
        return False  # retorno False

def is_irrelevant_word(word):
    """
    Elimina palabras irrelevantes de lista de palabras
    :param words: Lista de palabras
    :return: Lista de palabras sin palabras irrelevantes
    """
    pal_irrel = ['android', 'año', 'años', 'auriculares',
                 'calidad', 'conforme', 'compra', 'cosas', 'celulares',
                 'equipo', 'expectativas', 'funcion', 'funciones',
                 'gama', 'gusto', 'gracias',
                 'iphone',
                 'mano', 'mes', 'meses', 'momento', 'motorola',
                 'netflix', 'notebook',
                 'preciocalidad', 'persona', 'personas', 'prestaciones', 'producto', 'problema', 'problemas',
                 'redes', 'relacion', 'rendimiento', 'resto',
                 'tele', 'telefono', 'televisor', 'tiempo', 'tv',
                 'uso',
                 'verdad',
                 'samsung', 'super',
                 'xiaomi',
                 'whatsapp', 'windows']

    if word in pal_irrel:
        return True
    else:
        return False

def delete_related_words(l_palabras):
    """
    Elimina palabras que se refieran a una misma caracterisitca del producto dejando una sola de ellas
    :param l_palabras: Lista de palabras
    :return: Lista de palabras sin palabras que se refieran a una misma caracteristica
    """
    # Convierto lista de palabras a string
    str_palabras = "  ".join(l_palabras)

    # Por palabra
    for palabra in l_palabras:

        # Si esta en lista de palabras
        if palabra in l_palabras:

            # Defino variables
            palabra_plural = palabra + "s"  # no necesariemnte es asi pero al menos es lo mas probable
            l_related_words = find_related_words(palabra)  # Obtengo palabras relacionadas

            # Si esta la palabra en plural
            if palabra_plural in str_palabras:
                # La remuevo
                str_palabras = delete_substring_in_string(str_palabras, palabra_plural)
                print("Se removio palabra '{}' dado que ya esta '{}'".format(palabra_plural, palabra))

            # Por palabra relacionada
            for word in l_related_words[1:]:  # sin incluir palabra propiamente

                # Si esta en lista de palabras
                if word in str_palabras:
                    # La remuevo
                    str_palabras = delete_substring_in_string(str_palabras, word)
                    print("Se removio palabra '{}' dado que ya esta '{}'".format(word, palabra))

    return str_palabras.split()

def delete_substring_in_string(string, substring):
    if substring in string:
        idx_ini = string.find(substring)
        string_cleaned = string[:idx_ini] + string[idx_ini + len(substring) + 1:]
    else:
        string_cleaned = string
        print("No se encontro el substring {} en el string {}".format(substring, string))

    return string_cleaned


# UTILIZADA EN SELECT_CUSTOMER_NEEDS()
def is_possible_customer_need_wanted(possible_customer_need, most_freq_words):
    """
    Evita seleccionar una posible customer need que contenga un numero, una palabra irrelevante o dos o mas palabras
    de las mas frecuentes
    :param possible_customer_need: Frase de 3 palabras que contiene al menos 1 palabra relevante
    :param most_freq_words: Lista de palabras mas frecuentes
    :return: True si la customer need es deseada, o en caso contrario, False
    """
    # Defino variable
    n = 0
    pal_irrel = ['android', 'auriculares', 'notebook', 'producto', 'tele', 'telefono', 'televisor', 'tv', 'samsung', 'windows']

    # POR CADA PALABRA DE LA POSIBLE CUSTOMER NEED
    for palabra in possible_customer_need.split():

        # SI LA PALABRA ES DE LAS MAS FRECUENTES
        if palabra in most_freq_words:

            # sumo uno a cantidad de palabras mas frecuentes de la frase
            n += 1

        # SI LA PALABRA ES UN NUMERO O ES IRRELEVANTE
        elif palabra.isnumeric() or palabra in pal_irrel:
            # Descarto la posible customer need
            return False

        else:
            pass

    # Si tiene solo una palabra de las mas frecuentes
    if n == 1:
        # Selecciono posible customer need como customer need
        return True
    # Si tiene mas de una palabra de las mas frecuentes
    else:
        # Descarto la posible customer need
        return False


# UTILIZADAS EN FILTER_ATTR_AND_CUST_NEEDS()
def drop_unwanted_elements(l):
    """
    :param l:
    :return:
    """
    l_wanted = []

    # Por elemento
    for element in l:

        # Mientras la carga sea invalida
        while True:
            try:
                # Solicito 0 o 1 para determinar si el atributo sera considerado o no
                bool = int(input("Tendra en cuenta el elemento '{}' (0 o 1): ".format(element.upper())))

                # si el atribuo sera considera
                if bool == 0:
                    break

                elif bool == 1:
                    l_wanted.append(element)
                    break

            except ValueError:  # si el input no es un numero entero
                pass

    return l_wanted

def customer_needs_translation(l_cust_needs, cust_need):  # no se que enombre ponerle, busca relacion entre customer needs de 3 palabras y las de 1...
    """
    Traduce customer need de 1 palabra a customer need de 3 palabras
    :param customer_needs: Lista de customer needs de 3 palabras
    :param customer_needs_substring: String. Customer need de 1 palabra.
    :return:
    """
    # POR CUSTOMER NEED DE 3 PALABRAS
    for customer_need in l_cust_needs:

        # SI CUSTOMER NEED DE 1 PALABRA ESTA EN CUSTOMER NEED DE 3 PALABRAS
        if cust_need in customer_need:
            return customer_need  # retorno customer need de 3 palabras

def main(df_alt_cleaned, df_opi_tokenizado):

    print("Obtengo palabras mas frecuentes en opiniones...".center(120))
    l_most_freq_words = most_frequent_words(df_opi_tokenizado)
    print()

    print("Obtengo frases de 3 palabras mas frecuentes en opiniones...".center(120))
    l_possible_customer_needs = most_frequent_phrases(df_opi_tokenizado)
    print()

    print("Selecciono customer needs del producto...".center(120))
    l_cust_needs_one_word, l_cust_needs= select_customer_needs(l_most_freq_words, l_possible_customer_needs)  # podria devolver el df_cust_needs...
    print()

    print("Selecciono atributos y customer needs del producto que se relacionaran entre si...".center(120))
    l_atributos, l_cust_needs_one_word, l_cust_needs = filter_attr_and_cust_needs(l_atributos=df_alt_cleaned.columns[1:], l_cust_needs=l_cust_needs_one_word,
        l_cust_need_three_words=l_cust_needs)
    df_cust_needs = pd.DataFrame(data={"cust_needs_one_word": l_cust_needs_one_word, "cust_needs_three_words": l_cust_needs}, columns=["cust_needs_one_word", "cust_needs_three_words"])

    # Borrar atributos de dataframe alternativas cleaned que no esten en l_atributos
    for atributo in df_alt_cleaned.columns[1:]:
        if atributo not in l_atributos:
            df_alt_cleaned = df_alt_cleaned.drop([atributo], axis=1)
    print()

    return df_alt_cleaned, df_cust_needs

''' # para correr pruebas en archivo independientemente de main.py
main()
'''


''' EX DELETE_RELATED_WORDS PUES TENIA DOS LISTAS DE PALABRAS RELACIONADAS QUE ACTUALIZAR... (junto con la de sentiment)
def delete_related_words(l_palabras):
    """
    Elimina palabras que se refieran a una misma caracterisitca del producto dejando una sola de ellas
    :param l_palabras: Lista de palabras
    :return: Lista de palabras sin palabras que se refieran a una misma caracteristica
    """
    # Defino lista de palabras relacionadas compuesta por grupos de estas
    l = [['camara','camaras', 'foto', 'fotos'], ['memoria', 'fluidez', 'almacenamiento', 'ram', 'disco'], ["procesador",
        "velocidad", "funcionamiento", "software"], ['bateria','duracion'], ['pantalla', 'imagen', 'definicion', 'resolucion'],
         ['sonido','audio','volumen','musica']]

    # Por palabra
    for palabra in l_palabras:

        # Por grupo de palabras relacionadas
        for palabras_rel in l:

            # Si palabra pertenece a grupo de palabras relacionadas
            if palabra in palabras_rel:

                # reemplazar palabra por la principal palabra del grupo
                if palabra != palabras_rel[0]:
                    idx = l_palabras.index(palabra)
                    l_palabras[idx] = palabras_rel[0]
                    print("Reemplazo palabra {} por palabra {}".format(palabra, palabras_rel[0]))

                # Por palabra relacionada (sin incluir la principal)
                for palabra_rel in palabras_rel[1:]:

                    # Si esta en lista de palabras
                    if palabra_rel in l_palabras:

                        # Remover palabra adicional de lista
                        l_palabras.remove(palabra_rel)
                        print("Remuevo palabra {} dado que ya existe la palabra {}".format(palabra_rel, palabras_rel[0]))

    return l_palabras
'''


''' FUNCIONES QUE FILTRABAN LISTA DE PALABRAS MAS FRECUENTES PERO LAS DESCARTE PUES ES MEJOR NO TENER QUE LIMPIAR LA LISTA SINO NO GENERARLA SUCIA
def delete_irrelevant_words(words):
    """
    Elimina palabras irrelevantes de lista de palabras
    :param words: Lista de palabras
    :return: Lista de palabras sin palabras irrelevantes
    """
    freq_words_filt = []
    pal_irrel = ['android', 'auriculares', 'calidad', 'conforme', 'compra', 'equipo', 'expectativas', 'funciones',
                 'gama', 'iphone', 'momento', 'motorola', 'netflix', 'notebook', 'producto', 'problema', 'problemas',
                 'relacion', 'rendimiento', 'tele', 'telefono', 'televisor', 'tiempo', 'tv', 'uso', 'verdad','samsung',
                 'super', 'whatsapp', 'windows']

    # Por palabra frecuente
    for word in words:

        # Si la palabra es relevante
        if word not in pal_irrel:

            # la guardo
            freq_words_filt.append(word)

    return freq_words_filt


def select_nouns(words):
    """
    Selecciona sustantivos de lista de palabras
    :param words: Lista de palabras
    :return: Lista de sustantivos
    """
    # Defino variable
    nouns = []

    # Por palabra
    for word in words:

        # Si la palabra es sustantivo
        if is_noun(word) is True:

            # la guardo
            nouns.append(word)

    return nouns

'''