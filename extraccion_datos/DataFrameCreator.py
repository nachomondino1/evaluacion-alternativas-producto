# Importo librerias
import pandas as pd

def AgregarFilasAlDataFrame(d_data, df):
    """
    Agrega datos en un DataFrame existente

    :param d_data: diccionario con datos. Los value pueden ser un solo valor o una lista de valores
    :param df: DataFrame existente
    :return: DataFrame existente con nuevos datos agregados
    """

    # Convierto diccionario a DataFrame para poder concatenarlos luego
    try:
        new_df = pd.DataFrame(data=d_data)
    except:
        new_df = pd.DataFrame(data=d_data, index=[0])

    # Concateno los dataframe agregando la nueva publicacion a ya extraidas.
    df = pd.concat([df, new_df])

    return df


def CrearModelosDataFrame(campos_especificos):
    """
    Crea DataFrame (vacio, sin datos aun) de publicaciones con los nombres de las columnas de aquellos campos que
    deseo extraer de una publicacion

    :param campos_especificos: Lista de campos especificos de una subcategoria de productos de Mercado Libre que
    deseo extraer. Por ejemplo, "tamano de pantalla" para la subcategoria "Celulares y Smartphones". Su largo dependera
    de cada subcategoria, por lo que, la cantidad de columnas del df tambien variara de una subcategoria a otra.
    :return: DataFrame para guardar informacion de publicaciones de una subcategoria en particular
    """

    # A priori, extraigo de cada publicacion los campos generales a todas las subcategorias de productos
    campos_a_extraer = ['id_publicacion', 'precio']

    # Agrego los campos especificos de la subcategoria
    for campos_especifico in campos_especificos:
        campos_a_extraer.append(campos_especifico)

    # Creo el DataFrame con los campos a extraer como columnas de este
    df = pd.DataFrame(columns=campos_a_extraer)

    return df


def CrearOpinionsDataFrame():
    df = pd.DataFrame(columns=['id_publicacion', 'title', 'content', 'rate', 'likes', 'dislikes'])
    return df