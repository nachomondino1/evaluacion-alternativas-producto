import pandas as pd

def getting_to_know_data(df):
    # Data frame's dimensionality
    print("Dimensionality: ", df.shape)

    # See firsts 5 Dataframe's rows
    pd.set_option("display.max.columns", None)  # para ver todas las columnas del df y no que las colapse
    pd.set_option("display.precision", 2)  # mostrar maximo dos decimales
    # print(df.head())  # y .tail es para ver las ultimas filas

    # Displaying Data Types
    df.info()

    # Showing Basics Statistics
    # df.describe()  # basic descriptive statistics for all numeric columns
    df.describe(include=object)  # basic descriptive statistics for all columns

    # Exploring dataset
    # df["Marca"].value_counts()  # puedo usarlo paracualquier columna


def main():
    df_mod = pd.read_excel("/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_modelos_celulares.xlsx")
    df_opi = pd.read_excel("/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_opiniones_celulares.xlsx")

    # Describe dataframe modelos
    getting_to_know_data(df_mod)

    # Describe dataframe opiniones
    getting_to_know_data(df_opi)

main()