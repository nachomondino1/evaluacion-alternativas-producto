import pandas as pd

# Read data
df_mod = pd.read_excel("/data/df_extraccion_datos/df_modelos_celulares.xlsx")
df_opi = pd.read_excel("/data/df_extraccion_datos/df_opiniones_celulares.xlsx")

# 1) CANTIDAD DE OPINIONES POR VALOR DE CADA CAMPOR ESPECIFICO

# Defino cantidad de opiniones por id_publicacion
cant_opi_x_id = df_opi['id_publicacion'].value_counts()

# Defino variables utiles
df_aux = pd.DataFrame(columns=["Campo especifico", "Valor", "Cant de opis"])
d = {}

print(df_mod['Marca'].value_counts())

# Por campo especifico de los campos especificos
for campo_esp in df_mod.columns[2:]:

    # Obtengo valores del campo y su frecuencia
    valores_campo_y_frec = df_mod[campo_esp].value_counts()
    valores_campo = valores_campo_y_frec.index
    # print(valores_campo)

    # Por valor de los valores del campo
    for valor in valores_campo:

        # obtengo dataframe filtrado por valor
        df_un_val = df_mod[df_mod[campo_esp] == valor]

        cant_opi_id = 0

        # Por id en ...
        # obtener ids que tienen dicho valos especifico para este campo
        for id in df_un_val['id_publicacion']:

            # obtener cantidad de opiniones de esos ids
            # Sumar y obtener la cantidad de opiniones para ese valor
            cant_opi_id += cant_opi_x_id.loc[id]

        d[valor] = cant_opi_id

    # agrego fila al df_aux





''' Ex implementacion de explote_data en utils
# Importo librerias
import requests
import pandas as pd
import numpy as np

""" aca mi idea es poner todas las funciones generales que usaria para explorar cualquier dataset """

def download_data():
    """
    Creo que descarga archivos csv
    :return:
    """
    download_url = "https://raw.githubusercontent.com/fivethirtyeight/data/master/nba-elo/nbaallelo.csv"
    target_csv_path = "nba_all_elo.csv"

    response = requests.get(download_url)
    response.raise_for_status()    # Check that the request was successful
    with open(target_csv_path, "wb") as f:
        f.write(response.content)
    print("Download ready.")


def data_reader(path):

    # Recorro ultimos elementos del path hasta el punto
    if ".csv" in path:
        df = pd.read_csv(path)

    elif ".xlsx" in path:
        df = pd.read_excel(path)

    else:
        print("No se pudo leer el archivo pues no es de los archivos comunes")
        return None
    return df



'''