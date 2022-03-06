import pandas as pd
import requests


class MercadoLibreApi():

    def __init__(self):
        pass


    def getCategoriasID(self):
        df = pd.DataFrame(columns=['id_categoria', 'categoria','id_subcategoria','subcategoria'])
        url = "https://api.mercadolibre.com/sites/MLA/categories"
        categorias = requests.get(url)

        # Convierto variable r de Bytes a JSON para facilitar operacion
        categorias = categorias.json()

        # Recorro cada categoria
        for categoria in categorias:
            id_categoria = categoria['id']

            # Busco children categories
            url =  "https://api.mercadolibre.com/categories/" + id_categoria
            subcategorias = requests.get(url)

            # Convierto variable r de Bytes a JSON para facilitar operacion
            subcategorias = subcategorias.json()

            for subcategoria in subcategorias['children_categories']:
                df =  df.append({'id_categoria': categoria['id'], 'categoria': categoria['name'],'id_subcategoria': subcategoria['id'], 'subcategoria':subcategoria['name']}, ignore_index=True)

        # Creo archivo de excel para verificar que este bien el dataframe
        # df.to_excel('/Users/nachomondino/Desktop/categorias.xlsx', 'Hoja de datos', index=False)
        return df


    def getAtributosCategoria(self, id_categoria):
        """
        Atributos obligatorios
        Consultando el recurso /categories/$CATEGORY_ID/technical_specs/input podrás saber cuáles son los atributos obligatorios
        por categoría y completarlos con anticipación para evitar que las publicaciones se vean afectadas en el posicionamiento
        de los listados. Podrás identificar los atributos que serán obligatorios con el tag "required".
        """
        # Defino lista donde guardare los atributos de los productos de la categoria
        atributos = []

        # Defino manualmente los atributos no obligatorios y de relevancia 2 o 3 pero que me interesan
        atrib_relevantes = {'MLA1055':['Tamaño de la pantalla','Linea', 'Tipo de resolución de la pantalla','Capacidad de la batería',
                                       'Modelo del procesador','Cantidad de núcleos del procesador', 'Resolución de las cámaras traseras',
                                       'Resolución de las cámaras frontales']}

        # Defino manualmente los atributos no obligatorios de relevancia 1 que no me interesan.
        # Primero, los generales a la mayoria de las categorias.
        atrib_irrelevantes1_grales = ['Altura del paquete', 'Ancho del paquete', 'Largo del paquete', 'Peso del paquete', 'Código universal de producto', 'Unidades por envase',
                                      'SKU']
        # Segundo, los especificos por categoria.
        atrib_irrelevantes1_espec = {'MLA1055':['Sello SEC', 'Homologación Anatel Nº', 'Modelo detallado', 'IMEI', 'Compañía telefónica'],
                                     'MLA393366':['Número de legajo resolución 155/98']}

        # Esto despues lo borro es para ver los atributos que no tengo en cuenta por categoria
        atributos_desechados = []

        # Creo url con la categoria del producto Ej de url: "https://api.mercadolibre.com/categories/MLA1002/technical_specs/input"
        url = "https://api.mercadolibre.com/categories/" + id_categoria + "/technical_specs/input"
        r = requests.get(url)
        # print(r.content)

        # Convierto variable r de Bytes a JSON para facilitar operacion
        r = r.json()

        for element in r['groups']:
            for componente in element['components']:
                atributo_info = componente['attributes'][0] #pongo el [0] pues el['attributes'] es una lista de 1 elemento que contiene un dictionary
                #print(atributo)

                # Me fijo si el atributo es obligatorio pues en ese caso tiene "required" en tags --> HAY SUBCATEGORIAS QUE NO TIENEN CAMPOS OBLIGATORIOS :(
                if ("required" in atributo_info['tags']) and (atributo_info['name'] not in atrib_irrelevantes1_grales) and (atributo_info['name'] not in atrib_irrelevantes1_espec[id_categoria]):
                    # print("Obligatorio", atributo['name'])
                    atributos.append(atributo_info['name'])

                # Si los atributos obligatorios son pocos (para mi son pocos y faltan relevantes) puedo obtener segun el campo "relevance"
                # SERA DIFICIL IMPLEMENTAR MAS ATRIBUTOS...
                elif (atributo_info['relevance'] == 1) and (atributo_info['name'] not in atrib_irrelevantes1_grales) and (atributo_info['name'] not in atrib_irrelevantes1_espec[id_categoria]):
                    atributos.append(atributo_info['name'])

                else:
                    atributos_desechados.append(atributo_info['name'])

        # Agrego atributos de relevancia ≠ 1 pero que me interesan
        for atributos_relevantes in atrib_relevantes[id_categoria]:
            atributos.append(atributos_relevantes)

        # print(atributos)
        # print(atributos_desechados)
        return atributos

'''
                else:
                    if atributo['relevance'] == 3:
                        try:
                            print("RELEVANCIA 3:",atributo['name'],atributo['values'])
                        except:
                            print("RELEVANCIA 3:",atributo['name'])
    
                    elif atributo['relevance'] == 2:
                        try:
                            print("RELEVANCIA 2:", atributo['name'], atributo['values'])
                        except:
                            print("RELEVANCIA 2:", atributo['name'])
    
                    else:
                        try:
                            print("RELEVANCIA 1:", atributo['name'], atributo['values'])
                        except:
                            print("RELEVANCIA 1:", atributo['name'])
'''


''' EN DESUSO PORQUE HAY LIMITE DE EXTRACCION DE DATOS EN AMBOS CASES
    def getProductsCategory(self, id_categoria):
        url = "https://api.mercadolibre.com/sites/MLA/search?category=" + id_categoria
        r = requests.get(url)

        # Convierto variable r de Bytes a JSON para facilitar operacion
        r = r.json()

        r = r['results']
        i = 0
        for producto in r:
            i +=1
            #print(producto['id'])
            #print(producto['title'])
            #print(producto['attributes'])
        print(i)

        return r


    def getOpinions(self, id_publicacion):
        # Obtengo las opiniones de un producto
        url = "https://api.mercadolibre.com/reviews/item/" + id_publicacion
        r = requests.get(url)

        # Convierto variable r de Bytes a JSON para facilitar operacion
        r = r.json()

        # Se puede ver el total de opiniones de la publicacion y el limite de 5
        print(r)

        # Imprimo cada opinion
        for opinion in r["reviews"]:
            print(opinion)


        # curl -X GET  -H 'Authorization: Bearer $ACCESS_TOKEN' https://api.mercadolibre.com/categories/$CATEGORY_ID/technical_specs/input
'''


