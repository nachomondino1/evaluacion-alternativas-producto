from google.cloud import language_v1
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/meli-project-347018-2d3b34b14be4.json"

def sample_analyze_entity_sentiment(text_content):
    """
    Analyzing Entity Sentiment in a String

    Args:
      text_content The text content to analyze
    """
    data = {}

    client = language_v1.LanguageServiceClient()

    # Available types: PLAIN_TEXT, HTML
    type_ = language_v1.types.Document.Type.PLAIN_TEXT

    # Optional. If not specified, the language is automatically detected.
    # For list of supported languages: https://cloud.google.com/natural-language/docs/languages
    language = "es"
    document = {"content": text_content, "type_": type_, "language": language}

    # Available values: NONE, UTF8, UTF16, UTF32
    encoding_type = language_v1.EncodingType.UTF8

    response = client.analyze_entity_sentiment(request = {'document': document, 'encoding_type': encoding_type})
    # Loop through entitites returned from the API
    for entity in response.entities:  #para no modificar el codigo, podria devolver diccionario con entities como key y lista de mag, score y salience de values
        print(u"Representative name for the entity: {}".format(entity.name))
        # Get entity type, e.g. PERSON, LOCATION, ADDRESS, NUMBER, et al
        print(u"Entity type: {}".format(language_v1.Entity.Type(entity.type_).name))
        # Get the salience score associated with the entity in the [0, 1.0] range
        print(u"Salience score: {}".format(entity.salience))
        # Get the aggregate sentiment expressed for this entity in the provided document.
        sentiment = entity.sentiment
        print(u"Entity sentiment score: {}".format(sentiment.score))
        print(u"Entity sentiment magnitude: {}".format(sentiment.magnitude))
        # Loop over the metadata associated with entity. For many known entities,
        # the metadata is a Wikipedia URL (wikipedia_url) and Knowledge Graph MID (mid).
        # Some entity types may have additional metadata, e.g. ADDRESS entities
        # may have metadata for the address street_name, postal_code, et al.
        for metadata_name, metadata_value in entity.metadata.items():
            print(u"{} = {}".format(metadata_name, metadata_value))

        # Loop over the mentions of this entity in the input document.
        # The API currently supports proper noun mentions.
        for mention in entity.mentions:
            print(u"Mention text: {}".format(mention.text.content))
            # Get the mention type, e.g. PROPER for proper noun
            print(
                u"Mention type: {}".format(language_v1.EntityMention.Type(mention.type_).name)
            )

        data[entity.name] = [entity.salience, sentiment.score, sentiment.magnitude]

    # Get the language of the text, which will be the same as
    # the language specified in the request or, if not specified,
    # the automatically-detected language.
    print(u"Language of the text: {}".format(response.language))
    return data

# sample_analyze_entity_sentiment(text_content = 'Grapes are good. Bananas are bad.')
# sample_analyze_entity_sentiment(text_content = 'Uvas son buenas. Bananas son malas.')
# sample_analyze_entity_sentiment("Excelente el telefono samsung z flip 3. Es practico elegante , distinguido. Muy funcional. Solo la bateria no es de larga duracion. A mi no me afecta porque lo uso muy poco. Lo cargo cada 48 hs. Feliz con este equipo.")
# sample_analyze_entity_sentiment("Los puntos buenos primero, es rapido, la bateria dura casi 2 dias y se carga super rapido, en menos de 1 hora tenes carga completa. No tiene mas los botones en la pantalla pero los podes poner. La pantalla tiene colores muy nitidos. Podes elegir el estilo de los accesos a las app y el tipo de letra. Para mejorar la camara, no es muy estable. Todos los motorolas guardan las fotos en google fotos y a mi no me parece comodo.Hace 3 meses")
# sample_analyze_entity_sentiment(" Muy bueno. Lo único malo: la batería (no es la peor pero comparándola con los que le compiten se queda corto), es entendible ya que sino el precio sería distinto. El celu funciona barbaro, el display es hermoso, por ahora llevo 1 semana y todo bien, hay que ver con el tiempo. El tema de abrir y cerrarlo ni se preocupen que le pueden meter bomba tranqui")
# sample_analyze_entity_sentiment("En general el teléfono está bien buena camara. Buenos vídeos. Pero no se si es el sistema operativo. Que en algunas cosas es muy lento. Vengo de un iphone 8 y es más rápido en cosas sencillas. Cargar descargar videos. Pasar archivos. Cargar páginas. No se cuelga. Eso extraño del iphone por el resto esta bien. Y el teclado no es muy bueno le falta un poco pulir supongo. Pero dentro de todo esta bien")
# sample_analyze_entity_sentiment("Le doy 5 estrellas porque cumple para lo que uno lo compro. Economico y anda muy bien, recomendado para personas mayores y niños. Si pretenden mas de este celu, no sean ratas y compren algo mas caro.")
print(sample_analyze_entity_sentiment("Me parece un buen teléfono , es muy liviano es simple pero bueno, lo recomiendo para gente que quiera algo básico o para chicos yo se los compré a mis hijos y la verdad funciona bastante bien. Lo que si apesar de ser kodak lo único que tiene es que las cámaras no son guau!! pero para su precio me parece muy bueno."))
print(sample_analyze_entity_sentiment("parece buen telefono liviano simple bueno recomiendo gente quiera basico chicos compre hijos verdad funciona bien apesar ser kodak unico tiene camaras guau precio parece bueno"))