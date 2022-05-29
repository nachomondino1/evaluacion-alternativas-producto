# Importo librerias
import pandas as pd
import operator
import pickle
from p3_modelling.sentiment_atribution import contains_word_type

################################################ FUNCIONES PRINCIPALES ################################################
def most_frequent_words(df_opi_tokenizado):
    """
    Obtiene lista de las palabras mas frecuentes utilizadas en las opiniones de un producto
    :param df_opi_tokenizado: Dataframe cuya unidad de analisis es la opinion de un producto. Cada opinion debe estar
    tokenizada, es decir, debe ser una lista cuyos elementos son sus palabras
    :return: Lista de palabras mas frecuentes en opiniones y relevantes
    """
    # Defino variables
    QUANT_WORDS = 200  # parametro de cuantas mas frecuentes frases buscar. dependera del producto?
    d = {}
    idx_token = df_opi_tokenizado.columns.get_loc("opinion")  # agrega flexibilidad pues puedo pasarle el df_opiniones enterro e igual usa solo "opiniones"
    freq_ngrams_filt = []

    # POR OPINION
    for i in range(len(df_opi_tokenizado)):
        opinion = df_opi_tokenizado.iloc[i, idx_token]

        # POR PALABRA
        for palabra in opinion:

            # SUMO 1 A SU FRECUENCIA
            if palabra in d.keys():  # Si su frecuencia es mayor a 1
                d[palabra] += 1  # Sumar uno a su frecuencia
            else:  # Si aun no tiene frecuencia
                d[palabra] = 1 # lo inicializo

    # OBTENGO LAS PALABRAS MAS FRECUENTES
    freq_ngrams = most_frequent_dict_key(d, QUANT_WORDS)
    print("{} palabras mas frecuentes: {}".format(QUANT_WORDS, freq_ngrams))

    # FILTRO LAS PALABRAS MAS FRECUENTES
    print("Filtro palabras mas frecuentes")
    # Por palabra frecuente
    for palabra in freq_ngrams:

        # Si es sustantivo
        if contains_word_type(text=palabra, word_type=['NOUN']):  # if is_noun(palabra):

            # Si no es una palabra irrelevante
            if not is_irrelevant_word(palabra):

                # La guardo
                freq_ngrams_filt.append(palabra)

    # Elimono palabras relacionadas para evitar repeticion de customer needs
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
    CANT_POSIBLES_CUSTOMER_NEEDS = 4000  # parametro de cuantas mas frecuentes frases buscar. dependera del producto?
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
    print("Posibles customer needs: {}".format(freq_ngrams))      # print("Primeras {} posibles customer needs: {}".format(100, freq_ngrams[:100]))

    return freq_ngrams

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

        # Print resumen de cuantos ptos tiene cada customer need
        print("{:^40s}\t{:^40}".format("Customer need", "Suma de ptos de relaciones"))
        for cust_need in df_relation_matrix.index:
            print("{:^40s}\t{:^40}".format(cust_need, sum(df_relation_matrix.loc[cust_need].dropna())))

        '''
        # Si el atributo no tiene relacion con ninguna customer need       
        if sum(df_relation_matrix[atributo]) == 0:
            df_relation_matrix = df_relation_matrix.drop([atributo], axis=0)
        '''

    return df_relation_matrix


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


# UTILIZADA EN MOST_FREQUENT_WORDS()
def is_irrelevant_word(word):
    """
    Determina si una palabra es relevante o no para la seleccion de customer needs.
    :param word: String. Una sola palabra
    :return: True si la palabra es irrelevante para la seleccion de customer needs, de lo contrario, False
    """
    # Defino lista de palabras irrelevantes
    pal_irrel = ['android', 'año', 'años',
                 'calidad', 'conforme', 'compra', 'cosas', 'color', 'compu', 'cosa', 'caso', 'cuidado',
                 'descripcion',
                 'equipo', 'expectativas', 'encanto', 'estrellas', 'espectativas',
                 'funcion', 'funciones',
                 'gama', 'gusto', 'gracias', 'general',
                 'hora', 'horas', 'hs',
                 'mano', 'mes', 'meses', 'momento', 'maquina', 'modelo',
                 'netflix', 'nota',
                 'preciocalidad', 'persona', 'personas', 'prestaciones', 'producto', 'problema', 'problemas', 'punto', 'puntos', 'publicacion', 'poder',
                 'redes', 'relacion', 'rendimiento', 'resto', 'regalo', 'respecto',
                 'tiempo', 'tipo',
                 'uso',
                 'verdad',
                 'semana', 'super',
                 'whatsapp', 'windows']

    pal_irrel_cel = ['celulares', 'iphone','telefono']
    pal_irrel_tablets = ['tablet', 'tablets']
    pal_irrel_note = ['computadora','notebook', 'pc']
    pal_irrel_auris = ['auriculares', 'auris']
    pal_irrel_tv = ['tele', 'televisor', 'tv', 'control', 'remoto', 'canales', 'teclado', 'patas', 'smart', 'opcion', 'led', 'configuracion', 'marcas', 'internet', 'wifi', 'apps', 'conexion', 'video', 'chromecast', 'soporte', 'velocidad', 'falta', 'botones', 'pared', 'poder', 'boton', 'respuesta', 'parte', 'peliculas', 'prime'] # palabras que descarte en tv para seleccionar cust needs
    pal_irrel_smartband = ['smartwatch', 'band', 'pulsera', 'reloj', 'malla', 'gps', 'muñeca', 'datos', 'medicion', 'auriculares', 'entrenamiento', 'control', 'sangre', 'actividades', 'calorias', 'opcion', 'materiales', 'deporte', 'relojes', 'opciones']

    pal_irrel += pal_irrel_smartband

    # Si la palabra no es relvante
    if word in pal_irrel:
        return True
    # Si la palabra es relvante
    else:
        return False

def delete_related_words(l_palabras):
    """
    Elimina palabras que se refieran a una misma caracterisitca del producto dejando una sola de ellas
    :param l_palabras: Lista de palabras
    :return: Lista de palabras sin palabras que se refieran a una misma caracteristica
    """
    # Defino funcion
    find_related_words = lambda word, d_rel_words: d_rel_words[word] if word in d_rel_words.keys() else [word]

    # Importo diccionario de palabras relacionadas
    with open("d_rel_words.pkl", "rb") as tf:
        d_rel_words = pickle.load(tf)

    # Convierto lista de palabras a string
    str_palabras = "   ".join(l_palabras)  # agrego espacios porque eliminare strings que tienen espacios para evitar identificiarlo mal en opiniones

    # Por palabra
    for palabra in l_palabras:

        '''
        # ELIMINO PALABRA EN PLURAL DE LISTA
        # Por palabra en plural
        for palabra_plural in palabras_plural(palabra):
            # Si esta la palabra en plural
            if palabra_plural in str_palabras:
                # La remuevo
                str_palabras = delete_substring_in_string(str_palabras, palabra_plural)
                print("Se removio palabra '{}' dado que ya esta '{}'".format(palabra_plural, palabra))
        '''

        # ELIMINO PALABRAS RELACIONADAS DE LISTA
        # Obtengo sus palabras relacionadas
        l_related_words = find_related_words(palabra, d_rel_words)[1:]

        # Por palabra relacionada
        for word in l_related_words:  # sin incluir palabra propiamente

            # Si esta en lista de palabras
            if word in str_palabras:
                # La remuevo
                str_palabras = delete_substring_in_string(str_palabras, word)
                print("Se removio palabra '{}' dado que ya esta '{}'".format(word, palabra))

    return str_palabras.split()

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

def delete_substring_in_string(string, substring):  # falta doc
    if substring in string:
        idx_ini = string.find(substring)
        string_cleaned = string[:idx_ini] + string[idx_ini + len(substring) + 1:]
    else:
        string_cleaned = string
        print("No se encontro el substring {} en el string {}".format(substring, string))

    return string_cleaned


# UTILIZADA EN MOST_FREQUENT_PHRASES()
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



'''
def customer_needs_translation(l_cust_needs, cust_need):  # no se que enombre ponerle, busca relacion entre customer needs de 3 palabras y las de 1...
    # ES NECESARIA? O PUEDO USAR DF_CUST_NEEDS?
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
'''




'''
def select_attr_and_cust_needs(df_alt, df_cust_needs):
    """
    Permite seleccionar atributos y customer needs a traves de terminal
    :param l_atributos: Lista de atributos del producto
    :param l_cust_needs: Lista de customer needs del producto de 1 palabra
    :param l_cust_need_three_words: Lista de customer needs del producto de 3 palabras
    :return: Listas pasadas por parametro filtradas
    """
    # SELECCIONO ATRIBUTOS
    print("Selecciona atributos que se relacionaran con customer needs (evitar atributos extraidos unicamente para ser mostrados al cliente):")
    l_atributos_filt = drop_unwanted_elements(df_alt.columns[2:])  # elimino atributos no deseados

    # ELIMINO ATRIBUTOS NO RELEVANTES DE DATAFRAME ALTERNATIVAS
    # Por atributo
    for atributo in df_alt.columns[2:]:
        # Si no es relevante
        if atributo not in l_atributos_filt:
            # Elimino atributo
            df_alt = df_alt.drop([atributo], axis=1)

    # SELECCIONO CUSTOMER NEEDS
    print("Selecciona customer needs que se relacionaran con atributos (evitar customer needs que se refieran a lo mismo):")

    l_cust_needs_three = df_cust_needs['cust_needs_three_words']
    l_cust_needs_three_filt = drop_unwanted_elements(l_cust_needs_three)  # elimino atributos no deseados

    # ELIMINO CUSTOMER NEEDS NO RELEVANTES DE DATAFRAME DE CUSTOMER NEEDS
    # Por customer need
    for cust_need in df_cust_needs['cust_needs_three_words']:
        # Si no es relevante
        if cust_need not in l_cust_needs_three_filt:
            # Elimino customer need
            idx = df_cust_needs.index[df_cust_needs['cust_needs_three_words'] == cust_need]
            df_cust_needs = df_cust_needs.drop([idx], axis=0)

    """
    # Defino variables
    l_cust_needs_three_words_filt = []

    print("Selecciona atributos que se relacionaran con customer needs (evitar atributos extraidos unicamente para ser mostrados al cliente):")
    l_atributos_filt = drop_unwanted_elements(l_atributos)  # elimino atributos no deseados

    print("Selecciona customer needs que se relacionaran con atributos (evitar customer needs que se refieran a lo mismo):")
    l_cust_needs_filt = drop_unwanted_elements(l_cust_needs)  # elimino atributos no deseados

    # Por customer need de 1 palabra
    for cust_need in l_cust_needs_filt:
        # Selecciono su customer need de tres palabras
        l_cust_needs_three_words_filt.append(customer_needs_translation(l_cust_need_three_words, cust_need))
    """


    """
    # Borrar atributos de dataframe alternativas cleaned que no esten en l_atributos
    for atributo in df_alt_cleaned.columns[1:]:
        if atributo not in l_atributos:
            df_alt_cleaned = df_alt_cleaned.drop([atributo], axis=1)
    print()
    """

    # return l_atributos_filt, l_cust_needs_filt, l_cust_needs_three_words_filt
    return df_alt, df_cust_needs
'''

'''
def drop_unwanted_elements(l):
    """
    Permite seleccionar los elementos mas relevantes de una lista
    :param l: Lista
    :return: Lista con elementos relevantes
    """
    # Defino variable
    l_wanted = []  # Lista a retornar

    # Por elemento
    for element in l:

        # Mientras la carga sea invalida
        while True:
            try:
                # Solicito 0 o 1 para determinar si el atributo sera considerado o no
                bool = int(input("Tendra en cuenta el elemento '{}' (0 o 1): ".format(element.upper())))

                # si el atribuo sera considerado
                if bool == 0:
                    break

                elif bool == 1:
                    l_wanted.append(element)
                    break

            except ValueError:  # si el input no es un numero entero
                pass
    return l_wanted
'''


'''
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
'''


''' En desuso por contains_word_type
def is_noun(word): 
    """
    Identifica si la palabra es un sustantivo o no
    :param word: Palabra
    :return: True si la palabra es sustantivo, o bien, False
    """
    # Proceso palabra
    doc = pos_tagger(word)  # esta preparada para procesar un documento en lugar de una palabra
    pos = doc.sentences[0].words[0].pos  # Obtengo pos (noun, adj, adv, verb, etc) de la palabra

    # Si palabra es sustantivo
    if pos == "NOUN":
        return True  # retorno True
    # si palabra no es sustantivo
    else:
        return False  # retorno False
'''


'''
    pal_irrel = ['android', 'año', 'años', 'auriculares', 'auris',
                 'band',
                 'calidad', 'conforme', 'compra', 'cosas', 'celulares', 'color', 'compu', 'computadora', 'cosa', 'caso', 'cuidado',
                 'equipo', 'expectativas', 'encanto', 'estrellas',
                 'funcion', 'funciones',
                 'gama', 'gusto', 'gracias', 'general',
                 'hora', 'horas', 'hs',
                 'iphone',
                 'mano', 'mes', 'meses', 'momento', 'maquina', 'modelo',
                 'netflix', 'notebook', 'nota',
                 'preciocalidad', 'persona', 'personas', 'prestaciones', 'producto', 'problema', 'problemas', 'pulsera', 'pc', 'punto', 'puntos', 'publicacion',
                 'redes', 'relacion', 'rendimiento', 'resto', 'reloj', 'regalo', 'respecto',
                 'tele', 'telefono', 'televisor', 'tiempo', 'tv', 'tablet', 'tablets', 'tipo',
                 'uso',
                 'verdad',
                 'semana', 'super',
                 'whatsapp', 'windows']

'''