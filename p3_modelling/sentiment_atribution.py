# Importo librerias
import pandas as pd
from pysentimiento import create_analyzer
import stanza
import statistics as st

analyzer = create_analyzer(task="sentiment", lang="es")  # para realizar el sentiment
pos_tagger = stanza.Pipeline(lang='es', processors='tokenize,pos,mwt')

################################################ FUNCIONES PRINCIPALES ################################################
def to_customer_needs(df_opi, l_customer_needs_one_word, d_pal_rel, d_avoid_fp):
    """
    Identifica, si hay, customer needs en opiniones y asigna el sentiment a cada una mediante la libreria pysentimiento
    :param df_opi: Dataframe. Unidad de analisis: opinion del producto. Columnas: id_alternativa y opinion. Las opiniones
     no tienen procesamiento
    :param l_customer_needs_one_word: Lista. Customer needs en 1 sola palabra
    :return: Dataframe. Unidad de analisis: opinion del producto. Columnas: id_alternativa y una por customer need.
    Celdas: sentiment de la customer need en la opinion, o bien, si la opinion no habla de la customer need, None.
    """
    # DEFINO VARIABLES
    idx_id, idx_opi = df_opi.columns.get_loc("id_alternativa"), df_opi.columns.get_loc("opinion")  # indices utiles para tener flexibilidad en codigo (posibilidad de columnas en otra posicion)
    df_cust_needs_sent = pd.DataFrame(columns=["id_alternativa"] + l_customer_needs_one_word)  # dataframe a retornar
    choose_sep = lambda text: "," if text.count(",") >= 1 else ';'
    split_frase_in_commas = lambda frase: frase.split(choose_sep(frase)) if conviene_separar_comas(frase) else [frase]

    # POR OPINION
    for i in range(len(df_opi)):

        # Defino variables
        id_alt, opinion = df_opi.iloc[i, idx_id], df_opi.iloc[i, idx_opi]  # Defino id y opinion
        l_frases = opinion.split(".")  # Frases de la opinion
        df_frases_cust_needs = pd.DataFrame(columns=l_customer_needs_one_word)  # Dataframe con sent de frases de opinion
        print("NºFila: {}".center(120).format(i)), print("OPINION:", opinion)

        # OBTENGO SENTIMENT DE OPINION
        sent_opi = get_sentiment_score(sentence=opinion)
        print("\t Sentiment de toda la opinion: {:.2f}".format(sent_opi))
        print("Divido la opinion en {} frases.".format(len(l_frases)))

        # POR FRASE DE LA OPINION
        for j in range(len(l_frases)):  # for frase in l_frases: evito contador de frases

            # OBTENGO SENTIMENT DE FRASE
            frase = l_frases[j]
            sent_frase = get_sentiment_score(sentence=frase)
            print("FRASE Nº{}: {} \n\t Sentiment de la frase: {:.2f}".format(j + 1, frase, sent_frase))

            # IDENTIFICO QUE CUSTOMER NEEDS QUE MENCIONA
            df_cust_needs_mentioned = identificate_cust_needs_in_text(l_customer_needs_one_word, frase, d_pal_rel,d_avoid_fp)
            n_cust_need_ment = sum(df_cust_needs_mentioned.loc[0].values)  # numero de customer needs mencionadas en frase

            # SI MENCIONA AL MENOS 2 CUSTOMER NEEDS Y EL SENTIMENT NO ES CATEGORICO
            if (n_cust_need_ment >= 2) and (sent_frase < 0.4 and sent_frase > -0.4):

                # Divido frase segun comas
                l_frases_entre_comas = split_frase_in_commas(frase)
                print("Divido frase Nº{} en {} frase entre comas".format(j + 1, len(l_frases_entre_comas)))

                # POR FRASE ENTRE COMAS
                for frase_entre_comas in l_frases_entre_comas:

                    # IDENTIFICO CUSTOMER NEEDS
                    df_cust_needs_mentioned = identificate_cust_needs_in_text(l_customer_needs_one_word, frase_entre_comas, d_pal_rel,d_avoid_fp)
                    print("\t FRASE ENTRE COMAS: ", frase_entre_comas)

                    # SI HAY AL MENOS UNA CUSTOMER NEED
                    if sum(df_cust_needs_mentioned.loc[0].values) > 0:

                        # Obtengo sentiment de frase entre comas
                        sent_frase_entre_comas = get_sentiment_score(sentence=frase_entre_comas)
                        print("\t\t Sentiment de frase entre comas: {:.2f}".format(sent_frase_entre_comas))

                        # ASIGNO SENTIMENT A CUSTOMER NEEDS MENCIONADAS
                        df_frases_cust_needs = pd.concat([df_frases_cust_needs, assign_sentiment_to_cust_needs(frase_entre_comas, sent_opi, sent_frase_entre_comas, df_cust_needs_mentioned)])  # usaria sentiment de la frase en vez de opinion
                        print(df_frases_cust_needs)

                    # Si no hay customer needs
                    else:
                        print("\t\t La frase no contiene customer needs")

            # SI MENCIONA UNA CUSTOMER NEED, O BIEN, MAS DE UNA CUSTOMER NEED Y EL SENTIMENT ES CATEGORICO
            elif n_cust_need_ment > 0:  # ojo que puede haber frases que mencionen mas de una y sea categorica

                # ASIGNO SENTIMENT A CUSTOMER NEEDS MENCIONADAS
                df_frases_cust_needs = pd.concat([df_frases_cust_needs, assign_sentiment_to_cust_needs(frase, sent_opi,sent_frase,df_cust_needs_mentioned)])
                print(df_frases_cust_needs)

            # SI NO MENCIONA CUSTOMER NEEDS
            else:
                pass

        # OBTENGO SENTIMENT DE CUSTOMER NEEDS EN OPINION (pues puede aparecer en mas de una frase)
        df_cust_needs_sent.loc[i, 'id_alternativa'] = id_alt
        for customer_need in l_customer_needs_one_word:
            # Guardo el sentiment de la customer need en la opinion
            df_cust_needs_sent.loc[i, customer_need] = df_frases_cust_needs[customer_need].dropna().mean()
        print(df_cust_needs_sent)

    return df_cust_needs_sent

def to_attribute(df_alt, df_cust_needs_sent, df_relation_matrix):
    """
    Atribucion de sentiment de customer needs a atributos del producto mediante matriz de relaciones.
    :param df_alt: Dataframe. Unidad de analisis: alternativa del producto. Columnas: id_alternativa, precio y atributos
    del producto. Celdas: el valor que toma el atributo en una alternativa
    :param df_cust_needs_sent: Dataframe. Unidad de analisis: opinion del producto. Columnas:  id_alternativa y una por
    customer need. Celdas: sentiment de la customer need en la opinion, o bien, si la opinion no habla de la customer
    need, None.
    :param df_relation_matrix: Dataframe. Filas: customer need de producto. Columnas: atributos o campos especificos del
    producto. Celdas: relacion entre customer need  i y atributo j
    :return:
    - Dataframe. Unidad de analisis: valor de atributo del producto. Columnas: valor, atributo al que pertenece, numero
     de opiniones en que basa su sentiment y su sentiment.
    - Dataframe. Unidad de analisis: alternativa del producto. Columnas: id_alternativa, atributo (ficticio), numero
    de opiniones en que basa su sentiment y su sentiment.
    """
    # Defino sentiment que retornare
    df_values_attrs_sent = pd.DataFrame(columns=['valor', 'atributo', 'n_opi_con_sent', 'sent'])
    df_alts_sent = pd.DataFrame(columns=['id_alternativa', 'atributo', 'n_opi_con_sent', 'sent'])

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
                l_ids = df_alt[df_alt[atributo] == valor_unico]['id_alternativa']  # ids de alternativas donde atributo = valor
                df_cust_needs_sent_filt = df_cust_needs_sent[df_cust_needs_sent.id_alternativa.isin(l_ids)]  # opiniones de ids donde atributo = valor
                # print(df_opinion_cust_need_filt)

                # OBTENGO NºOPIS Y SENTIMENT Y LO GUARDO
                n_opis, sent = get_n_opis_and_sent(df_relation_matrix_atrib, df_cust_needs_sent_filt)
                df_values_attr_sent.loc[len(df_values_attr_sent)] = [valor_unico, atributo, n_opis, sent]
                print("\t Fila:", [valor_unico, atributo, n_opis, sent])

            # PONDERO SENTIMENT POR CANTIDAD DE OPINIONES
            # Si tiene mas de dos valores unicos
            if len(df_values_attr_sent) > 2:
                # Pondero sentiment
                df_sent_pond = sentiment_weighing_by_quantity_opinions(df_values_attr_sent)

            # Si tiene dos o menos valores unicos
            else:
                # No pondero sentiment
                df_sent_pond = df_values_attr_sent
                print("\t No pondero sentiment pues el atributo toma dos valores")

            # GUARDO DATOS DEL ATRIBUTO
            df_values_attrs_sent = pd.concat([df_values_attrs_sent, df_sent_pond])

        # SI EL ATRIBUTO FUE CREADO ARTIFICIALMENTE ("ATRIBUTO FICTICIO")
        else:
            # Defino variable
            df_alt_sent = pd.DataFrame(columns=['id_alternativa', 'atributo', 'n_opi_con_sent', 'sent'])  # Dataframe para valores del atributo

            # POR ALTERNATIVA
            for i in range(len(df_alt)):
                print("Nºalternativa: {}".format(i))

                # SELECCIONO SUS OPINIONES
                id_alt = df_alt.loc[i, 'id_alternativa']  # Id de alternativa
                df_cust_needs_sent_filt = df_cust_needs_sent[df_cust_needs_sent['id_alternativa'] == id_alt]

                # OBTENGO NºOPIS Y SENTIMENT Y LO GUARDO
                n_opis, sent = get_n_opis_and_sent(df_relation_matrix_atrib, df_cust_needs_sent_filt)
                df_alt_sent.loc[len(df_alt_sent)] = [id_alt, atributo, n_opis, sent]
                print("\t Fila:", [id_alt, atributo, n_opis, sent])

            # PONDERO SENITMENT POR CANTIDAD DE OPINIONES
            df_sent_pond = sentiment_weighing_by_quantity_opinions(df_alt_sent)

            # GUARDO DATOS DEL ATRIBUTO
            df_alts_sent = pd.concat([df_alts_sent, df_sent_pond])

    # Exporto Dataframes (solo en pruebas)
    df_values_attrs_sent.to_excel("/Users/nachomondino/Desktop/df_attr_values_sent.xlsx")
    df_alts_sent.to_excel("/Users/nachomondino/Desktop/df_alt_sent_opis.xlsx")
    return df_values_attrs_sent, df_alts_sent


################################################ FUNCIONES SECUNDARIAS ################################################
# UTILZADAS EN TO_CUSTOMER_NEEDS()
def get_sentiment_score(sentence):
    """
    Calcula el score (sentiment) de una frase
    :param sentence: String. Cadena de texto cualquiera
    :return: Float. Score o sentiment de frase
    """
    # Obtengo sentiment de sentence
    pred = analyzer.predict(sentence)  # ejemplo de output: AnalyzerOutput(output=NEU, probas={NEU: 0.802, NEG: 0.188, POS: 0.010})
    sent_frase = pred.probas  # accedo a probas de AnalyzerOutput

    # Calculo score
    score = sent_frase['POS'] - sent_frase['NEG']  # obtengo probabilidades de POS y NEG y calculo score
    return score

def identificate_cust_needs_in_text(l_cust_needs, text, d_rel_words, d_avoid_fp):
    """
    Determina si las customer needs son mencionadas en el texto.
    :param l_cust_needs: Lista de strings. Necesidades del cliente
    :param text: String. Cadena de texto.
    :return: Dataframe. Unidad de analisis: Cadena de texto. Columnas: una por customer need del producto. Celdas:
    1 o 0 segun si la palabra es mencionada en el texto o no respectivamente.
    """
    # Defino variables
    get_related_words = lambda word, d_rel_words: d_rel_words[word] if word in d_rel_words.keys() else [word]
    df = pd.DataFrame(columns=l_cust_needs)
    df.loc[0] = 0

    # Limpio texto
    text = " " + delete_accent(text.lower()) + " "  # limpio la frase para poder identificar customer needs en ella. Agrego espacios para identificar la primera y la ultima palabra
    text = text.replace(",", " ").replace("!", " ")

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
                            # NO DOY POR IDENTIFICADA LA CUSTOMER NEED
                            fp = True
                            break

                    # SI SE REFIERE A LA CUSTOMER NEED (Verdadero positivo)
                    if not fp:
                        # GUARDO EL DATO DE QUE LA CUST NEED ES MENCIONADA EN LA FRASE
                        df.loc[0, cust_need] = 1
                        break  # Dejo de buscar palabras relacionadas pues ya asigne sentiment a la customer need

                # SI NO TIENE OTROS SIGNIFICADOS (Verdadero positivo)
                else:
                    # GUARDO EL DATO DE QUE LA CUST NEED ES MENCIONADA EN LA FRASE
                    df.loc[0, cust_need] = 1
                    break  # Dejo de buscar palabras relacionadas pues ya asigne sentiment a la customer need
    return df

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

            # y no es un adjetivo
            if not contains_word_type(text=frase, word_type=['ADJ']):

                # No conviene separar por comas
                return False
    return True

def assign_sentiment_to_cust_needs(frase, sent_opi, sent_frase, df_cust_needs_mentioned):  # Vigente
    """
    Asigna sentiment a customer needs mencionadas en frase
    :param frase: String. Frase de opinion
    :param sent_opi: Float. Sentiment de opinion
    :param sent_frase: Float. Sentiment de frase de opinion
    :param df_cust_needs_mentioned: Dataframe. Unidad de analisis: frase de opinion. Columnas: una por customer need.
    Celdas: 1 si customer need es mencionada en frase, de lo contrario, 0
    :return: Dataframe. Unidad de analisis: frase de opinion. Columnas: una por customer need. Celdas: sentiment si
    customer need es mencionada en frase, de lo contrario, NaN
    """
    # Defino variable
    df_frases_cust_needs = pd.DataFrame(columns=list(df_cust_needs_mentioned.columns))  # Dataframe con sent de frases de opinion

    # SI FRASE CONTIENE AL MENOS UN ADJETIVO
    if contains_word_type(text=frase, word_type=['ADJ']):

        # Si el sentiment de la frase no se corresponde con el de la opinion
        if (sent_opi < -0.9 and sent_frase > 0 and sent_frase < 0.28) or (sent_opi > 0.9 and sent_frase > -0.28 and sent_frase < 0):
            # Seteo sentiment a asignar como el de la frase con ponderacion
            sent_to_assign = 0.8 * sent_frase + 0.2 * sent_opi
            print("\t\t Es probable que el sentiment de la frase sea incorrecto dado que el de la opinion es totalmente opuesto. Sentiment ponderado = {:.2f}".format(sent_frase), end=" ")
        # Si el sentiment de la frase si se corresponde con el de la opinion
        else:
            # Seteo sentiment a asignar como el de la frase
            sent_to_assign = sent_frase

    # SI FRASE NO CONTIENE ADJETIVOS PERO SU SENTIMENT ES CATEGORICO
    elif (sent_frase > 0.8 or sent_frase < -0.8) or ((sent_opi < -0.8 and sent_frase < -0.5) or (sent_opi > 0.8 and sent_frase > 0.5)):
        # Seteo sentiment a asignar como el sentiment de la frase
        sent_to_assign = sent_frase
        print("\t\t La frase no contiene adjetivos pero se guardara el sentiment de todas maneras")

    # Si no contiene adjetivos y su sentiment es neutral
    else:
        # Seteo sentiment a asignar como el sentiment de la frase
        sent_to_assign = None
        print("\t\t La frase no contiene adjetivos")

    # Por customer need
    for cust_need in df_cust_needs_mentioned.columns:
        # Asigno sentiment "sent_to_assign"
        df_frases_cust_needs.loc[0, cust_need] = sent_to_assign if df_cust_needs_mentioned.loc[0, cust_need] == 1 else None
    # print(df_frases_cust_needs)
    return df_frases_cust_needs

def contains_word_type(text, word_type):
    """
    Verifica si una cadena de texto tiene o no el word_type
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
            prom_sent += df_cust_needs_sent_filt[customer_need].dropna().mean() * relacion / sum_relaciones
            print('\t Customer need: {} \t Relacion con atributo: {} \t n_opi_con_sent: {} \t Sentiment: {:.2f}'.format(customer_need, relacion, n_opi_con_sent, prom_sent))

    # GUARDO VALOR, ATRIBUTO AL QUE PERTENECE, CANT DE OPINIONES Y SENTIMENT
    if n_opi_con_sent == 0 and prom_sent == 0:
        n_opi_con_sent, prom_sent = None, None

    return [n_opi_con_sent, prom_sent]

def sentiment_weighing_by_quantity_opinions(df):
    """
    Pondera sentiment segun cantidad de opiniones en que se basa
    :param df: Dataframe. Unidad de analisis: alternativa o valor de atributo. Columnas: Unidad de analisis (valor de
    atributo o alternativa del producto), atributo (ya sea real o ficticio), cantidad de opiniones y sentiment
    :return: Dataframe. Unidad de analisis: alternativa o valor de atributo. Columnas: sentiment (ponderado por cantidad
     de opiniones)
    """
    # Defino variables
    n_max_opis_attr = df["n_opi_con_sent"].max()  # factor 1, cant de opiniones max de un valor del atributo
    n_unique_val_with_opis = len(df[df['n_opi_con_sent'] > 0])  # no considero valores sin opiniones
    n_opt_opis_x_val = df["n_opi_con_sent"].sum() / n_unique_val_with_opis  # factor 2, cant optima de opis por valor del
    unidad_analisis = df.columns[0]
    print("Atributo: {}".format(df.loc[0, 'atributo']).center(120))

    # POR UNIDAD DE ANALISIS (VALOR ATRIBUTO O ALTERNATIVA SEGUN EL CASO)
    for i in df.index:  # for i in range(len(df)):
        print("Nº{}: {}".format(i, df.loc[i, unidad_analisis]))

        # OBTENGO CANTIDAD DE OPINIONES Y SENTIMENT
        n_opis = df.loc[i, 'n_opi_con_sent']
        sent = df.loc[i, 'sent']

        # SI NO TIENE OPINIONES, O BIEN, TIENE MUY POCAS OPINIONES
        if n_opis < 0.2 * n_opt_opis_x_val:

            # REEMPLAZO SENTIMENT POR NONE
            df.loc[i, 'sent'] = None

        # SI EL VALOR TIENE RELATIVAMENTE BUENA CANTIDAD DE OPINIONES (+ opis => + confiabilidad en sent)
        else:
            # CALCULO FACTOR
            f1 = n_opis / n_max_opis_attr  # Porcentaje de nºopis respecto a nºopis max del atributo
            f2 = n_opis / n_opt_opis_x_val  # Porcentaje de nºopis respecto a nºopis optima por valor del atributo
            f3 = get_factor_3(df, i) if unidad_analisis == 'valor' else 0
            ff = 1 if 0.1 * f1 + 0.9 * f2 + f3 > 1 else 0.1 * f1 + 0.9 * f2 + f3
            print("\t F1: {:.2f} \t F2: {:.2f} \t F3: {:.2f} \t --> \t Factor final: {:.2f}".format(f1, f2, f3, ff))

            # PONDERO SENTIMENT CON FACTOR Y LO GUARDO
            sent_pond = sent * ff
            df.loc[i,'sent'] = sent_pond
            print("\t Sentiment: {:.3f} --> {:.3f} ".format(sent, sent_pond))
    return df

def get_factor_3(df, idx):
    """
    Obtiene factor 3 de ponderacion para valor del atributo
    :param df: Dataframe. Unidad de analisis: valor de atributo del producto. Columnas: valor, atributo al que pertenece,
    numero de opiniones en que basa su sentiment y su sentiment.
    :param idx: Integer. Indice de valor del atributo en Dataframe
    :return: Float. Factor 3 de ponderacion
    """
    # Defino variables
    FACTOR = 0

    # SI EL ATRIBUTO ES NUMERICO
    if df['valor'].dtype == 'float64':

        # Defino variables
        df_filt = df[df['n_opi_con_sent'] > 25]  # remuevo valores con pocas opiniones. Agregan ruido a l_sent y l_unique_val. Por ej, hay valores con 1 opi y el mejor sent. Eso quita un cupo en lista de l_sent y esta mal que asi sea.
        l_unique_val_sort, l_sent_sort = sorted(df_filt['valor']), sorted(df_filt['sent'].dropna())
        idx_percentil = int(round(0.25 * len(df_filt), 0))  # Indice del valor del atributo que corresponde al percentil 0.25
        l_valores_ext = l_unique_val_sort[:idx_percentil] + l_unique_val_sort[-idx_percentil:]
        l_best_sent = l_sent_sort[-idx_percentil:]
        valor = df.loc[idx, 'valor']
        sent = df.loc[idx, 'sent']
        print("\t Valores extremos: {} \t Sentiment: {}".format(l_valores_ext, l_best_sent))

        # SI ES VALOR EXTREMO Y SU SENTIMENT ES DE LOS MEJORES
        if valor in l_valores_ext and sent in l_best_sent:
            # AYUDO EN PONDERACION DEL VALOR
            FACTOR = 0.5
            print("\t Ayudo al factor final en {:.2f}".format(FACTOR))
    return FACTOR


# CORRER PRUEBAS
'''
# Correr solo to_customer_needs()
from p3_modelling.diccionario_palabras_relacionadas import get_dict_related_words, get_dict_avoid
producto = 'celulares'
df_opi = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_opi_without_date.xlsx'.format(producto))
df_relation_matrix = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_relation_matrix.xlsx'.format(producto), index_col=0)
l_customer_needs_one_word = list(df_relation_matrix.index)
d_pal_rel = get_dict_related_words(producto)
d_avoid_fp = get_dict_avoid(producto)
df_cust_needs_sent = to_customer_needs(df_opi, l_customer_needs_one_word, d_pal_rel, d_avoid_fp)
df_cust_needs_sent.to_excel("/Users/nachomondino/Desktop/df_to_cust_need_prueba.xlsx")  # para ver que funcione bien los cambios
'''

'''
# Correr solo to_attributes()
producto = "smartband"
df_alt_cleaned = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_alt_cleaned.xlsx'.format(producto))
df_cust_need_sent = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/atribucion/{}/df_cust_need_sent.xlsx'.format(producto))
df_relation_matrix = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_relation_matrix.xlsx'.format(producto), index_col=0)
print(df_alt_cleaned), print(df_relation_matrix), print(df_cust_need_sent)

print("4.1.2 Atribuyo sentiment a valores de los atributos del producto...".center(120))
df_attr_values_sent, df_alts_sent = to_attribute(df_alt_cleaned, df_cust_need_sent, df_relation_matrix)

# df_attr_values_sent.to_excel('/Users/nachomondino/Desktop/df_attr_values_sent_nueva.xlsx'.format(producto), index=False)  # cuando corra tod@ junto pongo product.nombre
# df_attr_values_sent.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/atribucion/{}/df_attr_values_sent.xlsx'.format(producto), index=False)  # cuando corra tod@ junto pongo product.nombre
# df_alts_sent.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/atribucion/{}/df_attr_alt_sent.xlsx'.format(producto), index=False)  # cuando corra tod@ junto pongo product.nombre
'''

