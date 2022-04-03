import pandas as pd

# Read data
df_mod = pd.read_excel("/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_modelos_celulares.xlsx")
df_opi = pd.read_excel("/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_opiniones_celulares.xlsx")
# print(df_mod)
# print(df_opi)


# 1) FILAS REPETIDAS
def delete_repeated_rows(df):

    cant_filas = df.shape[0]
    print("Originalmente el dataframe tenia {} filas.".format(cant_filas),end=" ")

    df = df.drop_duplicates()
    cant_filas = df.shape[0]
    print("Tras eliminar filas duplicadas, el dataframe tiene {} filas".format(cant_filas))
    return df

print(" ------------------------ 1) ANALISIS DE FILAS REPETIDAS ------------------------ ")
# filas repetidas sin tener en cuenta el id_pub
print("DATAFRAME OPINIONES")
delete_repeated_rows(df_opi.iloc[:, 1:])
# print(df_opi.iloc[:, 1:].columns)

# filas repetidas sin tener en cuenta el id_pub y precio
print("DATAFRAME MODELOS")
delete_repeated_rows(df_mod.iloc[:, 2:])
# print(df_mod.iloc[:, 2:].columns)
print()


# 2) UNICIDAD DE VALORES
print(" ------------------------ 2) ANALISIS DE UNICIDAD DE VALORES ------------------------ ")
# 2.1 unicidad de ids
print('  - Unicidad de ids')
print("Deberia haber {} ids unicos".format(len(df_mod)))
print("Hay {} ids unicos en opiniones Dataframe".format(len(df_opi['id_publicacion'].unique())))
print("Hay {} ids unicos en modelos Dataframe".format(len(df_mod['id_publicacion'].unique())))
print()

# 2.2 unicidad de atributos
print('  - Unicidad de campos especificos')
for campo_esp in df_mod.columns[2:]:
    cant_valores = len(df_mod[campo_esp].unique())
    print("El campo especifico '{}' toma {} valores distintos en {} filas".format(campo_esp, cant_valores, len(df_mod)))
print()


# 3) CANTIDAD DE OPINIONES POR VALOR DE CADA CAMPO ESPECIFICO
print(" ------------------ 3) ANALISIS DE CANTIDAD DE OPINIONES POR VALOR DE CADA CAMPO ESPECIFICO ----------------- ")
# Defino cantidad de opiniones por id_publicacion
cant_opi_x_id = df_opi['id_publicacion'].value_counts()
# print(cant_opi_x_id)

# Defino variables utiles
df = pd.DataFrame(columns=["campo_esp", "valor", "cant_opi"])

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
        new_df = pd.DataFrame(data={"campo_esp": campo_esp, "valor": valor, "cant_opi": cant_opi}, index=[0])
        df = pd.concat([df, new_df])


# Exploring dataset
# campo_espec = pd.Series(df['campo_esp'].unique(), name='camp_esp')
count = pd.Series(df['campo_esp'].value_counts(), name='cant_valores')
prom = pd.Series(df.groupby("campo_esp")['cant_opi'].mean(), name='prom_opi_x_val')
max = pd.Series(df.groupby("campo_esp")['cant_opi'].max(), name='max_opi_x_val')
min = pd.Series(df.groupby("campo_esp")['cant_opi'].min(), name='min_opi_x_val')
df_aux = pd.concat([count, prom, max, min], axis=1)
pd.set_option("display.max.columns", None)
pd.set_option("display.precision", 0)
df_aux.to_excel('/Users/nachomondino/Desktop/df_campo_valores.xlsx', 'Hoja de datos', index=False)
print(df_aux)
