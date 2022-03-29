
def ultimas_pub_sin_data(historico_paginas, porc_min_ult_pub_extraidas, cant_ult_pub):
    """
    Evalua si conviene seguir extrayendo datos o no segun el % de las ultimas x publicaciones en que el crawler extrajo
    datos.

    :param historico_paginas: Lista de 0 y 1. Tiene un 1 por cada publicacion de la cual extrajo datos y un 0 en caso
    contrario
    :param porc_min_ult_pub_extraidas: Porcentaje minimo de las ultimas x publicaciones en que el crawler extrajo
    datos (Float de 0 a 1)
    :param cant_ult_pub: Numero que determina cuantas publicaciones son consideradas como las "ultimas publicaciones"
    :return: True si conviene dejar de extraer datos, o bien, False si conviene continuar extrayendo.
    """

    # Si no es la primera pagina (pues en la primera pagina, podria ser que las primeras publicaciones falle la extraccion y el porcentaje seria 0 y por ende cortarria)
    min_pub_a_visitar = 50

    # Si ya visite al menos <min_pub_a_visitar> publicaciones
    if len(historico_paginas) > min_pub_a_visitar:

        # Selecciono los boolean de las ultimas <cant_ult_pub> publicaciones
        ultimas_paginas = historico_paginas[-cant_ult_pub:]
        # print("Ultimas {}:".format(cant_ult_pag), ultimas_paginas)

        # Cantidad de ultimas publicaciones que logre extraer datos
        cant_ult_pag_extraidas = sum(ultimas_paginas)

        # Defino porcentaje de las ultimas publicaciones que logre extraer datos
        porc_ult_pub_extraidas = cant_ult_pag_extraidas / cant_ult_pub
        # print("Porcentaje de extraidas de ultimas", porc_ult_pag_extraidas)

        # Si el porcentaje de ultimas publicaciones extraidas es menor al porcentaje minimo
        if porc_ult_pub_extraidas < porc_min_ult_pub_extraidas:

            # Dejo de extraer datos
            print("Dejare extraccion de datos pues el Crawler ingreso al {} de las ultimas {} paginas".format(
                porc_ult_pub_extraidas, cant_ult_pub))
            return True

    return False


def explicacion_corte(pag_num, pag_max, no_mas_paginas, ult_pub_sin_data):
    """
    Imprime por pantalla la razon por la que finalizo la extraccion de datos

    :param pag_num: Numero de ultima pagina visitada
    :param pag_max: Numero maximo de paginas a visitar
    :param ult_pub_sin_data: 1 si extraje muy pocos datos de las ultimas publicaciones y 0 en caso contrario
    :return:
    """

    # Parametro de corte 1
    if pag_num == pag_max:
        print("Corto porque se visitaron las {} primeras paginas".format(pag_max))

    # Parametro de corte 2
    elif no_mas_paginas == 1:
        print("Corto por no haber mas paginas. Se recorrieron {} paginas".format(pag_num))

    # Parametro de corte 3
    else: # ult_pub_sin_data == 1:
        # print("Corto pues el Crawler ingreso al {} de las ultimas {} paginas".format(porc_ult_pag_extraidas, cant_ult_pag))
        print("Corto pues el Crawler ingreso a muy pocas de las publicaciones")

    '''    
    
    '''







