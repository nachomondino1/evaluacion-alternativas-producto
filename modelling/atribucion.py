# 4.2 Atribucion de sentiment de opinion a cada valor de cada campo especifico
import pandas as pd
import numpy

def create_relation_matrix(atributos, customer_needs):
    df = pd.DataFrame(columns=atributos, index=customer_needs)

    # Por atributo o campo especifico
    for atributo in atributos:

        # Por customer need
        for customer_need in customer_needs:

            # Pido al administrador relacion entre customer_need y atributo
            df.loc[customer_need, atributo] = int(input("Ingrese relacion entre atributo '{}' y customer need '{}'(0, 1, 3 o 9 ptos): ".format(atributo, customer_need)))
            # falta implementar validacion de ingreso..

    print(df)
    return df


# le paso df_opiniones con opinion y rate
def opinion_sentiment_to_customer_needs(df_opiniones, relevant_words):  #pasar df entero
    '''
    Con las relevant words actuales: (esto era con dataframe sin limpiar)
                            pantalla - memoria - precio - ram - tamaño - bateria - camara
    cant opis c/rate        653	276	938	308	148	203	232
    % de opi totales        16%	7%	23%	8%	4%	5%	6%

    Tras opi cleaned
    cant opis c/rate        825	669	950	278	955	314	152
    % de opi totales        20%	16%	23%	7%	23%	8%	4%
    Revisar opiniones manualmente y ver de atrib habala y de cuales no. IDentificar como identificar cuando habla de uno.
    :param df_opiniones:
    :param relevant_words:
    :return:
    '''

    # df_sent = pd.DataFrame(columns=[relevant_words])  #tendre que agregarr id_pub
    df_sent = pd.DataFrame()  #tendre que agregar id_pub

    idx_opi = df_opiniones.columns.get_loc("content")  # agrega flexibilidad pues puedo pasarle el df_opiniones enterro e igual usa solo "opiniones"
    idx_rate = df_opiniones.columns.get_loc("rate")  # agrega flexibilidad pues puedo pasarle el df_opiniones enterro e igual usa solo "opiniones"

    # Por opinion  --> tendre que guardar un sentiment a cada atrib y eso esta basado en una deteerminada cant de opis
    for i in range(len(df_opiniones)):
        opinion = df_opiniones.iloc[i, idx_opi]
        rate = df_opiniones.iloc[i, idx_rate]

        # inicializo diccionarios donde guardare datos por opinion
        d_sent = {'id_publicacion': df_opiniones.iloc[i, 0]}  # no se si inicializarlo asi o vacio..

        for word in relevant_words:

            # Si la opinion menciona el atributo
            try:
                if word in opinion:

                    d_sent[word] = rate

                # Si la opinion no menciona el atributo
                else:
                    # el atributo no toma sentiment
                    pass

            except TypeError:  # TypeError: argument of type 'float' is not iterable
                print("Hay un none value")  # puede haber dado que elimino stop words y tal vez elimino todo el content

        # Termino de ver si una opinion menciona a los atributos, guardo fila en df
        df_sent = df_sent.append(d_sent, ignore_index=True)

    print(df_sent)
    # df_sent.to_excel('/Users/nachomondino/Desktop/BBBBB2.xlsx', 'Hoja de datos', index=False)

    return df_sent


def customer_needs_sentiment_to_attribute_value(df_mod, df_sent, matriz_relaciones):
    """
    Dados los sentiment de cada customer need en las opinion y la matriz de relaciones entre customer needs y atributos,
     atribuye dichos sentiment a los valores que tome cada atributo.
    :param df_sent:
    :return:
    """
    df = pd.DataFrame(columns=['campo_especifico', 'valor', 'cant_opi_con_sent', 'prom_sent'])

    # Por campo especifico del producto
    for campo in df_mod.columns[1:]:  # no considero ni id_pub

        relaciones = []

        # Por valor unico del campo
        for valor_unico in df_mod[campo].unique():
            # print(valor_unico)

            # Obtengo ids cuyo campo <campo> tome el valor <valor_unico>
            ids = df_mod[df_mod[campo] == valor_unico]['id_publicacion']
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
                    if matriz_relaciones.loc[palabra_clave, campo] > 0:  # falta implementar que un atrib tenga dos rerlaciones en lugar de 1 y que cargue cuando nio tiene relacion con ningun campo

                        relaciones.append(matriz_relaciones.loc[palabra_clave, campo]) # ojpo que entra aca 20.000 veces. Yo pense que no. Estoy quemado ya.

                        # Obtener <cant_opi_con_sent> y <prom_sent>
                        cant_opi_con_sent = len(df_sent_filtrado[palabra_clave].dropna())
                        prom_sent = df_sent_filtrado[palabra_clave].mean()
                        # print(cant_opi_con_sent, prom_sent)

                        # Guardo fila en dataframe
                        df = df.append({'campo_especifico': campo, 'valor': valor_unico,
                                        'cant_opi_con_sent': cant_opi_con_sent, 'prom_sent': prom_sent}, ignore_index=True)
                        # print(df)

                except:
                    pass


            ''' solo para relacion atrib y palabra clave 1 a 1
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
            '''


        # Agrupo por campo (solo si un campo tiene relacion con mas de una customer need
        if len(relaciones) > 1:
            print('campo {} tiene mas de una relacion'.format(campo))

            df_aux_2 = pd.DataFrame()

            for valor_unico in df_mod[campo].unique():

                # Buscar todos los campos = valor del df
                filas = df[df['campo_especifico']==campo]
                filas = filas[filas['valor'] == valor_unico]
                # filas = df[df['campo_especifico'] ==campo and df['valor'] == valor_unico]

                print(relaciones[:2])
                print(filas['prom_sent'])
                cant_opi_con_sent = sum(filas['cant_opi_con_sent'])
                # tengo que solucionar relaciones y calculo del prom sent
                # prom_sent = relaciones[:2] * filas['prom_sent']
                # prom_sent = numpy.dot(relaciones[:2], filas['prom_sent']) #no se si es exactamenet un producot escalar

                # df_aux_2 = df_aux_2.append({'campo_especifico': campo, 'valor': valor_unico,'cant_opi_con_sent': cant_opi_con_sent, 'prom_sent': prom_sent}, ignore_index=True)
                df_aux_2 = df_aux_2.append({'campo_especifico': campo, 'valor': valor_unico,
                                            'cant_opi_con_sent': cant_opi_con_sent}, ignore_index=True)

    print(df)
    # tendre que unir df...
    df.to_excel('/Users/nachomondino/Desktop/resultados.xlsx', 'Hoja de datos', index=False)
    df_aux_2.to_excel('/Users/nachomondino/Desktop/resultados2.xlsx', 'Hoja de datos', index=False)
    return df




# Levanto el dataset --> en la vida real le paso df_cleanded
df_modelos = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_modelos_formateado.xlsx')
df_opiniones = pd.read_excel('/Users/nachomondino/Desktop/df_opiniones_cleaned.xlsx')
relevant_words = ['precio', 'bateria', 'camara', 'memoria', 'tamaño', 'pantalla', 'resolucion']
df_sent = opinion_sentiment_to_customer_needs(df_opiniones, relevant_words)
atrib = ['precio', 'Marca']
customer_needs = ['precio', 'bateria', 'camara']
df_sent_x_modelo = customer_needs_sentiment_to_attribute_value(df_modelos, df_sent, create_relation_matrix(atrib, customer_needs))



