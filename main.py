""" ex proceesamiento.py
Pseudocodigo de lo que quisiera que haga:
# Para una búsqueda de muchas búsquedas: # que busquedas? Podria guardar una lista de los 20/30 productos mas demandados por los clientes y tener esos datos ya preparados. El resto de las busquedas se podrian hacer en el momento llamando a main_collect_data.py y le podria mostrar un relojito al cliente porque va a tardar.
    1.- Extrae los datos mediante web scraping para esa busqueda o los busca (uso directorio de web scraping)
        1.1.-Busca atributos (pues necesito saber a que atributos debo extraerle su valor en cada publicacion.
    2.- Limpio el texto (uso directorio de text mining)
        2.1 Extrae Customer needs (a partir de analisis de opiniones)
    3. Me pide matriz de relaciones
    4. Sentiment Analysis
    (necesito matriz de relaciones si o si para linkear el sentiment de las customer needs a cada valor de cada atributo).
    Por ej, si una opinion dice que el celular le dura
    todo el dia entonces se relacion con la bateria y el tamaño de pantalla del celular (en menor medida) y le debere
    asignar ese sentiment al valor en particular que toma la bateria y el que toma el tamaño de pantalla. Si por ejemplo,
    “el celular le dura todo el dia” tiene un sentiment de 4.3, y el celularr tiene bateria de 4500 mAh y tamaño de pantalla de 5’’
    entonces le asigno 4.3 a bateria = 4500 mAh y 4.3 a tamaño de pantalla = 5’’ (tendria que ver de agregar la influencia de la relacion entre customer need y
    atributo pues tamaño de pantalla tiene menos relacion con  “el celular le dura tod@ el dia” que el atributo bateria por lo que, no deberian tener 4,3 los dos..)
"""
# Importo Librerias
import data_understanding.collect_data.dataframe_creator
import pandas as pd
from data_understanding.collect_data import main_collect_data, dataframe_creator, mercadolibre_crawler
from data_preparation import format_data, clean_data, construct_data
from modelling import sentiment_atribution

def main():
    '''
    # 1) EXTRACCION DE DATOS
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

    # 2) DATA PREPARATION
    print(" ------------------- (2) DATA PREPARATION  ------------------- \n")

    # 2.1 FORMAT DATA
    print(" +++++++++++++++++++ (2.1) FORMAT DATA  +++++++++++++++++++ ", end="\n")
    print("2.1.1 Convirtiendo columnas de strings con numeros a columnas numericas...")
    df_modelos = format_data.string_column_to_numeric_column(df_modelos)

    # 2.1.2 "YES" AND "NO" COLUMNS TO 1 AND 0 COLUMNS
    print("2.1.2 Convirtiendo columnas si-no a columnas 1-0... ")
    df_modelos = format_data.yes_no_column_to_ones_ceros_column(df_modelos)

    # 2.1.3 CORRECTION OF PRICE COLUMN
    print("2.1.3 Corrigiendo columna precio...")
    df_modelos['precio'] = format_data.correct_price_column(df_modelos['precio'])

    # 2.2 CLEAN DATA
    print(" +++++++++++++++++++ (2.2) CLEAN DATA  +++++++++++++++++++ ")
    # 2.2.1 ELIMINO NONE VALUES
    print("2.2.1 Eliminando none values...")
    df_opiniones.dropna()  # borra las pocas filas que no tienen title

    # 2.2.2 ELIMINO FILAS REPETIDAS --> ojo que tiene que ser sin id...
    print("2.2.2 Eliminando filas repetidas...")
    df_opiniones = df_opiniones.drop(clean_data.delete_repeated_rows(df_opiniones['content']))  # elimino duplicados teniendo en cuenta solo la columna content que es la que contiene opiniones propiamente

    #  2.2.3 CATEGORIZO VARIABLES NUMERICAS
    print("2.2.3 Categorizando campos numericos continuos...")
    df_modelos.iloc[:, 1:] = clean_data.categorize_numeric_columns(df_modelos.iloc[:, 1:])  # categorizo columnas numericas con valores continuos, no le paso columna id pues la categorizaria.

    #  2.2.4 ELIMINO CAMPOS ESPECIFICOS SEGUN CANTIDAD DE VALORES Y CANTIDAD DE OPINIONES POR VALOR
    print("2.2.4 Eliminando campos constantes y campos continuos...")
    df_modelos = clean_data.delete_attr_x_values(df_modelos)  # elimino columnas que toman 1 o muchos valores

    #  2.2.5 PREPARACION DE OPINIONES
    print("2.2.5 Preparando opiniones...")
    # Elimino fecha de emision al final de la opinion (por ej, "Hace x meses")
    df_opiniones = clean_data.correct_opinion_column(df_opiniones)

    # Limpio las opiniones
    df_opiniones_tokenizado, df_opiniones['content'] = clean_data.text_preparation(df_opiniones['content'])  # si el df_cleaned no lo uso para los modelos pues no mejoran el sentiment, entonces no lo uso...
    df_opiniones.dropna()  # borra las pocas filas que no tienen title. Al remover palabras innecesarias quedo al menos 1 opinion vacia...
    df_opiniones.to_excel('/Users/nachomondino/Desktop/df_opiniones_cleaned.xlsx', 'Hoja de datos', index=False)

    # 2.3 CONSTRUCT DATA
    print(" +++++++++++++++++++ (2.3) CONSTRUCT DATA  +++++++++++++++++++ ")
    # Defino customer needs (ngrams = 3) y relevant words para el sentiment (ngrams=1)
    attr_name_words = construct_data.get_attributes_name_words(df_modelos)  # TENGO QUE TERMINAR DE DESARROLLAR LAS FUNCIONES
    possible_costumer_needs = construct_data.define_possible_customer_needs(df_opiniones_tokenizado)
    customer_needs, customer_needs_one_word = construct_data.select_customer_needs(possible_costumer_needs, attr_name_words)

    # 3) ATRIBUCION (sentiment de opinion a cada valor de cada campo especifico)
    print(" ------------------- (3) ATRIBUCION  ------------------- ")
    df_sent = sentiment_atribution.to_customer_needs(df_opiniones, customer_needs_one_word)
    # relation_matrix = atribucion.create_relation_matrix(producto.atributos, customer_needs_one_word) # ahorra es sin producto.atributos
    relation_matrix = sentiment_atribution.create_relation_matrix(df_modelos.columns[1:], customer_needs_one_word)  # incluyo el precio
    df_sent_por_valor = sentiment_atribution.to_attribute_value(df_modelos, df_sent, relation_matrix)
    df_sent_por_valor.to_excel('/Users/nachomondino/Desktop/df_final.xlsx', 'Hoja de datos', index=False)

    # GUARDO RESULTADOS EN MY SQL?

if __name__ == '__main__':
    main()




''' EN EXTRACCION DE DATOS AL PPIO: hacerr lista de productos a relevar me pareece muy largo y hay mucha prob de falla
# Defino productos para los cuales hacer el relevamiento
# lista_prod = ['auriculares', 'azúcar', 'fundas de celular', 'crema facial', 'suplementos', 'celulares', 'TV', 'smartband', 'notebook']
# lista_prod = ["tv"]

# Por producto de la lista de productos
for producto in lista_prod:
    ...
'''