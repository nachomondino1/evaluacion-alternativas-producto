# Importo librerias
import pandas as pd
import nltk
from pysentimiento import create_analyzer


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
        print(df_opinion_cust_needs)

    # EXPORTO DATAFRAME
    df_opinion_cust_needs.to_excel('/Users/nachomondino/Desktop/df_opinion_cust_needs.xlsx', 'Hoja de datos',index=False)
    print(df_opinion_cust_needs)

    return df_opinion_cust_needs

def create_relation_matrix(atributos, customer_needs):
    """
    Crea matriz de relaciones entre customer needs y atributos del producto. Para ello, pide al usuario por terminal
    la relacion entre cada uno.
    :param atributos: Lista de atributos o campos especificos de un producto
    :param customer_needs: Lista de customer needs (de 1 sola palabra) de un producto
    :return: Dataframe con atributos como columnas y customer needs como filas. Celda indica relacion entre customer
    need  i y atributo j
    """
    # REMUEVO ATRIBUTOS CUYOS VALORES NO DEBERIAN TENER SENTIMENT (tipicamente los que solo son extraidos para ser mostrado al cliente)
    atributos_a_no_considerar = ["Modelo", "Línea"]  # Defino lista de atributos a no incluir en matriz de relaciones
    # Por atributo a no considerar
    for atributo in atributos_a_no_considerar:
        # Si el atributo estan en atributos
        try:
            # quito el atributo a no considerar
            atributos.remove(atributo)
        # Si el atributo no esta en atributos
        except ValueError:  # ValueError: list.remove(x): x not in list
            # no hago nada
            pass

    # DEFINO VARIABLES
    relation_matrix = pd.DataFrame(columns=atributos, index=customer_needs)  # Dataframe a retornar

    # POR ATRIBUTO O CAMPO ESPECIFICO DEL PRODUCTO
    for atributo in atributos:

        # POR CUSTOMER NEED DEL PRODUCTO
        for customer_need in customer_needs:

            # SOLICITO RELACION ENTRE ATRIBUTO Y CUSTOMER NEED POR TERMINAL
            # Validacion de ingreso de datos, solicito relacion hasta que el input sea 0, 1, 3 o 9
            while True:
                try:
                    input_admin = int(input("Ingrese relacion entre atributo '{}' y customer need '{}'(0, 1, 3 o 9 ptos): ".format(atributo.upper(),customer_need.upper())))

                    # Si el input del admin es 0, 1, 3 o 9
                    if input_admin in [0, 1, 3, 9]:
                        # Administrador cargo relacion correctamente
                        relation_matrix.loc[customer_need, atributo] = input_admin
                        break
                    # Si el input del admin no es 0, 1, 3 o 9
                    else:
                        print("Ingreso no valido. El ingreso debe ser un numero, en particular, 0, 1, 3 o 9. ")

                # Si el input no es un numero
                except ValueError:
                    # sigo en el ciclo while hasta que cargue la relacion correctamente
                    print("Ingreso no valido. El ingreso debe ser un numero, en particular, 0, 1, 3 o 9. ")

    # EXPORTO MATRIZ DE RELACIONES
    relation_matrix.to_excel('/Users/nachomondino/Desktop/relation_matrix.xlsx', 'Hoja de datos', index_label="customer_need")
    return relation_matrix

def to_attribute_value(df_alternativas, df_opinion_cust_need, relation_matrix):
    """
    Mediante la matriz de relaciones, atribuyo los sentiment de las customer needs a los valores de los atributos del
    producto. Tendre que considerar la complicacion de la cantidad de opiniones en que se basa el sentiment de cada
    valor.
    :param df_alternativas: Dataframe cuya unidad de analisis es cada una de las alternativas del producto, sus columnas son
    los atributos del producto y las celdas el valor que toma el atributo en una alternativa
    :param df_opinion_cust_need: Dataframe cuya unidad de analisis es una opinion, sus columnas son cada customer
    need y las celdas el sentiment o score de la customer need en la opinion
    :param relation_matrix: Dataframe con atributos como columnas y customer needs como filas. Celda indica relacion
    entre customer need i y atributo j
    :return: Dataframe cuya unidad de analisis son los valores de los atributos del producto. Sus columnas son valor,
     atributo al que perenece y su sentiment
    """
    # Defino sentiment que retornare
    df_values_attrs_sent_pond = pd.DataFrame(columns=['valor', 'atributo', 'sent'])
    df_attr_value_sent_2 = pd.DataFrame(columns=['valor', 'atributo', 'cant_opi_con_sent', 'sent'])

    print(relation_matrix)

    # POR CAMPO ESPECIFICO O ATRIBUTO DEL PRODUCTO
    for atributo in relation_matrix.columns:
        print(atributo)

        # Defino variables
        df_values_attr_sent = pd.DataFrame(columns=['valor', 'atributo', 'cant_opi_con_sent', 'sent'])  # Dataframe para valores del atributo
        sum_relaciones = sum(relation_matrix[atributo])  # suma de valores de relaciones que tiene el atributo

        # POR VALOR DEL ATRIBUTO
        for valor_unico in df_alternativas[atributo].dropna().unique():  # hay modelos cuyo atrib toma valor none por eso hago un dropna(), funciona joya
            print(valor_unico)

            # Defino variables
            fila_df_val_att_sent = []  # Reinicio fila del dataframe para valores del atributo
            relaciones = []  # los saco...
            l_prom_sent = []  #
            cant_opi_con_sent, prom_sent = 0, 0  # inicializo variables pues el atrib puede tener relacion con mas de una customer need

            # SELECCIONO LAS OPINIONES SEGUN IDS DE ALTERNATIVAS CUYO ATRIBUTO TOMA EL VALOR
            # Obtengo ids de alternativas cuyo atributo toma el valor
            ids = df_alternativas[df_alternativas[atributo] == valor_unico]['id_alternativa']
            print(ids)
            # Filtro dataframe "df_opinion_cust_need" quedandome con opiniones cuyo id este en ids
            df_opinion_cust_need_filt = df_opinion_cust_need[df_opinion_cust_need.id_alternativa.isin(ids)]  # ver si falla o no con alternativas sin opiniones
            print(df_opinion_cust_need_filt['id_alternativa'].unique())
            # print(df_opinion_cust_need_filt)

            # POR CUSTOMER NEED
            for customer_need in df_opinion_cust_need_filt.columns[1:]:  # no incluyo id_alt --> por que no use index de matriz de relaciones? que no tiene el id...

                # Obtengo relacion entre atributo y customer need
                relacion = relation_matrix.loc[customer_need, atributo]

                # Si hay relacion
                if relacion > 0:

                    # Obtengo cantidad de opiniones y prom sent (ponderado segun relaciones)
                    cant_opi_con_sent += len(df_opinion_cust_need_filt[customer_need].dropna())
                    prom_sent += df_opinion_cust_need_filt[customer_need].dropna().mean() / sum_relaciones # lo quiero probar en vez de las lineas que estan abajo en comentario...
                    print("Atributo = {}, Customer need = {}, Relacion = {}, Promedio sentiment: {}".format(atributo, customer_need, relacion, prom_sent))

            # GUARDO VALOR, ATRIBUTO AL QUE PERTENECE, CANT DE OPINIONES Y SENTIMENT
            # comentar...
            fila_df_val_att_sent.append(valor_unico), fila_df_val_att_sent.append(atributo)
            if cant_opi_con_sent > 0 and prom_sent != 0:
                fila_df_val_att_sent.append(cant_opi_con_sent), fila_df_val_att_sent.append(prom_sent)
            else:
                fila_df_val_att_sent.append(None), fila_df_val_att_sent.append(None)

            df_values_attr_sent.loc[len(df_values_attr_sent)] = fila_df_val_att_sent  # rabino el index pero funciona joya
            print("Fila:", fila_df_val_att_sent)

        df_attr_value_sent_2 = pd.concat([df_attr_value_sent_2, df_values_attr_sent], ignore_index=True)  # para ver cantidad de opiniones en que se basa el sent de cada valor
        # GUARDO EL ATRIBUTO, SUS VALORES Y SUS SENTIMENT SOLO SI EL ATRIBUTO TIENE AL MENOS UNA RELACION
        # Si el atributo tiene relacion con al menos una customer need
        if sum_relaciones > 0:

            # Pondero sentiment de cada valor del atributo segun cantidad de opiniones
            df_values_attr_sent_pond = quantity_opinions_weighing(df_values_attr_sent)

            # Guardo datos del atributo
            df_values_attrs_sent_pond = pd.concat([df_values_attrs_sent_pond, df_values_attr_sent_pond], ignore_index=True)

        # Si el atributo no tiene relacion con las customer needs
        else:
            # No guardo el atributo
            print("El atributo {} no tiene relacion con ninguna customer need".format(atributo))

    df_attr_value_sent_2.to_excel('/Users/nachomondino/Desktop/df_attr_value_sent_cant_opi.xlsx', 'Hoja de datos')
    df_values_attrs_sent_pond.to_excel('/Users/nachomondino/Desktop/df_attr_value_sent.xlsx', 'Hoja de datos')

    return df_values_attrs_sent_pond

def quantity_opinions_weighing(df_attr):  #no la revise...
    """
    Pondera sentiment de cada valor de un atributo del producto segun cantidad de opiniones en que se basa
    :param df_attr: Dataframe cuya unidad de analisis son los valores de un mismo atributo del producto. Sus columnas
    son valor, atributo al que perenece, cantidad de opiniones en que se basa en sentiment y el sentiment
    :return: Dataframe cuya unidad de analisis son los valores de un mismo atributo del producto. Sus columnas
    son valor, atributo al que perenece y el sentiment ponderado segun cantidad de opiniones
    """
    # Defino variables
    df = pd.DataFrame(columns=['valor', 'atributo', 'sent'])
    FACTOR = 0.5
    attr = df_attr.loc[0, 'atributo']

    # Obtengo el menor sentiment de sus valores
    max_cant_opi_attr = df_attr["cant_opi_con_sent"].max()  # max y no sum porque no quiero modificar los sentiment de los que tienen muchas opis
    print(max_cant_opi_attr)

    # POR VALOR DEL ATRIBUTO
    for valor in df_attr['valor']:
        print(valor)

        # SI EL VALOR TIENE SENTIMENT
        try:
            # Obtengo cant de opis del valor y prom_sent
            cant_opi_valor = int(df_attr[df_attr['valor'] == valor]['cant_opi_con_sent'])
            sent_valor = float(df_attr[df_attr['valor'] == valor]['sent'])
            print(cant_opi_valor, sent_valor)

            # Calculo factor
            porc_cant_opi = cant_opi_valor / max_cant_opi_attr
            # print("porcentaje:", porc_cant_opi)
            sent_a_atenuar = sent_valor * (1 - porc_cant_opi) # ate = prom_sent_valor - prom_sent_valor * porc_cant_opi
            # print("ate:", ate)

            # Afecto sentiment
            new_sent_valor = sent_valor - FACTOR * sent_a_atenuar
            print("nuevo sentiment:", new_sent_valor)

            # Guardo fila del valor
            df.loc[len(df)] = [valor, attr, new_sent_valor]

        # SI EL VALOR TIENE SENTIMENT NAN
        except TypeError:
            # No pondero el sentiment y lo guardo como NaN
            df.loc[len(df)] = [valor, attr, None]
            print("El valor {} tiene sentiment NaN".format(valor))

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

def palabras_relacionadas(palabra):  # diccionario que mantener actualizado
    """
    Obtiene palabras relacionadas a la palabra pasada como parametro
    :param palabra: String
    :return: Lista de palabras relacionadas (incluido el string)
    """
    # Defino diccionario de palabras relacionadas para mejorar identificacion de customer needs
    d_pal_rel = {'aplicaciones': ['app'], 'bateria': ['duracion'], 'camara': [' foto', 'definicion', 'selfie'],
                 'memoria': [' fluid', 'almacenamiento', ' ram', 'velocidad', 'rapido', ' lento', ' tilda'],
                 'pantalla': ['pantall', 'resolucion', 'definicion', 'imagen'],
                 "precio": ['costo', ' caro', 'barato', 'economico'],
                 "procesador": ["velocidad", "funcionamiento", "software", 'rapido', ' lento', ' tilda']
                }

    # Si la palabra tiene palabras relacionadas
    if palabra in d_pal_rel.keys():
        # Agrego palabras relacionadas a lista a retornar
        palabras_a_buscar = [palabra] + d_pal_rel[palabra]

    # Si la palabra no tiene palabras relacionadas
    else:
        # Solo la palabra en lista a retornar
        palabras_a_buscar = [palabra]

    return palabras_a_buscar

''' # Probando to_customer_needs
df_opiniones = pd.read_excel('/Users/nachomondino/Desktop/df_opiniones_menos_menos_cleaned.xlsx')
customer_needs = ['pantalla', 'memoria','precio', 'tamaño','bateria','camara', 'resolucion']
# palabras_adicionales = {'precio': ['caro', 'barato'],'camara': ['camaras', 'foto', 'fotos'],'memoria': ['rapido', 'lento', 'fluido', 'funcionamiento', 'almacenamiento', 'ram']}

to_customer_needs(df_opiniones, customer_needs)
'''

'''
# Probando create_relation_matrix()
df_modelos = pd.read_excel('/Users/nachomondino/Desktop/df_modelos_cleaned.xlsx')
atributos = list(df_modelos.columns[1:])
customer_needs = ['pantalla', 'memoria','precio', 'tamaño','bateria','camara', 'resolucion']
relation_matrix = create_relation_matrix(atributos, customer_needs)
print(relation_matrix)
'''

'''
# Probando to_attr_values()
df_alt = pd.read_excel('/Users/nachomondino/Desktop/df_alt_celulares_cleaned.xlsx', index_col=0)
df_opinion_cust_need = pd.read_excel('/Users/nachomondino/Desktop/df_opinion_cust_needs.xlsx')
# relation_matrix = pd.read_excel('/Users/nachomondino/Desktop/relation_matrix.xlsx')
atributos = list(df_alt.columns[1:])
# customer_needs = ['pantalla', 'memoria','precio', 'tamaño','bateria','camara', 'resolucion']
customer_needs = ['precio', 'bateria', 'camara', 'pantalla', 'memoria', 'carga', 'cargador']

# df_opiniones = pd.read_excel('/Users/nachomondino/Desktop/df_opiniones_cleaned.xlsx')
# customer_needs_one_word = ['pantalla', 'camara']

df = to_attribute_value(df_alt, df_opinion_cust_need, create_relation_matrix(atributos, customer_needs))
# df = to_attribute_value(df_modelos, df_costumer_needs_sent, relation_matrix)
# df.to_excel('/Users/nachomondino/Desktop/df_attr_value_sent_14.xlsx', 'Hoja de datos')
# df.to_excel('/Users/nachomondino/Desktop/df_attr_value_sent_cant_opi.xlsx', 'Hoja de datos')
'''

'''
# Probando cant_opinines_ponderacion(df_attr_value_sent)
df = pd.read_excel('/Users/nachomondino/Desktop/df_attr_value_sent3.xlsx', 'Hoja de datos')
df = df.drop(['Unnamed: 0'],axis=1)
print(df)
cant_opinines_ponderacion(df)
'''


'''
# Levanto el dataset --> en la vida real le paso df_cleanded
df_modelos = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/df_modelos_formateado.xlsx')
df_opiniones = pd.read_excel('/Users/nachomondino/Desktop/df_opiniones_cleaned.xlsx')
relevant_words = ['precio', 'bateria', 'camara', 'memoria', 'tamaño', 'pantalla', 'resolucion']
df_sent = to_customer_needs(df_opiniones, relevant_words)
atrib = ['precio', 'Marca']
customer_needs = ['precio', 'bateria', 'camara']
df_sent_x_modelo = to_attribute_value(df_modelos, df_sent, create_relation_matrix(atrib, customer_needs))
'''