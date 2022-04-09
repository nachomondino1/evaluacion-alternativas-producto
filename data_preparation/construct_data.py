# Uno campos especificos como modelo y marca?
# reemplazo id_pub por id_modelo
# implemento definicion de customer needs

# Importo librerias
import operator
from data_preparation import preparacion_texto as tp


def possible_words_to_identify_customer_needs(df_modelos):  # agreegar notas y mejorar nombres de funciones
    """
    obtiene palabras de los nombres de las caracteristicas del producto. Podrian ser usadas por los clientes...
    Ayuda a poder seleccionar las customer needs de mayor relevancia dentro de todas las posibles
    :param df_modelos:
    :return:
    """

    # Obteniendo set de palabras de campos especificos
    a = str()
    for columna in df_modelos.columns[1:]:  # no incluyo id
        name_column = tp.delete_accent(columna).lower()
        a += name_column + " "
    # print("strings:", a)
    l = set(a.split())
    l2 = tp.stop_word_removal(l)  # lista con palabras de campos especificos sin palabras vacias y sin acentos
    # print("set:", l2)

    print("Posibles palabras relevantes:", l2)

    return l2


def define_possible_customer_needs(df_tokenizado):

    CANT_POSIBLES_CUSTOMER_NEEDS = 200  # dependera del producto?
    # el df puede estar steam o no... el ngrams recibe lista como sequuencia
    d = {}
    freq_ngrams = []

    # print(df_tokenizado)
    df_tokenizado = df_tokenizado[
        'tokens']  # horrible esta linea pero sino me pone el nombre de la columna en cada fila..

    # Obtengo n grams
    for i in range(len(df_tokenizado)):
        opinion = df_tokenizado.iloc[i]

        ngrams = generate_n_grams(opinion, ngram=3)  # es tri en ralidad pero ees para probar

        # Por cada two_gram
        for ngram in ngrams:

            # Si el two_gram ya fue cargado
            if ngram in d.keys():
                # Sumar uno a su frecuencia
                d[ngram] += 1

            # Si el two_gram no fue cargado
            else:
                # lo inicializo
                d[ngram] = 1

    # OBTENER LISTA DE LOS N GRAMS MAS FRECUENTES
    sorted_dict = sorted(d.items(), key=operator.itemgetter(1))  # Lista con pares key-value ordenados crecientemente segun el value
    sorted_dict = sorted_dict[::-1]  # invierto lista, ahora ordenados descendientemnete

    for item in sorted_dict[:CANT_POSIBLES_CUSTOMER_NEEDS]:  # hasta los primeros x
        key = item[0]
        freq_ngrams.append(key)

    print("Posibles {} Customer needs: {}".format(CANT_POSIBLES_CUSTOMER_NEEDS ,freq_ngrams))

    return freq_ngrams


def generate_n_grams(text, ngram):
    # words = [word for word in text.split(" ") if word not in set(stopwords.words('english'))]
    # print("Sentence after removing stopwords:", text)
    temp = zip(*[text[i:] for i in range(0, ngram)])
    ans = [' '.join(ngram) for ngram in temp]
    return ans


def select_customer_needs(df_tokenizado, attribute_words):
    """
    Selecciono de las frases mas frecuentes aquellas que seran las customer needs. Para ello, utilizo las palabras
    que forman a los nombres de los atributos del producto.
    :param freq_ngrams:
    :param possible_words:
    :return:
    """
    # Defino variables
    customer_needs = []
    palabras_clave = []

    copy_possible_words = attribute_words.copy()

    # Defino posibles costumer needs. Aprox 200 frases de 3 palabras, en particular, las mas frecuentes.
    possible_customer_needs = define_possible_customer_needs(df_tokenizado)

    # Por cada posible customer need
    for possible_customer_need in possible_customer_needs:  # hasta los primeros x

        # Por cada palabra de la frase
        for palabra in possible_customer_need.split():

            # Si la palabra es de las relevantes
            if palabra in attribute_words:

                # y la frase solo contiene 1 de las posibles palabras relevantes y no tiene numeros
                if check_not_numeric_or_repeated(possible_customer_need, copy_possible_words):

                    # Elimino campo especifico para no obtener una customer need parecida
                    attribute_words.remove(palabra)

                    # Agrego a palabra claves para poder determinar si una opinion habla o no de una customer need
                    palabras_clave.append(palabra)

                    # La agrego
                    customer_needs.append(possible_customer_need)
                    break
            else:
                pass


    # filtro de frase con sentido...
    # podria sacar customer needs con dos o mas palabras en possible words usando la copia

    print("Customer needs:", customer_needs)
    print("Palabras clave:", palabras_clave)

    return customer_needs, palabras_clave


def check_not_numeric_or_repeated(possible_customer_need, attribute_words):
    # Se fija que una customer need no tenga dos atributos en lugar de uno (evita repeticion)
    n = 0

    # Por cada palabra de la frase
    for palabra in possible_customer_need.split():

        # Si la palabra es de las relevantes
        if palabra in attribute_words:
            n += 1

        # Si la frase tiene un numero
        elif palabra.isnumeric():
            # la descarto
            n = 0
            break

        else:
            pass

    if n == 1:
        return True
    else:
        return False
