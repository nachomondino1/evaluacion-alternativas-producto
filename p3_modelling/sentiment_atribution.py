# Importo librerias
import pandas as pd
from pysentimiento import create_analyzer
import stanza
import pickle
import statistics as st
from p3_modelling.utils import diccionario_palabras_relacionadas


analyzer = create_analyzer(task="sentiment", lang="es")  # para realizar el sentiment
pos_tagger = stanza.Pipeline(lang='es', processors='tokenize,pos,mwt')

################################################ FUNCIONES PRINCIPALES ################################################
def to_customer_needs(df_opi, l_customer_needs_one_word, d_pal_rel, d_avoid_fp):
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
        id, opinion = df_opi.iloc[i, idx_id], df_opi.iloc[i, idx_opi]  # Defino id y opinion sin parentesis
        fila_df = [id]  # inicializo variable que guardara la fila del nuevo dataframe
        df_frases_cust_needs = pd.DataFrame(columns=l_customer_needs_one_word)  # Dataframe con sent de frases de opinion
        cont = 0

        # OBTENGO SENTIMENT DE OPINION
        sent_opi = get_sentiment_score(sentence=opinion)

        # Imprimo para seguir funcionamiento de la funcion
        print("NºFila: {}".center(120).format(i)), print("OPINION:", opinion)
        print("\t Sentiment de toda la opinion: {:.2f}".format(sent_opi))
        print("Divido la opinion en {} frases.".format(len(opinion.split("."))))

        # POR FRASE DE LA OPINION
        for frase in opinion.split("."):

            # OBTENGO SENTIMENT DE FRASE
            sent_frase = get_sentiment_score(sentence=frase)

            # IDENTIFICO QUE CUSTOMER NEEDS MENCIONA
            frase_limpia = clean_text(frase)  #  " " + delete_accent(frase.lower()) + " " # limpio la frase para poder identificar customer needs en ella. Agrego espacios para identificar la primera y la ultima palabra
            d_cust_needs_mentioned = cust_needs_in_text(l_customer_needs_one_word, frase_limpia, d_pal_rel, d_avoid_fp)  # diccionario con customer needs como key y 1 o 0 como value segun si la frase la menciona o no.
            n_cust_need_ment = sum(d_cust_needs_mentioned.values())  # numero de customer needs mencionadas en frase

            # Imprimo para seguir funcionamiento de la funcion
            cont += 1
            print("FRASE Nº{}: {}".format(cont, frase)), print("\t Sentiment de la frase: {:.2f}".format(sent_frase))


            # PRUEBA
            palabras_comp = [' anterior ', ' comparad']
            for pal in palabras_comp:
                if pal in frase:
                    print("Evitaria esta frase!, palabra presente: {} ".format(pal))


            # SI MENCIONA AL MENOS 2 CUSTOMER NEEDS Y EL SENTIMENT NO ES CATEGORICO
            if (n_cust_need_ment >= 2) and (sent_frase < 0.4 and sent_frase > -0.4):

                # Divido frase segun comas
                frases_entre_comas = split_frase_in_commas(frase)
                print("Divido frase Nº{} en {} frase entre comas".format(cont, len(frases_entre_comas)))

                # Por frase entre comas
                for sentence in frases_entre_comas:

                    # Identifico customer need en frase entre comas
                    sentence_limpia = clean_text(sentence)   #  " " + delete_accent(sentence.lower()) + " "
                    d_cust_needs_mentioned = cust_needs_in_text(l_customer_needs_one_word, sentence_limpia, d_pal_rel, d_avoid_fp)
                    print("\t FRASE ENTRE COMAS: ", sentence)

                    # Si hay una customer need
                    if sum(d_cust_needs_mentioned.values()) > 0:

                        # Obtengo sentiment de frase entre comas
                        sent_frase_entre_comas = get_sentiment_score(sentence=sentence)
                        print("\t\t Sentiment de frase entre comas: {:.2f}".format(sent_frase_entre_comas))

                        # Si contiene adjetivos
                        if contains_word_type(text=sentence, word_type=['ADJ']):

                            # Si el sentiment de la frase no se corresponde con el de la opinion  ---> FALTA DOC
                            if (sent_opi < -0.9 and sent_frase_entre_comas > 0 and sent_frase_entre_comas < 0.28) or (sent_opi > 0.9 and sent_frase_entre_comas > -0.28 and sent_frase_entre_comas < 0):

                                # Pondero sentiment
                                sent_frase_entre_comas = 0.8 * sent_frase_entre_comas + 0.2 * sent_opi
                                print("\t\t Es probable que el sentiment de la frase sea incorrecto dado que el de la opinion es totalmente opuesto.", end=" ")
                                print("\t\t Sentiment ponderado = {:.2f} ".format(sent_frase_entre_comas))

                            df_frases_cust_needs.loc[len(df_frases_cust_needs)] = assign_sentiment_to_cust_needs(d_cust_needs_mentioned, sent_frase_entre_comas)  # df_frases_cust_needs.loc[len(df_frases_cust_needs)] = lambda x, y: assign_sentiment(x,y) if sum(x.values()) > 1 else

                        # Si no hay adjetivos  # pero el sentiment de la frase entre comas es categorico tal como el de la opinion
                        elif (sent_opi < -0.8 and sent_frase_entre_comas < -0.5) or (sent_opi > 0.8 and sent_frase_entre_comas > 0.5):
                            print("\t\t La frase no contiene adjetivos pero se guardara el sentiment de todas maneras")
                            df_frases_cust_needs.loc[len(df_frases_cust_needs)] = assign_sentiment_to_cust_needs(d_cust_needs_mentioned, sent_frase_entre_comas)

                        #Si no hay adjetivos, pero si el sentiment de la frase es categorico independientemente del de la opinion
                        elif sent_frase_entre_comas > 0.8 or sent_frase_entre_comas < -0.8:  # nuevo
                            print("\t\t La frase no contiene adjetivos pero se guardara el sentiment de todas maneras")
                            df_frases_cust_needs.loc[len(df_frases_cust_needs)] = assign_sentiment_to_cust_needs(d_cust_needs_mentioned, sent_frase_entre_comas)

                        else:
                            print("\t\t La frase no contiene adjetivos")

                    # Si no hay customer needs
                    else:
                        print("\t\t La frase no contiene customer needs")

            # SI MENCIONA UNA CUSTOMER NEED
            elif n_cust_need_ment > 0:  # ojo que puede haber frases que mencionen mas de una y sea categorica

                # SI CONTIENE AL MENOS UN ADJETIVO
                if contains_word_type(text=frase, word_type=['ADJ']):

                    # PRUEBA
                    if (sent_opi < -0.9 and sent_frase > 0 and sent_frase < 0.28) or (sent_opi > 0.9 and sent_frase > -0.28 and sent_frase < 0):

                        # Pondero sentiment
                        sent_frase = 0.8 * sent_frase + 0.2 * sent_opi
                        print("\t Es probable que el sentiment de la frase sea incorrecto dado que el de la opinion es totalmente opuesto.", end=" ")
                        print("\t Sentiment ponderado = {:.2f} ".format(sent_frase))

                    # ASIGNO SENTIMENT A CUSTOMER NEED MENCIONADA
                    df_frases_cust_needs.loc[len(df_frases_cust_needs)] = assign_sentiment_to_cust_needs(d_cust_needs_mentioned, sent_frase)

                # SI NO CONTIENE ADJETIVOS, PERO el sentiment de la opinion es categorico y el de la frasee no categ
                elif (sent_opi < -0.8 and sent_frase < -0.5) or (sent_opi > 0.8 and sent_frase > 0.5):
                    df_frases_cust_needs.loc[len(df_frases_cust_needs)] = assign_sentiment_to_cust_needs(d_cust_needs_mentioned, sent_frase)
                    print("\t La frase no contiene adjetivos pero se guardara el sentiment de todas maneras")

                # SI NO CONTIENE ADJETIVOS,  pero si el sentiment de la frase es categorico independientemente del de la opinion
                elif sent_frase > 0.8 or sent_frase < -0.8:  # nuevo  # bajaria a 0.7 al menos
                    df_frases_cust_needs.loc[len(df_frases_cust_needs)] = assign_sentiment_to_cust_needs(d_cust_needs_mentioned, sent_frase)
                    print("\t La frase no contiene adjetivos pero se guardara el sentiment de todas maneras")

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

def to_attribute(df_alt, df_cust_needs_sent, df_relation_matrix):
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
    df_values_attrs_sent_pond = pd.DataFrame(columns=['valor','atributo', 'n_opi_con_sent', 'sent'])
    df_alts_sent = pd.DataFrame(columns=['id_alternativa', 'atributo', 'n_opi_con_sent', 'sent'])
    df_attr_value_sent_2 = pd.DataFrame(columns=['valor', 'atributo', 'n_opi_con_sent', 'sent'])

    # POR CAMPO ESPECIFICO O ATRIBUTO DEL PRODUCTO
    for atributo in df_relation_matrix.columns:

        print(atributo.upper().center(120))
        df_relation_matrix_atrib = df_relation_matrix.loc[:, atributo]  # filtro matriz de relaciones por atributo

        # SI EL ATRIBUTO NO FUE CREADO ARTIFICIALMENTE
        if atributo in df_alt.columns:

            # Defino variables
            df_values_attr_sent = pd.DataFrame(columns=['valor', 'atributo', 'n_opi_con_sent', 'sent'])  # Dataframe para valores del atributo

            # POR VALOR DEL ATRIBUTO
            for valor_unico in df_alt[atributo].dropna().unique():  # hay modelos cuyo atrib toma valor none por eso hago un dropna(), funciona joya
                print('VALOR UNICO: {}'.format(valor_unico))

                # SELECCIONO LAS OPINIONES SEGUN IDS DE ALTERNATIVAS CUYO ATRIBUTO TOMA EL VALOR
                ids = df_alt[df_alt[atributo] == valor_unico]['id_alternativa']  # ids de alternativas donde atributo = valor
                df_cust_needs_sent_filt = df_cust_needs_sent[df_cust_needs_sent.id_alternativa.isin(ids)]  # opiniones de ids donde atributo = valor
                # print(df_opinion_cust_need_filt)

                n_opis, sent = get_n_opis_and_sent(df_relation_matrix_atrib, df_cust_needs_sent_filt)
                df_values_attr_sent.loc[len(df_values_attr_sent)] = [valor_unico, atributo, n_opis, sent]
                print("\t Fila:", [valor_unico, atributo, n_opis, sent])

            df_attr_value_sent_2 = pd.concat([df_attr_value_sent_2, df_values_attr_sent], ignore_index=True)  # para ver cantidad de opiniones en que se basa el sent de cada valor

            # PONDERO SENITMENT POR CANTIDAD DE OPINIONES PARA EL ATRIBUTO (salvo atrib con dos valores) (hay atrib 1-0 con proporcion 75-25, siempre ganara el 75 por la ponderacion..)
            df_values_attr_sent_pond = df_values_attr_sent.loc[:, ['valor', 'atributo','n_opi_con_sent']]
            # Si el atributo tiene mas de dos valores
            if len(df_values_attr_sent) > 2:
                # si tiene valores extremos...
                # handicap_sentiment_extreme_values(df_values_attr_sent)
                # Pondero
                # df_values_attr_sent_pond['sent'] = sentiment_weighing_by_quantity_opinions(df_values_attr_sent.loc[:, ['n_opi_con_sent', 'sent']])
                df_values_attr_sent_pond['sent'] = sentiment_weighing_by_quantity_opinions(df_values_attr_sent)

            # Si el atributo tiene dos valores (tipicamente atributos 1-0)
            else:
                # no pondero
                df_values_attr_sent_pond['sent'] = df_values_attr_sent['sent']

            # ESTANDARIZO SENTIMENT DE LOS VALORES DEL ATRIBUTO (se estandariza por atributo y no tod@ junto)
            df_values_attrs_sent_pond_norm = standardize_sentiment(df_values_attr_sent_pond)

            # Guardo datos del atributo
            df_values_attrs_sent_pond = pd.concat([df_values_attrs_sent_pond, df_values_attrs_sent_pond_norm], ignore_index=True)

        # SI EL ATRIBUTO FUE CREADO ARTIFICIALMENTE
        else:
            # asignar sent por alternativa en lugar de por valor...
            df_alt_sent = pd.DataFrame(columns=['id_alternativa', 'atributo', 'n_opi_con_sent', 'sent'])  # Dataframe para valores del atributo

            # Por alternativa
            for i in range(len(df_alt)):
                print("Nºalternativa: {}".format(i))

                # Obtengo sus opiniones
                id = df_alt.loc[i, 'id_alternativa']
                df_cust_needs_sent_filt = df_cust_needs_sent[df_cust_needs_sent['id_alternativa'] == id]

                n_opis, sent = get_n_opis_and_sent(df_relation_matrix_atrib, df_cust_needs_sent_filt)
                df_alt_sent.loc[len(df_alt_sent)] = [id, atributo, n_opis, sent]
                print("\t Fila:", [id, atributo, n_opis, sent])

            # PONDERO SENITMENT POR CANTIDAD DE OPINIONES PARA EL ATRIBUTO
            df_alt_sent_pond = df_alt_sent.loc[:, ['id_alternativa', 'atributo', 'n_opi_con_sent']]  # agregue 'n_opi_con_sent' para podeer ver cant de opis a pesar de ya pondere..
            df_alt_sent_pond['sent'] = sentiment_weighing_by_quantity_opinions(df_alt_sent)

            # ESTANDARIZO SENTIMENT DE LOS VALORES DEL ATRIBUTO (se estandariza por atributo y no tod@ junto)
            df_alt_sent_norm = standardize_sentiment(df_alt_sent_pond)

            # Guardo datos del atributo
            df_alts_sent = pd.concat([df_alts_sent, df_alt_sent_norm])

    # Exporto Dataframes (solo en pruebas)
    df_attr_value_sent_2.to_excel("/Users/nachomondino/Desktop/df_value_sent_opis.xlsx")
    df_values_attrs_sent_pond.to_excel("/Users/nachomondino/Desktop/df_attr_values_sent.xlsx")
    df_alts_sent.to_excel("/Users/nachomondino/Desktop/df_alt_sent_opis.xlsx")
    return df_values_attrs_sent_pond, df_alts_sent


################################################ FUNCIONES SECUNDARIAS ################################################
# UTILZADAS EN TO_CUSTOMER_NEEDS()
def cust_needs_in_text(l_cust_needs, text, d_rel_words, d_avoid_fp):
    """
    Determina si las palabras estan en el texto.
    :param l_cust_needs: Lista de strings. Necesidades del cliente
    :param text: String. Cadena de texto.
    :return: Diccionario cuyas keys son cada palabra y cuyos values son 1 o 0 segun si la palabra es mencionada en el
    texto o no respectivamente.
    """
    get_related_words = lambda word, d_rel_words: d_rel_words[word] if word in d_rel_words.keys() else [word]

    # Inicializo el diccionario a retornar
    d = {}
    for cust_need in l_cust_needs:
        d[cust_need] = 0

    # POR CUSTOMER NEED
    for cust_need in l_cust_needs:

        # POR PALABRA RELACIONADA (customer need y, si tiene, sus palabras relacionadas)
        for rel_word in get_related_words(word=cust_need, d_rel_words=d_rel_words):

            # SI ESTA EN LA FRASE
            if rel_word in text:

                # SI PUEDE TENER OTROS SIGNIFICADOS (Falso positivo)
                if rel_word.strip() in d_avoid_fp.keys():

                    fp = False  # Falso positivo

                    # POR SIGNIFICADO
                    for word in d_avoid_fp[rel_word.strip()]:

                        # SI TIENE OTRO SIGNIFICADO EN FRASE
                        if word in text:
                            fp = True
                            break

                    # SI SE REFIERE A LA CUSTOMER NEED (Verdadero positivo)
                    if not fp:
                        # GUARDO EL DATO DE QUE LA CUST NEED ES MENCIONADA EN LA FRASE
                        d[cust_need] = 1
                        break  # Dejo de buscar palabras relacionadas pues ya asigne sentiment a la customer need


                # SI NO TIENE OTROS SIGNIFICADOS (Verdadero positivo)
                else:
                    # GUARDO EL DATO DE QUE LA CUST NEED ES MENCIONADA EN LA FRASE
                    d[cust_need] = 1
                    break  # Dejo de buscar palabras relacionadas pues ya asigne sentiment a la customer need

                # break  # Dejo de buscar palabras relacionadas pues ya asigne sentiment a la customer need

    return d

def get_sentiment_score(sentence):
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

def assign_sentiment_to_cust_needs(d_cust_needs_mentioned, sent):  # estaria bueno que reciba sentence y cust needs y asigne. No se si lo puedo implemeentar porque uso info de n_cust_needs_ment antes...
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

def clean_text(text):

    # Lower
    text = text.lower()

    # Remuevo acentos
    text = delete_accent(text)

    # Agrego espacios al final y al principio
    text = " " + text + " "

    # Reemplazo comas por espacios
    text = text.replace(",", " ")
    text = text.replace("!", " ")

    return text

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

# UTILZADAS EN TO_ATTRIBUTES()
def get_n_opis_and_sent(df_relation_matrix_atrib, df_cust_needs_sent_filt):
    # Obtiene el sentiment del atributo en dataframe cust needs habiendo previamente el/los id/s que correspondan
    # return atributo, numero de opiniones con sent y sentiment
    # le podes pasar todas las alterntivas cuyo atrib tiene tal valor o bien, solo una alternativa...
    # Defino variables
    sum_relaciones = sum(df_relation_matrix_atrib)  # suma de valores de relaciones que tiene el atributo
    n_opi_con_sent, prom_sent = 0, 0  # inicializo variables pues el atrib puede tener relacion con mas de una customer need

    # POR CUSTOMER NEED
    for customer_need in df_relation_matrix_atrib.index:  # df_opinion_cust_need_filt.columns[1:]:  # no incluyo id_alt --> por que no use index de matriz de relaciones? que no tiene el id...

        # obtengo relacion entre customer need y relacion
        relacion = df_relation_matrix_atrib.loc[customer_need]
        # print("\t Customer need: {} ; Relacion con atributo: {} ".format(customer_need, relacion))

        # SI HAY RELACION ENTRE CUSTOMER NEED Y ATRIBUTO
        if relacion > 0:
            # OBTENGO CANTIDAD DE OPINIONES Y SENTIMENT PROMEDIO
            n_opi_con_sent += len(df_cust_needs_sent_filt[customer_need].dropna())
            prom_sent += df_cust_needs_sent_filt[customer_need].dropna().mean() / sum_relaciones
            print('\t Customer need: {} \t Relacion con atributo: {} \t n_opi_con_sent: {} \t Sentiment: {:.2f}'.format(customer_need, relacion, n_opi_con_sent, prom_sent))

    # GUARDO VALOR, ATRIBUTO AL QUE PERTENECE, CANT DE OPINIONES Y SENTIMENT
    if n_opi_con_sent == 0 and prom_sent == 0:
        n_opi_con_sent, prom_sent = None, None

    return [n_opi_con_sent, prom_sent]

def sentiment_weighing_by_quantity_opinions(df):
    """
    Pondera sentiment segun cantidad de opiniones en que se basa
    :param df: Dataframe. Unidad de analisis: alternativa o valor de atributo. Columnas: cantidad de opiniones en que se
    basa en sentiment y sentiment
    :return: Dataframe. Unidad de analisis: alternativa o valor de atributo. Columnas: sentiment (ponderado por cantidad
     de opiniones)
    """
    # Defino variables
    df_sent_pond = pd.DataFrame(columns=['sent'])  # Dataframe a retornar
    n_max_opis_attr = df["n_opi_con_sent"].max()  # factor 1, cant de opiniones max de un valor del atributo
    n_unique_val_with_opis = len(df[df['n_opi_con_sent'] > 0])  # no considero valores sin opiniones
    n_opt_opis_x_val = df["n_opi_con_sent"].sum() / n_unique_val_with_opis  # factor 2, cant optima de opis por valor del
    get_factor_final = lambda f1, f2, f3: 1 if 0.1 * f1 + 0.9 * f2 + f3 > 1 else 0.1 * f1 + 0.9 * f2 + f3
    unidad_analisis = df.columns[0]
    print("Atributo: {}".format(df.loc[0, 'atributo']).center(120))

    # POR FILA DEL DATAFRAME
    for i in range(len(df)):
        print("Nº{}: {}".format(i, df.loc[i, unidad_analisis]))

        # OBTENGO CANTIDAD DE OPINIONES Y SENTIMENT
        n_opis = df.loc[i, 'n_opi_con_sent']
        sent = df.loc[i, 'sent']

        # SI EL VALOR NO TIENE OPINIONES, O BIEN, TIENE MUY POCAS OPINIONES
        if str(sent) == 'nan' or n_opis < 0.25 * n_opt_opis_x_val:

            # Guardo sentiment None
            df_sent_pond.loc[len(df_sent_pond)] = [None]

        # SI EL VALOR TIENE RELATIVAMENTE BUENA CANTIDAD DE OPINIONES (+ opis => + confiabilidad en sent)
        else:
            # CALCULO FACTOR
            f1 = n_opis / n_max_opis_attr  # Porcentaje de nºopis respecto a nºopis max del atributo
            f2 = n_opis / n_opt_opis_x_val  # Porcentaje de nºopis respecto a nºopis optima por valor del atributo
            f3 = get_factor_3(df, i)
            ff = get_factor_final(f1, f2, f3)
            print("\t F1: {:.2f} \t F2: {:.2f} \t F3: {:.2f} \t --> \t Factor final: {:.2f}".format(f1, f2, f3, ff))

            # PONDERO SENTIMENT CON FACTOR Y LO GUARDO
            sent_pond = sent * ff
            df_sent_pond.loc[len(df_sent_pond)] = [sent_pond]
            print("\t Sentiment: {:.3f} --> {:.3f} ".format(sent, sent_pond))

        '''   
        # SI EL VALOR TIENE SENTIMENT
        if str(sent) != 'nan':
            # print("\t Sentiment: {:.3f} \t Cantidad de opis: {}".format(sent, n_opis))
            
            # Si el valor tiene muy pocas opiniones (Agrega ruido pues su ponderacion lo llevara a sent = 0)
            if n_opis < 0.1 * n_opt_opis_x_val:
                
                # Reemplazo sentiment por NaN (para evitar enmascaramiento en estandarizacion)
                sent_pond = None
                
            # Si el valor tiene sentiment relativamente confiable (no tiene tan pocas opiniones)
            else:
                # CALCULO FACTOR
                f1 = n_opis / n_max_opis_attr  # Porcentaje de nºopis respecto a nºopis max del atributo
                f2 = n_opis / n_opt_opis_x_val  # Porcentaje de nºopis respecto a nºopis optima por valor del atributo
                f3 = get_factor_3(df, i)
                ff = get_factor_final(f1,f2,f3)
                print("\t F1: {:.2f} \t F2: {:.2f} \t F3: {:.2f} \t --> \t Factor final: {:.2f}".format(f1, f2, f3, ff))
    
                # PONDERO SENTIMENT CON FACTOR
                sent_pond = sent * ff
            
            # Guardo sentiment ponderado
            df_sent_pond.loc[len(df_sent_pond)] = [sent_pond]
            print("\t Sentiment: {:.3f} --> {:.3f} ".format(sent, sent_pond))

        # SI EL VALOR TIENE SENTIMENT NAN
        else:
            # NO PONDERO EL SENTIMENT Y LO GUARDO COMO NAN
            df_sent_pond.loc[len(df_sent_pond)] = [None]
            # print("El valor {} tiene sentiment NaN".format(valor))
        '''

    return df_sent_pond

def get_factor_3(df, idx):
    # DEFINO VARIABLES
    FACTOR = 0

    # solo para valores de atrib (no para alternativas)
    if 'valor' in df.columns:

        # Defino variables
        df_filt = df[df['n_opi_con_sent'] > 25]  # remuevo valores con pocas opiniones. Agregan ruido a l_sent y l_unique_val. Por ej, hay valores con 1 opi y el mejor sent. Eso quita un cupo en lista de l_sent y esta mal que asi sea.
        l_unique_val_sort, l_sent_sort = sorted(df_filt['valor']), sorted(df_filt['sent'].dropna())
        idx_percentil = int(round(0.25 * len(df_filt), 0))
        l_valores_ext = l_unique_val_sort[:idx_percentil] + l_unique_val_sort[-idx_percentil:]
        l_best_sent = l_sent_sort[-idx_percentil:]
        print(idx_percentil)
        print("\t Valores extremos: {} \t Sentiment: {}".format(l_valores_ext, l_best_sent))

        # SI EL ATRIBUTO ES NUMERICO
        if df['valor'].dtype == 'float64':

            # Defino variables
            valor = df.loc[idx, 'valor']
            sent = df.loc[idx, 'sent']

            # SI ES VALOR EXTREMO Y SU SENTIMENT ES DE LOS MEJORES
            if valor in l_valores_ext and sent in l_best_sent:
                FACTOR = 0.5
                print("\t Ayudo al factor final en {:.2f}".format(FACTOR))
    return FACTOR

def standardize_sentiment(df):
    """
    Normaliza los sentiment de los valores de un atributo. Esto quita las escala para los diferentes atributos
    :param df: Daraframe. Unidad de analisis: alternativa o valor de un atributo. Las columnas son valor, atributo al que
    pertenece este y su sentiment ya ponderado
    :return: Daraframe igual al pasado por parametro salvo con columna sentiment normalizada
    """
    # Defino variable
    df_sin_nan = df.dropna(subset=['sent'])  # borro unidedes de analisis cuyo sentiment=NaN

    # Los atributos que toman un solo valor y por ende tienen un solo sent, fallan en el calculo del desvio porque se necesitan al menos dos data points (es decir, al menos dos valores cada uno con su sentiment)
    # Si tiene dos o mas sentiment distintos (evita attr con 1 solo sentiment)
    if len(set(df_sin_nan['sent'])) >= 2:
        # Obtengo media y desvio de sentiments
        media = st.mean(df_sin_nan['sent'])  # media de sentiment de los valores del atributo
        desv = st.stdev(df_sin_nan['sent'])  # desvio de sentiment de los valores del atributo

        # NORMALIZO EL SENTIMENT
        # Por fila del dataframe
        for i in list(df_sin_nan.index):  # solo indices de sent≠NaN
            # Obtengo el sentiment del valor
            sent_valor = df.loc[i, 'sent']
            # Normalizo dicho sentiment y lo guardo
            new_sent_valor = (sent_valor - media) / desv
            df.loc[i, 'sent'] = new_sent_valor
    else:
        print("ERROR! Columna que fallo: ", df['atributo'].unique())
    return df



'''
# Correr solo to_attributes()
producto = "celulares"
df_alt_cleaned = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_alt_cleaned.xlsx'.format(producto))
df_cust_need_sent = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/atribucion/{}/df_cust_need_sent.xlsx'.format(producto))
df_relation_matrix = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_relation_matrix.xlsx'.format(producto), index_col=0)
print(df_alt_cleaned), print(df_relation_matrix), print(df_cust_need_sent)

print("4.1.2 Atribuyo sentiment a valores de los atributos del producto...".center(120))
df_attr_values_sent, df_alts_sent = to_attribute(df_alt_cleaned, df_cust_need_sent, df_relation_matrix)

df_attr_values_sent.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/atribucion/{}/df_attr_values_sent.xlsx'.format(producto), index=False)  # cuando corra tod@ junto pongo product.nombre
df_alts_sent.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/atribucion/{}/df_attr_alt_sent.xlsx'.format(producto), index=False)  # cuando corra tod@ junto pongo product.nombre
'''





''' Deje de borrar parentesis por el momento...
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
'''