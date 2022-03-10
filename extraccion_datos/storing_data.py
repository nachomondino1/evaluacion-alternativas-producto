import pandas as pd

# verr como unificar y cambiar la nota de las funciones...
def AgregarFilasAlDataFrame1(d_data_publicacion, df):
    """
    Agrega  los datos de todas las publicaciones de una misma subcategoria de productos en un solo DataFrame
    :param id_publicacion: id que identifica como unica a una publicacion de Mercado Libre
    :param d_data_publicacion: diccionario con datos de una sola publicacion. Sus keys son los campos que se extrajeron
    de dicha publicacion y los value los respectivos valores que toma cada campo.
    :param df: DataFrame con los datos de las publicaciones ya extraidas
    :return: DataFrame con los datos de publicaciones ya extradias y, ademas, con los datos de la nueva publicacion
    """

    # Convierto diccionario a DataFrame para poder concatenarlos luego
    new_df = pd.DataFrame(data=d_data_publicacion) #index=[0]

    # Concateno los dataframe agregando la nueva publicacion a ya extraidas.
    df = pd.concat([df, new_df])

    return df

def AgregarFilasAlDataFrame2(d_data_publicacion, df):
    """
    Agrega  los datos de todas las publicaciones de una misma subcategoria de productos en un solo DataFrame
    :param id_publicacion: id que identifica como unica a una publicacion de Mercado Libre
    :param d_data_publicacion: diccionario con datos de una sola publicacion. Sus keys son los campos que se extrajeron
    de dicha publicacion y los value los respectivos valores que toma cada campo.
    :param df: DataFrame con los datos de las publicaciones ya extraidas
    :return: DataFrame con los datos de publicaciones ya extradias y, ademas, con los datos de la nueva publicacion
    """

    # Convierto diccionario a DataFrame para poder concatenarlos luego
    new_df = pd.DataFrame(data=d_data_publicacion, index=[0])

    # Concateno los dataframe agregando la nueva publicacion a ya extraidas.
    df = pd.concat([df, new_df])

    return df



''' EX FUNCION PublicacionesDataFrame() ANTES DE HACER UNA MEJOR EXTRACCION DE ATRIBUTOS O CAMPOS ESPECIFICOS 
EN MercadoLibreCrawler.PublicationExtractor()
def PublicacionesDataFrame(id_publicacion, d_data_publicacion, df):
    """
    Agrega  los datos de todas las publicaciones de una misma subcategoria de productos en un solo DataFrame
    :param id_publicacion: id que identifica como unica a una publicacion de Mercado Libre
    :param d_data_publicacion: diccionario con datos de una sola publicacion. Sus keys son los campos que se extrajeron
    de dicha publicacion y los value los respectivos valores que toma cada campo.
    :param df: DataFrame con los datos de las publicaciones ya extraidas
    :return: DataFrame con los datos de publicaciones ya extradias y, ademas, con los datos de la nueva publicacion
    """
    # Creo diccionario auxiliar para solucionar inconsistencia entre los campos del diccionario (pasados como parametro)
    # y los campos del DataFrame (pasados como parametro). El diccionario puede no tener campos (en sus keys) que el
    # df si tiene (en sus columnas) en el caso en que la publicacion no tiene dicho atributo en su tabla de atributos
    d_aux = {}
    
    # Agrego al diccionario el unico campo que le falta, id_publicacion, antes de unirlo al Dataframe
    d_data_publicacion['id_publicacion'] = id_publicacion

    # Busco cada campo (columna) del df en el diccionario. Si esta, extraigo el valor que tome dicho campo y si no esta,
    # (es porque la publicacion no tiene dicho atributo) entonces le asigno un valor None al campo.
    for column in df.columns:
        if column in d_data_publicacion.keys():
            d_aux[column] = d_data_publicacion[column]
        else:
            d_aux[column] = None

    # Convierto diccionario a DataFrame para poder concatenarlos luego
    new_df = pd.DataFrame(data=d_aux, index=[0])

    # Concateno los dataframe agregando la nueva publicacion a ya extraidas.
    df = pd.concat([df, new_df])

    return df
    
EX OpinionsDataFrame()
def OpinionsDataFrame(id_publicacion, l_data_opiniones, df):
    """
    Agrega los datos de las opiniones de las publicaciones de una misma subcategoria de productos en un solo DataFrame

    :param id_publicacion: id que identifica como unica a una publicacion de Mercado Libre
    :param l_data_opiniones: lista con datos de opiniones de una sola publicacion. Cada elemento es uno de los
    campos a extraer y dentro de cada elemento hay una lista con los valores del respectivo campo para las distintas
    opiniones de la publicacion.
    :param df: DataFrame con los datos de opiniones de las publicaciones ya extraidas
    :return: DataFrame con los datos de opiniones de publicaciones ya extradias y, ademas, con los datos de las
    opiniones de una nueva publicacion
    """
    # Defino parametros que utilizare despues
    idx, l_id_publicacion, d = 0, [], {}

    # Defino variable con nombres de columnas del df de opiniones
    nombres_columnas = ['id_publicacion','title','content','rate', 'likes', 'dislikes']

    # Dado que una publicacion (que tiene un id_publicacion) tiene muchas opiniones, entonces muchas opiniones
    # pertenecen a un mismo id. Para que cada opinion (1 fila del df) de la publicacion tenga el mismo id,
    # debo crear una lista con el mismo id, de largo igual a la cantidad de opiniones.
    for i in range(len(l_data_opiniones[0])): # Le puse [0] pues necesito el largo de cualquiera de los elementos de l_data_opiniones...
        l_id_publicacion.append(id_publicacion)

    # Inserto la lista de id_publicacion en la primera posicion de l_data_opiniones
    l_data_opiniones.insert(0, l_id_publicacion)

    # Para crear el df, requiero que los datos esten en un diccionario (no es necesario pero asi quiero que sea) donde
    # cada key es una columna y el value el valor que toma para determinada opinion. Por ello, transformo
    # l_data_opiniones en un diccionario cuyas key es cada columna y sus values una lista de valores para esa columna
    for columna in l_data_opiniones:
        d[nombres_columnas[idx]] = columna
        idx += 1

    # Creo nuevo dataframe pasandole como dato el diccionario creado anteriormente
    new_df = pd.DataFrame(data=d)

    # Concateno los dataframes, el que tiene los datos de las opiniones ya extraidas y el que tiene los datos
    # de las opiniones de una nueva publicacion
    df = pd.concat([df, new_df])

    return df
'''