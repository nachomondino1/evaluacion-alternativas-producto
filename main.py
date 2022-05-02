# Importo Librerias
import data_understanding.collect_data.dataframe_creator
import pandas as pd
from data_understanding.collect_data import main_collect_data, dataframe_creator, mercadolibre_crawler
from data_understanding import describe_data, explore_data
from data_preparation import format_data, clean_data, construct_data
from modelling import sentiment_atribution
import requests

def main():
    '''
    print(" (1) DATA UNDERSTANDING ".center(120, '#'))
    print(" (1.1) COLLECT INITIAL DATA ".center(120))
    # Pido producto a relevar al administrador
    producto = str(input("Ingrese producto a relevar: "))

    # Creo objeto producto
    product = mercadolibre_crawler.Product(producto)  # despues lo saco

    print("A) Validando producto ingresado...".center(120))
    # Valido el producto buscado tal que no sea una busqueda tan amplia
    product.search_validation()

    # Obtengo atributos o caracteristicas mas relevantes del producto
    print("B) Buscando atributos del producto...".center(120))
    product.atributos, name_attrs = product.get_product_attributes()  # el segundo return es parrte de la prueba...

    # En base al producto a buscar, creo los data
    df_opiniones = dataframe_creator.create_dataframe_opiniones()
    df_alternativas = dataframe_creator.create_dataframe_alternativas(product.atributos)

    print("C) Extrayendo datos del producto...".center(120))
    # Carga de datos a data
    df_opiniones, df_alternativas = main_collect_data.data_extractor(product, df_opiniones, df_alternativas)

    '''
    # Levanto el dataframe ES PRUEBA DE (2)
    df_alternativas = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_alternativas_celulares.xlsx')
    df_opiniones = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_opiniones_celulares.xlsx')


    print(" (1.2) DESCRIBE DATA ".center(120))
    describe_data.getting_to_know_data(df_alternativas)
    describe_data.getting_to_know_data(df_opiniones)

    print(" (1.3) EXPLORE DATA ".center(120))
    print(" a) Analisis de unicidad de ids ".center(120))
    explore_data.id_uniqueness_check(df_alternativas, df_opiniones)

    print(" b) Analisis de filas repetidas ".center(120))
    print("Dataframe opiniones")
    explore_data.check_repeated_rows(df_opiniones['opinion']) # filas repetidas sin tener en cuenta el id_pub
    print("Dataframe alternativas")
    explore_data.check_repeated_rows(df_alternativas.iloc[:, 2:])  # filas repetidas sin tener en cuenta el id_pub y precio

    print(" c) Analisis de cantidad de opiniones por valor de cada campo especifico ".center(120))
    explore_data.n_opi_by_value(df_alternativas, df_opiniones)

    # Exporto data (podria ser por seguridad)
    # df_opiniones.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_opiniones_{}.xlsx'.format(product.nombre), 'Hoja de datos', index=False)
    # df_alternativas.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_alternativas_{}.xlsx'.format(product.nombre), 'Hoja de datos', index=False)

    # Levanto el dataframe ES PRUEBA DE (2)
    # df_modelos = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_modelos_celulares.xlsx')
    # df_opiniones = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_opiniones_celulares.xlsx')


    print(" (2) DATA PREPARATION ".center(120, "#"))
    print(" (2.1) FORMAT DATA ".center(120))
    print("A) Dataframe Alternativas: Convirtiendo columnas de strings con numeros a columnas numericas...".center(120))
    df_alternativas = format_data.string_column_to_numeric_column(df_alternativas)

    print("B) Dataframe Alternativas: Convirtiendo columnas si-no a columnas 1-0... ".center(120))
    df_alternativas = format_data.yes_no_column_to_one_zero_column(df_alternativas)


    print("C) Dataframe Alternativas: Corrigiendo columna precio...".center(120))
    df_alternativas['precio'].dropna()  # ESTOY PROBANDO
    df_alternativas['precio'] = format_data.correct_price_column(df_alternativas['precio'])


    print("(2.2) CLEAN DATA ".center(120))  #podria dividirlo por dataframe...
    # print("2.2.1 Dataframe Opiniones: Eliminando none values...".center(120))
    # df_opiniones.dropna()  # borra las pocas filas que no tienen title

    print("2.2.1 Dataframe Opiniones: Eliminando filas repetidas...".center(120))
    df_opiniones = df_opiniones.drop(clean_data.delete_repeated_rows(df_opiniones['opinion']))  # elimino duplicados teniendo en cuenta solo la columna content que es la que contiene opiniones propiamente

    print("2.2.2 Dataframe Alternativas: Categorizando campos numericos continuos...".center(120))
    df_alternativas.iloc[:, 1:] = clean_data.categorize_numeric_columns(df_alternativas.iloc[:, 1:])  # categorizo columnas numericas con valores continuos, no le paso columna id pues la categorizaria.

    print("2.2.3 Dataframe Alternativas: Eliminando campos constantes y campos continuos...".center(120))
    df_alternativas = clean_data.delete_attr_x_values(df_alternativas)  # elimino columnas que toman 1 o muchos valores

    print("2.2.4 Dataframe Opiniones: Preparando opiniones...".center(120))
    # Elimino fecha de emision al final de la opinion (por ej, "Hace x meses")
    df_opiniones = clean_data.correct_opinion_column(df_opiniones)

    # Limpio las opiniones
    df_opiniones_tokenizado = clean_data.text_preparation(df_opiniones['opinion'])  # si el df_cleaned no lo uso para los modelos pues no mejoran el sentiment, entonces no lo uso...
    print(df_opiniones_tokenizado.head(5))
    # df_opiniones_customer.dropna()  # borra las pocas filas que no tienen title. Al remover palabras innecesarias quedo al menos 1 opinion vacia...
    # df_opiniones.to_excel('/Users/nachomondino/Desktop/df_opiniones_cleaned.xlsx', 'Hoja de datos', index=False)
    # df_opiniones.to_excel('/Users/nachomondino/Desktop/df_opiniones_menos_cleaned.xlsx', 'Hoja de datos', index=False)

    print(" (2.3) CONSTRUCT DATA ".center(120))
    print("Selecciono customer needs del producto...".center(120))
    # customer_needs, customer_needs_one_word = construct_data.select_customer_needs(df_opiniones_tokenizado)

    # Exporto customer needs Ojo es una lista...
    # customer_needs.to_csv('/Users/nachomondino/Desktop/customer_needs.csv', index=False)
    # df_alternativas.to_excel('/Users/nachomondino/Desktop/df_modelos_cleaned_2.xlsx')

    '''
    print(" (3) MODELLING ".center(120, "#"))
    print(" (3.1) ATRIBUCION ".center(120))
    print("3.1.1 Atribuyo sentiment a customer needs...".center(120))
    df_sent = sentiment_atribution.to_customer_needs(df_opiniones, customer_needs_one_word)  # df_opi sin limpieza

    print("3.1.2 Creo matriz de relaciones...".center(120))
    # relation_matrix = atribucion.create_relation_matrix(producto.atributos, customer_needs_one_word) # ahorra es sin producto.atributos
    relation_matrix = sentiment_atribution.create_relation_matrix(df_alternativas.columns[1:], customer_needs_one_word)  # incluyo el precio
    relation_matrix.to_excel('/Users/nachomondino/Desktop/relation_matrix.xlsx', 'Hoja de datos', index=False)

    print("3.1.3 Atribuyo sentiment a valores de los atributos del producto...".center(120))
    df_sent_por_valor = sentiment_atribution.to_attribute_value(df_alternativas, df_sent, relation_matrix)
    df_sent_por_valor.to_excel('/Users/nachomondino/Desktop/df_final.xlsx', 'Hoja de datos', index=False)

    print(" (3.2) CLUSTERING ".center(120))
    print("3.2.1 Creo dataframe para clustering...".center(120))
    df_clustering = clustering.create_clustering_dataframe(df_alternativas, df_sent_por_valor)
    print(df_clustering)

    print("3.2.2 Corro modelo clustering...".center(120))
    clustering.k_means(df_clustering)
    '''

    '''
    url = GoogleDrive.leer_archivo('relation_matrix.xlsx')
    print(url)

    s = requests.get(url).content
    print(s)
    df = pd.read_csv(s)
    print(df)
    '''

    # GoogleDrive.bajar_archivo_por_nombre('relation_matrix.xlsx', '/Users/nachomondino/Desktop/prueba/')  # funciona!
    # GUARDO RESULTADOS EN MY SQL?


if __name__ == '__main__':
    main()
