
# DEJO TODOS MIS INTENTOS FRUSTRADOS POR LAS DUDAS.

"""
Necesito el df_categorias pues tengo el nombre y el id de una subcategoria. El id lo uso para obtener los atributos de
cada subcategoria y el nombre pues de la busqueda del cliente obtengo el nombre. necesito el df_Categorias pues linkea ambos campos.

Guardo el archivo perfectamente y cada elemento de atributos es una lista. El problema es cuando exporto el archivi
y lo abro en otro archivo... ahi convierte las listas en string.
"""




def CrearDataFrameCategorias():
    """
    Le agregaria la columna atributos a CrearDataFrameCategorias
    PROBLEMA: genera df de categorias y subcategorias con su id y los atributos pero cada celda de atributos es un string
    en lugar de una lista... por lo que, no puedo extraer los atributos que es para lo que la quiero.
    """
    # Creo objeto de MercadoLibreApi()
    api = MercadoLibreApi()

    # Creo Dataframe de categorias aunque aun faltan los atributos por cada una
    d_categorias = api.getCategoriasID()

    # Defino lista en donde guardare los atributos de todas las categorias
    atributos_categoria = []

    # Busco atributos por categoria usando la api
    for id_subcategoria in d_categorias['id_subcategoria']:
        atributos_categoria.append(api.getAtributosSubcategoria(id_subcategoria))

    # Agrego columna "Atributos" al Dataframe de categorias
    # df_categorias['Atributos'] = atributos_categoria # new_df = df_categorias.assign(Atributos=atributos_categoria)
    d_categorias["atributos"] = atributos_categoria

    # Guardo el diccionario en un archivo
    # np.save('d_categorias.npy', d_categorias)

    df_categorias = pd.DataFrame(data=d_categorias)
    path = '/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/extraccion_datos/df_categorias.csv'
    df_categorias.to_csv(path, index=False)

# CrearDataFrameCategorias()


''' Para guardar diccionario en csv
# load csv module
import csv

# define a dictionary with key value pairs
dict = CrearDataFrameCategorias()

# open file for writing, "w" is writing
w = csv.writer(open("output.csv", "w"))

# loop over dictionary keys and values
for key, val in dict.items():

    # write every key and value to file
    w.writerow([key, val])
'''

'''
# Convierto el diccionario de datos a un DataFrame
df_categorias = pd.DataFrame(data=d_categorias)

# Guardo el Dataframe en un archivo para visualizar el rdo (solamente visualizarlo pues guarda a "Atributos" como
# un string.
df_categorias.to_excel(
    '/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/extraccion_datos/df_categorias.xlsx',
    'Hoja de datos', index=False)
'''


# CrearDataFrameCategorias()


'''
# Guardo el Dataframe en un archivo para visualizar el rdo (solamente visualizarlo pues guarda a "Atributos" como
# un string.
df_categorias.to_excel(
    '/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/extraccion_datos/df_categorias.xlsx',
    'Hoja de datos', index=False)
'''




'''
def main():
    # Creo objeto de MercadoLibreApi()
    api = MercadoLibreApi()

    # Creo Dataframe de categorias aunque aun faltan los atributos por cada una
    df_categorias = api.getCategoriasID()

    d_categorias = {}

    # Busco atributos de cada subcategoria
    for id_subcat in df_categorias['id_subcategoria']:
        atributo_categoria = api.getAtributosSubcategoria(id_subcat)
        d_categorias[id_subcat] = atributo_categoria
    
    
    # Guardo el diccionario en un archivo
    np.save('d_categorias.npy', d_categorias)

main()


def DictIdAtributos():
    """

    :return: Diccionario cuyas keys son los id_subcategoria y cuyos values son una lista de atributos que me interesan
    de la respectiva categoria
    """
    # Creo objeto de MercadoLibreApi()
    api = MercadoLibreApi()

    # Creo Dataframe de categorias aunque aun faltan los atributos por cada una
    df_categorias = api.getCategoriasID()

    # Defino diccionario donde guardare el id de la categoria y sus atributos
    d = {}

    # Busco atributos por categoria usando la api
    for id_subcategoria in df_categorias['id_subcategoria']:
        d[id_subcategoria] = getAtributosSubcategoria(id_subcategoria, api)

    # Guardo el diccionario en un archivo
    np.save('file.npy', d)
    return d



def CrearDataFrameCategorias():
    
    # Creo objeto de MercadoLibreApi()
    api = MercadoLibreApi()

    # Creo Dataframe de categorias aunque aun faltan los atributos por cada una
    df_categorias = api.getCategoriasID()

    # Guardo el Dataframe en un archivo para visualizar el rdo (solamente visualizarlo pues guarda a "Atributos" como
    # un string.
    df_categorias.to_excel(
        '/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/extraccion_datos/df_categorias.xlsx',
        'Hoja de datos', index=False)
    

def main():
    api = MercadoLibreApi()
    api.getCategoriasID()
    DictIdAtributos()

main()



def CrearDataFrameCategorias2():
    """
    Le agregaria la columna atributos a CrearDataFrameCategorias
    PROBLEMA: genera df de categorias y subcategorias con su id y los atributos pero cada celda de atributos es un string
    en lugar de una lista... por lo que, no puedo extraer los atributos que es para lo que la quiero.
    """
    # Creo objeto de MercadoLibreApi()
    api = MercadoLibreApi()

    # Creo Dataframe de categorias aunque aun faltan los atributos por cada una
    df_categorias = api.getCategoriasID()

    # Defino lista en donde guardare los atributos de todas las categorias
    atributos_categoria = []

    # Busco atributos por categoria usando la api
    for id_subcategoria in df_categorias['id_subcategoria']:
        atributo_categoria = getAtributosSubcategoria(id_subcategoria,api)
        atributos_categoria.append(atributo_categoria)

    # Agrego columna "Atributos" al Dataframe de categorias
    df_categorias['Atributos'] = atributos_categoria # new_df = df_categorias.assign(Atributos=atributos_categoria)

    # Guardo el Dataframe en un archivo para visualizar el rdo (solamente visualizarlo pues guarda a "Atributos" como
    # un string.
    df_categorias.to_excel(
        '/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/extraccion_datos/df_categorias.xlsx',
        'Hoja de datos', index=False)

'''