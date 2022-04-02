""" ex proceesamiento.py
Pseudocodigo de lo que quisiera que haga:
# Para una búsqueda de muchas búsquedas: # que busquedas? Podria guardar una lista de los 20/30 productos mas demandados por los clientes y tener esos datos ya preparados. El resto de las busquedas se podrian hacer en el momento llamando a data_extractor.py y le podria mostrar un relojito al cliente porque va a tardar.
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
    atributo pues tamaño de pantalla tiene menos relacion con  “el celular le dura todo el dia” que el atributo bateria por lo que, no deberian tener 4,3 los dos..)
"""

# Importo Librerias
from data_understanding.collect_data.mercadolibre_crawler import Product
from data_understanding.collect_data import dataframe_creator as df_creator
from data_understanding.collect_data.data_extractor import data_extractor
from data_preparation import clean_data
from data_preparation import preparacion_texto


def main():
    # 1) EXTRACCION DE DATOS
    # Defino productos para los cuales hacer el relevamiento
    # lista_prod = ['auriculares', 'azúcar', 'fundas de celular', 'crema facial', 'suplementos', 'celulares', 'TV', 'smartband', 'notebook']
    lista_prod = ["celulares"]

    # Por producto de la lista de productos
    for producto in lista_prod:

        # Creo objeto producto
        product = Product(producto)  # despues lo saco

        # Valido el producto buscado tal que no sea una busqueda tan amplia
        product.search_validation()

        # Obtengo atributos o caracteristicas mas relevantes del producto
        product.atributos = product.get_product_attributes()

        # En base al producto a buscar, creo los data
        df_opiniones = df_creator.create_opinions_dataframe()
        df_modelos = df_creator.create_models_dataframe(product.atributos)

        # Carga de datos a data
        df_opiniones, df_modelos = data_extractor(producto, df_opiniones, df_modelos)

        # Exporto data (podria ser por seguridad)
        # df_opiniones.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_opiniones_{}.xlsx'.format(producto.nombre), 'Hoja de datos', index=False)
        # df_modelos.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_modelos_{}.xlsx'.format(producto.nombre), 'Hoja de datos', index=False)


        # 2) PREPARACION DEL TEXTO (uso directorio de text mining)
        # Limpio el dataset de modelos
        clean_data.delete_attr_x_values(df_modelos)
        clean_data.delete_none_values(df_modelos)

        # Limpio el dataset de opiniones
        preparacion_texto(df_modelos)

        # establezco customer needs


        # 3) PIDE MATRIZ DE RELACIONES



        # 4) SENTIMENT ANALYSIS



        # GUARDO RESULTADOS EN MY SQL?


main()
