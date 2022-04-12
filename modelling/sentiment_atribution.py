# Atribucion de sentiment de opinion a cada valor de cada campo especifico
import pandas as pd

def to_customer_needs(df_opiniones, customer_needs_one_word):  #pasar df entero
    """
    :param df_opiniones: Dataframe cuya unidad de analisis son opiniones
    :param customer_needs_one_word: Lista de customer needs como frases de 1 sola palabra
    :return: Dataframe cuya unidad de analisis es una opinion y cuyas columnas son cada customer need. La celda indicara
    el sentiment que toma la customer need, el cual sera el rate de la opinion si la customer need es nombrada en ella,
    en caso contrario, None.
    """
    df_opiniones = df_opiniones.dropna()  #tiene none por usar stop worrd removal... despues lo saco pues ya lo implemente en main.py

    # Defino Dataframes vacios
    df_costumer_needs_sent = pd.DataFrame(columns=["id_publicacion"] + customer_needs_one_word)

    # Obtengo indices de columnas que contiene opiniones y la que contiene el sentiment de estas
    idx_id = df_opiniones.columns.get_loc("id_publicacion")  # agrega flexibilidad pues puedo pasarle el df_opiniones enterro e igual usa solo "opiniones"
    idx_opi = df_opiniones.columns.get_loc("content")  # agrega flexibilidad pues puedo pasarle el df_opiniones enterro e igual usa solo "opiniones"
    idx_rate = df_opiniones.columns.get_loc("rate")  # agrega flexibilidad pues puedo pasarle el df_opiniones enterro e igual usa solo "opiniones"

    # Por opinion  --> tendre que guardar un sentiment a cada atrib y eso esta basado en una deteerminada cant de opis
    for i in range(len(df_opiniones)):
        id, opinion, rate = df_opiniones.iloc[i, idx_id], df_opiniones.iloc[i, idx_opi], df_opiniones.iloc[i, idx_rate]
        fila = [id]  # inicializo variable que guardara la fila del nuevo dataframe

        print("NºFila:", i)
        print("Opinion:", opinion)

        # Por customer need
        for customer_need in customer_needs_one_word:
            # print(customer_need)

            # Si la customer need es mencionada en la opinion
            if customer_need in opinion:

                # asigno rate de opinion a customeer need
                fila.append(rate)

            # Si la opinion no menciona el atributo
            else:
                # el atributo toma sentiment None
                fila.append(None)

        # Agrego fila al dataframe
        print("Fila:", fila)
        df_costumer_needs_sent.loc[i] = fila

    print(df_costumer_needs_sent)
    df_costumer_needs_sent.to_excel('/Users/nachomondino/Desktop/df_costumer_needs_sent.xlsx', 'Hoja de datos', index=False)
    return df_costumer_needs_sent

def create_relation_matrix(atributos, customer_needs):
    """
    Crea matriz de relaciones entre customer needs y atributos pidiendole al usuario por terminal la relacion entre
    cada uno.
    :param atributos: Lista de atributos o campos especificos de un producto
    :param customer_needs: Lista de customer needs (de 1 sola palabra) de un producto
    :return: Dataframe con atributos como columnas y customer needs como fila. Celda indica relacion entre fila i y
    atributo j
    """
    # Remuevo atributos que no deberian tener sentiment
    atrib_limpios = []  # agrego campo precio
    for atributo in atributos:
        if atributo in ["Modelo", "Línea"]:
            pass
        else:
            atrib_limpios.append(atributo)

    # Creo dataframe con atributos como columnas y customer needs como filas
    relation_matrix = pd.DataFrame(columns=atributos, index=customer_needs)

    # Por atributo o campo especifico
    for atributo in atrib_limpios:

        # Por customer need
        for customer_need in customer_needs:

            # Pido al administrador relacion entre customer_need y atributo
            try:
                relation_matrix.loc[customer_need, atributo] = int(input("Ingrese relacion entre atributo '{}' y customer need '{}'(0, 1, 3 o 9 ptos): ".format(atributo, customer_need)))
            except ValueError:
                relation_matrix.loc[customer_need, atributo] = int(input("Ingrese relacion entre atributo '{}' y customer need '{}'(0, 1, 3 o 9 ptos): ".format(atributo, customer_need)))
            # falta implementar validacion de ingreso de uno de esos numeros...

    relation_matrix.to_excel('/Users/nachomondino/Desktop/relation_matrix.xlsx', 'Hoja de datos')
    return relation_matrix

def to_attribute_value(df_mod, df_costumer_needs_sent, matriz_relaciones):
    """
    Dados los sentiment de cada customer need en las opiniones y la matriz de relaciones entre customer needs y
    atributos, atribuye dichos sentiment a los valores que tome cada atributo.
    :param df_costumer_needs_sent:
    :return: Dataframe cuya unidad de analisis son los valores de los atributos del producto. Incluye a que atributo
     pertenece, su sentiment y la cantidad de opiniones en que se basa dicho sentiment.
    """
    # Defino sentiment que retornare
    df_attr_value_sent = pd.DataFrame(columns=['valor', 'campo_especifico', 'cant_opi_con_sent', 'prom_sent'])

    # Por campo especifico del producto o atributo
    for atributo in matriz_relaciones.columns:  # no considero id_pub
        print(atributo)

        # Por valor unico del campo
        for valor_unico in df_mod[atributo].unique():
            print(valor_unico)
            fila = [valor_unico, atributo]  #inicializo la lista con valor y atributo
            relaciones = []
            l_prom_sent = []
            cant_opi_con_sent, prom_sent = 0, 0  # inicializo variables pues el atrib pueede tenre relacion con mas de una customer need

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
                try:  # momentaneamente en pruebas
                    if matriz_relaciones.loc[customer_need, atributo] > 0:  # falta implementar que un atrib tenga dos rerlaciones en lugar de 1 y que cargue cuando nio tiene relacion con ningun campo
                        relaciones.append(matriz_relaciones.loc[customer_need, atributo])  # ojpo que entra aca 20.000 veces. Yo pense que no. Estoy quemado ya.
                        print("relacion entre", customer_need, atributo, relaciones)

                        # Obtener <cant_opi_con_sent> y <prom_sent>
                        cant_opi_con_sent += len(df_costumer_needs_sent_filtrado[customer_need].dropna())

                        l_prom_sent.append(df_costumer_needs_sent_filtrado[customer_need].mean())

                        if len(relaciones) >= 2:
                            prom_sent = 0

                            for i in range(len(relaciones)):
                                print(relaciones[i], sum(relaciones), l_prom_sent[i])
                                prom_sent += relaciones[i] / sum(relaciones) * l_prom_sent[i]
                        else:
                            prom_sent = df_costumer_needs_sent_filtrado[customer_need].mean()

                        print(cant_opi_con_sent, prom_sent)

                # Atributo y customer need sin relacion
                except:
                    pass

            # Guardo fila en Dataframe
            try:
                fila.append(cant_opi_con_sent)
                fila.append(prom_sent)
                print("Fila:", fila)
                df_attr_value_sent.loc[len(df_attr_value_sent)] = fila  # rabino el index pero funciona joya
            except ValueError:
                fila.append(None)
                fila.append(None)
                df_attr_value_sent.loc[len(df_attr_value_sent)] = fila  # rabino el index

            '''
            # Obtengo ids cuyo campo <campo> tome el valor <valor_unico>
            ids = df_mod[df_mod[atributo] == valor_unico]['id_publicacion']
            # print(ids)

            # Filtro df_sent por ids
            df_aux = pd.DataFrame()
            for id in ids:
                df_sent_1 = df_sent[df_sent['id_publicacion'] == id]
                df_aux = pd.concat([df_aux, df_sent_1])
            df_sent_filtrado = df_aux
            # print(df_sent_filtrado)

            # Por palabra clave
            for palabra_clave in df_sent_filtrado.columns[1:]:  # no incluyo id_pub
                # print(palabra_clave, campo)

                # Si tiene relacion con <campo>
                try:
                    # print("relacion entre {} y {} = {}".format(palabra_clave, campo, matriz_relaciones.loc[palabra_clave, campo]))
                    if matriz_relaciones.loc[palabra_clave, atributo] > 0:  # falta implementar que un atrib tenga dos rerlaciones en lugar de 1 y que cargue cuando nio tiene relacion con ningun campo

                        relaciones.append(matriz_relaciones.loc[palabra_clave, atributo]) # ojpo que entra aca 20.000 veces. Yo pense que no. Estoy quemado ya.

                        # Obtener <cant_opi_con_sent> y <prom_sent>
                        cant_opi_con_sent = len(df_sent_filtrado[palabra_clave].dropna())
                        prom_sent = df_sent_filtrado[palabra_clave].mean()
                        # print(cant_opi_con_sent, prom_sent)

                        # Guardo fila en dataframe
                        df = df.append({'campo_especifico': atributo, 'valor': valor_unico,
                                        'cant_opi_con_sent': cant_opi_con_sent, 'prom_sent': prom_sent}, ignore_index=True)
                        # print(df)

                except:
                    pass


            """ solo para relacion atrib y palabra clave 1 a 1
            # Por palabra clave
            for palabra_clave in df_sent_filtrado.columns:
                print(palabra_clave, campo)
                
                # Si tiene relacion con <campo>
                if matriz_relaciones.loc[palabra_clave, campo] > 0 : # falta implementar que un atrib tenga dos rerlaciones en lugar de 1 y que cargue cuando nio tiene relacion con ningun campo

                    # Obtener <cant_opi_con_sent> y <prom_sent>
                    cant_opi_con_sent = len(df_sent_filtrado[palabra_clave].dropna())
                    prom_sent = df_sent_filtrado[palabra_clave].mean()
                    print(cant_opi_con_sent, prom_sent)

                    # Guardo fila en dataframe
                    df = df.append({'campo_especifico': campo, 'valor': valor_unico,
                                    'cant_opi_con_sent': cant_opi_con_sent, 'prom_sent': prom_sent}, ignore_index=True)
                    print(df)
            """


        # Agrupo por campo (solo si un campo tiene relacion con mas de una customer need
        if len(relaciones) > 1:
            print('campo {} tiene mas de una relacion'.format(atributo))

            df_aux_2 = pd.DataFrame()

            for valor_unico in df_mod[atributo].unique():

                # Buscar todos los campos = valor del df
                filas = df[df['campo_especifico']==atributo]
                filas = filas[filas['valor'] == valor_unico]
                # filas = df[df['campo_especifico'] ==campo and df['valor'] == valor_unico]

                print(relaciones[:2])
                print(filas['prom_sent'])
                cant_opi_con_sent = sum(filas['cant_opi_con_sent'])
                # tengo que solucionar relaciones y calculo del prom sent
                # prom_sent = relaciones[:2] * filas['prom_sent']
                # prom_sent = numpy.dot(relaciones[:2], filas['prom_sent']) #no se si es exactamenet un producot escalar

                # df_aux_2 = df_aux_2.append({'campo_especifico': campo, 'valor': valor_unico,'cant_opi_con_sent': cant_opi_con_sent, 'prom_sent': prom_sent}, ignore_index=True)
                df_aux_2 = df_aux_2.append({'campo_especifico': atributo, 'valor': valor_unico,
                                            'cant_opi_con_sent': cant_opi_con_sent}, ignore_index=True)

    print(df)
    # tendre que unir df...
    df.to_excel('/Users/nachomondino/Desktop/atribution_to_attribute_values.xlsx', 'Hoja de datos', index=False)
    df_aux_2.to_excel('/Users/nachomondino/Desktop/resultados2.xlsx', 'Hoja de datos', index=False)
    '''
    return df_attr_value_sent



'''

atributos = ['precio', 'bateria']
customer_needs = ['pantalla', 'camara']
relation_matrix = create_relation_matrix(atributos, customer_needs)
print(relation_matrix)
# df.to_excel('/Users/nachomondino/Desktop/relation_matrix.xlsx', 'Hoja de datos', index_label='customer_need')

df_opiniones = pd.read_excel('/Users/nachomondino/Desktop/df_opiniones_cleaned.xlsx')
customer_needs_one_word = ['pantalla', 'camara']

df_sent = pd.read_excel('/Users/nachomondino/Desktop/df_costumer_needs_sent.xlsx')

df_modelos = pd.read_excel('/Users/nachomondino/Desktop/df_modelos_cleaned.xlsx')

to_attribute_value(df_modelos, df_sent, relation_matrix)
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

