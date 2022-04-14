# Importo Librerias
import data_understanding.collect_data.dataframe_creator
import pandas as pd
from data_understanding.collect_data import main_collect_data, dataframe_creator, mercadolibre_crawler
from data_preparation import format_data, clean_data, construct_data
from modelling import sentiment_atribution_primer_intento
import GoogleDrive
import requests

def main():
    '''
    print(" ------------------- (1) EXTRACCION DE DATOS  ------------------- ")
    # Pido producto a relevar al administrador
    producto = str(input("Ingrese producto a relevar:"))

    # Creo objeto producto
    product = mercadolibre_crawler.Product(producto)  # despues lo saco

    # Valido el producto buscado tal que no sea una busqueda tan amplia
    product.search_validation()

    # Obtengo atributos o caracteristicas mas relevantes del producto
    product.atributos = product.get_product_attributes()

    # En base al producto a buscar, creo los data
    df_opiniones = dataframe_creator.create_opinions_dataframe()
    df_modelos = dataframe_creator.create_models_dataframe(product.atributos)

    # Carga de datos a data
    df_opiniones, df_modelos = main_collect_data.data_extractor(product, df_opiniones, df_modelos)

    # Exporto data (podria ser por seguridad)
    # df_opiniones.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_opiniones_{}.xlsx'.format(product.nombre), 'Hoja de datos', index=False)
    # df_modelos.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_modelos_{}.xlsx'.format(product.nombre), 'Hoja de datos', index=False)
    '''

    # Levanto el dataframe ES PRUEBA DE (2)
    df_modelos = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_modelos_celulares.xlsx')
    df_opiniones = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_opiniones_celulares.xlsx')

    print(" ------------------- (2) DATA PREPARATION  ------------------- ")
    print(" +++++++++++++++++++ (2.1) FORMAT DATA  +++++++++++++++++++ ")
    print("2.1.1 Convirtiendo columnas de strings con numeros a columnas numericas...")
    df_modelos = format_data.string_column_to_numeric_column(df_modelos)

    print("2.1.2 Convirtiendo columnas si-no a columnas 1-0... ")
    df_modelos = format_data.yes_no_column_to_ones_ceros_column(df_modelos)

    print("2.1.3 Corrigiendo columna precio...")
    df_modelos['precio'] = format_data.correct_price_column(df_modelos['precio'])

    print(" +++++++++++++++++++ (2.2) CLEAN DATA  +++++++++++++++++++ ")
    print("2.2.1 Eliminando none values...")
    df_opiniones.dropna()  # borra las pocas filas que no tienen title

    print("2.2.2 Eliminando filas repetidas...")
    df_opiniones = df_opiniones.drop(clean_data.delete_repeated_rows(df_opiniones['content']))  # elimino duplicados teniendo en cuenta solo la columna content que es la que contiene opiniones propiamente

    print("2.2.3 Categorizando campos numericos continuos...")
    df_modelos.iloc[:, 1:] = clean_data.categorize_numeric_columns(df_modelos.iloc[:, 1:])  # categorizo columnas numericas con valores continuos, no le paso columna id pues la categorizaria.

    print("2.2.4 Eliminando campos constantes y campos continuos...")
    df_modelos = clean_data.delete_attr_x_values(df_modelos)  # elimino columnas que toman 1 o muchos valores

    print("2.2.5 Preparando opiniones...")
    # Elimino fecha de emision al final de la opinion (por ej, "Hace x meses")
    df_opiniones = clean_data.correct_opinion_column(df_opiniones)

    # Limpio las opiniones
    df_opiniones_tokenizado, df_opiniones['content'] = clean_data.text_preparation(df_opiniones['content'])  # si el df_cleaned no lo uso para los modelos pues no mejoran el sentiment, entonces no lo uso...
    df_opiniones.dropna()  # borra las pocas filas que no tienen title. Al remover palabras innecesarias quedo al menos 1 opinion vacia...
    # df_opiniones.to_excel('/Users/nachomondino/Desktop/df_opiniones_cleaned.xlsx', 'Hoja de datos', index=False)
    df_opiniones.to_excel('/Users/nachomondino/Desktop/df_opiniones_menos_cleaned.xlsx', 'Hoja de datos', index=False)

    '''
    print(" +++++++++++++++++++ (2.3) CONSTRUCT DATA  +++++++++++++++++++ ")
    # Defino customer needs (ngrams = 3) y relevant words para el sentiment (ngrams=1)
    attr_name_words = construct_data.get_attributes_name_words(df_modelos)  # TENGO QUE TERMINAR DE DESARROLLAR LAS FUNCIONES
    possible_costumer_needs = construct_data.define_possible_customer_needs(df_opiniones_tokenizado)
    customer_needs, customer_needs_one_word = construct_data.select_customer_needs(possible_costumer_needs, attr_name_words)

    print(" ------------------- (3) ATRIBUCION  ------------------- ")
    df_sent = sentiment_atribution_primer_intento.to_customer_needs(df_opiniones, customer_needs_one_word)

    # relation_matrix = atribucion.create_relation_matrix(producto.atributos, customer_needs_one_word) # ahorra es sin producto.atributos
    relation_matrix = sentiment_atribution_primer_intento.create_relation_matrix(df_modelos.columns[1:], customer_needs_one_word)  # incluyo el precio
    relation_matrix.to_excel('/Users/nachomondino/Desktop/relation_matrix.xlsx', 'Hoja de datos', index=False)
    # GoogleDrive.subir_archivo('/Users/nachomondino/Desktop/relation_matrix.xlsx', '1Y1DiQFQ5sQi-uod2uQ61Dmenh3GPNO3p')

    df_sent_por_valor = sentiment_atribution_primer_intento.to_attribute_value(df_modelos, df_sent, relation_matrix)
    df_sent_por_valor.to_excel('/Users/nachomondino/Desktop/df_final.xlsx', 'Hoja de datos', index=False)
    # GoogleDrive.subir_archivo('/Users/nachomondino/Desktop/df_final.xlsx','1Y1DiQFQ5sQi-uod2uQ61Dmenh3GPNO3p')


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
