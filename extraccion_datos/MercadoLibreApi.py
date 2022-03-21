import pandas as pd
import requests


class MercadoLibreApi():

    def __init__(self):
        pass


    def getCategoriasID(self):
        """
        Obtengo informacion de cada categoria de productos de mercado libre, su id y sus subcategorias con sus
        respectivos id. Utilizo la API de Mercado Libre.
        :return: DataFrame con 4 columnas: id de la categoria, nombre de la categoria, id de la subcategoria y
        nombre de la subcategoria
        """
        # Creo el DataFrame en el que guardare la informacion sobre las categorias
        df = pd.DataFrame(columns=['id_categoria', 'nombre_categoria', 'id_subcategoria', 'nombre_subcategoria'])

        # Hago un GET pidiendo informacion sobre las categorias de los productos a la API de Mercado Libre
        url = "https://api.mercadolibre.com/sites/MLA/categories"
        categorias = requests.get(url)

        # Para facilitar operacion, transformo el type de la variable "categorias", de Bytes a JSON.
        categorias = categorias.json()

        # Recorro cada categoria de las categorias
        for categoria in categorias:
            id_categoria = categoria['id']

            # Con el id de una categoria, hago un GET pidiendo informacion sobre sus subcategorias de productos a la API de Mercado Libre
            url =  "https://api.mercadolibre.com/categories/" + id_categoria
            subcategorias = requests.get(url)

            # Para facilitar operacion, transformo el type de la variable "subcategorias", de Bytes a JSON.
            subcategorias = subcategorias.json()

            # Recorro cada subcategoria de las subcategorias dentro de una categoria
            for subcategoria in subcategorias['children_categories']:

                # Guardo informacion de la subcategoria en particular y de la categoria a la que pertenece
                df = df.append({'id_categoria': categoria['id'], 'nombre_categoria': categoria['name'],'id_subcategoria': subcategoria['id'], 'nombre_subcategoria':subcategoria['name']}, ignore_index=True)

        # Creo archivo de excel para verificar que este bien el dataframe
        # df.to_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/extraccion_datos/df_categorias.xlsx','Hoja de datos', index=False)
        return df


    def getAtributosSubcategoria(self, id_subcat):
        """
        Obtengo atributos de una subcategoria de productos de Mercado Libre. Utilizo la API de Mercado Libre. Luego,
        selecciono los atributos que mas me interesan para dicha subcategoria.

        :param id_subcat: id de una subcategoria de productos de Mercado Libre
        :return: Lista de atributos interesantes para la subcategoria
        """
        # Defino lista donde guardare los atributos de los productos de la subcategoria
        atributos = []

        # Defino manualmente los atributos (generales a la mayoria de las categorias) de relevancia 1 que no me interesan.
        attr_rel1_remove = ['Altura del paquete', 'Ancho del paquete', 'Largo del paquete', 'Peso del paquete',
                            'Código universal de producto', 'Unidades por envase', 'SKU',
                            'Número de registro/certificación INMETRO']

        # Por categoria, defino manualmente los atributos de relevancia 1 que no me interesan
        attr_xcat_rel1_remove = {
            'MLA1055': ['Sello SEC', 'Homologación Anatel Nº', 'Modelo detallado', 'IMEI', 'Compañía telefónica'],
            'MLA393366': ['Número de legajo resolución 155/98']}

        # Por categoria, defino manualmente los atributos de relevancia 2 o 3 (no los incluidos por default) pero que me interesan
        attr_xcat_rel2y3_add = {
            'MLA1055': ['Tamaño de la pantalla', 'Tipo de resolución de la pantalla', 'Capacidad de la batería',
                        'Modelo del procesador', 'Cantidad de núcleos del procesador',
                        'Resolución de las cámaras traseras', 'Resolución de las cámaras frontales']}

        # Hago un GET pidiendo informacion sobre los atributos de una subcategoria a la API de Mercado Libre
        url = "https://api.mercadolibre.com/categories/" + id_subcat + "/technical_specs/input"
        r = requests.get(url)

        # Convierto variable r de Bytes a JSON para facilitar operacion
        r = r.json()

        try:
            for element in r['groups']:

                # Recorro cada atributo
                for componente in element['components']:

                    # Accedo a clave "attributes" donde tenemos mas informacion sobre el atributo. El [0] es porque
                    # llamativamente el diccionario resultante esta dentro de una lista
                    atributo_info = componente['attributes'][0]
                    # print(atributo_info['name'])

                    # Si el atributo es obligatorio o de relevancia 1
                    if ("required" in atributo_info['tags']) or (atributo_info['relevance'] == 1):
                        # print('Atributo es de relevancia 1',end = '')

                        # y si no es de los atributos generales que no me interesan
                        if atributo_info['name'] not in attr_rel1_remove:
                            #print('Atributo es de relevancia 1 y me interesa', end='')

                            #  ni de los especificos de la categoria que no me interesan
                            if id_subcat in attr_xcat_rel1_remove.keys():
                                if atributo_info['name'] not in attr_xcat_rel1_remove[id_subcat]:
                                    # entonces lo guardo
                                    #print(atributo_info['name'])
                                    atributos.append(atributo_info['name'])
                            else:
                                # entonces lo guardo
                                atributos.append(atributo_info['name'])

                    # Si el atributo es de relevancia 2 o 3
                    else:
                        try:
                            # y si es de los que me interesa
                            if atributo_info['name'] in attr_xcat_rel2y3_add[id_subcat]:
                                atributos.append(atributo_info['name'])
                                #print('Atributo es de relevancia 2/3 y me interesa',end = '')

                        except:
                            pass
        except:
            # 24 de las mas de 400 subcategorias no tienen atributos
            print("Fallo la busqueda de atributos para la categoria", id_subcat)
            atributos = []

        return atributos


    def getProductsCategory(self, id_categoria):
        """ EN DESUSO PORQUE HAY LIMITE DE EXTRACCION DE DATOS  """
        """ Extraeria los productos dentro de una categoria"""

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
        """ EN DESUSO PORQUE HAY LIMITE DE EXTRACCION DE DATOS  """

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


