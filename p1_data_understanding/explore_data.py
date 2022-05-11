# Importo librerias
import pandas as pd


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


'''
def main():
    # READ DATA
    df_mod = pd.read_excel("/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/df_alternativas_celulares.xlsx")
    df_opi = pd.read_excel("/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/df_opiniones_celulares.xlsx")
    # df_mod = pd.read_excel("/Users/nachomondino/Desktop/df_categorizado.xlsx")
    # df_mod = pd.read_excel("/Users/nachomondino/Desktop/df_modelos_cleaned.xlsx")

    # 1) UNICIDAD DE VALORES
    print(" ------------------------ 1) ANALISIS DE UNICIDAD DE IDS ------------------------ ")
    id_uniqueness_check(df_mod, df_opi)

    # 2) ANALISIS DE FILAS REPETIDAS
    print(" ------------------------ 2) ANALISIS DE FILAS REPETIDAS ------------------------ ")
    # filas repetidas sin tener en cuenta el id_pub
    print("DATAFRAME OPINIONES")
    # delete_repeated_rows(df_opi.iloc[:, 1:])  # ojo que luego de aqui sigo trabajando con df con filas repetidas...
    check_repeated_rows(df_opi['opinion'])  # ojo que luego de aqui sigo trabajando con df con filas repetidas...

    # filas repetidas sin tener en cuenta el id_pub y precio
    print("DATAFRAME MODELOS")
    check_repeated_rows(df_mod.iloc[:, 2:])  # ojo que luego de aqui sigo trabajando con df con filas repetidas...
    print()

    # 3) CANTIDAD DE OPINIONES POR VALOR DE CADA CAMPO ESPECIFICO
    print(" ---------------- 3) ANALISIS DE CANTIDAD DE OPINIONES POR VALOR DE CADA CAMPO ESPECIFICO --------------- ")
    # attributes_values(df_mod)
    n_opi_by_value(df_mod, df_opi)


main()
'''
