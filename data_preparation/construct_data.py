# Importo librerias
import operator
from data_preparation import preparacion_texto as tp


def define_possible_customer_needs(df_tokenizado):
    """
    Obtiene lista de las posibles customer needs de un producto pues son las frases de 3 palabras mas frecuentes en las
    opiniones de dicho producto.
    :param df_tokenizado: Dataframe con columna "tokens" donde cada fila tiene una lista de palabras (puede estar
    lemmatizado, steam o ninguno)
    :return: Lista de las <CANT_POSIBLES_CUSTOMER_NEEDS> frases de 3 palabras mas frecuentes
    """
    # Defino variables
    CANT_POSIBLES_CUSTOMER_NEEDS = 50  # parametro de cuantas mas frecuentes frases buscar. dependera del producto?
    d = {}
    freq_ngrams = []
    idx_token = df_tokenizado.columns.get_loc("tokens")  # agrega flexibilidad pues puedo pasarle el df_opiniones enterro e igual usa solo "opiniones"
    # df_tokenizado = df_tokenizado['tokens']  # horrible esta linea pero sino me pone el nombre de la columna en cada fila..

    # POR OPINION
    for i in range(len(df_tokenizado)):
        opinion = df_tokenizado.iloc[i, idx_token]

        # OBTENGO SUS FRASES DE 3 PALABRAS O "TRIGRAMS" (una opinion estara compuesta de mas de un trigram)
        ngrams = generate_n_grams(opinion, ngram=1)

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
    sorted_dict = sorted(d.items(), key=operator.itemgetter(1))  # Lista con pares key-value ordenados crecientemente segun el value
    sorted_dict = sorted_dict[::-1]  # invierto lista, ahora ordenados descendientemnete

    for item in sorted_dict[:CANT_POSIBLES_CUSTOMER_NEEDS]:  # hasta los primeros x
        key = item[0]
        freq_ngrams.append(key)

    print("Posibles {} Customer needs: {}".format(CANT_POSIBLES_CUSTOMER_NEEDS ,freq_ngrams))

    return freq_ngrams

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

def select_customer_needs(possible_customer_needs, attribute_words):
    """
    De las frases mas frecuentes, selecciono aquellas que seran las customer needs. Para ello, utilizo las palabras
    que forman a los nombres de los atributos del producto.
    :param possible_customer_needs: Lista de las <CANT_POSIBLES_CUSTOMER_NEEDS> frases de 3 palabras mas frecuentes
    :param attribute_words: Lista de palabras unicas de los nombres de las caracteristicas o atributos del producto
    :return: Lista de customer needs como frases de 3 palabras y como 1 sola palabra
    """
    # Defino variables
    customer_needs = []
    customer_needs_one_word = []
    copy_possible_words = attribute_words.copy()
    i = 0

    # Por cada posible customer need
    for possible_customer_need in possible_customer_needs:
        i += 1

        # Por cada palabra de la frase
        for palabra in possible_customer_need.split():

            # Si la palabra es de las relevantes
            if palabra in attribute_words:

                # y la frase solo contiene 1 de las posibles palabras relevantes y no tiene numeros
                if check_not_numeric_or_repeated(possible_customer_need, copy_possible_words):

                    # Elimino campo especifico para no obtener una customer need parecida
                    attribute_words.remove(palabra)

                    # Agrego a palabra claves para poder determinar si una opinion habla o no de una customer need
                    customer_needs_one_word.append(palabra)

                    # La agrego
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

# 3º intento
def get_attributes_name_words(l_col):  # podria quedarme solo con entities o sustantivos, NO ME GUSTA.
    """
    Obtiene las palabras unicas de los nombres de las caracteristicas o atributos del producto. Es probable que el
    cliente use al menos una de ellas en sus opiniones. Asi, podria seleccionar las customer needs de mayor relevancia
    dentro de todas las posibles.
    :param l_col: Lista de todos los atributos del producto
    :return: Lista de palabras unicas de los nombres de las caracteristicas o atributos del producto
    """
    # Defino variable auxiliar (en caso que el nombre de la columna sea mas de 1 palabra)
    aux = str()

    # Por columna en dataframe modelos
    for atributo in l_col:  # no incluyo id

        # Obtengo nombre de la columna sin accentos y en miniscula
        name_column = tp.delete_accent(atributo).lower()
        aux += name_column + " "

    # Guardo palabras unicas de los nombres de los campos especificos
    attr_name_words = set(aux.split())
    attr_name_words = tp.stop_word_removal(attr_name_words)  # lista con palabras de campos especificos sin palabras vacias y sin acentos
    print("Palabras unicas de nombres de atributos:", attr_name_words)

    return attr_name_words

''' # 1 intento
def get_attributes_name_words(df_alt):  # podria quedarme solo con entities o sustantivos, NO ME GUSTA.
    """
    Obtiene las palabras unicas de los nombres de las caracteristicas o atributos del producto. Es probable que el
    cliente use al menos una de ellas en sus opiniones. Asi, podria seleccionar las customer needs de mayor relevancia
    dentro de todas las posibles.
    :param df_alt: Dataframe cuya unidad de analisis es la alternativa de un producto
    :return: Lista de palabras unicas de los nombres de las caracteristicas o atributos del producto
    """
    # Defino variable auxiliar (en caso que el nombre de la columna sea mas de 1 palabra)
    aux = str()

    # Por columna en dataframe modelos
    for columna in df_alt.columns[1:]:  # no incluyo id

        # Obtengo nombre de la columna sin accentos y en miniscula
        name_column = tp.delete_accent(columna).lower()
        aux += name_column + " "

    # Guardo palabras unicas de los nombres de los campos especificos
    attr_name_words = set(aux.split())
    attr_name_words = tp.stop_word_removal(attr_name_words)  # lista con palabras de campos especificos sin palabras vacias y sin acentos
    print("Palabras unicas de nombres de atributos:", attr_name_words)

    return attr_name_words
'''

def check_not_numeric_or_repeated(possible_customer_need, attribute_words):
    """
    Evita customer needs con repeticion (dos que se refieran al mismo atributo) o con numeros
    :param possible_customer_need: Frase de 3 palabras que contiene al menos 1 palabra relevante
    :param attribute_words: Lista de palabras relevantes
    :return: True si contiene una sola palabra relevante y ningun numero, o en caso contrario, False
    """
    # Defino variable
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


'''
def select_customer_needs(possible_customer_needs, attribute_words):
    """
    De las frases mas frecuentes, selecciono aquellas que seran las customer needs. Para ello, utilizo las palabras
    que forman a los nombres de los atributos del producto.
    :param possible_customer_needs: Lista de las <CANT_POSIBLES_CUSTOMER_NEEDS> frases de 3 palabras mas frecuentes
    :param attribute_words: Lista de palabras unicas de los nombres de las caracteristicas o atributos del producto
    :return: Lista de customer needs como frases de 3 palabras y como 1 sola palabra
    """
    # Defino variables
    customer_needs = []
    customer_needs_one_word = []
    copy_possible_words = attribute_words.copy()

    # Por cada posible customer need
    for possible_customer_need in possible_customer_needs:

        # Por cada palabra de la frase
        for palabra in possible_customer_need.split():

            # Si la palabra es de las relevantes
            if palabra in attribute_words:

                # y la frase solo contiene 1 de las posibles palabras relevantes y no tiene numeros
                if check_not_numeric_or_repeated(possible_customer_need, copy_possible_words):

                    # Elimino campo especifico para no obtener una customer need parecida
                    attribute_words.remove(palabra)

                    # Agrego a palabra claves para poder determinar si una opinion habla o no de una customer need
                    customer_needs_one_word.append(palabra)

                    # La agrego
                    customer_needs.append(possible_customer_need)
                    break
            else:
                pass

    # podria filtro de frase con sentido...
    # podria sacar customer needs con dos o mas palabras en possible words usando la copia
    print("Customer needs:", customer_needs)
    print("Customer need en una palabra:", customer_needs_one_word)

    return customer_needs, customer_needs_one_word

def get_attributes_name_words(df_alt):  # podria quedarme solo con entities o sustantivos, NO ME GUSTA.
    """
    Obtiene las palabras unicas de los nombres de las caracteristicas o atributos del producto. Es probable que el
    cliente use al menos una de ellas en sus opiniones. Asi, podria seleccionar las customer needs de mayor relevancia
    dentro de todas las posibles.
    :param df_alt: Dataframe cuya unidad de analisis es la alternativa de un producto
    :return: Lista de palabras unicas de los nombres de las caracteristicas o atributos del producto
    """
    # Defino variable auxiliar (en caso que el nombre de la columna sea mas de 1 palabra)
    aux = str()

    # Por columna en dataframe modelos
    for columna in df_alt.columns[1:]:  # no incluyo id

        # Obtengo nombre de la columna sin accentos y en miniscula
        name_column = tp.delete_accent(columna).lower()
        aux += name_column + " "

    # Guardo palabras unicas de los nombres de los campos especificos
    attr_name_words = set(aux.split())
    attr_name_words = tp.stop_word_removal(attr_name_words)  # lista con palabras de campos especificos sin palabras vacias y sin acentos
    print("Palabras unicas de nombres de atributos:", attr_name_words)

    return attr_name_words

def check_not_numeric_or_repeated(possible_customer_need, attribute_words):
    """
    Evita customer needs con repeticion (dos que se refieran al mismo atributo) o con numeros
    :param possible_customer_need: Frase de 3 palabras que contiene al menos 1 palabra relevante
    :param attribute_words: Lista de palabras relevantes
    :return: True si contiene una sola palabra relevante y ningun numero, o en caso contrario, False
    """
    # Defino variable
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

'''