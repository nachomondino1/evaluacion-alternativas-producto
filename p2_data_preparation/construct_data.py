# Importo librerias
import operator
import stanza
# stanza.download('es')       # This downloads the English models for the neural pipeline
nlp = stanza.Pipeline('es')  # This sets up a default neural pipeline in English


def most_frequent_words(df_tokenizado):
    """
    Obtiene lista de las palabras mas frecuentes utilizadas en las opiniones de un producto
    :param df_tokenizado: Dataframe cuya unidad de analisis es la opinion de un producto. Cada opinion debe estar
    tokenizada, es decir, debe ser una lista cuyos elementos son sus palabras
    :return: Lista de palabras mas frecuentes filtradas
    """
    print("BUSCO PALABRAS MAS FRECUENTES")
    # Defino variables
    QUANT_WORDS = 50  # parametro de cuantas mas frecuentes frases buscar. dependera del producto?
    d = {}
    idx_token = df_tokenizado.columns.get_loc("opinion")  # agrega flexibilidad pues puedo pasarle el df_opiniones enterro e igual usa solo "opiniones"

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
    print("Selecciono unicamente palabras que sean sustantivos")
    freq_ngrams = select_nouns(freq_ngrams)
    print("{} palabras restantes: {}".format(len(freq_ngrams), freq_ngrams))

    print("Elimino palabras irrelevantes")
    freq_ngrams = delete_irrelevant_words(freq_ngrams)
    print("{} palabras restantes: {}".format(len(freq_ngrams), freq_ngrams))

    print("Elimino palabras relacionadas para evitar repeticion de customer needs")
    freq_ngrams = delete_related_words(freq_ngrams)
    print("{} palabras restantes: {}".format(len(freq_ngrams), freq_ngrams))

    return freq_ngrams

def most_frequent_phrases(df_tokenizado):
    """
    Obtiene lista de frases de 3 palabras mas frecuentes utilizadas en las opiniones de un producto
    :param df_tokenizado: Dataframe cuya unidad de analisis es la opinion de un producto. Cada opinion debe estar
    tokenizada, es decir, debe ser una lista cuyos elementos son sus palabras
    :return: Lista de las <CANT_POSIBLES_CUSTOMER_NEEDS> frases de 3 palabras mas frecuentes
    """
    print("BUSCO POSIBLES CUSTOMER NEEDS")
    # Defino variables
    CANT_POSIBLES_CUSTOMER_NEEDS = 200  # parametro de cuantas mas frecuentes frases buscar. dependera del producto?
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
    print("Posibles {} Customer needs: {}".format(CANT_POSIBLES_CUSTOMER_NEEDS, freq_ngrams))

    return freq_ngrams

def select_customer_needs(df_opi_tokenizado):
    """
    Selecciona las customer needs de un producto a partir de las frases mas frecuentes en las opiniones del producto
    :param df_opi_tokenizado: Dataframe cuya unidad de analisis es la opinion de un producto. Cada opinion debe estar
    tokenizada, es decir, debe ser una lista cuyos elementos son sus palabras
    :return: Lista de customer needs como frases de 3 palabras, lista de customer needs como frase de 1 sola palabra
    """
    # Defino variables
    customer_needs, customer_needs_one_word = [], []  # Listas donde guardare el output
    most_freq_words = most_frequent_words(df_opi_tokenizado)
    possible_customer_needs = most_frequent_phrases(df_opi_tokenizado)
    copy_most_freq_words = most_freq_words.copy()
    i = 0

    # POR POSIBLE CUSTOMER NEED
    for possible_customer_need in possible_customer_needs:
        i += 1

        # POR CADA PALABRA DE ESTA
        for palabra in possible_customer_need.split():

            # SI LA PALABRA ES DE LA MAS FRECUENTES
            if palabra in most_freq_words:

                # SI LA POSIBLE CUSTOMER NEED ES DESEADA
                if is_possible_customer_need_wanted(possible_customer_need, copy_most_freq_words):

                    # Elimino palabra frecuente para no obtener una customer need parecida
                    most_freq_words.remove(palabra)

                    # Guardo customer need
                    customer_needs_one_word.append(palabra)
                    customer_needs.append(possible_customer_need)

                    print(possible_customer_need, i)
                    break

            # SI LA PALABRA NO ES DE LA MAS FRECUENTES
            else:
                # pasar
                pass

    # podria filtro de frase con sentido...
    print("Customer needs:", customer_needs)
    print("Customer need en una palabra:", customer_needs_one_word)

    return customer_needs, customer_needs_one_word

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

def is_noun(word):
    """
    Identifica si la palabra es un sustantivo o no
    :param word: Palabra
    :return: True si la palabra es sustantivo, o bien, False
    """
    # Proceso palabra
    doc = nlp(word)

    # Obtengo pos (noun, adj, adv, verb, etc) de la palabra
    pos = doc.sentences[0].words[0].pos  # nlp esta preparada para procesar un documento en lugar de una palabra

    # Si palabra es sustantivo
    if pos == "NOUN":
        # retorno True
        return True

    # si palabra no es sustantivo
    else:
        # retorno False
        return False

def delete_irrelevant_words(words):
    """
    Elimina palabras irrelevantes de lista de palabras
    :param words: Lista de palabras
    :return: Lista de palabras sin palabras irrelevantes
    """
    freq_words_filt = []
    pal_irrel = ['android', 'auriculares', 'calidad', 'conforme', 'compra', 'equipo', 'gama', 'netflix', 'notebook',
                 'producto', 'relacion', 'tele', 'telefono', 'televisor', 'tv', 'uso', 'verdad','samsung', 'super',
                 'windows']

    # Por palabra frecuente
    for word in words:

        # Si la palabra es relevante
        if word not in pal_irrel:

            # la guardo
            freq_words_filt.append(word)

    return freq_words_filt

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

    '''
    # d = {'camara': ['camaras', 'foto', 'fotos'], 'memoria': ['fluidez', 'almacenamiento', 'ram', 'disco'],"procesador":["velocidad", "funcionamiento", "software"], 'bateria': 'duracion', ''}

    # Por palabra
    for palabra in l_palabras:

        # SI TIENE PALABRAS ADICIONALES
        if palabra in list(d.keys()):

            # REMUEVO PALABRAS ADICIONALES
            # Por valor
            for valor in d[palabra]:

                # Si esta en la lista
                if valor in l_palabras:

                    # Borro el valor
                    l_palabras.remove(valor)

        # SI ES UNA DE LAS PALABRAS ADICIONALES
        # elif palabra in list(d.values()):
        # REEMPLAZO PALABRA ADICIONAL POR LA CLAVE

        # NO ESTA EN DICCIONARIO DE PALABRAS ADICIONALES
        else:
            pass
    '''

    return l_palabras

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
