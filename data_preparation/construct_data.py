# Uno campos especificos como modelo y marca?
# reemplazo id_pub por id_modelo
# implemento definicion de customer needs

# Importo librerias
import operator
from data_preparation import preparacion_texto as tp


def define_customer_needs(df_tokenizado, campos_esp):
    # el df puede estar steam o no... el ngrams recibe lista como sequuencia
    d = {}
    freq_ngrams = []
    palabra_clave = []

    # print(df_tokenizado)
    df_tokenizado = df_tokenizado[
        'tokens']  # horrible esta linea pero sino me pone el nombre de la columna en cada fila..

    # 2 palabras
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
    sorted_dict = sorted(d.items(), key=operator.itemgetter(
        1))  # Lista con pares key-value ordenados crecientemente segun el value
    sorted_dict = sorted_dict[::-1]  # invierto lista, ahora ordenados descendientemnete

    for item in sorted_dict[:100]:  # hasta los primeros 50
        key = item[0]

        # Por palabra del ngram
        for palabra in key.split():

            # si al menos 1 palabra esta en los campos especificos...
            if palabra in campos_esp:
                print(item)

                # Elimino campo especifico para no obtener una customer need parecida
                campos_esp.remove(palabra)

                # Agrego a palabra claves para poder determinar si una opinion habla o no de una customer need
                palabra_clave.append(palabra)

                # La agrego
                freq_ngrams.append(key)
                break

    # print(freq_bigrams)
    print(palabra_clave)

    '''
    # OBTENER LISTA DE LOS N GRAMS MAS FRECUENTES
    print('++')
    print(d.values())
    sortedDict = sorted(d.items(), key=operator.itemgetter(1))  # ordena par key-value del diccionario segun el value
    print(sortedDict)
    freq_items = sortedDict[-10:]  # seleccionar las 10 maximas frecuencias
    print(freq_items)

    for freq_item in freq_items:
        print(freq_item)
        key = freq_item[0]
        freq_bigrams.append(key)

    print(freq_bigrams)
    '''
    return freq_ngrams, palabra_clave


def generate_n_grams(text, ngram):
    # words = [word for word in text.split(" ") if word not in set(stopwords.words('english'))]
    # print("Sentence after removing stopwords:", text)
    temp = zip(*[text[i:] for i in range(0, ngram)])
    ans = [' '.join(ngram) for ngram in temp]
    return ans


def possible_relevant_words(df_modelos):
    # obtiene palabras de los nombres de las caracteristicas del producto. Podrian ser usadas por los clientes...

    # Obteniendo set de palabras de campos especificos
    a = str()
    for columna in df_modelos.columns[1:]:  # no incluyo id
        name_column = tp.delete_accent(columna).lower()
        a += name_column + " "
    # print("strings:", a)
    l = set(a.split())
    l2 = tp.stop_word_removal(l)  # lista con palabras de campos especificos sin palabras vacias y sin acentos
    # print("set:", l2)
    return l2