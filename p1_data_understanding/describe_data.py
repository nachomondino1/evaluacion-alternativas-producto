import pandas as pd

def getting_to_know_data(df):
    """
    Describe dataframe pasado como parametro
    :param df: Dataframe
    :return: funcion sin retorno
    """
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

'''
def main():
    df_mod = pd.read_excel("/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/df_alternativas_celulares.xlsx")
    df_opi = pd.read_excel("/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/df_opiniones_celulares.xlsx")

    # Describe dataframe modelos
    getting_to_know_data(df_mod)

    # Describe dataframe opiniones
    getting_to_know_data(df_opi)

main()
'''