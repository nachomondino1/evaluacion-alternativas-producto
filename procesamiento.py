"""
Pseudocodigo de lo que quisiera que haga:
# Para una búsqueda de muchas búsquedas: # que busquedas? Podria guardar una lista de los 20/30 productos mas demandados por los clientes y tener esos datos ya preparados. El resto de las busquedas se podrian hacer en el momento llamando a main.py y le podria mostrar un relojito al cliente porque va a tardar.
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
from meli_web_scraping.MercadoLibreApi import MercadoLibreApi


# 1.- Extrae los datos mediante web scraping para esa busqueda o los busca (uso directorio de web scraping)
# 1.1.- Busca atributos
extractor = MercadoLibreApi()

# # para la busqueda del usuario, extraer id_categoria (del link) y llamar a la siguiente funcion
# # Ejs de codigos: MLA1055 (para celulares) ; MLA1002 (no se de que es)
# # DOS ALTERNATIVAS: con API o con web Scraping...

extractor.getIdCategorias()

extractor.getAtributosObligatorios("MLA3502")



# 2.- Limpio el texto (uso directorio de text mining)


# 3. Me pide matriz de relaciones



# 4. Sentiment Analysis

