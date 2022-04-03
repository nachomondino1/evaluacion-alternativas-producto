# Importo librerias
import pandas as pd


def delete_repeated_rows(df):
    # Defino cantidad de filas
    cant_filas = df.shape[0]
    print("Originalmente el dataframe tenia {} filas.".format(cant_filas), end=" ")

    # Elimino filas duplicadas
    df = df.drop_duplicates()

    # Defino nueva cantidad de filas
    cant_filas = df.shape[0]
    print("Tras eliminar filas duplicadas, el dataframe tiene {} filas".format(cant_filas))
    return df


def id_unique_verification(df_mod, df_opi):
    print("Deberia haber {} ids unicos".format(len(df_mod)))
    print("Hay {} ids unicos en opiniones Dataframe".format(len(df_opi['id_publicacion'].unique())))
    print("Hay {} ids unicos en modelos Dataframe".format(len(df_mod['id_publicacion'].unique())))
    print()


def n_opi_per_value(df_mod, df_opi):
    # Defino cantidad de opiniones por id_publicacion
    cant_opi_x_id = df_opi['id_publicacion'].value_counts()
    # print(cant_opi_x_id)

    # Defino variables utiles
    df = pd.DataFrame(columns=["campo_esp", "valor", "cant_pub", "cant_opi_pubs"])

    # Por campo especifico de los campos especificos
    for campo_esp in df_mod.columns[2:]:

        # Obtengo valores del campo y su frecuencia
        valores_campo_y_frec = df_mod[campo_esp].value_counts()
        valores_campo = valores_campo_y_frec.index
        # print(" ++++ {} ++++".format(campo_esp))
        # print(valores_campo)

        # Por valor de los valores del campo
        for valor in valores_campo:
            # print(valor)

            # obtengo dataframe filtrado por valor
            df_un_val = df_mod[df_mod[campo_esp] == valor]
            # print(df_un_val)
            ids_val = df_un_val['id_publicacion']
            # print(ids_val)
            cant_opi = 0

            # Por id de los id cuyos <campo especifico> toma <valor>
            for id in ids_val:
                # print(id)

                # obtener cantidad de opiniones de esos ids
                # Sumar y obtener la cantidad de opiniones para ese valor
                cant_opi += cant_opi_x_id.loc[id]

            # print(valor, cant_opi)
            # Guardo datos del valor y su cantidad de opiniones
            new_df = pd.DataFrame(data={"campo_esp": campo_esp, "valor": valor, "cant_pub": valores_campo_y_frec[valor],
                                        "cant_opi_pubs": cant_opi}, index=[0])
            df = pd.concat([df, new_df])

    path = '/Users/nachomondino/Desktop/df_campo_valores.xlsx'
    print("Se guarda el archivo en {}".format(path))
    df.to_excel(path, 'Hoja de datos', index=False)


def main():
    # READ DATA
    df_mod = pd.read_excel(
        "/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_modelos_celulares.xlsx")
    df_opi = pd.read_excel(
        "/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_opiniones_celulares.xlsx")

    # 1) UNICIDAD DE VALORES
    print(" ------------------------ 1) ANALISIS DE UNICIDAD DE IDS ------------------------ ")
    id_unique_verification(df_mod, df_opi)

    # 2) ANALISIS DE FILAS REPETIDAS
    print(" ------------------------ 2) ANALISIS DE FILAS REPETIDAS ------------------------ ")
    # filas repetidas sin tener en cuenta el id_pub
    print("DATAFRAME OPINIONES")
    # delete_repeated_rows(df_opi.iloc[:, 1:])  # ojo que luego de aqui sigo trabajando con df con filas repetidas...
    delete_repeated_rows(df_opi['content'])  # ojo que luego de aqui sigo trabajando con df con filas repetidas...

    # filas repetidas sin tener en cuenta el id_pub y precio
    print("DATAFRAME MODELOS")
    delete_repeated_rows(df_mod.iloc[:, 2:])  # ojo que luego de aqui sigo trabajando con df con filas repetidas...
    print()

    # 3) CANTIDAD DE OPINIONES POR VALOR DE CADA CAMPO ESPECIFICO
    print(" ---------------- 3) ANALISIS DE CANTIDAD DE OPINIONES POR VALOR DE CADA CAMPO ESPECIFICO --------------- ")
    # attributes_values(df_mod)
    n_opi_per_value(df_mod, df_opi)


main()
