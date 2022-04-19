# Atribucion de sentiment de opinion a cada valor de cada campo especifico
import pandas as pd
from modelling import google_sentiment_api

def to_customer_needs(df_opiniones, customer_needs_one_word):  #pasar df entero
    """
    :param df_opiniones: Dataframe cuya unidad de analisis son opiniones
    :param customer_needs_one_word: Lista de customer needs como frases de 1 sola palabra
    :return: Dataframe cuya unidad de analisis es una opinion y cuyas columnas son cada customer need. La celda indicara
    el sentiment que toma la customer need, el cual sera el rate de la opinion si la customer need es nombrada en ella,
    en caso contrario, None.
    """
    # DEFINO VARIABLES
    # Defino diccionarios de palabras relacionadas (lo hago aca?)
    d_palabras_adic = {'camara': ['camaras', 'foto', 'fotos'], 'memoria': ['fluidez', 'almacenamiento', 'ram'],
                       "procesador": ["velocidad", "funcionamiento", "software"]}
    # Creo Dataframe a retornar. Aun vacio pero con los nombres de las columnas correspondientes
    df_costumer_needs_sent = pd.DataFrame(columns=["id_publicacion"] + customer_needs_one_word)
    # Obtengo indices de columnas que contiene opiniones y la que contiene el sentiment de estas
    idx_id = df_opiniones.columns.get_loc("id_publicacion")  # agrega flexibilidad pues puedo pasarle el df_opiniones enterro e igual usa solo "opiniones"
    idx_opi = df_opiniones.columns.get_loc("content")  # agrega flexibilidad pues puedo pasarle el df_opiniones enterro e igual usa solo "opiniones"

    # Por opinion
    for i in range(len(df_opiniones)):
        id, opinion = df_opiniones.iloc[i, idx_id], df_opiniones.iloc[i, idx_opi]
        fila = [id]  # inicializo variable que guardara la fila del nuevo dataframe
        print("NºFila:", i)
        print("Opinion:", opinion)

        # Obtengo sentiment de cada entity de la opinion
        d_entities_sent = google_sentiment_api.sample_analyze_entity_sentiment(opinion)

        # Por customer need
        for customer_need in customer_needs_one_word:

            # Agrego palabras adicionales para identificar mejor customer need
            # Obtengo, si hay, palabras adicionales para identificar dicha customer need
            try:  # MEJORAR IMPLEMENTACION...
                palabras_adic = d_palabras_adic[customer_need]
                palabras_a_buscar = [customer_need] + palabras_adic

            except KeyError:
                palabras_a_buscar = [customer_need]

            bool = True

            # Por palabra relevante para identificar customer need
            for palabra_a_buscar in palabras_a_buscar:

                # Si la opinion menciona a la palabra
                if palabra_a_buscar in d_entities_sent.keys():

                    # Guardo su score
                    fila.append(d_entities_sent[palabra_a_buscar])

                    # contemplar caso que mas de una palabra a buscar este en diccionario... por ahora break...
                    bool = False
                    break

            # Si la opinion no menciona el atributo
            if bool:
                # el atributo toma sentiment None
                fila.append(None)

        # Agrego fila al dataframe
        print("Fila:", fila)
        df_costumer_needs_sent.loc[i] = fila

    print(df_costumer_needs_sent)
    df_costumer_needs_sent.to_excel('/Users/nachomondino/Desktop/df_costumer_needs_sent_sin_limp_abs_5.xlsx', 'Hoja de datos',index=False)
    return df_costumer_needs_sent

def create_relation_matrix(atributos, customer_needs):
    """
    Crea matriz de relaciones entre customer needs y atributos del producto. Para ello, pide al usuario por terminal
    la relacion entre cada uno.
    :param atributos: Lista de atributos o campos especificos de un producto
    :param customer_needs: Lista de customer needs (de 1 sola palabra) de un producto
    :return: Dataframe con atributos como columnas y customer needs como filas. Celda indica relacion entre fila i y
    atributo j
    """
    # Remuevo atributos que no deberian tener sentiment
    try:
        atributos.remove("Modelo")
        atributos.remove("Línea")

    except ValueError: # ValueError: list.remove(x): x not in list
        pass

    # Creo dataframe con atributos como columnas y customer needs como filas
    relation_matrix = pd.DataFrame(columns=atributos, index=customer_needs)

    # Por atributo o campo especifico
    for atributo in atributos:

        # Por customer need
        for customer_need in customer_needs:

            # Validacion de ingreso de relaciones
            # Mientras que la carga no sea un numero entero
            while True:
                # Pido al administrador relacion entre customer_need y atributo
                try:
                    relation_matrix.loc[customer_need, atributo] = int(input("Ingrese relacion entre atributo '{}' y customer need '{}'(0, 1, 3 o 9 ptos): ".format(atributo.upper(),customer_need.upper())))
                    # Administrador cargo relacion correctamente
                    break

                # Si la relacion no es un numero
                except ValueError:
                    # sigo en el ciclo while hasta que cargue la relacion correctamente
                    pass

            # relation_matrix.loc[customer_need, atributo] = int(input("Ingrese relacion entre atributo '{}' y customer need '{}'(0, 1, 3 o 9 ptos): ".format(atributo, customer_need)))

    relation_matrix.to_excel('/Users/nachomondino/Desktop/relation_matrix.xlsx', 'Hoja de datos',index_label="customer_need")
    return relation_matrix

def to_attribute_value(df_mod, df_costumer_needs_sent, matriz_relaciones):
    """
    Dados los sentiment de cada customer need en las opiniones y la matriz de relaciones entre customer needs y
    atributos, atribuye dichos sentiment a los valores que tome cada atributo.
    :param df_mod:
    :param df_costumer_needs_sent:
    :param matriz_relaciones:
    :return: Dataframe cuya unidad de analisis son los valores de los atributos del producto. Incluye a que atributo
     pertenece, su sentiment y la cantidad de opiniones en que se basa dicho sentiment
    """
    # Defino sentiment que retornare
    df_attr_value_sent = pd.DataFrame(columns=['valor', 'campo_especifico', 'cant_opi_con_sent', 'prom_sent'])

    # Por campo especifico o atributo del producto
    for atributo in matriz_relaciones.columns:  # evito columna con customer needs...
        print(atributo)

        # Por valor unico del campo
        for valor_unico in df_mod[atributo].dropna().unique():  # hay modelos cuyo atrib toma valor none por eso hago un dropna(), funciona joya
            print(valor_unico)
            fila, relaciones, l_prom_sent = [], [], []
            cant_opi_con_sent, prom_sent = 0, 0  # inicializo variables pues el atrib puede tenre relacion con mas de una customer need

            # Obtengo ids de modelos cuyo atributo tome el valor_unico
            ids = df_mod[df_mod[atributo] == valor_unico]['id_publicacion']
            # print(ids)

            # Selecciono opiniones de dichos ids
            df_aux = pd.DataFrame()
            for id in ids:
                df_aux = pd.concat([df_aux, df_costumer_needs_sent[df_costumer_needs_sent['id_publicacion'] == id]])
            df_costumer_needs_sent_filtrado = df_aux
            # print(df_costumer_needs_sent_filtrado)

            # Por customer need
            for customer_need in df_costumer_needs_sent_filtrado.columns[1:]:  # no incluyo id_pub

                # Si tiene relacion con atributo
                # try:  # momentaneamente en pruebas
                if matriz_relaciones.loc[customer_need, atributo] > 0:

                    # Guardo relacion y prom_sent por si el atributo tiene mas de una relacion
                    relaciones.append(matriz_relaciones.loc[customer_need, atributo])
                    l_prom_sent.append(df_costumer_needs_sent_filtrado[customer_need].mean())
                    print("Relacion entre {} y {}: {}".format(customer_need, atributo, relaciones))

                    # Obtengo <cant_opi_con_sent>
                    cant_opi_con_sent += len(df_costumer_needs_sent_filtrado[customer_need].dropna())

                    # Obtengo <prom_sent>
                    # Si el atributo ya tiene relacion con otra/s customer needs
                    if len(relaciones) >= 2:
                        prom_sent = 0

                        # Hago promedio ponderado segun relaciones
                        for i in range(len(relaciones)):
                            print(relaciones[i], sum(relaciones), l_prom_sent[i])
                            prom_sent += relaciones[i] / sum(relaciones) * l_prom_sent[i]

                    # Si el atributo aun no tiene relacion con otra customer needs
                    else:
                        # Obtengo prom_sent
                        prom_sent = df_costumer_needs_sent_filtrado[customer_need].mean()

                    # print(cant_opi_con_sent, prom_sent)

                # Atributo y customer need sin relacion
                # except:
                #    pass

            '''
            # Guardo <cant_opi_con_sent> y <prom_sent> en fila --> es el try except de abajao pero nunca entra al except... pues defino arriba cant opi y prom sent
            # Si el valor tiene opiniones pero no un prom_sent
            if cant_opi_con_sent > 0 and (str(prom_sent) == 'nan' or prom_sent == 0):
                cant_opi_con_sent, prom_sent = correct_nan(ids)
                print("Asigno promedio de rate de opiniones con dicho valor, basado en {} opiniones, seria {}".format(cant_opi_con_sent, prom_sent))
                fila.append(valor_unico), fila.append(atributo), fila.append(cant_opi_con_sent), fila.append(prom_sent)

            # Si el valor tiene opiniones y prom_sent
            else:
                fila.append(valor_unico), fila.append(atributo), fila.append(cant_opi_con_sent), fila.append(prom_sent)
            '''
            fila.append(valor_unico), fila.append(atributo), fila.append(cant_opi_con_sent), fila.append(prom_sent)
            print("Fila:", fila)
            # Guardo fila en dataframe
            df_attr_value_sent.loc[len(df_attr_value_sent)] = fila  # rabino el index pero funciona joya


            '''
            # Si el atributo tiene al menos una relacion
            try:
                # Guardo <cant_opi_con_sent> y <prom_sent> en fila
                fila.append(cant_opi_con_sent), fila.append(prom_sent)
                print("Fila:", fila)
                # Guardo fila en dataframe
                df_attr_value_sent.loc[len(df_attr_value_sent)] = fila  # rabino el index pero funciona joya

            # si el atributo no tiene relacion con ninguna customer need
            except ValueError:  # no entro nadie...
                # Seteo <cant_opi_con_sent> y <prom_sent> a None en fila
                print("El valor cargado es NONE. CHEQUIAR")
                fila.append(None), fila.append(None)
                # cant_opi, prom_sent = correct_nan(ids)
                # print("El valor {} seria NAN pero ahora asignaria promedio de rate de opiniones con dicho valor {}, basado en {} opiniones".format(valor_unico, prom_sent, cant_opi))
                # Guardo fila en dataframe
                df_attr_value_sent.loc[len(df_attr_value_sent)] = fila  # rabino el index
            '''

    return df_attr_value_sent

def correct_nan(ids):
    df_opiniones = pd.read_excel('/Users/nachomondino/Desktop/df_opiniones_menos_menos_cleaned.xlsx')

    # Filtro df opiniones por ids
    df_aux = pd.DataFrame(columns=df_opiniones.columns)
    for id in ids:
        df_aux = pd.concat([df_aux, df_opiniones[df_opiniones['id_publicacion'] == id]])
    df_opiniones_filtrado = df_aux
    # print(df_costumer_needs_sent_filtrado)

    # Obtengo cant_opis
    cant_opi = len(df_opiniones_filtrado)

    # Obtengo prom_sent
    # Llevo escala de rate_min,rate_max a -1,1
    # Construyo recta a partir de dos puntos
    # y1, y2 = -1, 1
    y1, y2 = 0, 1
    # rate_min = df_opiniones['rate'].min()  # x1
    rate_prom = df_opiniones['rate'].mean()  # x1, pruebo a poner el cero en la media de los rates en lugar de poner el -1 en el minimo pues sino el score tiende a ser siempre posistivo dado que hay muchos valores cercanos al maximo...
    rate_max = df_opiniones['rate'].max()  # x2
    rate = df_opiniones_filtrado['rate'].mean()  # x

    m = (y2 - y1) / (rate_max - rate_prom)  # pendiente de recta
    score = m * (rate - rate_prom) + y1

    return cant_opi, score

def cant_opinines_ponderacion(df_attr_value_sent):

    df = pd.DataFrame(columns=['valor', 'campo_especifico', 'prom_sent'])

    # Por atributo
    for attr in df_attr_value_sent['campo_especifico'].unique():
        df_attr = df_attr_value_sent[df_attr_value_sent['campo_especifico']==attr]
        print(df_attr)

        # Obtengo el menor sentiment de sus valores
        max_cant_opi_attr = df_attr["cant_opi_con_sent"].max()  # max y no sum porque no quiero modificar los sentiment de los que tienen muchas opis
        print(max_cant_opi_attr)

        # Por valor de atributo
        for valor in df_attr['valor'].unique():
            print(valor)

            # Obtengo cant de opis del valor
            df_valor = df_attr[df_attr['valor'] == valor]
            # idx = df_valor.index
            # idx_opi = df_valor.columns.get_loc("cant_opi_con_sent")  # agrega flexibilidad pues puedo pasarle el df_opiniones enterro e igual usa solo "opiniones"
            # idx_sent = df_valor.columns.get_loc("prom_sent")  # agrega flexibilidad pues puedo pasarle el df_opiniones enterro e igual usa solo "opiniones"
            # print(idx, idx_opi, idx_sent)
            # print(df_valor)

            cant_opi_valor = int(df_attr_value_sent[(df_attr_value_sent['campo_especifico']==attr) & (df_attr_value_sent['valor']==valor)]['cant_opi_con_sent'])
            prom_sent_valor = float(df_attr_value_sent[(df_attr_value_sent['campo_especifico']==attr) & (df_attr_value_sent['valor']==valor)]['prom_sent'])

            print(cant_opi_valor, prom_sent_valor)
            # prom_sent_valor = df_valor["prom_sent"]

            # cant_opi_valor = df_valor.iloc[idx, idx_opi]
            # prom_sent_valor = df_valor.iloc[idx, idx_sent]
            # print(cant_opi_valor, prom_sent_valor)


            # Calculo factor
            porc_cant_opi = cant_opi_valor / max_cant_opi_attr
            # print("porcentaje:", porc_cant_opi)
            ate = prom_sent_valor - prom_sent_valor * porc_cant_opi
            # print("ate:", ate)
            FACTOR = 0.5

            # Afecto sentiment
            prom_sent_valor_nuevo = prom_sent_valor - FACTOR * ate
            print("nuevo sentiment:", prom_sent_valor_nuevo)

            # Guardo nuevo sentiment
            # df_attr_value_sent[df_attr_value_sent['valor']==valor]['prom_sent'] == prom_sent_valor_nuevo
            fila = [valor, attr, prom_sent_valor_nuevo]

            # Guardo fila del valor
            df.loc[len(df)] = fila

    df.to_excel('/Users/nachomondino/Desktop/df_ponderado_2.xlsx', 'Hoja de datos')
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
df_modelos = pd.read_excel('/Users/nachomondino/Desktop/df_modelos_cleaned.xlsx')
df_costumer_needs_sent = pd.read_excel('/Users/nachomondino/Desktop/df_costumer_needs_sent_sin_limp_abs_5.xlsx')
relation_matrix = pd.read_excel('/Users/nachomondino/Desktop/relation_matrix.xlsx')
atributos = list(df_modelos.columns[1:])
customer_needs = ['pantalla', 'memoria','precio', 'tamaño','bateria','camara', 'resolucion']
# df_opiniones = pd.read_excel('/Users/nachomondino/Desktop/df_opiniones_cleaned.xlsx')
# customer_needs_one_word = ['pantalla', 'camara']

df = to_attribute_value(df_modelos, df_costumer_needs_sent, create_relation_matrix(atributos, customer_needs))
# df = to_attribute_value(df_modelos, df_costumer_needs_sent, relation_matrix)
df.to_excel('/Users/nachomondino/Desktop/df_attr_value_sent2.xlsx', 'Hoja de datos')
'''


# Probando cant_opinines_ponderacion(df_attr_value_sent)
df = pd.read_excel('/Users/nachomondino/Desktop/df_attr_value_sent2.xlsx', 'Hoja de datos')
df = df.drop(['Unnamed: 0'],axis=1)
print(df)
cant_opinines_ponderacion(df)


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

