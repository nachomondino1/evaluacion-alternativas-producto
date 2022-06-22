# Importo librerias
import pandas as pd
import operator
from p3_modelling.sentiment_atribution import contains_word_type

################################################ FUNCIONES PRINCIPALES ################################################
def most_frequent_ngrams(df_opi_tokenizado, n_ngram, QUANT_NGRAMS): # acordate que no se puede probar individualmente porque se levanta mal el df_opi_tokenizado (en vez de lista lo entinede como string)
    """
    Obtiene lista de los ngrams mas frecuentes utilizados en las opiniones de un producto
    :param QUANT_NGRAMS: Parametro de cuantas palabras mas frecuentes buscar
    :param df_opi_tokenizado: Dataframe cuya unidad de analisis es la opinion de un producto. Cada opinion debe estar
    tokenizada, es decir, debe ser una lista cuyos elementos son sus palabras
    :return: Lista de palabras mas frecuentes en opiniones y relevantes
    """
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

    # OBTENGO LISTA DE LOS 3-GRAMS MAS FRECUENTES
    l_freq_ngrams = most_frequent_dict_key(d, QUANT_NGRAMS)
    print("{} frases de {} palabra mas frecuentes: {}".format(QUANT_NGRAMS, n_ngram, l_freq_ngrams))

    # Exporto dataframe de palabras mas frecuentes (momentaneamente lo pongo aca)
    if n_ngram == 1:
        df = pd.DataFrame(data=d.values(), columns=['frecuencia'], index=d.keys())
        df = df.sort_values(by='frecuencia', ascending=False)  # sorted() no es para dataframes
        df.to_excel('/Users/nachomondino/Desktop/df_most_freq_words.xlsx')

    return l_freq_ngrams

def filter_most_frequent_words(l_freq_words, d_rel_words):
    # Filtro lista de palabras mas frecuentes!

    # DEFINO VARIABLES
    l_freq_words_filt = []
    l_pal_irrel = ['android', 'año', 'años', 'amazon',
                 'calidad', 'conforme', 'compra', 'cosas', 'color', 'compu', 'cosa', 'caso', 'cuidado',
                 'descripcion', 'disney',
                 'equipo', 'expectativas', 'encanto', 'estrellas', 'espectativas',
                 'funcion', 'flow',
                 'gama', 'gusto', 'gracias', 'general', 'google', 'gb',
                 'hora', 'horas', 'hs',
                 'mano', 'mes', 'meses', 'momento', 'maquina', 'modelo',
                 'netflix', 'nota',
                 'preciocalidad', 'persona', 'personas', 'prestaciones', 'producto', 'problema', 'problemas', 'punto', 'puntos', 'publicacion', 'poder', 'pena',
                 'redes', 'relacion', 'rendimiento', 'resto', 'regalo', 'respecto',
                 'tiempo', 'tipo', 'tv',
                 'uso',
                 'verdad',
                 'semana', 'super',
                 'youtube',
                 'whatsapp', 'windows']

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

def select_customer_needs(l_most_freq_words, l_possible_customer_needs):
    """
    Selecciona las customer needs de un producto a partir de las frases mas frecuentes en las opiniones del producto
    :param most_freq_words: Lista de palabras mas frecuentes en opiniones y relevantes
    :param possible_customer_needs: Lista de frases de 3 palabras mas frecuentes en opiniones
    :return: Lista de customer needs como frases de 3 palabras, lista de customer needs como frase de 1 sola palabra
    """
    # Defino variables
    df_cust_needs = pd.DataFrame(columns=["cust_needs_three_words"])  # Dataframe a retornar
    i = 0
    print("{:^40s}\t{:^40}".format("Posible customer need", "Posicion en frecuencia "))

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

                # y si ademas contiene al menos un adjetivo o adverbio:
                # if contains_word_type(text=possible_customer_need, word_type=['ADJ', 'ADV']) or possible_customer_need == 'relacion precio calidad':

                # Pregunto a administrador
                # Mientras la carga sea invalida
                try:
                    # Solicito 0 o 1 para determinar si customer need sera considerada o no
                    bool = input("Ingrese 'y' si tendra en cuenta la customer need '{} de posicion {}': ".format(possible_customer_need.upper(), i))

                    if bool == "y":
                        # Guardo customer need
                        df_cust_needs.loc[freq_word] = possible_customer_need
                        print("{:^40s}\t{:^40}".format(possible_customer_need, i))

                except ValueError:  # si el input no es un numero entero
                    pass

                # df_cust_needs.loc[freq_word] = possible_customer_need

                # print("{:^40s}\t{:^40}".format(possible_customer_need, i))

                #else:
                #    print("La customer need '{}' fue descartada por no contener ADJ ni ADV".format(possible_customer_need))

    # ELIMINO CUSTOMER NEEDS NO DESEADAS
    print("Seleccionar customer needs:")  # Evito repeticion como "calidad fotos videos" y "tiene buena camara", customer needs quee no tienen atributos para relacionar como "tiene buen sonido"
    df_cust_needs = discard_unwanted_cust_needs(df_cust_needs)

    # Imprimo resultados
    print("Customer needs seleccionadas:")
    print(df_cust_needs)
    return df_cust_needs

def create_relation_matrix(l_atributos, l_cust_needs):
    """
    Crea matriz de relaciones entre customer needs y atributos del producto. Para ello, pide al usuario por terminal
    la relacion entre cada uno.
    :param l_atributos: Lista de atributos o campos especificos de un producto
    :param l_cust_needs: Lista de customer needs (de 1 sola palabra) de un producto
    :return: Dataframe con atributos como columnas y customer needs como filas. Celda indica relacion entre customer
    need  i y atributo j
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

    # Si el atributo no tiene relacion con ninguna customer need
    # Por customer need
    for customer_need in l_cust_needs:

        # Si no tiene relacion con ningun atributo
        if sum(df_relation_matrix.loc[customer_need]) == 0:

            # Creo atributo con el cual relacionarla
            df_relation_matrix[customer_need] = 0

            # Asigno relacion de 9 con atributo creado
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


def palabras_plural(palabra): # falta doc y ver si la dejo
    """
    Obtiene la palabra en plural
    :param palabra: String. Cadena de texto. Una sola palabra
    :return: Lista de posibles palabras en plural de palabra pasada como parametro
    """
    plurales = ["s", 'es']
    palabra_en_plural = []

    for i in range(len(plurales)):
        palabra_en_plural.append(palabra+plurales[i])
    return palabra_en_plural


# UTILIZADA EN SELECT_CUSTOMER_NEEDS()
def freq_word_in_cust_need(possible_customer_need, l_most_freq_words):
    l_freq_words_in_cust_need = []

    # POR CADA PALABRA DE ESTA
    for palabra in possible_customer_need.split():

        # SI LA PALABRA ES DE LA MAS FRECUENTES
        if palabra in l_most_freq_words:
            l_freq_words_in_cust_need.append(palabra)

    return l_freq_words_in_cust_need

def is_possible_customer_need_wanted(possible_customer_need, most_freq_words):  # en desuso temporalmente
    """
    Evita seleccionar una posible customer need que contenga un numero, una palabra irrelevante o dos o mas palabras
    de las mas frecuentes
    :param possible_customer_need: Frase de 3 palabras que contiene al menos 1 palabra relevante
    :param most_freq_words: Lista de palabras mas frecuentes
    :return: True si la customer need es deseada, o en caso contrario, False
    """
    # Defino variable
    n = 0
    # pal_irrel = ['android', 'auriculares', 'notebook', 'producto', 'tele', 'telefono', 'televisor', 'tv', 'samsung', 'windows']

    # Si la customer need contiene al menos un adjetivo
    if contains_adjective(possible_customer_need):

        # POR CADA PALABRA DE LA POSIBLE CUSTOMER NEED
        for palabra in possible_customer_need.split():

            # SI LA PALABRA ES DE LAS MAS FRECUENTES
            if palabra in most_freq_words:

                # sumo uno a cantidad de palabras mas frecuentes de la frase
                n += 1

            # SI LA PALABRA ES UN NUMERO O ES IRRELEVANTE
            elif palabra.isnumeric(): #or palabra in pal_irrel:
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

    # Si la customer need no contiene al menos un adjetivo
    else:
        print("La customer need '{}' es descartada por no contener adjetivos".format(possible_customer_need))
        return False

def discard_unwanted_cust_needs(df_cust_needs):
    """
    Permite seleccionar customer needs mas relvantes a traves de terminal
    :param df_cust_needs: Dataframe con customer needs de 3 palabras en columna y con customer needs de 1 palabra en
    index
    :return: Dataframe pasado por parametro sin customer needs irrelevantes
    """
    # Defino variable
    l_cust_needs_remove = []  # lista de customer needs a remover

    # Por customer need
    for customer_need in df_cust_needs.index:

        # Mientras la carga sea invalida
        while True:
            try:
                # Solicito 0 o 1 para determinar si customer need sera considerada o no
                bool = int(input("Tendra en cuenta la customer need '{}' (0 o 1): ".format(customer_need.upper())))

                # Si la carga es valida
                if bool == 0 or bool == 1:

                    # Si la customer need se refiere a lo mismo que otra customer need, o bien, no tiene atributo con el que relacionarse
                    if bool == 0:
                        # Elimino customer need
                        l_cust_needs_remove.append(customer_need)
                    break

            except ValueError:  # si el input no es un numero entero
                pass

    # ELIMINO CUSTOMER NEEDS NO RELEVANTES DE DATAFRAME DE CUSTOMER NEEDS
    df_cust_needs = df_cust_needs.drop(l_cust_needs_remove, axis=0)
    return df_cust_needs

def main(df_alt_cleaned, df_opi_tokenizado):
    print("Obtengo palabras mas frecuentes en opiniones...".center(120))
    l_most_freq_words = most_frequent_words(df_opi_tokenizado)
    print()

    print("Obtengo frases de 3 palabras mas frecuentes en opiniones...".center(120))
    l_possible_customer_needs = most_frequent_phrases(df_opi_tokenizado)
    print()

    print("Selecciono customer needs del producto...".center(120))
    df_cust_needs = select_customer_needs(l_most_freq_words, l_possible_customer_needs)
    print()

    print("Selecciono atributos y customer needs del producto que se relacionaran entre si...".center(120))
    df_alt_cleaned = select_attributes(df_alt_cleaned)

    print("Obtengo matriz de relaciones...".center(120))
    df_relation_matrix = create_relation_matrix(list(df_alt_cleaned.columns[1:]), list(df_cust_needs.index))

    return df_alt_cleaned, df_cust_needs, df_relation_matrix

'''
# para correr pruebas en archivo independientemente de main.py
df_alt_cleaned = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/celulares/df_alt_cleaned.xlsx')
df_opi_tokenizado = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/celulares/df_opi_cleaned.xlsx', index_col=0)
print(df_alt_cleaned)
print(df_opi_tokenizado)
main(df_alt_cleaned, df_opi_tokenizado)
'''
