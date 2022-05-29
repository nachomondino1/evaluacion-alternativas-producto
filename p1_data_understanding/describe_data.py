import pandas as pd

def getting_to_know_data(df):
    """
    Describe dataframe pasado como parametro
    :param df: Dataframe
    :return: funcion sin retorno
    """
    print("DESCRIPCION DE DATAFRAME:".center(120))

    # Data frame's dimensionality
    print("Dataframe shape: ", df.shape)

    # See firsts 5 Dataframe's rows
    print("Primeras 5 filas del dataframe:")
    pd.set_option("display.max.columns", None)  # para ver todas las columnas del df y no que las colapse
    pd.set_option("display.precision", 2)  # mostrar maximo dos decimales
    print(df.head())  # y .tail es para ver las ultimas filas

    # Displaying Data Types
    print("Dataframe info:")
    df.info()

    # Showing Basics Statistics
    # print("Dataframe basic statistics:")
    # df.describe()  # basic descriptive statistics for all numeric columns  # Por que no funciona?
    # df.describe(include=object)  # basic descriptive statistics for all columns
    print()


def main(df_alt, df_opi):

    print("Dataframe opiniones".center(120))
    getting_to_know_data(df_opi)

    print("Dataframe alternativas".center(120))
    getting_to_know_data(df_alt)
    print()

""" # Para correr pruebas en archivo independientemente de main.py
df_alt = pd.read_excel("/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/{}/df_alt.xlsx".format("celulares"))
df_opi = pd.read_excel("/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/{}/df_opi.xlsx".format("celulares"))
main(df_alt, df_opi)
"""
