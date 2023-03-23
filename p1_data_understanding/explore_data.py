# Importo librerias
import pandas as pd


def check_ids(df_alt, df_opi): # notas
    """
    Verifica unicidad de ids y consistencia entre dataframes
    :param df_alt:
    :param df_opi:
    :return:
    """
    # Obtengo cantidad de ids unicos en cada dataframe
    ids = list(df_alt['id_alternativa'])  # ids en dataframe altenativas
    ids_con_opi = df_opi['id_alternativa'].unique()  # ids en dataframe opiniones
    cant_ids = len(ids)
    cant_ids_opi = len(ids_con_opi)

    # Verifico que ids con opinion tengan id en Dataframe alternativas
    print("Verifico que toda opinion tenga un id asociado en Dataframe alternativas")
    i = 0
    for id_con_opi in ids_con_opi:
        if id_con_opi not in ids:
            i += 1
    print("Hay {} ids que estan en Dataframe opiniones y no en Dataframe Alternativas!".format(i)), print()

    print("Verifico unicidad de ids:")
    print("Dataframe alternativas --> Hay {} id de los cuales {} son unicos".format(cant_ids, len(df_alt['id_alternativa'].unique())))
    print("Dataframe opiniones    --> Hay {} id de los cuales {} son unicos".format(cant_ids_opi, len(df_opi['id_alternativa'].unique())))

def check_repeated_rows(df):
    """
    Revisa si un Dataframe tiene filas repetidas e imprime los resultados por pantalla
    :param df: Dataframe a revisar
    :return: funcion sin retorno
    """
    # Defino cantidad de filas
    cant_filas = df.shape[0]
    print("Originalmente el dataframe tiene {} filas.".format(cant_filas), end=" ")

    # Elimino filas duplicadas
    df = df.drop_duplicates()

    # Defino nueva cantidad de filas
    cant_filas = df.shape[0]
    print("Si eliminase filas duplicadas el dataframe quedaria de {} filas".format(cant_filas))

def n_opi_by_value(df_alt, df_opi):
    """
    Crea un dataframe cuya unidad de analisis es el valor de un atributo del producto. Por cada valor, podre ver a que
    atributo pertenece y, segun las alternativas en que el atributo toma el valor, la cantidad de opiniones asociadas
    (cada alternativa tiene x cantidad de opiniones)
    :param df_alt: Dataframe alternativas
    :param df_opi: Dataframe opiniones
    :return: exporta archivo excel con Dataframe
    """
    # Defino variables
    df = pd.DataFrame(columns=["campo_esp", "valor", "cant_alt", "cant_opi_alt"])  # dataframe a retornar

    # Por atributo o campo especifico del producto
    for campo_esp in df_alt.columns[2:]:

        # Obtengo valores del atributo y su frecuencia
        valores_campo_y_frec = df_alt[campo_esp].value_counts()
        valores_campo = valores_campo_y_frec.index
        # print(" ++++ {} ++++".format(campo_esp))
        # print(valores_campo)

        # Por valor
        for valor in valores_campo:

            # Selecciono alternativas cuyo <atributo> toma <valor> y obtengo sus ids
            df_un_val = df_alt[df_alt[campo_esp] == valor]
            ids_val = df_un_val['id_alternativa']

            # Obtengo cantidad de opiniones segun ids anteriores
            cant_opi = len(df_opi[df_opi.id_alternativa.isin(ids_val)])

            # Recorridos todos los ids, guardo el valor y su cantidad de opiniones
            new_df = pd.DataFrame(data={"campo_esp": campo_esp, "valor": valor, "cant_alt": valores_campo_y_frec[valor],
                                        "cant_opi_alt": cant_opi}, index=[0])
            df = pd.concat([df, new_df])

    # Exporto archivo excel con los datos recabados
    path = '/Users/nachomondino/Desktop/df_opiniones_per_value.xlsx'
    print("Se guarda el archivo en {}".format(path))
    return df.to_excel(path, 'Hoja de datos', index=False)

def main(df_alt, df_opi):

    print(" a) Analisis de unicidad de ids ".center(120))
    check_ids(df_alt, df_opi)
    # id_uniqueness_check(df_alt, df_opi)
    print()

    print(" b) Analisis de filas repetidas ".center(120))
    print("Dataframe opiniones (considerando unicamente opiniones)")
    check_repeated_rows(df_opi['opinion'])  # filas repetidas sin tener en cuenta el id_pub
    print("Dataframe alternativas (sin considerar id_alternativa ni precio)")
    check_repeated_rows(df_alt.iloc[:, 2:])  # filas repetidas sin tener en cuenta el id_pub y precio
    print()

    print(" c) Analisis de cantidad de opiniones por valor de cada campo especifico ".center(120))
    n_opi_by_value(df_alt, df_opi)
    print(), print()

"""# Para correr pruebas en archivo independientemente de main.py
df_alt = pd.read_excel("/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/{}/df_alt.xlsx".format("celulares")))
df_opi = pd.read_excel("/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/{}/df_opi.xlsx".format("celulares"))
main()
"""


''' # REEMPLAZADA POR CHECK_ID QUE LE AGREGA NUEVA VERIF
def id_uniqueness_check(df_alt, df_opi):
    """
    Chequea unicidad de ids en cada dataframe e indica su cantidad
    :param df_alt: Dataframe alternativas
    :param df_opi: Dataframe opiniones
    :return: funcion sin retorno
    """
    # Obtengo cantidad de ids unicos en cada dataframe
    cant_ids_opi = len(df_opi['id_alternativa'].unique())
    cant_ids_alt = len(df_alt['id_alternativa'].unique())

    # Imprimo resultados por pantalla
    print("Deberia haber {} ids unicos. Hay {} ids unicos en Dataframe alternativas".format(len(df_alt), cant_ids_alt))
    print("Hay {} ids unicos en Dataframe opiniones".format(cant_ids_opi))
    print()
'''