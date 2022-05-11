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
    # DEFINO MINIMO DE PUBLICACIONES A VISITAR
    MIN_PUB_A_VISITAR = 50  # es mas de 50 para que se estabilicen los % de publicaciones extraidas

    # SI YA VISITE AL MENOS <MIN_PUB_A_VISITAR> PUBLICACIONES
    if len(historico_paginas) > MIN_PUB_A_VISITAR:

        # SELECCIONO LOS BOOLEAN DE LAS ULTIMAS <CANT_ULT_PUB> PUBLICACIONES
        ultimas_paginas = historico_paginas[-cant_ult_pub:]
        # print("Ultimas {}:".format(cant_ult_pag), ultimas_paginas)

        # DEFINO CANTIDAD x DE LAS ULTIMAS <CANT_ULT_PUB> PUBS EN QUE LOGRE EXTRAER DATOS
        cant_ult_pag_extraidas = sum(ultimas_paginas)

        # DEFINO PORCENTAJE DE LAS ULTIMAS <CANT_ULT_PUB> PUBLICACIONES EN QUE LOGRE EXTRAER DATOS
        porc_ult_pub_extraidas = cant_ult_pag_extraidas / cant_ult_pub
        # print("Porcentaje de extraidas de ultimas", porc_ult_pag_extraidas)

        # SI EL PORCENTAJE ANTERIOR ES MENOR AL PORCENTAJE MINIMO
        if porc_ult_pub_extraidas < porc_min_ult_pub_extraidas:

            # DEJO DE EXTRAER DATOS
            print("Dejare extraccion de datos pues el Crawler ingreso al {} de las ultimas {} paginas".format(
                porc_ult_pub_extraidas, cant_ult_pub))
            return True

    return False


def explicacion_corte(pag_num, pag_max, ult_pub_sin_data):
    """
    Imprime por pantalla la razon por la que finalizo la extraccion de datos
    :param pag_num: Cantidad de paginas visitadas (de paginacion)
    :param pag_max: Cantidad de pagonas maximas a visitas (de paginacion)
    :param ult_pub_sin_data: Boolean, 1 si extraje muy pocos datos de las ultimas publicaciones y 0 en caso contrario
    :return: funcion sin return
    """
    # Si extraje pocos datos de las ultimas paginas (Parametro de corte 1)
    if ult_pub_sin_data == 1:
        # Imprimo mensaje
        print("Corto pues el Crawler ingreso a muy pocas de las publicaciones")

    # Si alcance el maximo de paginas a visitar (de paginacion) (Parametro de corte 2)
    elif pag_num == pag_max:
        # Imprimo mensaje
        print("Corto porque se visitaron las {} primeras paginas".format(pag_max))

    # Si no hay siguiente pagina (de paginacion) (Parametro de corte 3)
    else:
        # Imprimo mensaje
        print("Corto por no haber mas paginas. Se recorrieron {} paginas".format(pag_num))
