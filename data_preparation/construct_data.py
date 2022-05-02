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
    # Defino variables
    QUANT_WORDS = 50  # parametro de cuantas mas frecuentes frases buscar. dependera del producto?
    d = {}
    idx_token = df_tokenizado.columns.get_loc("tokens")  # agrega flexibilidad pues puedo pasarle el df_opiniones enterro e igual usa solo "opiniones"

    # POR OPINION
    for i in range(len(df_tokenizado)):
        opinion = df_tokenizado.iloc[i, idx_token]

        # OBTENGO PALABRAS DE OPINION
        ngrams = generate_n_grams(opinion, ngram=1)

        # GUARDO FRECUENCIA DE CADA PALABRA
        # Por cada palabra
        for ngram in ngrams:
            # Si el ngram es sustantivo --> no lo hago aca por costo computacional, entra (cant ngrams de una opi * cant opis) veces...
            # if is_noun(ngram) is True:

            # Si su frecuencia es mayor a 1
            if ngram in d.keys():
                # Sumar uno a su frecuencia
                d[ngram] += 1

            # Si aun no tiene frecuencia
            else:
                # lo inicializo
                d[ngram] = 1

    # OBTENGO LOS N GRAMS MAS FRECUENTES
    freq_ngrams = most_frequent_dict_key(d, QUANT_WORDS)
    print("{} palabras mas frecuentes: {}".format(QUANT_WORDS, freq_ngrams))

    # FILTRO NGRAMS MAS FRECUENTES
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
    # Defino variables
    CANT_POSIBLES_CUSTOMER_NEEDS = 400  # parametro de cuantas mas frecuentes frases buscar. dependera del producto?
    d = {}
    idx_token = df_tokenizado.columns.get_loc("tokens")  # agrega flexibilidad pues puedo pasarle el df_opiniones enterro e igual usa solo "opiniones"

    # POR OPINION
    for i in range(len(df_tokenizado)):
        opinion = df_tokenizado.iloc[i, idx_token]

        # OBTENGO SUS FRASES DE 3 PALABRAS O "TRIGRAMS" (una opinion estara compuesta de mas de un trigram)
        ngrams = generate_n_grams(opinion, ngram=3)

        # GUARDO FRECUENCIAS DE CADA TRIGRAM
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

    # OBTENGO LISTA DE LOS N GRAMS MAS FRECUENTES
    freq_ngrams = most_frequent_dict_key(d, CANT_POSIBLES_CUSTOMER_NEEDS)
    print("Posibles {} Customer needs: {}".format(CANT_POSIBLES_CUSTOMER_NEEDS, freq_ngrams))

    return freq_ngrams

def select_customer_needs(df_tokenizado):
    """
    Selecciona las customer needs de un producto a partir de las frases mas frecuentes en las opiniones del producto
    :param df_tokenizado: Dataframe cuya unidad de analisis es la opinion de un producto. Cada opinion debe estar
    tokenizada, es decir, debe ser una lista cuyos elementos son sus palabras
    :return: Lista de customer needs como frases de 3 palabras, lista de customer needs como frase de 1 sola palabra
    """
    # Defino variables
    customer_needs, customer_needs_one_word = [], []
    print("BUSCO POSIBLES CUSTOMER NEEDS DE UNA PALABRA")
    possible_customer_needs_one_word = most_frequent_words(df_tokenizado)
    print("BUSCO POSIBLES CUSTOMER NEEDS DE TRES PALABRAS")
    possible_customer_needs = most_frequent_phrases(df_tokenizado)
    copy_possible_words = possible_customer_needs_one_word.copy()
    i = 0

    # Por cada posible customer need
    for possible_customer_need in possible_customer_needs:
        i += 1

        # Por cada palabra de la frase
        for palabra in possible_customer_need.split():

            # Si la palabra es de las relevantes
            if palabra in possible_customer_needs_one_word:

                # y la frase solo contiene 1 de las posibles palabras relevantes y no tiene numeros
                if check_not_numeric_or_repeated(possible_customer_need, copy_possible_words):

                    # Elimino campo especifico para no obtener una customer need parecida
                    possible_customer_needs_one_word.remove(palabra)

                    # Guardo customer need
                    customer_needs_one_word.append(palabra)
                    customer_needs.append(possible_customer_need)

                    print(possible_customer_need, i)
                    break
            else:
                pass

    # podria filtro de frase con sentido...
    # podria sacar customer needs con dos o mas palabras en possible words usando la copia
    print("Customer needs:", customer_needs)
    print("Customer need en una palabra:", customer_needs_one_word)

    return customer_needs, customer_needs_one_word

def most_frequent_dict_key(dict, quantity_freq):
    """
    De un diccionario de frecuencias (value es numerico, en particular, la frecuencia de la key), selecciona las keys
    mas frecuentes
    :param dict: Dictionary cuyos values son valores numericos tal que puedo ordenar el diccionario por frecuencia
    :param quantity_freq: Cantidad de palabras a seleccionar de las mas frecuentes
    :return: Lista de palabras mas frecuentes de largo quantity_freq
    """
    l_freq = []

    # Ordeno diccionario de frecuencias por valor
    sorted_dict = sorted(dict.items(), key=operator.itemgetter(1))  # Lista con pares key-value ordenados crecientemente segun el value
    sorted_dict = sorted_dict[::-1]  # invierto lista, ahora ordenados descendientemnete

    # Selecciono las palabras (key de dict) de mayor frecuencia
    for item in sorted_dict[:quantity_freq]:  # hasta los primeros x
        key = item[0]
        l_freq.append(key)

    return l_freq

def generate_n_grams(text, ngram):
    """
    Obtiene lista de los n-grams de un texto
    :param text: Texto tokenizado, es decir, como lista de palabras
    :param ngram: largo de frases a buscar
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
    freq_words_filt = []

    # Por palabra frecuente
    for word in words:

        # Si la palabra es sustantivo
        if is_noun(word) is True:

            # la guardo
            freq_words_filt.append(word)

    return freq_words_filt

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

        # Si la palabra no es irrelevante
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
    # Defino variables
    l = [['camara','camaras', 'foto', 'fotos'], ['memoria', 'fluidez', 'almacenamiento', 'ram', 'disco'], ["procesador",
        "velocidad", "funcionamiento", "software"], ['bateria','duracion'], ['pantalla', 'imagen', 'definicion', 'resolucion'],
         ['sonido','audio','volumen','musica']]

    # Por palabra
    for palabra in l_palabras:

        # Por grupo de palabras relacionadas
        for palabras_rel in l:

            # Si palabra pertenece a grupo de palabras relacionadas
            if palabra in palabras_rel:

                # reemplazar palabra por la cero en palabras rel
                if palabra != palabras_rel[0]:
                    idx = l_palabras.index(palabra)
                    l_palabras[idx] = palabras_rel[0]
                    print("Reemplazo palabra {} por palabra {}".format(palabra, palabras_rel[0]))

                # Remover palabras adicionales si existen...
                for palabra_rel in palabras_rel[1:]:

                    if palabra_rel in l_palabras:

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

def is_noun(word):
    """
    Identifica si la palabra es un sustantivo o no
    :param word: Palabra
    :return: True si la palabra es sustantivo, o bien, False
    """
    # Proceso palabra
    doc = nlp(word)

    # Por frase del doc
    for i, sent in enumerate(doc.sentences):

        # Por palabra de la frase
        for word in sent.words:

            # Imprimo resultados
            # print("{:12s}\t{:12s}\t{:6s}\t{:d}\t{:12s}".format(word.text, word.lemma, word.pos, word.head, word.deprel))

            # Si palabra es sustantivo
            if word.pos == "NOUN":
                # retorno True
                res = True

            # si palabra no es sustantivo
            else:
                # retorno False
                res = False

            return res

def check_not_numeric_or_repeated(possible_customer_need, attribute_words):
    """
    Evita customer needs con repeticion (dos que se refieran al mismo atributo) o con numeros
    :param possible_customer_need: Frase de 3 palabras que contiene al menos 1 palabra relevante
    :param attribute_words: Lista de palabras relevantes
    :return: True si contiene una sola palabra relevante y ningun numero, o en caso contrario, False
    """
    # Defino variable
    n = 0
    pal_irrel = ['android', 'auriculares', 'notebook', 'producto', 'tele', 'telefono', 'televisor', 'tv', 'samsung', 'windows']
    '''
    Por que debo borrar de nuevo palabras irrelevantes?
    Porque si bien no puede ser una customer need de una palabra puede estar presente en la customer need de 3 palabras...
    Por ejemplo, en producto tv elimine android de possible customer needs de one word pero aparecia la siguiente 
    customer need de 3 "sistema operativo android". La obtenia gracias a la palabra "sistema".
    
    Por que no puedo usar la funcion que ya cree para eliminar palabras irrelevantes?
    Borra mas customer needs de las que deseo. Por ejemplo, me borra relacion precio calidad por decir calidad..
    '''

    # Por cada palabra de la frase
    for palabra in possible_customer_need.split():

        # Si la palabra es de las relevantes
        if palabra in attribute_words:
            n += 1

        # Si la frase tiene un numero
        elif palabra.isnumeric():
            # la descarto
            return False

        # Si la frase tiene una palabra irrelevante
        elif palabra in pal_irrel:
            # la descarto
            return False

        else:
            pass

    if n == 1:
        return True
    else:
        return False
