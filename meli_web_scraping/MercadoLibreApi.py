import pandas as pd
import requests


class MercadoLibreApi():

    def __init__(self):
        pass


    def getIdCategorias(self):
        df = pd.DataFrame(columns=['id_categoria', 'categoria','id_subcategoria','subcategoria'])
        url = "https://api.mercadolibre.com/sites/MLA/categories"
        categorias = requests.get(url)

        # Convierto variable r de Bytes a JSON para facilitar operacion
        categorias = categorias.json()

        # Recorro cada categoria
        for categoria in categorias:

            # df = df.append({'id': categoria['id'], 'name': categoria['name']}, ignore_index=True)
            id_categoria = categoria['id']
            name_categoria = categoria['name']

            # Busco children categories
            url =  "https://api.mercadolibre.com/categories/" + id_categoria
            subcategorias = requests.get(url)

            # Convierto variable r de Bytes a JSON para facilitar operacion
            subcategorias = subcategorias.json()

            for subcategoria in subcategorias['children_categories']:
                df =  df.append({'id_categoria': categoria['id'], 'categoria': categoria['name'],'id_subcategoria': subcategoria['id'], 'subcategoria':subcategoria['name']}, ignore_index=True)

        df.to_excel('/Users/nachomondino/Desktop/categorias.xlsx', 'Hoja de datos', index=False)
        return df


    def getAtributosObligatorios(self, id_categoria):
        """
        Atributos obligatorios
        Consultando el recurso /categories/$CATEGORY_ID/technical_specs/input podrás saber cuáles son los atributos obligatorios
        por categoría y completarlos con anticipación para evitar que las publicaciones se vean afectadas en el posicionamiento
        de los listados. Podrás identificar los atributos que serán obligatorios con el tag "required".
        """
        # Creo url con la categoria del producto Ej de url: "https://api.mercadolibre.com/categories/MLA1002/technical_specs/input"
        url = "https://api.mercadolibre.com/categories/" + id_categoria + "/technical_specs/input"
        r = requests.get(url)
        # print(r.content)

        # Convierto variable r de Bytes a JSON para facilitar operacion
        r = r.json()

        for element in r['groups']:
            for el in element['components']:
                atributo = el['attributes'][0] #pongo el [0] pues el['attributes'] es una lista de 1 elemento que contiene un dictionary
                #print(atributo)

                # Me fijo si el atributo es obligatorio pues en ese caso tiene "required" en tags --> HAY SUBCATEGORIAS QUE NO TIENEN CAMPOS OBLIGATORIOS :(
                if "required" in atributo['tags']:
                    print("Obligatorio", atributo['name'])

                # Si los atributos obligatorios son pocos (para mi son pocos y faltan relevantes) puedo obtener segun el campo "relevance"
                # SERA DIFICIL IMPLEMENTAR MAS ATRIBUTOS...
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


                    #id = atributo['id']
                    #print(id)
            # print(element)


        # implementar obtencion de atributos oblitorios


    def getOpinions():
        # Obtengo las opiniones de un producto
        r = requests.get("https://api.mercadolibre.com/reviews/item/MLA813473400")
        print(r.content)

        # Convierto variable r de Bytes a JSON para facilitar operacion
        r = r.json()
        # print(type(r))
        # print(r["reviews"])
        # print(type(r["reviews"]))

        # Imprimo cada opinion
        for element in r["reviews"]:
            print(element)

        # print(r["reviews"][0])
        # print(type(r["reviews"][0]))


        # curl -X GET  -H 'Authorization: Bearer $ACCESS_TOKEN' https://api.mercadolibre.com/categories/$CATEGORY_ID/technical_specs/input

        """
        1er intento: LIBRERIA REQUESTS
        # Obtengo las opiniones de un producto
        r = requests.get("https://api.mercadolibre.com/reviews/item/MLA813473400")
        print(r.content)
        
        # Convierto variable r de Bytes a JSON para facilitar operacion
        r = r.json()
        # print(type(r))
        #print(r["reviews"])
        #print(type(r["reviews"]))
        
        # Imprimo cada opinion
        for element in r["reviews"]:
        print(element)
        
        # print(r["reviews"][0])
        # print(type(r["reviews"][0]))
        
        
        # 2DO intento: LIBRERIA PYCURL
        # importo libreria
        import pycurl
        from io import BytesIO
        
        b_obj = BytesIO()
        crl = pycurl.Curl()
        
        # Set URL value
        crl.setopt(crl.URL, 'https://api.mercadolibre.com/reviews/item/MLA813473400')
        
        # Write bytes that are utf-8 encoded
        crl.setopt(crl.WRITEDATA, b_obj)
        
        # Perform a file transfer
        crl.perform()
        
        # End curl session
        crl.close()
        
        # Get the content stored in the BytesIO object (in byte characters)
        get_body = b_obj.getvalue()
        
        # Decode the bytes stored in get_body to HTML and print the result
        print('Output of GET request:\n%s' % get_body.decode('utf8'))
        
        # curl -X GET -H 'Authorization: Bearer $ACCESS_TOKEN' https://api.mercadolibre.com/reviews/item/MLA813473400
        """




