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

        # Defino manualmente los atributos (generales a la mayoria de las categorias) de relevancia 1 que no me interesan.
        attr_rel1_remove = ['Altura del paquete', 'Ancho del paquete', 'Largo del paquete','Peso del paquete', 'Código universal de producto', 'Unidades por envase', 'SKU']

        # Por categoria, defino manualmente los atributos de relevancia 1 que no me interesan
        attr_xcat_rel1_remove = {'MLA1055':['Sello SEC', 'Homologación Anatel Nº', 'Modelo detallado', 'IMEI', 'Compañía telefónica'],
                                 'MLA393366':['Número de legajo resolución 155/98']}

        # Por categoria, defino manualmente los atributos de relevancia 2 o 3 (no los incluidos por default) pero que me interesan
        attr_xcat_rel2y3_add = {'MLA1055': ['Tamaño de la pantalla', 'Tipo de resolución de la pantalla', 'Capacidad de la batería', 'Modelo del procesador', 'Cantidad de núcleos del procesador', 'Resolución de las cámaras traseras', 'Resolución de las cámaras frontales']}

        #  Por categoria, defino manualmente los atributos que la API NO TE TRAE cuando llamas a atributos y se encuentra dentro de "otras caracteristicas en las publicaciones
        attr_xcat_add = {'MLA1338': ['Tipo de mancuerna', 'Peso', 'Recubrimiento de la mancuerna', 'Material de recubrimiento de la mancuerna', 'Forma de la mancuerna', 'Material de la mancuerna', 'Largo', 'Diámetro de la barra', 'Cromado', 'Mango ergonómico', 'Identificador de Peso', 'Antideslizante', 'Es ajustable']}

        # Esto despues lo borro es para ver los atributos que no tengo en cuenta por categoria
        atributos_desechados = []

        # Creo url con la categoria del producto Ej de url: "https://api.mercadolibre.com/categories/MLA1002/technical_specs/input"
        url = "https://api.mercadolibre.com/categories/" + id_categoria + "/technical_specs/input"
        r = requests.get(url)
        # print(r.content)

        # Convierto variable r de Bytes a JSON para facilitar operacion
        r = r.json()

        for element in r['groups']:

            # Recorro cada atributo, y en particular, toda la informacion relacionado a cada uno.
            for componente in element['components']:
                atributo_info = componente['attributes'][0] #pongo el [0] pues el['attributes'] es una lista de 1 elemento que contiene un dictionary
                # print(atributo_info['name'])

                # Si el atributo es obligatorio o de relevancia 1
                if ("required" in atributo_info['tags']) or (atributo_info['relevance'] == 1):
                    # print('Atributo es de relevancia 1',end = '')

                    # y si no es de los atributos generales que no me interesan
                    if atributo_info['name'] not in attr_rel1_remove:
                        # print('Atributo es de relevancia 1 y me interesa',end = '')

                        #  ni de los especificos de la categoria que no me interesan
                        if id_categoria in attr_xcat_rel1_remove.keys():
                            if atributo_info['name'] not in attr_xcat_rel1_remove[id_categoria]:
                                # print('Atributo es de relevancia 1 y me interesa x2',end = '')
                                atributos.append(atributo_info['name'])
                        else:
                            atributos.append(atributo_info['name'])

                # Si el atributo es de relevancia 2 o 3
                else:
                    try:
                        # y si es de los que me interesa
                        if atributo_info['name'] in attr_xcat_rel2y3_add[id_categoria]:
                            atributos.append(atributo_info['name'])
                            # print('Atributo es de relevancia 2/3 y me interesa',end = '')

                    except:
                        pass
                #print()

        # Agrego atributos que me interesan y la API no te los devuelve (ni como relevancia 1, ni 2, ni 3)
        if id_categoria in attr_xcat_add.keys():
            for atributo in attr_xcat_add[id_categoria]:
                atributos.append(atributo)

        return atributos


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


