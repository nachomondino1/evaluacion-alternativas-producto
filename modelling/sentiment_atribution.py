# Importo librerias
import pandas as pd
import nltk
from sentiment_analysis_spanish import sentiment_analysis

def to_customer_needs(df_opiniones, customer_needs_one_word):
    """
    Identifica, si hay, customer needs en opiniones y asigna el sentiment a cada una mediante la libreria pysentimiento
    :param df_opiniones: Dataframe cuya unidad de analisis son opiniones (sin limpiar pues necesito los puntos...aunque para verr si la palabra esta en la frase esta debe ser lower y sin acentos...)
    :param customer_needs_one_word: Lista de customer needs como frases de 1 sola palabra
    :return: Dataframe cuya unidad de analisis es una opinion y cuyas columnas son cada customer need. La celda es el
    sentiment de la customer need en la opinion, o bien si la opinion no habla de la customer need, None.
    """
    # DEFINO VARIABLES
    # Defino indices utiles para tener flexibilidad en codigo (posibilidad de columnas en otra posicion)
    idx_id = df_opiniones.columns.get_loc("id_alternativa")  # indice de columna que contiene ids de publicaciones
    idx_opi = df_opiniones.columns.get_loc("opinion")  #  indice de columna que contiene opiniones
    # Defino dataframe a retornar
    df_costumer_needs_sent = pd.DataFrame(columns=["id_alternativa"] + customer_needs_one_word)
    # Defino diccionario de palabras relacionadas para mejorar identificacion de customer needs (lo hago aca?)
    d_palabras_adic = {'camara': ['camaras', 'foto', 'fotos'], 'memoria': ['fluidez', 'almacenamiento', 'ram'],
                       "procesador": ["velocidad", "funcionamiento","software"], 'bateria':'duracion'}

    sent = sentiment_analysis.SentimentAnalysisSpanish()

    """FALTA IMPLEMENTAR CASO EN QUE LA CUSTOMER NEED SEA NOMBRADA EN MAS DE UNA FRASE.... """
    """FALTA LOWER Y ELIMINAR ACENTOS DE FRASE AL VER SI LA CUSTOMER NEED ESTA O NO EN ELLA"""

    # POR OPINION
    for i in range(len(df_opiniones)):
        id, opinion = df_opiniones.iloc[i, idx_id], df_opiniones.iloc[i, idx_opi]  # Defino id y opinion
        fila = [id]  # inicializo variable que guardara la fila del nuevo dataframe
        print("NºFila:", i)
        print("Opinion:", opinion)

        # POR FRASE DE OPINION
        for frase in nltk.tokenize.sent_tokenize(opinion):
            print(frase)

            # OBTENGO SENTIMENT DE FRASE CON PYSENTIMIENTO
            sent_frase = sent.sentiment(frase)

            # POR CUSTOMER NEED
            for customer_need in customer_needs:

                # ANTES DE VER SI LA CUSTOMER NEED ESTA EN LA FRASE, AGREGO, SI HAY, PALABRAS ADICIONALES A LA CUSTOMER
                # NEED QUE LA PUEDAN AYUDAR A IDENTIFICAR MEJOR
                # Si la customer need tiene palabras adicionales
                if customer_need in d_palabras_adic.keys():
                    # Agrego palabras adicionales a palabras a buscar
                    palabras_a_buscar = [customer_need] + d_palabras_adic[customer_need]

                # Si la customer need no tiene palabras adicionales
                else:
                    # Solo la customer need como palabra a buscar
                    palabras_a_buscar = [customer_need]

                # Variable para cortar busqueda de sentiment de customer need con palabras adicionales
                bool = True

                # POR PALABRA A BUSCAR
                for palabra_a_buscar in palabras_a_buscar:

                    # SI LA PALABRA ESTA EN LA OPINION
                    if palabra_a_buscar in frase:

                        # ASIGNO SENTIMENT DE FRASE
                        fila.append(sent_frase)

                        # EN CASO DE HABER PALABRAS ADICIONALES, DEJO DE BUSCAR PALABRAS PARA ESTA CUSTOMER NEED
                        bool = False
                        break

                # SI LA OPINION NO MENCIONA A LA CUSTOMER NEED
                if bool:
                    # ASIGNO SCORE O SENTIMENT NONE
                    fila.append(None)

            # TRAS OBTENER SENTIMENT DE TODAS LAS CUSTOMER NEEDS EN UNA OPINION, AGREGO FILA AL DATAFRAME
            df_costumer_needs_sent.loc[i] = fila
            print("Fila:", fila)

    # EXPORTO DATAFRAME
    # df_costumer_needs_sent.to_excel('/Users/nachomondino/Desktop/df_costumer_needs_sent_sin_limp_abs_5.xlsx', 'Hoja de datos',index=False)
    print(df_costumer_needs_sent)

    return df_costumer_needs_sent

def create_relation_matrix(atributos, customer_needs):
    """
    Crea matriz de relaciones entre customer needs y atributos del producto. Para ello, pide al usuario por terminal
    la relacion entre cada uno.
    :param atributos: Lista de atributos o campos especificos de un producto
    :param customer_needs: Lista de customer needs (de 1 sola palabra) de un producto
    :return: Dataframe con atributos como columnas y customer needs como filas. Celda indica relacion entre customer
    need  i y atributo j
    """
    # REMUEVO ATRIBUTOS QUE NO DEBERIAN TENER SENTIMENT
    try:
        atributos.remove("Modelo")
        atributos.remove("Línea")

    except ValueError: # ValueError: list.remove(x): x not in list
        pass

    # CREO DATAFRAME A RETORNAR. CON ATRIBUTOS COMO COLUMNAS Y CUSTOMER NEEDS COMO FILAS
    relation_matrix = pd.DataFrame(columns=atributos, index=customer_needs)

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

def to_attribute_value(df_modelos, df_costumer_needs_sent, matriz_relaciones):
    """
    Mediante la matriz de relaciones, atribuyo los sentiment de las customer needs a los valores de los atributos del
    producto. Tendre que considerar la complicacion de la cantidad de opiniones en que se basa el sentiment de cada
    valor.
    :param df_modelos: Dataframe cuya unidad de analisis es cada una de las alternativas del producto, sus columnas son
    los atributos del producto y las celdas el valor que toma el atributo en una alternativa
    :param df_costumer_needs_sent: Dataframe cuya unidad de analisis es una opinion, sus columnas son cada customer
    need y las celdas el sentiment o score de la customer need en la opinion
    :param matriz_relaciones: Dataframe con atributos como columnas y customer needs como filas. Celda indica relacion
    entre customer need i y atributo j
    :return: Dataframe cuya unidad de analisis son los valores de los atributos del producto. Sus columnas son valor,
     atributo al que perenece y su sentiment
    """
    # Defino sentiment que retornare
    df_attr_value_sent = pd.DataFrame(columns=['valor', 'campo_especifico', 'prom_sent'])

    # POR CAMPO ESPECIFICO O ATRIBUTO DEL PRODUCTO
    for atributo in matriz_relaciones.columns:  # evito columna con customer needs...
        print(atributo)

        # Defino dataframe para el atributo
        df_attr = pd.DataFrame(columns=['valor', 'campo_especifico', 'cant_opi_con_sent', 'prom_sent'])
        sum_relaciones = sum(matriz_relaciones[atributo])

        # POR VALOR DEL ATRIBUTO
        for valor_unico in df_modelos[atributo].dropna().unique():  # hay modelos cuyo atrib toma valor none por eso hago un dropna(), funciona joya
            print(valor_unico)

            # Defino variables
            fila, relaciones, l_prom_sent = [], [], []
            cant_opi_con_sent, prom_sent = 0, 0  # inicializo variables pues el atrib puede tenre relacion con mas de una customer need

            # OBTENGO IDS DE ALTERNATIVAS CUYO ATRIBUTO TOMA EL VALOR
            ids = df_modelos[df_modelos[atributo] == valor_unico]['id_publicacion']
            # print(ids)

            # SELECCIONO LAS OPINIONES SEGUN IDS DE ALTERNATIVAS CUYO ATRIBUTO TOMA EL VALOR
            df_aux = pd.DataFrame()
            for id in ids:
                df_aux = pd.concat([df_aux, df_costumer_needs_sent[df_costumer_needs_sent['id_publicacion'] == id]])
            df_costumer_needs_sent_filtrado = df_aux
            # print(df_costumer_needs_sent_filtrado)

            # POR CUSTOMER NEED
            for customer_need in df_costumer_needs_sent_filtrado.columns[1:]:  # no incluyo id_pub

                # Obtengo relacion entre atributo y customer need
                relacion = matriz_relaciones.loc[customer_need, atributo]

                # Si hay relacion
                if relacion > 0:

                    # Obtengo cantidad de opiniones y prom sent (ponderado segun relaciones)
                    cant_opi_con_sent += len(df_costumer_needs_sent_filtrado[customer_need].dropna())
                    if str(df_costumer_needs_sent_filtrado[customer_need].mean()) != 'nan':
                        prom_sent += relacion * df_costumer_needs_sent_filtrado[customer_need].mean() / sum_relaciones
                    # print("Atributo = {}, Customer need = {}, Relacion = {}, Promedio sentiment: {}".format(atributo, customer_need, relacion, prom_sent))

            # GUARDO VALOR, ATRIBUTO AL QUE PERTENECE, CANT DE OPINIONES Y SENTIMENT
            # comentar...
            fila.append(valor_unico), fila.append(atributo)
            if cant_opi_con_sent > 0 and prom_sent != 0:
                fila.append(cant_opi_con_sent), fila.append(prom_sent)
            else:
                fila.append(None), fila.append(None)

            df_attr.loc[len(df_attr)] = fila  # rabino el index pero funciona joya
            print("Fila:", fila)

        # df_attr_value_sent = pd.concat([df_attr_value_sent, df_attr], ignore_index=True)
        # GUARDO EL ATRIBUTO, SUS VALORES Y SUS SENTIMENT SOLO SI EL ATRIBUTO TIENE AL MENOS UNA RELACION
        # Si el atributo tiene relacion con al menos una customer need
        if sum_relaciones > 0:

            # Pondero sentiment de cada valor del atributo segun cantidad de opiniones
            df_attr_ponderado = quantity_opinions_weighing(df_attr)

            # Guardo datos del atributo
            df_attr_value_sent = pd.concat([df_attr_value_sent, df_attr_ponderado], ignore_index=True)

        # Si el atributo no tiene relacion con las customer needs
        else:
            # No guardo el atributo
            print("El atributo {} no tiene relacion con ninguna customer need".format(atributo))

    return df_attr_value_sent

def quantity_opinions_weighing(df_attr):
    """
    Pondera sentiment de cada valor de un atributo del producto segun cantidad de opiniones en que se basa
    :param df_attr: Dataframe cuya unidad de analisis son los valores de un mismo atributo del producto. Sus columnas
    son valor, atributo al que perenece, cantidad de opiniones en que se basa en sentiment y el sentiment
    :return: Dataframe cuya unidad de analisis son los valores de un mismo atributo del producto. Sus columnas
    son valor, atributo al que perenece y el sentiment ponderado segun cantidad de opiniones
    """
    # Defino variables
    df = pd.DataFrame(columns=['valor', 'campo_especifico', 'prom_sent'])
    FACTOR = 0.5
    attr = df_attr.loc[0, 'campo_especifico']

    # Obtengo el menor sentiment de sus valores
    max_cant_opi_attr = df_attr["cant_opi_con_sent"].max()  # max y no sum porque no quiero modificar los sentiment de los que tienen muchas opis
    print(max_cant_opi_attr)

    # Por valor de atributo
    for valor in df_attr['valor']:
        print(valor)

        # si el sentiment y la cantidad de opiniones no son NaN
        try:
            # Obtengo cant de opis del valor y prom_sent
            cant_opi_valor = int(df_attr[df_attr['valor'] == valor]['cant_opi_con_sent'])
            prom_sent_valor = float(df_attr[df_attr['valor'] == valor]['prom_sent'])
            print(cant_opi_valor, prom_sent_valor)

            # Calculo factor
            porc_cant_opi = cant_opi_valor / max_cant_opi_attr
            # print("porcentaje:", porc_cant_opi)
            sent_a_atenuar = prom_sent_valor * (1 - porc_cant_opi) # ate = prom_sent_valor - prom_sent_valor * porc_cant_opi
            # print("ate:", ate)

            # Afecto sentiment
            prom_sent_valor_nuevo = prom_sent_valor - FACTOR * sent_a_atenuar
            print("nuevo sentiment:", prom_sent_valor_nuevo)

            # Guardo fila del valor
            df.loc[len(df)] = [valor, attr, prom_sent_valor_nuevo]

        # si el valor tiene sentiment NaN
        except TypeError:
            # No pondero el sentiment y lo guardo como NaN
            df.loc[len(df)] = [valor, attr, None]
            print("El valor {} tiene sentiment NaN".format(valor))

    return df



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
df_modelos = pd.read_excel('/Users/nachomondino/Desktop/df_modelos_cleaned_2.xlsx', index_col=0)
df_costumer_needs_sent = pd.read_excel('/Users/nachomondino/Desktop/df_costumer_needs_sent_sin_limp_abs_5.xlsx')
relation_matrix = pd.read_excel('/Users/nachomondino/Desktop/relation_matrix.xlsx')
atributos = list(df_modelos.columns[1:])
customer_needs = ['pantalla', 'memoria','precio', 'tamaño','bateria','camara', 'resolucion']
# df_opiniones = pd.read_excel('/Users/nachomondino/Desktop/df_opiniones_cleaned.xlsx')
# customer_needs_one_word = ['pantalla', 'camara']

df = to_attribute_value(df_modelos, df_costumer_needs_sent, create_relation_matrix(atributos, customer_needs))
# df = to_attribute_value(df_modelos, df_costumer_needs_sent, relation_matrix)
# df.to_excel('/Users/nachomondino/Desktop/df_attr_value_sent_14.xlsx', 'Hoja de datos')
df.to_excel('/Users/nachomondino/Desktop/df_attr_value_sent_cant_opi.xlsx', 'Hoja de datos')
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
df_modelos = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_modelos_formateado.xlsx')
df_opiniones = pd.read_excel('/Users/nachomondino/Desktop/df_opiniones_cleaned.xlsx')
relevant_words = ['precio', 'bateria', 'camara', 'memoria', 'tamaño', 'pantalla', 'resolucion']
df_sent = to_customer_needs(df_opiniones, relevant_words)
atrib = ['precio', 'Marca']
customer_needs = ['precio', 'bateria', 'camara']
df_sent_x_modelo = to_attribute_value(df_modelos, df_sent, create_relation_matrix(atrib, customer_needs))
'''
