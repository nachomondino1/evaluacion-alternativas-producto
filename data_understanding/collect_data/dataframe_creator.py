# Importo librerias
import pandas as pd

def add_lines_to_dataframe(d_data, df):
    """
    Agrega filas en un DataFrame existente
    :param d_data: diccionario con datos. Sus keys deben ser igual a los nombres de las columnas del dataframe
    existente. Sus value pueden ser tanto un solo valor como una lista de valores.
    :param df: DataFrame existente (puede estar vacio aunque si o si con los nombres de las columnas)
    :return: DataFrame agregado con nuevas filas
    """
    # CONVIERTO DICCIONARIO PASADO COMO PARAMETRO A DATAFRAME
    try:
        new_df = pd.DataFrame(data=d_data)
    except:
        new_df = pd.DataFrame(data=d_data, index=[0])

    # CONCATENO EL NUEVO DATAFRAME CON EL DATAFRAME PASADO COMO PARAMETRO
    df = pd.concat([df, new_df])

    return df


def create_dataframe_alternativas(campos_especificos):
    """
    Crea DataFrame de alternativas con los nombres de las columnas correspondientes y sin filas (vacio).
    Los nombres de las columnas dependeran de cada producto, por lo que, son pasados como parametro.
    :param campos_especificos: Lista de campos especificos (o "atributos") del producto de Mercado Libre que deseo
        extraer. Por ejemplo, "tamano de pantalla" para el producto "celulares". Su largo dependera de cada producto.
    :return: Dataframe "alternativas" con los nombres de las columnas correspondientes y sin filas (vacio)
    """
    # DEFINO LISTA CON CAMPOS QUE SON INDEPENDIENTES DEL PRODUCTO
    campos_a_extraer = ['id_alternativa', 'precio']

    # POR CAMPO ESPECIFICO
    for campos_especifico in campos_especificos:

        # LO AGREGO A LA LISTA ANTERIOR
        campos_a_extraer.append(campos_especifico)

    # CREO DATAFRAME DONDE CADA ELEMENTO DE LA LISTA ES EL NOMBRE DE UNA DE SUS COLUMNAS
    df = pd.DataFrame(columns=campos_a_extraer)

    return df


def create_dataframe_opiniones():
    """
    Crea Dataframe de opiniones
    :return: Dataframe "opiniones" con los nombres de las columnas correspondientes y sin filas (vacio)
    """
    # df = pd.DataFrame(columns=['id_alternativa', 'title', 'opinion', 'rate', 'likes', 'dislikes'])
    df = pd.DataFrame(columns=['id_alternativa', 'opinion'])

    return df
