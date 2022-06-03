# Importo librerias
import pandas as pd
from pysentimiento import create_analyzer
import stanza
import pickle
import statistics as st

analyzer = create_analyzer(task="sentiment", lang="es")  # para realizar el sentiment
pos_tagger = stanza.Pipeline(lang='es', processors='tokenize,pos,mwt')

################################################ FUNCIONES PRINCIPALES ################################################
def to_customer_needs(df_opi, l_customer_needs_one_word):
    """
    Identifica, si hay, customer needs en opiniones y asigna el sentiment a cada una mediante la libreria pysentimiento
    :param df_opi: Dataframe opiniones cuya unidad de analisis son opiniones que no tienen procesamiento
    :param l_customer_needs_one_word: Lista de customer needs como frases de 1 sola palabra
    :return: Dataframe cuya unidad de analisis es una opinion y cuyas columnas son cada customer need. La celda es el
    sentiment de la customer need en la opinion, o bien si la opinion no habla de la customer need, None.
    """
    # DEFINO VARIABLES
    idx_id, idx_opi = df_opi.columns.get_loc("id_alternativa"), df_opi.columns.get_loc("opinion")  # indices utiles para tener flexibilidad en codigo (posibilidad de columnas en otra posicion)
    df_cust_needs_sent = pd.DataFrame(columns=["id_alternativa"] + l_customer_needs_one_word)  # dataframe a retornar
    choose_sep = lambda text: "," if text.count(",") >= 1 else ';'
    split_frase_in_commas = lambda frase: frase.split(choose_sep(frase)) if conviene_separar_comas(frase) else [frase]

    # POR OPINION
    for i in range(len(df_opi)):

        # Defino variables
        id, opinion = df_opi.iloc[i, idx_id], delete_parentesis(df_opi.iloc[i, idx_opi])  # Defino id y opinion sin parentesis
        fila_df = [id]  # inicializo variable que guardara la fila del nuevo dataframe
        df_frases_cust_needs = pd.DataFrame(columns=l_customer_needs_one_word)  # Dataframe con sent de frases de opinion
        cont = 0

        # OBTENGO SENTIMENT DE OPINION
        sent_opi = sentiment(sentence=opinion)

        # Imprimo para seguir funcionamiento de la funcion
        print("NºFila: {}".center(120).format(i)), print("OPINION:", opinion)
        print("\t Sentiment de toda la opinion: {:.2f}".format(sent_opi))
        print("Divido la opinion en {} frases.".format(len(opinion.split("."))))

        # POR FRASE DE LA OPINION
        for frase in opinion.split("."):

            # OBTENGO SENTIMENT DE FRASE
            sent_frase = sentiment(sentence=frase)

            # IDENTIFICO QUE CUSTOMER NEEDS MENCIONA
            frase_limpia = " " + delete_accent(frase.lower()) + " " # limpio la frase para poder identificar customer needs en ella. Agrego espacios para identificar la primera y la ultima palabra
            d_cust_needs_mentioned = words_mentioned_in_text(words=l_customer_needs_one_word, text=frase_limpia)  # diccionario con customer needs como key y 1 o 0 como value segun si la frase la menciona o no.
            n_cust_need_ment = sum(d_cust_needs_mentioned.values())  # numero de customer needs mencionadas en frase

            # Imprimo para seguir funcionamiento de la funcion
            cont += 1
            print("FRASE Nº{}: {}".format(cont, frase)), print("\t Sentiment de la frase: {:.2f}".format(sent_frase))

            # SI MENCIONA AL MENOS 2 CUSTOMER NEEDS Y EL SENTIMENT NO ES CATEGORICO
            if (n_cust_need_ment >= 2) and (sent_frase < 0.5 and sent_frase > -0.5):

                # Divido frase segun comas
                frases_entre_comas = split_frase_in_commas(frase)
                print("Divido frase Nº{} en {} frase entre comas".format(cont, len(frases_entre_comas)))

                # Por frase entre comas
                for sentence in frases_entre_comas:

                    # Identifico customer need en frase entre comas
                    sentence_limpia = " " + delete_accent(sentence.lower()) + " "
                    d_cust_needs_mentioned = words_mentioned_in_text(words=l_customer_needs_one_word, text=sentence_limpia)
                    print("\t FRASE ENTRE COMAS: ", sentence)

                    # Si hay una customer need
                    if sum(d_cust_needs_mentioned.values()) >= 1:

                        # Obtengo sentiment de frase entre comas
                        sent_frase_entre_comas = sentiment(sentence=sentence)
                        print("\t\t Sentiment de frase entre comas: {:.2f}".format(sent_frase_entre_comas))

                        # Si contiene adjetivos
                        if contains_word_type(text=sentence, word_type=['ADJ']):

                            # Si el sentiment de la frase no se corresponde con el de la opinion  ---> FALTA DOC
                            if (sent_opi < -0.9 and sent_frase_entre_comas > 0 and sent_frase_entre_comas < 0.28) or (sent_opi > 0.9 and sent_frase_entre_comas > -0.28 and sent_frase_entre_comas < 0):

                                # Pondero sentiment
                                sent_frase_entre_comas = 0.8 * sent_frase_entre_comas + 0.2 * sent_opi
                                print("\t\t Es probable que el sentiment de la frase sea incorrecto dado que el de la opinion es totalmente opuesto.", end=" ")
                                print("\t\t Sentiment ponderado = {:.2f} ".format(sent_frase_entre_comas))

                            df_frases_cust_needs.loc[len(df_frases_cust_needs)] = assign_sentiment(d_cust_needs_mentioned, sent_frase_entre_comas)  # df_frases_cust_needs.loc[len(df_frases_cust_needs)] = lambda x, y: assign_sentiment(x,y) if sum(x.values()) > 1 else

                        # Si no hay adjetivos  # pero el sentiment de la frase entre comas es categorico tal como el de la opinion
                        elif (sent_opi < -0.8 and sent_frase_entre_comas < -0.5) or (sent_opi > 0.8 and sent_frase_entre_comas > 0.5):
                            print("c1) La frase no contiene adjetivos pero se guardara el sentiment de todas maneras")
                            df_frases_cust_needs.loc[len(df_frases_cust_needs)] = assign_sentiment(d_cust_needs_mentioned, sent_frase_entre_comas)

                        #Si no hay adjetivos, pero si el sentiment de la frase es categorico independientemente del de la opinion
                        elif sent_frase_entre_comas > 0.8 or sent_frase_entre_comas < -0.8:  # nuevo
                            print("c2) La frase no contiene adjetivos pero se guardara el sentiment de todas maneras")
                            df_frases_cust_needs.loc[len(df_frases_cust_needs)] = assign_sentiment(d_cust_needs_mentioned, sent_frase_entre_comas)

                        else:
                            print("La frase no contiene adjetivos")

                    # Si no hay customer needs
                    else:
                        print("\t\t La frase no contiene customer needs")

            # SI MENCIONA UNA CUSTOMER NEED
            elif n_cust_need_ment >= 1:  # ojo que puede haber frases que mencionen mas de una y sea categorica

                # SI CONTIENE AL MENOS UN ADJETIVO
                if contains_word_type(text=frase, word_type=['ADJ']):

                    # PRUEBA
                    if (sent_opi < -0.9 and sent_frase > 0 and sent_frase < 0.28) or (sent_opi > 0.9 and sent_frase > -0.28 and sent_frase < 0):

                        # Pondero sentiment
                        sent_frase = 0.8 * sent_frase + 0.2 * sent_opi
                        print("\t Es probable que el sentiment de la frase sea incorrecto dado que el de la opinion es totalmente opuesto.", end=" ")
                        print("\t Sentiment ponderado = {:.2f} ".format(sent_frase))

                    # ASIGNO SENTIMENT A CUSTOMER NEED MENCIONADA
                    df_frases_cust_needs.loc[len(df_frases_cust_needs)] = assign_sentiment(d_cust_needs_mentioned, sent_frase)

                # SI NO CONTIENE ADJETIVOS, PERO el sentiment de la opinion es categorico y el de la frasee no categ
                elif (sent_opi < -0.8 and sent_frase < -0.5) or (sent_opi > 0.8 and sent_frase > 0.5):
                    df_frases_cust_needs.loc[len(df_frases_cust_needs)] = assign_sentiment(d_cust_needs_mentioned, sent_frase)
                    print("c1) La frase no contiene adjetivos pero se guardara el sentiment de todas maneras")

                # SI NO CONTIENE ADJETIVOS,  pero si el sentiment de la frase es categorico independientemente del de la opinion
                elif sent_frase > 0.8 or sent_frase < -0.8:  # nuevo
                    df_frases_cust_needs.loc[len(df_frases_cust_needs)] = assign_sentiment(d_cust_needs_mentioned, sent_frase)
                    print("c2) La frase no contiene adjetivos pero se guardara el sentiment de todas maneras")

                else:
                    print("\t La frase no contiene adjetivos")

            # SI NO MENCIONA CUSTOMER NEEDS
            else:
                pass

        # OBTENGO SENTIMENT DE CUSTOMER NEEDS EN OPINION (pues puede aparecer en mas de una frase)
        # Por customer need
        for customer_need in l_customer_needs_one_word:

            # Obtengo promedio de sentiment en frases en que es mencionada
            sent_cn_opi = df_frases_cust_needs[customer_need].dropna().mean()
            # print("Customer need: {}, sentiment: {}".format(customer_need, sent_cn_opi))

            # Guardo el sentiment de la customer need en la opinion
            fila_df.append(sent_cn_opi)

        # GUARDO SENTIMENT DE LAS CUSTOMER NEEDS EN LA OPINION
        df_cust_needs_sent.loc[i] = fila_df
        # print("Fila:", fila_df)

    return df_cust_needs_sent

def to_attribute_value(df_alt, df_cust_needs_sent, df_relation_matrix):
    """
    Mediante la matriz de relaciones, atribuyo los sentiment de las customer needs a los valores de los atributos del
    producto. Tendre que considerar la complicacion de la cantidad de opiniones en que se basa el sentiment de cada
    valor.
    :param df_alt: Dataframe cuya unidad de analisis es cada una de las alternativas del producto, sus columnas son
    los atributos del producto y las celdas el valor que toma el atributo en una alternativa
    :param df_cust_needs_sent: Dataframe cuya unidad de analisis es una opinion, sus columnas son cada customer
    need y las celdas el sentiment o score de la customer need en la opinion
    :param df_relation_matrix: Dataframe con atributos como columnas y customer needs como filas. Celda indica relacion
    entre customer need i y atributo j
    :return: Dataframe cuya unidad de analisis son los valores de los atributos del producto. Sus columnas son valor,
     atributo al que perenece y su sentiment
    """
    # Defino sentiment que retornare
    df_values_attrs_sent_pond = pd.DataFrame(columns=['atributo', 'valor', 'sent'])
    df_attr_value_sent_2 = pd.DataFrame(columns=['atributo', 'valor', 'cant_opi_con_sent', 'sent'])

    # POR CAMPO ESPECIFICO O ATRIBUTO DEL PRODUCTO
    for atributo in df_relation_matrix.columns:
        print(atributo.upper().center(120))

        # Defino variables
        df_values_attr_sent = pd.DataFrame(columns=['atributo', 'valor', 'cant_opi_con_sent', 'sent'])  # Dataframe para valores del atributo
        sum_relaciones = sum(df_relation_matrix[atributo])  # suma de valores de relaciones que tiene el atributo

        # POR VALOR DEL ATRIBUTO
        for valor_unico in df_alt[atributo].dropna().unique():  # hay modelos cuyo atrib toma valor none por eso hago un dropna(), funciona joya

            # Defino variables
            cant_opi_con_sent, prom_sent = 0, 0  # inicializo variables pues el atrib puede tener relacion con mas de una customer need

            # SELECCIONO LAS OPINIONES SEGUN IDS DE ALTERNATIVAS CUYO ATRIBUTO TOMA EL VALOR
            ids = df_alt[df_alt[atributo] == valor_unico]['id_alternativa']  # ids de alternativas donde atributo = valor
            df_cust_needs_sent_filt = df_cust_needs_sent[df_cust_needs_sent.id_alternativa.isin(ids)]  # opiniones de ids donde atributo = valor
            # print(df_opinion_cust_need_filt)

            # POR CUSTOMER NEED
            for customer_need in df_relation_matrix.index: # df_opinion_cust_need_filt.columns[1:]:  # no incluyo id_alt --> por que no use index de matriz de relaciones? que no tiene el id...

                # obtengo relacion entre customer need y relacion
                relacion = df_relation_matrix.loc[customer_need, atributo]
                print("Customer need: {} ; Relacion con atributo: {} ".format(customer_need, relacion))

                # SI HAY RELACION ENTRE CUSTOMER NEED Y ATRIBUTO
                if relacion > 0:

                    # OBTENGO CANTIDAD DE OPINIONES Y SENTIMENT PROMEDIO
                    cant_opi_con_sent += len(df_cust_needs_sent_filt[customer_need].dropna())
                    prom_sent += df_cust_needs_sent_filt[customer_need].dropna().mean() / sum_relaciones
                    print("Valor = {} ; Sentiment prom: {}".format(valor_unico, prom_sent))

            # GUARDO VALOR, ATRIBUTO AL QUE PERTENECE, CANT DE OPINIONES Y SENTIMENT
            if cant_opi_con_sent == 0 and prom_sent == 0:
                cant_opi_con_sent, prom_sent = None, None
            df_values_attr_sent.loc[len(df_values_attr_sent)] = [atributo, valor_unico, cant_opi_con_sent, prom_sent]
            print("Fila:", [atributo, valor_unico, cant_opi_con_sent, prom_sent])

        df_attr_value_sent_2 = pd.concat([df_attr_value_sent_2, df_values_attr_sent], ignore_index=True)  # para ver cantidad de opiniones en que se basa el sent de cada valor

        # PONDERO SENITMENT POR CANTIDAD DE OPINIONES PARA EL ATRIBUTO
        # if sum_relaciones > 0:  #Pues sino agrego atributos sin relacion y por ende con sent None y rompe el clustering..  # CON LO QUE AGREGUE EN RELATION MATRIX PODRIA SACARLO
        df_values_attr_sent_pond = quantity_opinions_weighing(df_values_attr_sent)

        # ESTANDARIZO SENTIMENT DE LOS VALORES DEL ATRIBUTO (se estandariza por atributo y no tod@ junto)
        df_values_attrs_sent_pond_norm = standardize_sentiment(df_values_attr_sent_pond)

        # Guardo datos del atributo
        df_values_attrs_sent_pond = pd.concat([df_values_attrs_sent_pond, df_values_attrs_sent_pond_norm], ignore_index=True)

    # Exporto (solo en pruebas)
    df_attr_value_sent_2.to_excel("/Users/nachomondino/Desktop/df_value_sent_opis.xlsx")
    df_values_attrs_sent_pond.to_excel("/Users/nachomondino/Desktop/df_attr_values_sent.xlsx")
    return df_values_attrs_sent_pond


################################################ FUNCIONES SECUNDARIAS ################################################
# UTILZADAS EN TO_CUSTOMER_NEEDS()
def words_mentioned_in_text(text, words):
    """
    Determina si las palabras estan en el texto.
    :param text: String. Cadena de texto.
    :param words: Lista de strings
    :return: Diccionario cuyas keys son cada palabra y cuyos values son 1 o 0 segun si la palabra es mencionada en el
    texto o no respectivamente.
    """
    find_related_words = lambda word, d_rel_words: d_rel_words[word] if word in d_rel_words.keys() else [word]

    # Importo diccionario de palabras relacionadas
    with open("d_rel_words.pkl", "rb") as tf:
        d_rel_words = pickle.load(tf)

    # Inicializo el diccionario a retornar
    d = {}
    for word in words:
        d[word] = 0

    # POR WORD
    for word in words:

        # BUSCO PALABRAS RELACIONADAS A LA WORD (para identificar mejor customer need en frase)
        palabras_a_buscar = find_related_words(word, d_rel_words)

        # POR PALABRA A BUSCAR (customer need y, si tiene, sus palabras relacionadas)
        for palabra_a_buscar in palabras_a_buscar:

            # SI LA PALABRA ESTA EN LA FRASE (uso frase limpia)
            if palabra_a_buscar in text:

                # Asigno 1 a palabra pues es mencionada en texto
                d[word] = 1

                break  # Dejo de buscar palabras relacionadas pues ya asigne sentiment a la customer need

    return d

def sentiment(sentence):
    """
    Calcula el score (sentiment) de una frase
    :param sentence: String. Cadena de texto
    :return: Score (sentiment) de frase
    """
    # Obtengo sentiment de sentence
    pred = analyzer.predict(sentence)  # ejemplo de output: AnalyzerOutput(output=NEU, probas={NEU: 0.802, NEG: 0.188, POS: 0.010})
    sent_frase = pred.probas  # accedo a probas de AnalyzerOutput

    # Calculo score
    score = sent_frase['POS'] - sent_frase['NEG']  # obtengo probabilidades de POS y NEG y calculo score
    return score

def assign_sentiment(d_cust_needs_mentioned, sent):
    """
    # Segun si es mencionado o no en texto, asigno sentiment de frase o None
    :param d_cust_needs_mentioned: Diccionario
    :param sent: Float. Sentiment de frase que menciona customer needs.
    :return:
    """
    # Defino variables
    l_frase_cust_needs_sent, l_cust_needs_ment = [], []

    # Por customer need
    for cust_need in d_cust_needs_mentioned.keys():

        # Si la customer need es mencionada en frase
        if d_cust_needs_mentioned[cust_need] == 1:
            # Asigno sentiment de frase
            l_frase_cust_needs_sent.append(sent)
            l_cust_needs_ment.append(cust_need)  # Guardo customer need mencionada para imprimir por pantalla

        # Si la customer need no es mencionada en frase
        else:
            # Asigno sentiment None
            l_frase_cust_needs_sent.append(None)

    # Imprimo customer needs mencionadas en frase (tomaran sentiment de esta)
    print("\t Customer needs mencionadas: ", l_cust_needs_ment)
    return l_frase_cust_needs_sent

def contains_word_type(text, word_type):
    """
    Identifica si una cadena de texto tiene al menos un adjetivo
    :param text: String. Cadena de texto
    :param word_type: Lista. Tipos de palabra a buscar en texto
    :return: True si el texto tiene al menos uno de los tipos de palabras, de lo contrario, False
    """
    # Proceso palabra
    doc = pos_tagger(text)

    # Por frase del texto
    for i, sent in enumerate(doc.sentences):

        # Por palabra
        for word in sent.words:

            # Si es adjetivo
            if word.pos in word_type:

                # La frase contiene al menos un adjetivo
                return True

    # La frase no contiene adjetivos
    return False

def conviene_separar_comas(text):
    """
    Determina si es o no conveniente separar una frase segun las comas que tenga
    :param text: String. Cadena de texto.
    :return: True si conviene separar en comas, o bien, False
    """
    # Separo frase segun comas
    l_frase_entre_comas = text.split(",")

    # Por frase entre comas
    for frase in l_frase_entre_comas:

        # Defino variables
        palabras_frase = frase.split()
        cant_palabras = len(palabras_frase)

        # Si la frase tiene una sola palabra
        if cant_palabras <= 1:

            # y no es un adejetivo
            if not contains_word_type(text=frase, word_type=['ADJ']):

                # No conviene separar por comas
                return False

    return True

def delete_accent(text):
    """
    Remueve acentos de textos de un texto
    :param text: String (ya sea una palabra o una frase)
    :return: String pasado como parametro sin acentos
    """
    # Defino variables
    d = {'á': "a", 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u'}  # diccionario, letra con acento en key y sin en value
    new_text = str()

    # Recorro cada letra del texto
    for i in range(len(text)):

        # Si la letra tiene acento
        if text[i] in d.keys():

            # Reemplazo letra con acento por letra sin acento
            new_text += d[text[i]]

        # Si la letra no tiene acento
        else:
            # no reemplazo nada
            new_text += text[i]
    return new_text

def delete_parentesis(text):
    """
    Elimina todos los parentesis de una cadena de texto
    :param text: Text string
    :return: Text string sin frases entre parentesis
    """
    # Defino variables
    cant_parentesis_apertura = text.count("(")  # Numero de parentesis de apertura en text
    cant_parentesis_cierre = text.count(")")  # Numero de parentesis de cierre en text
    text_cleaned = str()  # Variable que guardara el texto sin parentesis
    text_left = text  # Variable auxiliar para construir text_cleaned
    is_idx_last_char = lambda idx, text: True if idx == len(text) - 1 else False  # funcion

    # Si cada parentesis de apertura tiene su parentesis de cierre
    if cant_parentesis_apertura == cant_parentesis_cierre:

        # Por parentesis
        for i in range(cant_parentesis_apertura):

            # Defino indices de posicion de parentesis
            idx_ini = text_left.find("(")  # posicion del primer "(" en texto
            idx_fin = text_left.find(")")  # posicion del primer ")" en texto

            # Guardo el texto antes del parentesis
            text_cleaned += text_left[:idx_ini]

            # Guardo el texto restante desde el cierre de parentesis
            if is_idx_last_char(idx_fin, text_left):
                pass  # no hay texto luego del ultimo parentesis
            else:
                text_left = text_left[idx_fin+1:]

        # Guardo el texto luego del ultimo paretesis
        text_cleaned += text_left
    return text_cleaned


# UTILZADAS EN TO_ATTR_VALUES()
def quantity_opinions_weighing(df_attr):
    """
    Pondera sentiment de cada valor de un atributo del producto segun cantidad de opiniones en que se basa
    :param df_attr: Dataframe cuya unidad de analisis son los valores de un mismo atributo del producto. Sus columnas
    son valor, atributo al que perenece, cantidad de opiniones en que se basa en sentiment y el sentiment
    :return: Dataframe cuya unidad de analisis son los valores de un mismo atributo del producto. Sus columnas
    son valor, atributo al que perenece y el sentiment ponderado segun cantidad de opiniones
    """
    # Defino variables
    df = pd.DataFrame(columns=['atributo','valor', 'sent'])  # Dataframe a retornar
    attr = df_attr.loc[0, 'atributo']  # nombre del atributo al que pertencen los valores cuyos sentiment se ponderaran
    max_cant_opi_attr = df_attr["cant_opi_con_sent"].max()  # factor 1, cant de opiniones max de un valor del atributo
    n_val_with_opis = len(df_attr[df_attr['cant_opi_con_sent'] > 0])  # no considero valores sin opiniones
    cant_opi_opt = df_attr["cant_opi_con_sent"].sum() / n_val_with_opis  # factor 2, cant optima de opis por valor del
    print("Ponderacion de sentiments por cantidad de opiniones para atributo {}".center(120, "-").format(attr))

    # POR VALOR DEL ATRIBUTO
    for valor in df_attr['valor']:

        # SI EL VALOR TIENE SENTIMENT
        try:
            # OBTENGO SU CANTIDAD DE OPINIONES DEL VALOR Y SU SENTIMENT
            cant_opi_valor = int(df_attr[df_attr['valor'] == valor]['cant_opi_con_sent'])
            sent_valor = float(df_attr[df_attr['valor'] == valor]['sent'])
            print("Valor: {} ; Sentiment: {:.3f}; Cantidad de opis: {}".format(valor, sent_valor, cant_opi_valor))

            # CALCULO FACTOR
            # Calculo factor 1
            porc_max_cant_opi = cant_opi_valor / max_cant_opi_attr
            # Calculo factor 2
            porc_opt_cant_opi = cant_opi_valor / cant_opi_opt
            # Calculo factor final
            factor_final = 0.1 * porc_max_cant_opi + 0.9 * porc_opt_cant_opi  # asigno mas peso a factor 2
            if factor_final > 1:  # si el factor final es mayor que 1
                factor_final = 1  # lo seteo a 1
            print("Factor 1: {:.2f}; Factor 2: {:.2f}; Factor final: {:.2f}".format(porc_max_cant_opi, porc_opt_cant_opi, factor_final))

            # PONDERO SENTIMENT CON FACTOR
            sent_valor_pond = sent_valor * factor_final
            print("Sentiment ponderado: {:.3f}".format(sent_valor_pond))

            # GUARDO FILA DEL VALOR
            df.loc[len(df)] = [attr, valor, sent_valor_pond]

        # SI EL VALOR TIENE SENTIMENT NAN
        except TypeError:
            # NO PONDERO EL SENTIMENT Y LO GUARDO COMO NAN
            df.loc[len(df)] = [attr, valor, None]
            print("El valor {} tiene sentiment NaN".format(valor))

    return df

def standardize_sentiment(df):
    """
    Normaliza los sentiment de los valores de un atributo. Esto quita las escala para los diferentes atributos
    :param df: Daraframe cuya unidad de analisis es el valor de un atributo. Las columnas son valor, atributo al que
    pertenece este y su sentiment ya ponderado
    :return: Daraframe igual al pasado por parametro salvo con columna sentiment normalizada
    """
    # Defino variable
    l_sent = df['sent'].dropna()
    try:
        # Obtengo media y desvio de sentiments
        media = st.mean(l_sent)  # media de sentiment de los valores del atributo
        desv = st.stdev(l_sent)  # desvio de sentiment de los valores del atributo
        # Los atributos que toman un solo valor y por ende tienen un solo sent, fallan en el calculo del desvio porque se necesitan al menos dos data points (es decir, al menos dos valores cada uno con su sentiment)

        # NORMALIZO EL SENTIMENT DE CADA VALOR
        # Por valor
        for i in range(len(df)):
            # Obtengo el sentiment del valor
            sent_valor = df.loc[i, 'sent']

            # Normalizo dicho sentiment y lo guardo
            new_sent_valor = (sent_valor - media) / desv
            df.loc[i, 'sent'] = new_sent_valor
    except:
        print("Columna que fallo: ", df['atributo'].unique())
        pass

    return df

def main(df_alt_cleaned, df_opi, df_relation_matrix):

    # Para correr pruebas
    # df_cust_need_sent = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/atribucion/auriculares/df_cust_need_sent.xlsx')
    # print(df_cust_need_sent)

    l_cust_needs_one_word = list(df_relation_matrix.index)

    print("4.1.1 Atribuyo sentiment a customer needs...".center(120))
    df_cust_need_sent = to_customer_needs(df_opi, l_cust_needs_one_word)  # df_opi falta eliminar acentos...

    print("4.1.2 Atribuyo sentiment a valores de los atributos del producto...".center(120))
    df_attr_values_sent = to_attribute_value(df_alt_cleaned, df_cust_need_sent, df_relation_matrix)

    # df_attr_values_sent.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/atribucion/auriculares/df_attr_values_sent.xlsx', index=False)  # cuando corra tod@ junto pongo product.nombre

    return df_cust_need_sent, df_attr_values_sent

'''
# Para correr pruebas
producto = "auriculares"
df_alt_cleaned = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_alt_cleaned.xlsx'.format(producto))
df_opi = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/{}/df_opi.xlsx'.format(producto))
df_relation_matrix = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_relation_matrix.xlsx'.format(producto), index_col=0)
print(df_alt_cleaned), print(df_opi), print(df_relation_matrix)
main(df_alt_cleaned, df_opi, df_relation_matrix)
'''


'''
def to_customer_needs(df_opiniones, customer_needs_one_word):
    """
    Identifica, si hay, customer needs en opiniones y asigna el sentiment a cada una mediante la libreria pysentimiento
    :param df_opiniones: Dataframe opiniones cuya unidad de analisis son opiniones que no tienen procesamiento
    :param customer_needs_one_word: Lista de customer needs como frases de 1 sola palabra
    :return: Dataframe cuya unidad de analisis es una opinion y cuyas columnas son cada customer need. La celda es el
    sentiment de la customer need en la opinion, o bien si la opinion no habla de la customer need, None.
    """
    # DEFINO VARIABLES
    # Defino indices utiles para tener flexibilidad en codigo (posibilidad de columnas en otra posicion)
    idx_id, idx_opi = df_opiniones.columns.get_loc("id_alternativa"), df_opiniones.columns.get_loc("opinion")
    # Defino dataframe a retornar
    df_opinion_cust_needs = pd.DataFrame(columns=["id_alternativa"] + customer_needs_one_word)
    # Uso funcion create_analyzer para realizar el sentiment de las frases
    analyzer = create_analyzer(task="sentiment", lang="es")

    # POR OPINION
    for i in range(len(df_opiniones)):

        # Defino variables
        id, opinion = df_opiniones.iloc[i, idx_id], df_opiniones.iloc[i, idx_opi]  # Defino id y opinion
        fila_df_opi_cn = [id]  # inicializo variable que guardara la fila del nuevo dataframe
        df_frases_cust_needs = pd.DataFrame(columns=customer_needs_one_word)  #lo reinicio por opinion

        print("NºFila:", i)
        print("Opinion:", opinion)

        # POR FRASE DE LA OPINION
        for frase in nltk.tokenize.sent_tokenize(opinion):  #esto funciona?? Espectacular pa
            print("Frase: ", frase)

            # Defino variables
            fila_df_frase_cn = []  # Fila de sentiment de customer needs en la frase

            # LIMPIO FRASE PARA PODER IDENTIFICAR CUSTOMER NEEDS EN ELLA (la hago miniscula y quito acentos)
            frase_limpia = delete_accent(frase.lower())

            # OBTENGO SENTIMENT DE FRASE
            pred = analyzer.predict(frase)  # ejemplo de output: AnalyzerOutput(output=NEU, probas={NEU: 0.802, NEG: 0.188, POS: 0.010})
            sent_frase = pred.probas  # accedo a probas de AnalyzerOutput
            score = sent_frase['POS'] - sent_frase['NEG']  # obtengo probabilidades de POS y NEG y calculo score
            print("Sentiment frase: ", score)

            # POR CUSTOMER NEED
            for customer_need in customer_needs_one_word:

                # Defino variable
                bool = True  # Variable para cortar busqueda de sentiment de customer need con palabras adicionales

                # BUSCO PALABRAS RELACIONADAS A LA CUSTOMER NEED (para identificar mejor customer need en frase)
                palabras_a_buscar = palabras_relacionadas(customer_need)

                # POR PALABRA A BUSCAR (customer need y, si tiene, sus palabras relacionadas)
                for palabra_a_buscar in palabras_a_buscar:

                    # SI LA PALABRA ESTA EN LA FRASE (uso frase limpia)
                    if palabra_a_buscar in frase_limpia:

                        # ASIGNO SENTIMENT DE FRASE A LA CUSTOMER NEED
                        fila_df_frase_cn.append(score)

                        # Dejo de buscar palabras relacionadas pues ya asigne sentiment a la customer need
                        bool = False
                        break

                # SI LA CUSTOMER NEED NO ESTA EN LA FRASE
                if bool:
                    # ASIGNO SENTIMENT NONE
                    fila_df_frase_cn.append(None)

            # GUARDO SENTIMENT DE LAS CUSTOMER NEEDS EN LA FRASE
            df_frases_cust_needs.loc[len(df_frases_cust_needs)] = fila_df_frase_cn
            print(df_frases_cust_needs)

        # OBTENGO SENTIMENT DE CUSTOMER NEEDS EN OPINION (pues puede aparecer en mas de una frase)
        # Por customer need
        for customer_need in customer_needs_one_word:

            # Obtengo promedio de sentiment en frases en que es mencionada
            sent_cn_opi = df_frases_cust_needs[customer_need].dropna().mean()
            print("Customer neeed: {}, sentiment: {}".format(customer_need, sent_cn_opi))

            # Guardo el sentiment de la customer need en la opinion
            fila_df_opi_cn.append(sent_cn_opi)

        # GUARDO SENTIMENT DE LAS CUSTOMER NEEDS EN LA OPINION
        df_opinion_cust_needs.loc[i] = fila_df_opi_cn
        print("Fila:", fila_df_opi_cn)
        # print(df_opinion_cust_needs)

    # EXPORTO DATAFRAME
    df_opinion_cust_needs.to_excel('/Users/nachomondino/Desktop/df_opinion_cust_needs.xlsx', 'Hoja de datos', index=False)
    print(df_opinion_cust_needs)

    return df_opinion_cust_needs

'''


''' ULTIMO INTENTO DE CUSTOMER NEEDS Y HASTA AHORA VIGENTE
def to_customer_needs(df_opiniones, customer_needs_one_word):
    """
    Identifica, si hay, customer needs en opiniones y asigna el sentiment a cada una mediante la libreria pysentimiento
    :param df_opiniones: Dataframe opiniones cuya unidad de analisis son opiniones que no tienen procesamiento
    :param customer_needs_one_word: Lista de customer needs como frases de 1 sola palabra
    :return: Dataframe cuya unidad de analisis es una opinion y cuyas columnas son cada customer need. La celda es el
    sentiment de la customer need en la opinion, o bien si la opinion no habla de la customer need, None.
    """
    # DEFINO VARIABLES
    # Defino indices utiles para tener flexibilidad en codigo (posibilidad de columnas en otra posicion)
    idx_id, idx_opi = df_opiniones.columns.get_loc("id_alternativa"), df_opiniones.columns.get_loc("opinion")
    # Defino dataframe a retornar
    df_opinion_cust_needs = pd.DataFrame(columns=["id_alternativa"] + customer_needs_one_word)
    # Uso funcion create_analyzer para realizar el sentiment de las frases
    analyzer = create_analyzer(task="sentiment", lang="es")

    # POR OPINION
    for i in range(len(df_opiniones)):

        # Defino variables
        id, opinion = df_opiniones.iloc[i, idx_id], df_opiniones.iloc[i, idx_opi]  # Defino id y opinion
        fila_df_opi_cn = [id]  # inicializo variable que guardara la fila del nuevo dataframe
        df_frases_cust_needs = pd.DataFrame(columns=customer_needs_one_word)  #lo reinicio por opinion

        print("NºFila: {}".center(120).format(i))
        print("Opinion:", opinion)

        # POR FRASE DE LA OPINION
        for frase in split_text_into_sentences(text=opinion, sep='.'):
            print("Frase: ", frase)

            # Defino variables
            fila_df_frase_cn = []  # Fila de sentiment de customer needs en la frase

            # LIMPIO FRASE PARA PODER IDENTIFICAR CUSTOMER NEEDS EN ELLA (la hago miniscula y quito acentos)
            frase_limpia = delete_accent(frase.lower())
            # IDENTIFICO QUE CUSTOMER NEEDS MENCIONA
            # funcion que me devuelva dict con key cada cn y cuo values es 0 o 1 segun si es menciona o no en la frase.
            d_cust_needs_mentioned = words_mentioned_in_text(words=customer_needs_one_word, text=frase_limpia)
            n_cust_need_ment = sum(d_cust_needs_mentioned.values())

            sent_frase = sentiemnt_sentence(analyzer=analyzer, sentence=frase)  # es por prueba

            if n_cust_need_ment >= 2 and sent_frase < 0.6 :
                print("aqui aqui aqui")

            # SI LA FRASE MENCIONA AL MENOS UNA CUSTOMER NEED
            elif n_cust_need_ment >= 1:  # es if en realidad perro es por la prueb

                # OBTENGO SENTIMENT
                sent_frase = sentiemnt_sentence(analyzer=analyzer, sentence=frase)

                # Por customer need
                for cust_need in d_cust_needs_mentioned.keys():

                    # Si la customer need es mencionada
                    if d_cust_needs_mentioned[cust_need] == 1:
                        # Asigno sentiment de frase
                        fila_df_frase_cn.append(sent_frase)

                    # Si la customer need no es mencionada
                    else:
                        # Asigno sentiment None
                        fila_df_frase_cn.append(None)

                # GUARDO SENTIMENT DE LAS CUSTOMER NEEDS EN LA FRASE
                df_frases_cust_needs.loc[len(df_frases_cust_needs)] = fila_df_frase_cn
                print(df_frases_cust_needs)
                print()

            # SI LA FRASE NO MENCIONA CUSTOMER NEEDS
            else:
                pass

        # OBTENGO SENTIMENT DE CUSTOMER NEEDS EN OPINION (pues puede aparecer en mas de una frase)
        # Por customer need
        for customer_need in customer_needs_one_word:

            # Obtengo promedio de sentiment en frases en que es mencionada
            sent_cn_opi = df_frases_cust_needs[customer_need].dropna().mean()
            print("Customer need: {}, sentiment: {}".format(customer_need, sent_cn_opi))

            # Guardo el sentiment de la customer need en la opinion
            fila_df_opi_cn.append(sent_cn_opi)

        # GUARDO SENTIMENT DE LAS CUSTOMER NEEDS EN LA OPINION
        df_opinion_cust_needs.loc[i] = fila_df_opi_cn
        print("Fila:", fila_df_opi_cn)
        # print(df_opinion_cust_needs)

    # EXPORTO DATAFRAME
    df_opinion_cust_needs.to_excel('/Users/nachomondino/Desktop/df_opinion_cust_needs.xlsx', 'Hoja de datos', index=False)
    print(df_opinion_cust_needs)

    return df_opinion_cust_needs
'''

'''
def split_text_into_sentences(text, sep): #esta buenisima pero es lo mismo que hacer .split(".")
    """
    Separate a text string into sentences by element
    :param text: Text string
    :param sep: Separating element
    :return: list whose elements are each setence
    """
    # Defino variables
    sentences = []
    pos_ini = 0

    # Por caracter de la cadena
    for pos, char in enumerate(text):

        # Si el caracter es el separador
        if (char == sep):

            # Obtengo sentence
            sentences.append(text[pos_ini:pos])
            pos_ini = pos + 1

    # Si el separador no es el ultimo caracter del texto
    if pos_ini != len(text):

        # Guardo ultima sentence
        sentences.append(text[pos_ini:len(text)])

    return sentences
'''

'''
def is_adjetive(word):  # fue embebida en contains_adjective()
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
    if pos == "ADJ":
        return True  # retorno True

    # si palabra no es sustantivo
    else:
        return False  # retorno False
'''

'''# PRUEBA EN CUSTOMER NEEDS - SEPARACION DE FRASES QUE MENCIONAN MAS DE DOS CUST NEEDS: tal vez estaria bueno separadores como "lo unico" o "pero"
def split_in_word(text, word):

    if word in text:
        idx_ini = text.find(word)

        text_ant = text[:idx_ini]
        text_desp = text[idx_ini + len(word):]

        return [text_ant, text_desp]

dentro de to_customer_needs:
pal_sep = ['pero', 'lo unico']
if len(frases_entre_comas) == 1:

    for word in pal_sep:

        if word in frase:

            frases_entre_comas = split_in_word(frase, word)
            print("FUNCIONO!!!!!")
            print(frases_entre_comas)


'''


''' #DEEJO ACA LA FUNCION ACTIVA HASTA AHORA PARA PODER HACERLE CAMBIOS
def to_customer_needs(df_opi, l_customer_needs_one_word):
    """
    Identifica, si hay, customer needs en opiniones y asigna el sentiment a cada una mediante la libreria pysentimiento
    :param df_opi: Dataframe opiniones cuya unidad de analisis son opiniones que no tienen procesamiento
    :param l_customer_needs_one_word: Lista de customer needs como frases de 1 sola palabra
    :return: Dataframe cuya unidad de analisis es una opinion y cuyas columnas son cada customer need. La celda es el
    sentiment de la customer need en la opinion, o bien si la opinion no habla de la customer need, None.
    """
    # DEFINO VARIABLES
    idx_id, idx_opi = df_opi.columns.get_loc("id_alternativa"), df_opi.columns.get_loc("opinion")  # indices utiles para tener flexibilidad en codigo (posibilidad de columnas en otra posicion)
    df_cust_needs_sent = pd.DataFrame(columns=["id_alternativa"] + l_customer_needs_one_word)  # dataframe a retornar
    choose_sep = lambda text: "," if text.count(",") >= 1 else ';'
    split_frase_in_commas = lambda frase: frase.split(choose_sep(frase)) if conviene_separar_comas(frase) else [frase]

    # POR OPINION
    for i in range(len(df_opi)):

        # Defino variables
        id, opinion = df_opi.iloc[i, idx_id], df_opi.iloc[i, idx_opi]  # Defino id y opinion
        opinion = delete_parentesis(opinion)  # quito todos los parentesis de la opinion
        frases = opinion.split(".")
        fila_df = [id]  # inicializo variable que guardara la fila del nuevo dataframe
        df_frases_cust_needs = pd.DataFrame(columns=l_customer_needs_one_word)  #lo reinicio por opinion
        cont = 0
        print("NºFila: {}".center(120).format(i)), print("OPINION:", opinion)

        # OBTENGO SENTIMENT DE OPINION
        sent_opi = sentiment(sentence=opinion)
        print("\t Sentiment de toda la opinion: {:.2f}".format(sent_opi))
        print("Divido la opinion en {} frases.".format(len(frases)))

        # POR FRASE DE LA OPINION
        for frase in frases:
            cont += 1
            print("FRASE Nº{}: {}".format(cont, frase))

            # OBTENGO SENTIMENT DE FRASE
            sent_frase = sentiment(sentence=frase)
            print("\t Sentiment de la frase: {:.2f}".format(sent_frase))

            # IDENTIFICO QUE CUSTOMER NEEDS MENCIONA
            frase_limpia = delete_accent(frase.lower())  # limpio la frase para poder identificar customer needs en ella
            d_cust_needs_mentioned = words_mentioned_in_text(words=l_customer_needs_one_word, text=frase_limpia)  # diccionario con customer needs como key y 1 o 0 como value segun si la frase la menciona o no.
            n_cust_need_ment = sum(d_cust_needs_mentioned.values())  # numero de customer needs mencionadas en frase


            # SI MENCIONA AL MENOS 2 CUSTOMER NEEDS Y EL SENTIMENT NO ES CATEGORICO
            if (n_cust_need_ment >= 2) and (sent_frase < 0.5 and sent_frase > -0.5):

                # Divido frase segun comas
                frases_entre_comas = split_frase_in_commas(frase)

                # Si no conviene dividir frase entre comas, o bien, no tiene
                # if len(frases_entre_comas) == 1:
                #    print("\t No conviene dividir frase entre comas, o bien, no tiene")

                print("Divido frase Nº{} en {} frase entre comas".format(cont, len(frases_entre_comas)))

                # Por frase entre comas
                for sentence in frases_entre_comas:
                    print("\t FRASE ENTRE COMAS: ", sentence)

                    # Identifico customer need en frase entre comas
                    sentence_limpia = delete_accent(sentence.lower())
                    d_cust_needs_mentioned = words_mentioned_in_text(words=l_customer_needs_one_word, text=sentence_limpia)

                    # Si hay una customer need
                    if sum(d_cust_needs_mentioned.values()) >= 1:

                        # Obtengo sentiment de frase entre comas
                        sent_frase_entre_comas = sentiment(sentence=sentence)
                        print("\t\t Sentiment de frase entre comas: {:.2f}".format(sent_frase_entre_comas))

                        # Si contiene adjetivos
                        if contains_word_type(text=sentence, word_type=['ADJ']):

                            # Si el sentiment de la frase no se corresponde con el de la opinion  ---> FALTA DOC
                            if (sent_opi < -0.9 and sent_frase_entre_comas > 0 and sent_frase_entre_comas < 0.28) or (sent_opi > 0.9 and sent_frase_entre_comas > -0.28 and sent_frase_entre_comas < 0):

                                # Pondero sentiment
                                sent_frase_entre_comas_pond = 0.8 * sent_frase_entre_comas + 0.2 * sent_opi
                                print("\t\t Es probable que el sentiment de la frase sea incorrecto dado que el de la opinion es totalmente opuesto")
                                print("\t\t Sentiment ponderado = {:.2f} ".format(sent_frase_entre_comas_pond))

                                df_frases_cust_needs.loc[len(df_frases_cust_needs)] = assign_sentiment(d_cust_needs_mentioned, sent_frase_entre_comas_pond)
                                print("\t\t NO HARIA PONDERACION")

                            # Si el sentiment de la frase se corresponde con el de la opinion
                            else:
                                df_frases_cust_needs.loc[len(df_frases_cust_needs)] = assign_sentiment(d_cust_needs_mentioned, sent_frase_entre_comas)  # df_frases_cust_needs.loc[len(df_frases_cust_needs)] = lambda x, y: assign_sentiment(x,y) if sum(x.values()) > 1 else

                            """
                            elif (sent_opi < -0.8 and sent_frase_entre_comas > 0 and sent_frase_entre_comas < 0.28) or (sent_opi > 0.8 and sent_frase_entre_comas > -0.28 and sent_frase_entre_comas < 0):
                                print("intento 2")

                            elif (sent_opi < -0.7 and sent_frase_entre_comas > 0 and sent_frase_entre_comas < 0.28) or (sent_opi > 0.7 and sent_frase_entre_comas > -0.28 and sent_frase_entre_comas < 0):
                                print("intento 3")
                            """

                        # Si no hay adjetivos
                        else:
                            # pero el sentiment de la frase entre comas es categorico tal como el de la opinion
                            if (sent_opi < -0.8 and sent_frase_entre_comas < -0.5) or (sent_opi > 0.8 and sent_frase_entre_comas > 0.5):
                                print("c1) La frase no contiene adjetivos pero se guardara el sentiment de todas maneras")
                                df_frases_cust_needs.loc[len(df_frases_cust_needs)] = assign_sentiment(d_cust_needs_mentioned, sent_frase_entre_comas)

                            # si el sentiment de la frase es categorico independientemente del de la opinion
                            elif sent_frase_entre_comas > 0.8 or sent_frase_entre_comas < -0.8:  # nuevo
                                print("c2) La frase no contiene adjetivos pero se guardara el sentiment de todas maneras")
                                df_frases_cust_needs.loc[len(df_frases_cust_needs)] = assign_sentiment(d_cust_needs_mentioned, sent_frase_entre_comas)

                            else:
                                print("La frase no contiene adjetivos")

                    # Si no hay customer needs
                    else:
                        print("\t\t La frase no contiene customer needs")

            # SI MENCIONA UNA CUSTOMER NEED
            elif n_cust_need_ment >= 1:  # ojo que puede haber frases que mencionen mas de una y sea categorica

                # SI CONTIENE AL MENOS UN ADJETIVO
                if contains_word_type(text=frase, word_type=['ADJ']):

                    # PRUEBA
                    if (sent_opi < -0.9 and sent_frase > 0 and sent_frase < 0.28) or (sent_opi > 0.9 and sent_frase > -0.28 and sent_frase < 0):

                        # Pondero sentiment
                        sent_frase_pond = 0.8 * sent_frase + 0.2 * sent_opi
                        print("\t Es probable que el sentiment de la frase sea incorrecto dado que el de la opinion es totalmente opuesto")
                        print("\t Sentiment ponderado = {:.2f} ".format(sent_frase_pond))

                        # ASIGNO SENTIMENT A CUSTOMER NEED MENCIONADA
                        df_frases_cust_needs.loc[len(df_frases_cust_needs)] = assign_sentiment(d_cust_needs_mentioned, sent_frase_pond)

                    else:
                        # ASIGNO SENTIMENT A CUSTOMER NEED MENCIONADA
                        df_frases_cust_needs.loc[len(df_frases_cust_needs)] = assign_sentiment(d_cust_needs_mentioned, sent_frase)

                    """
                    elif (sent_opi < -0.8 and sent_frase > 0 and sent_frase < 0.28) or (sent_opi > 0.8 and sent_frase > -0.28 and sent_frase < 0):
                        print("intento 2")

                    elif (sent_opi < -0.7 and sent_frase > 0 and sent_frase < 0.28) or (sent_opi > 0.7 and sent_frase > -0.28 and sent_frase < 0):
                        print("intento 3")
                    """


                # SI CONTIENE ADJETIVOS
                else:
                    if (sent_opi < -0.8 and sent_frase < -0.5) or (sent_opi > 0.8 and sent_frase > 0.5):
                        df_frases_cust_needs.loc[len(df_frases_cust_needs)] = assign_sentiment(d_cust_needs_mentioned, sent_frase)
                        print("c1) La frase no contiene adjetivos pero se guardara el sentiment de todas maneras")

                    # si el sentiment de la frase es categorico independientemente del de la opinion
                    elif sent_frase > 0.8 or sent_frase < -0.8:  # nuevo
                        df_frases_cust_needs.loc[len(df_frases_cust_needs)] = assign_sentiment(d_cust_needs_mentioned, sent_frase)
                        print("c2) La frase no contiene adjetivos pero se guardara el sentiment de todas maneras")

                    else:
                        print("\t La frase no contiene adjetivos")

            # SI NO MENCIONA CUSTOMER NEEDS
            else:
                pass

        # OBTENGO SENTIMENT DE CUSTOMER NEEDS EN OPINION (pues puede aparecer en mas de una frase)
        # Por customer need
        for customer_need in l_customer_needs_one_word:

            # Obtengo promedio de sentiment en frases en que es mencionada
            sent_cn_opi = df_frases_cust_needs[customer_need].dropna().mean()
            # print("Customer need: {}, sentiment: {}".format(customer_need, sent_cn_opi))

            # Guardo el sentiment de la customer need en la opinion
            fila_df.append(sent_cn_opi)

        # GUARDO SENTIMENT DE LAS CUSTOMER NEEDS EN LA OPINION
        df_cust_needs_sent.loc[i] = fila_df
        # print("Fila:", fila_df)

    # EXPORTO DATAFRAME
    df_cust_needs_sent.to_excel('/Users/nachomondino/Desktop/df_cust_needs_sent.xlsx', 'Hoja de datos', index=False)
    print(df_cust_needs_sent)

    return df_cust_needs_sent



'''