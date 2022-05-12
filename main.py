# Importo Librerias
import pandas as pd
from p1_data_understanding.collect_data import main_collect_data, dataframe_creator, mercadolibre_crawler
from p1_data_understanding import describe_data, explore_data
from p2_data_preparation import format_data, clean_data, construct_data
from p2_data_preparation.utils import preparacion_texto
from p3_modelling import sentiment_atribution
import requests

def main():
    '''
    print(" (1) DATA UNDERSTANDING ".center(120, '#'))
    print(" (1.1) COLLECT INITIAL DATA ".center(120))
    # Pido producto a relevar al administrador
    producto = str(input("Ingrese producto a relevar: "))

    # Creo objeto de clase Product()
    product = mercadolibre_crawler.Product(producto)  # despues lo saco

    print("A) Validando producto ingresado...".center(120))
    # Valido el producto buscado tal que no sea una busqueda tan amplia
    product.search_validation()

    # Obtengo atributos o caracteristicas mas relevantes del producto
    print("B) Buscando atributos del producto...".center(120))
    product.atributos = product.get_product_attributes()

    # En base al producto a buscar, creo los dataframes
    df_opiniones = dataframe_creator.create_dataframe_opiniones()
    df_alternativas = dataframe_creator.create_dataframe_alternativas(product.atributos)

    print("C) Extrayendo datos del producto...".center(120))
    # Carga de datos a dataframes
    df_opiniones, df_alternativas = main_collect_data.data_extractor(product, df_opiniones, df_alternativas)

    # Exporto datasets
    df_opiniones.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/df_opi_{}.xlsx'.format(product.nombre), 'Hoja de datos', index=False)
    df_alternativas.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/df_alt_{}.xlsx'.format(product.nombre), 'Hoja de datos', index=False)

    '''
    # Levanto el dataframe ES PRUEBA DE (2)
    df_alternativas = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/df_alt_celulares.xlsx')
    df_opiniones = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/df_opi_celulares.xlsx')
    # df_alternativas = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/df_alternativas_tv.xlsx')
    # df_opiniones = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/df_opiniones_tv.xlsx')

    print(" (1.2) DESCRIBE DATA ".center(120))
    print("Dataframe opiniones".center(120))
    describe_data.getting_to_know_data(df_opiniones)
    print("Dataframe alternativas".center(120))
    describe_data.getting_to_know_data(df_alternativas)
    print()

    print(" (1.3) EXPLORE DATA ".center(120))
    print(" a) Analisis de unicidad de ids ".center(120))
    explore_data.id_uniqueness_check(df_alternativas, df_opiniones)
    print()

    print(" b) Analisis de filas repetidas ".center(120))
    print("Dataframe opiniones")
    explore_data.check_repeated_rows(df_opiniones['opinion']) # filas repetidas sin tener en cuenta el id_pub
    print("Dataframe alternativas")
    explore_data.check_repeated_rows(df_alternativas.iloc[:, 2:])  # filas repetidas sin tener en cuenta el id_pub y precio
    print()

    print(" c) Analisis de cantidad de opiniones por valor de cada campo especifico ".center(120))
    explore_data.n_opi_by_value(df_alternativas, df_opiniones)
    print(), print()

    # Exporto data (podria ser por seguridad)
    # df_opiniones.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/df_opiniones_{}.xlsx'.format(product.nombre), 'Hoja de datos', index=False)
    # df_alternativas.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/df_alternativas_{}.xlsx'.format(product.nombre), 'Hoja de datos', index=False)

    print(" (2) DATA PREPARATION ".center(120, "#"))
    print(" (2.1) FORMAT DATA ".center(120))
    print("2.1.1 Dataframe Alternativas: Corrigiendo columna precio...".center(120))
    df_alternativas['precio'].dropna()  # ESTOY PROBANDO
    df_alternativas['precio'] = format_data.correct_price_column(df_alternativas['precio'])  # DOCUMENTAR QUE LO HAGO PRIMERO...
    print()

    print("2.1.2 Dataframe Alternativas: Convirtiendo columnas de strings con numeros a columnas numericas...".center(120))
    df_alternativas = format_data.string_column_to_numeric_column(df_alternativas)
    print()

    print("2.1.3 Dataframe Alternativas: Convirtiendo columnas si-no a columnas 1-0... ".center(120))
    df_alternativas = format_data.yes_no_column_to_one_zero_column(df_alternativas)
    print()

    print("(2.2) CLEAN DATA ".center(120))
    print("2.2.1 Dataframe Opiniones: Eliminando filas repetidas...".center(120))
    df_opiniones = df_opiniones.drop_duplicates(subset='opinion',ignore_index=True)  # elimino duplicados teniendo en cuenta solo la columna content que es la que contiene opiniones propiamente
    print()

    print("2.2.2 Dataframe Opiniones: Preparando opiniones...".center(120))
    df_opiniones = clean_data.delete_date_of_issue_from_opinion(df_opiniones)  # Elimino fecha de emision al final de la opinion (por ej, "Hace x meses")
    df_opiniones_tokenizado = df_opiniones.copy()  # el df_opiniones recibia el mismo procesamiento que df_opiniones tokenizado, no se por que
    df_opiniones_tokenizado = clean_data.clean_opinions(df_opiniones_tokenizado)  # Limpio las opiniones
    print()

    print("2.2.3 Dataframe Alternativas: Elimino outliers...".center(120))
    df_alternativas = clean_data.delete_alternatives_with_wrong_values(df_alternativas)
    print()

    print("2.2.4 Dataframe Alternativas: Discretizando campos numericos continuos...".center(120))
    df_alternativas.iloc[:, 1:] = clean_data.categorize_numeric_columns(df_alternativas.iloc[:, 1:])  # categorizo columnas numericas con valores continuos, no le paso columna id pues la categorizaria.
    print()

    print("2.2.5 Dataframe Alternativas: Eliminando campos constantes y campos continuos...".center(120))
    df_alternativas = clean_data.delete_attr_x_values(df_alternativas)
    print()


    print(" (2.3) CONSTRUCT DATA ".center(120))
    print("Selecciono customer needs del producto...".center(120))
    customer_needs, customer_needs_one_word = construct_data.select_customer_needs(df_opiniones_tokenizado)
    print()

    # Exporto customer needs Ojo es una lista...
    # customer_needs.to_csv('/Users/nachomondino/Desktop/customer_needs.csv', index=False)

    df_alternativas.to_excel('/Users/nachomondino/Desktop/df_alt_celulares_cleaned.xlsx', index=False)
    df_opiniones_tokenizado.to_excel('/Users/nachomondino/Desktop/df_opiniones_celulares_cleaned.xlsx')


    print(" (3) MODELLING ".center(120, "#"))
    print(" (3.1) ATRIBUCION ".center(120))
    print("3.1.1 Atribuyo sentiment a customer needs...".center(120))
    df_opinion_cust_need = sentiment_atribution.to_customer_needs(df_opiniones, customer_needs_one_word)  # df_opi falta eliminar acentos...

    '''
    print("3.1.2 Creo matriz de relaciones...".center(120))
    # relation_matrix = atribucion.create_relation_matrix(producto.atributos, customer_needs_one_word) # ahorra es sin producto.atributos
    # relation_matrix = sentiment_atribution.create_relation_matrix(df_alternativas.columns[1:], customer_needs_one_word)  # incluyo el precio
    # relation_matrix.to_excel('/Users/nachomondino/Desktop/relation_matrix.xlsx', 'Hoja de datos', index=False)
    relation_matrix = pd.read_excel('/Users/nachomondino/Desktop/relation_matrix.xlsx', index_col=0)
    print(relation_matrix)

    print("3.1.3 Atribuyo sentiment a valores de los atributos del producto...".center(120))
    df_sent_por_valor = sentiment_atribution.to_attribute_value(df_alternativas, df_opinion_cust_need, relation_matrix)
    df_sent_por_valor.to_excel('/Users/nachomondino/Desktop/df_final.xlsx', 'Hoja de datos', index=False)

    print(" (3.2) CLUSTERING ".center(120))
    print("3.2.1 Creo dataframe para clustering...".center(120))
    df_clustering = clustering.create_clustering_dataframe(df_alternativas, df_sent_por_valor)
    print(df_clustering)

    print("3.2.2 Corro modelo clustering...".center(120))
    clustering.k_means(df_clustering)
    '''

if __name__ == '__main__':
    main()
