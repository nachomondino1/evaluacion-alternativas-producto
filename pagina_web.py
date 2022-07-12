# Importo librerias
import pandas as pd
import streamlit as st
from PIL import Image

def main():
    # (1) SOLICITO TIPO DE CLIENTE EN SIDEBAR (por default 'usuario final')
    st.sidebar.write('# Tipo de análisis')  # titulo 1 de sidebar
    l_client_options = ['Evaluacion de alternativas', 'Posicionamiento de marcas']  # Usuario define si es empresa o usuario final
    # client_help = "Si sos un consumidor final, como la gran mayoría, tu opcion es 'Usuario final'. Solo si sos empresario y queres conocer la posicion de tu empresa en el mercado, la opcion correcta es 'Empresa'"
    client = st.sidebar.radio(label='¿Que tipo de análisis hacer?', options=l_client_options)  # client = st.sidebar.selectbox('1) ¿Que tipo de cliente eres?', client_options)
    product_options = ['', 'Celulares', 'Smartband', 'TV']  # ['Auriculares', 'Celulares', 'Fundas de celular', 'Notebook', 'Smartband', 'Suplementos','Tablets', 'TV']  # Lista de productos

    # SI EL ANALISIS ES LA EVALUACION DE ALTERNATIVAS
    if client == 'Evaluacion de alternativas':
    # if client == 'Usuario final':

        st.header('EVALUACION DE ALTERNATIVAS')  # imprimo titulo  # # st.title('EVALUACION AUTOMATICA DE ALTERNATIVAS EN PROCESO DE COMPRA')
        # ESCRIBO INTRODUCCION AL PROBLEMA QUE RESUELVE LA HERRAMIENTA
        st.write("Antes de comprar cualquier producto que deseamos, solemos **evaluar las distintas alternativas** posibles. "
                 "Normalmente buscamos información en internet, por ejemplo, leemos opiniones, vemos videos que hagan "
                 "una reseña, entre otros.")

        image_1 = Image.open('./p5_deployment/utils/investigar_alternativas.jpeg') # Imagen de persona antes ≠ alternativas
        col1, col2, col3 = st.columns([0.2, 5, 0.2])
        col2.image(image_1, use_column_width=True)

        st.write("Hoy en día, cada vez hay mas alternativas lo que hace que la elección de una sola de ellas, sea un "
                 "proceso extramadamente desgastante. Es muy probable que consumamos mucho de nuestro valioso tiempo y "
                 "encima no terminemos escogiendo la alternativa ideal para nosotros.")

        image_2 = Image.open('./p5_deployment/utils/alternativas_posibles.png')
        col1, col2, col3 = st.columns([0.2, 5, 0.2])
        col2.image(image_2, use_column_width=True)

        st.write("Afortundamente, podrás facilitar este proceso utilizando la siguiente herramienta pensada para "
                 "encontrar **la mejor alternativa para vos** en solo 3 pasos")

        # (2) SOLICITO PRODUCTO
        st.write('### PASO 1 DE 3: ELEGI TU PRODUCTO')
        product = st.selectbox('¿Que producto desea evaluar?', product_options)  # product = st.sidebar.selectbox('2) ¿Que producto desea evaluar?', product_options)
        product = product.lower()

        # SI SELECCIONO UN PRODUCTO
        if product != '':
            # IMPORTO ARCHIVOS
            # Archivos de (2) Data preparation
            df_alt = pd.read_excel('./data/collect_initial_data/{}/df_alt.xlsx'.format(product))
            df_alt_cleaned = pd.read_excel('./data/data_preparation/{}/df_alt_cleaned.xlsx'.format(product))
            df_alt_to_client = df_alt[df_alt.id_alternativa.isin(df_alt_cleaned["id_alternativa"].unique())].reset_index(drop=True)  # Borro alternativas que elimine de analisis (ademas de no usarlas en analisis tampoco seran mostradas al cliente)
            df_cust_needs = pd.read_excel("./data/data_preparation/{}/df_cust_needs.xlsx".format(product), index_col=0)
            # Archivos de (3) Modelling
            df_attr_alt_sent = pd.read_excel('./data/modelling/atribucion/{}/df_attr_alt_sent.xlsx'.format(product))
            df_value_sent = pd.read_excel('./data/modelling/atribucion/{}/df_attr_values_sent.xlsx'.format(product))
            df_relation_matrix = pd.read_excel("./data/data_preparation/{}/df_relation_matrix.xlsx".format(product), index_col=0)

            # (3) SOLICITO PESOS DE LAS CUSTOMER NEEDS
            # Imprimo titulo
            st.write('### PASO 2 DE 3: IMPORTANCIA DE CADA NECESIDAD DEL CLIENTE'.format(product))
            st.write('Ya elegiste el producto! Estás en el paso 2 de 3, yo le diría a Usain Bolt que se empiece a preocupar!')
            st.write("Ahora, tenes que asignar que importancia tiene para vos, cada necesidad del cliente típica de {}. "
                     "Bueno, seguramente mas de uno se esta preguntando 'y como hago eso?' (tal vez usando alguna palabrita mas)".format(product))
            st.write("Es muy sencillo! A continuación, por cada necesidad del cliente habrá una barra donde podes elegir "
                     "la importancia que tiene ésta para vos")
            st.write("Una vez que hayas asignado lo importante para vos, clikea el boton 'Procesar' abajo de todo.")

            # Solicito pesos al cliente
            df_cust_needs_with_weight = set_customer_needs_weigths(df_cust_needs, product)

            # SI EL CLIENTE DA CLICK A BOTON "PROCESAR"
            if st.button('Procesar'):  # Para que no calcule tabla de recomendacion ante cada cambio de los pesos

                # (4) CALCULO IMPORTANCIA TECNICA DE CADA ATRIBUTO (SEGUN PESOS DE NECESIDADES DEL CLIENTE)
                d_attrs_tech_imp = get_attrs_technical_importance(df_cust_needs_with_weight, df_relation_matrix)
                # df_prueba = pd.DataFrame([[key, d_attrs_tech_imp[key]] for key in d_attrs_tech_imp.keys()], columns=['Atributo', 'Importancia'])
                # st.dataframe(df_prueba) # st.write("Verifico (3): ",d_attrs_tech_imp)

                # (5) CALCULO VALORACION FINAL DE CADA ALTERNATIVA
                df_alts_val_fin = get_alts_final_value(df_alt_cleaned, df_attr_alt_sent, df_value_sent, d_attrs_tech_imp)
                # st.write("Verifico (4): ", df_alts_val_fin)

                # (6) MUESTRO RESULTADOS
                # Tabla de recomendacion
                st.write('### PASO 3 DE 3: ELECCION DE ALTERNATIVA')
                st.write('Llegaste al último paso! Acá te presentamos las 10 alternativas que mejor se ajustan a lo que '
                         'buscas, solo tendrás que elegir una. Y quedate tranquil@, analizamos toooodas '
                         'las alternativas (¡Y si!... podes decir que lo hiciste todo vos!).')
                # st.write('Dada la importancia que le da a cada necesidad del cliente, buscamos las alternativas mas idoneas para vos')
                st.write('#### Las 10 alternativas que más te recomendamos')
                # Calculo porcentaje de recomendacion de cada alternativa
                df_alts_recommend = create_recomendation_table(df_alt_to_client, df_alts_val_fin)   # OJO! DF_ALT TIENE ALTS QUE DF_ALT_CLEANED NO Y POR ENDE EL INDICE ES ≠
                # Selecciono las 10 alternativas de mayor porcentaje de recomendacion
                df_top_ten = df_alts_recommend.iloc[0:10, 1:]  # df_top_ten = pd.DataFrame(columns=['Marca', "Modelo", "precio", 'porcentaje_recomendacion'])
                st.dataframe(df_top_ten)
                st.balloons()

                # Disclaimer de ultima actualizacion de datos (ppalmente por precio)
                st.write("*Fecha de ultima actualización de los datos: 29 de Junio de 2022*")

                # Listado de todas las alternativas tenidas en cuenta en el analisis
                with st.expander("Ver todas las alternativas tenidas en cuenta en el analisis"):
                    st.write("Acá, podras ver todas las alternativas con las que trabajó la herramienta, así, podes "
                             "verificar que no falta ninguna")
                    st.dataframe(df_alts_recommend.iloc[:, 1:])

    # SI EL ANALISIS ES EL POSICIONAMIENTO DE LA MARCA
    else:
        st.header('POSICIONAMIENTO DE MARCAS')  # imprimo titulo  # # st.title('EVALUACION AUTOMATICA DE ALTERNATIVAS EN PROCESO DE COMPRA')
        # ESCRIBO INTRODUCCION AL PROBLEMA QUE RESUELVE LA HERRAMIENTA
        st.write('La herramienta tiene como objetivo identificar el **posicionamiento en el mercado de las marcas de un '
                 'producto**. Al final del analisis podras contestar preguntas como:')
        st.write('- ¿Que necesidades del cliente prioriza la marca?')
        st.write('- ¿La marca ofrece calidad al menor precio posible?')
        st.write('- ¿Que marcas estan mejor posicionadas?')

        image_3 = Image.open('./p5_deployment/utils/posicion_mercado.jpeg')
        col1, col2, col3 = st.columns([0.2, 5, 0.2])
        col2.image(image_3, use_column_width=True)

        st.write('En dos simples pasos, podras conocer el posicionamiento en el mercado de las marcas. Seleccionas un producto y te mostramos el posicionamiento de las marcas de este.')

        # (2) SOLICITO PRODUCTO
        st.write('### PASO 1: ELEGI TU PRODUCTO')
        product = st.selectbox('¿Que producto desea evaluar?', product_options)  # product = st.sidebar.selectbox('2) ¿Que producto desea evaluar?', product_options)
        product = product.lower()

        # SI SELECCIONO UN PRODUCTO
        if product != '':
            # IMPORTO ARCHIVOS DE CLUSTERING
            df_alt_cleaned_cluster = pd.read_excel('./data/modelling/clustering/{}/df_alt_cleaned_cluster.xlsx'.format(product), index_col=0)
            df_alt_per_clust = pd.read_excel('./data/modelling/clustering/{}/df_alt_per_clust.xlsx'.format(product), index_col=0)
            df_centroids_values = pd.read_excel('./data/modelling/clustering/{}/df_centroids_values.xlsx'.format(product), index_col=0)
            df_brand_per_cluster = pd.read_excel('./data/modelling/clustering/{}/df_brand_per_cluster.xlsx'.format(product), index_col=0)
            df_best_cluster_per_cust_need = pd.read_excel('./data/modelling/clustering/{}/df_best_cluster_per_cust_need.xlsx'.format(product),index_col=0)

            # (3) MUESTRO RESULTADOS
            # Numero de grupos y sus nombres
            st.write('### PASO 2: ANALISIS DE RESULTADOS')

            st.write('Con el objetivo de posicionar las marcas en el mercado, llevamos a cabo un análisis en el que '
                     'agrupamos las alternativas de un producto segun la similaridad de sus caracteristicas.')

            st.write('El analsis se divide en dos etapas:')
            st.write('1) Conocimiento de grupos')
            st.write('2) Distribucion de marcas en grupos')

            st.write("En la primera etapa, conocemos profundamente a cada grupo en terminos de que grupos hay, que nombres"
                     "tienen, como es una alternativa tipica del grupo, como se posicion en cada necesidade del cliente."
                     "En la segunda etapa, ")

            st.write("#### 2.1. CONOCIMIENTO DE GRUPOS")
            st.write('Conozcamos que hay dentro de cada uno de estos grupos!')

            st.write('##### Cantidad de grupos y sus nombres')
            st.write("* Nº GRUPOS: {}".format(len(df_alt_per_clust)))
            st.write("* NOMBRES DE GRUPOS:  {}".format("  -  ".join(list(df_alt_per_clust.index))))

            # Numero de alternativas por grupo
            st.write('##### Cantidad de alternativas por grupo')  # st.write('##### Tabla 1: Número de alternativas por grupo')
            st.write("Podemos ver la cantidad de alternativas dentro de cada uno de estos grupos.")
            image_5 = Image.open('./p5_deployment/utils/cant_alt_{}.png'.format(product))  # st.bar_chart(df_alt_per_clust)
            col1, col2, col3 = st.columns([0.2, 5, 0.2])
            col2.image(image_5, use_column_width=True)

            # Ejemplo tipico de cada grupo
            st.write('##### Alternativa tipica por grupo')  # st.write('##### Tabla 2: Ejemplo típico de cada grupo')  #  CENTROIDES DE CLUSTERS SEGUN VALORES DE ATRIBUTOS
            st.write('En la siguiente tabla, se responde a la pregunta "¿Como es la alternativa tipica de cada grupo?"')
            st.write(df_centroids_values)

            st.write('##### Posicion de cada grupo en las necesidades del cliente')  # st.write('##### Tabla 4: Mejores marcas por necesidad del cliente')
            # Mejores marcas por necesidad del cliente
            st.write("A continuación, podra ver las mejores marcas por necesidad del cliente")
            st.dataframe(df_best_cluster_per_cust_need)


            st.write("#### 2.2. DISTRIBUCION DE MARCAS EN GRUPOS")
            # Distribucion de marcas en grupos
            st.write("Tal como en la tabla 1, podemos ver cuantas alternativas hay por grupo. Pero ahora, le sumaremos "
                     "la variable marca. Así, veremos como se distribuye cada marca en los distintos grupos")
            st.write('En que grupo se ubica mi marca? ')
            st.write(df_brand_per_cluster)

            st.write('Un grafico suele ayudar a visualizar mejor los resultados, veamos la tabla anterior en el siguiente '
                     'grafico')
            image_4 = Image.open('./p5_deployment/utils/brand_{}.png'.format(product))
            col1, col2, col3 = st.columns([0.2, 5, 0.2])
            col2.image(image_4, use_column_width=True)

            with st.expander("Ayuda en interpretacion del grafico", expanded=False):
                st.write('* Marcas con mayor cantidad de verde -->  marcas con mejor relacion precio-calidad')
                st.write('* Marcas con mayor cantidad de amarillo - naranja -->  marcas con relacion precio-calidad media')
                st.write('* Marcas con mayor cantidad de rojo -->  marcas con peor relacion precio-calidad')

            # Listado de todas las alternativas tenidas en cuenta en el analisis
            with st.expander("Ver todas las alternativas tenidas en cuenta en el análisis"):
                st.write("Acá, podras ver todas las alternativas con las que trabajó la herramienta, así, podes "
                         "verificar que no falta ninguna")
                st.dataframe(df_alt_cleaned_cluster.iloc[:, 1:])

def set_customer_needs_weigths(df_cust_needs, product):
    """
    Obtengo peso (o importancia) de cada customer need para el cliente
    :param df_cust_needs: Dataframe. Unidad de analisis: Customer need. Columnas: customer need de 1 palabra (index) y
    customer need de 3 palabras.
    :param product: String. Nombre del producto
    :return: Dataframe. Unidad de analisis: Customer need. Columnas: customer need de 1 palabra (index), customer need
    de 3 palabras y peso de la customer need.
    """
    # Defino variables
    l_cust_needs_one_word, l_cust_needs_three_words =  list(df_cust_needs.index), list(df_cust_needs['cust_needs_three_words'])
    df_cust_needs['Peso'] = None  # Inicializo columna peso de customer needs
    l_categorias = ["No es importante", 'Poco importante', 'Algo importante', 'Importante', 'Muy importante']
    d_categorias_peso = {"No es importante": 1, 'Poco importante': 2, 'Algo importante': 3, 'Importante': 4,
                         'Muy importante': 5}  # antes: -10, -2.5, 0, 2.5, 10 --> no esta bien que neutral sea 0

    # COLOCO CONTAINER PARA SELECCIONAR UN USO DEL PRODUCTO CON PESOS PREDETERMINADOS (si tiene)
    # Obtengo usos del producto con pesos predeterminados
    d_usos = get_usos(product)  # Diccionario con usos del producto como keys y pesos como values
    # Si el producto tiene usos especificados
    if d_usos is not None:
        # Coloco container para que el cliente pueda seleccionar un uso
        st.write("Y si todavía no tenes claro cómo hacer, podes usar el sector 'Ayuda' donde fijamos las importancias según uso del producto")
        col1, col2 = st.columns([2, 0.8])
        uso_selected = col2.selectbox('AYUDA: Orientación de importancias según uso del producto', ['Reestablecer'] + list(d_usos.keys()))
    # Si el producto no tiene usos especificados
    else:
        # No coloco container para que el cliente pueda seleccionar un uso
        uso_selected = 'Reestablecer'

    # POR CUSTOMER NEED
    for i in range(len(l_cust_needs_three_words)):

        # Defino variables
        st.write('#### {}) {}'.format(i + 1, l_cust_needs_three_words[i].upper()))  # titulo de cada slider  # st.subheader('{}) {}:'.format(i + 1, l_cust_needs_three_words[i].upper()))  # titulo de cada slider
        label = 'Ingrese que importancia tiene para vos "{}":'.format(l_cust_needs_three_words[i].upper())  # titulo de cada slider
        help = get_help_button(l_cust_needs_one_word[i], product)  # Texto help de cada slider

        # SI EL CLIENTE NO SELECCIONO UN USO, O BIEN, EL PRODUCTO NO LOS TIENE ESPECIFICADOS
        if uso_selected == "Reestablecer":
            # SETEO SLIDER (INICIALMENTE EN PESO "ALGO IMPORTANTE")
            peso = st.select_slider(label=label, options=l_categorias, value="Algo importante", help=help)  # puedo agregarle help y sus palabras relacionadas por ej
            st.write(" ")
            st.write(" ")

        # SI EL CLIENTE SELECCIONO UN USO
        else:
            # SETEO SLIDER CON PESO PREDETERMINADO DEL USO
            uso = d_usos[uso_selected]
            peso = st.select_slider(label=label, options=l_categorias, value=uso[l_cust_needs_one_word[i]], help=help)  # puedo agregarle help y sus palabras relacionadas por ej
            st.write(" ")
            st.write(" ")


        # GUARDO PESO NUMERICO
        df_cust_needs.loc[l_cust_needs_one_word[i], 'Peso'] = d_categorias_peso[peso]
    return df_cust_needs

def get_help_button(cust_need, producto):
    """
    Texto de ayuda por cada customer need de cada producto
    :param cust_need: String. Customer need
    :param producto: String. Nombre de producto
    :return: String. Texto 'help' que explica el significado de la customer need para dicho producto.
    """
    # Defino 'help' generales
    help_precio =  "Precio y marca del dispositivo. Aclaración: Generalmente, a mayor importancia, se buscaran precios " \
                   "mas bajos aunque siempre se priorizara una mayor relacion precio-calidad"
    help_bateria = 'Duración de la batería'
    help_tam = "Tamaño de pantalla del dispositivo. Aclaración: Generalmente, a mayor importancia, se priorizaran " \
                  "tamaños de pantalla mas grandes"
    help_dis = "Estética, calidad de materiales y resistencia a caídas, a agua y a polvo "
    help_vel = 'Velocidad de procesamiento del dispositivo'

    d = {'celulares':
             {'precio': help_precio,
              'bateria': help_bateria,
              'camara': 'Resoluciones de foto y video tanto de la cámara frontal como de la cámara trasera',
              'diseño': help_dis,
              'memoria': "Capacidad de almacenamiento interna. En otras palabras, espacio para descargar muchas "
                         "aplicaciones, guardar muchas fotos o documentos, etcetera ",
              'pantalla': 'Calidad de imagen de la pantalla',
              'sistema': 'Facilidad de uso del dispositivo, cantidad y calidad de funciones (por ejemplo, navegacion por '
                         'gestos, infrarrojo, entre otros) y frecuencia de actualizaciones del sistema operativo (tal '
                         'que no quede obseleto en pocos años)',
              'sonido': 'Calidad del sonido, cantidad de parlantes y ubicacion de los mismos',
              'tamaño': help_tam,
              'velocidad': help_vel
              },
         # TV
         'tv': {'control': "Sencillez y calidad del control remoto (facilidad de uso, teclado numerico en "
                           "control, integrado con comando por voz, etcetera)",
                'conexion': "Estabilidad en las distintas conexiones (internet, ethernet y bluetooth) y cantidad de "
                            "entradas/puertos",
                'diseño': 'Estetica y calidad de materiales',
                'imagen': 'Calidad de imagen de la pantalla',
                'precio': help_precio,
                'sistema': 'Facilidad de uso del dispositivo y cantidad y calidad de aplicaciones que trae o que se '
                           'pueden instalar (por ejemplo, netflix, youtube, disney+, spotify, etcetera)',
                'sonido': 'Calidad de sonido y cantidad de parlantes',
                'tamaño': help_tam,
                'velocidad': help_vel},
         # SMARTBAND
         'smartband': {'bluetooth': 'Alcance del bluetooth y sincronización de datos con celular',
                      'bateria': help_bateria,
                      'diseño': help_dis,
                      'funciones': 'Cantidad y calidad de funciones (cuenta pasos, estres, etcetera)',
                      'pantalla': 'Calidad de imagen de la pantalla y tamaño de ésta',
                      'precio': help_precio}
         }

    return d[producto][cust_need]

def get_usos(product):
    """
    Obtiene pesos predeterminados de las customer needs segun el uso del producto
    :param product: String. Nombre del producto
    :return: Diccionario. Key: uso del producto. Value: diccionario cuyas keys son cada customer need del producto y
    sus values la importancia o peso de la customer need. Si el producto no tiene usos especificados, None.
    """
    # INTENTO AGREGAR PERFILES DE CLIENTES --> QUE SETEEN PESOS PREDETERMINADOS
    d_usos = {
        'celulares': {'Para jugar': {'precio': 'Algo importante', 'bateria': 'Importante', 'camara': 'Poco importante',
                                'pantalla': 'Importante', 'memoria': 'Algo importante', 'tamaño': 'Algo importante',
                                'velocidad': 'Muy importante', 'sonido': 'Algo importante', 'diseño': 'No es importante',
                                'sistema': 'Poco importante'},
                      'Para trabajar': {'precio': 'Muy importante', 'bateria': 'Importante', 'camara': 'Algo importante',
                                   'pantalla': 'Algo importante', 'memoria': 'Importante', 'tamaño': 'Poco importante',
                                   'velocidad': 'Muy importante', 'sonido': 'Poco importante', 'diseño': 'Algo importante',
                                   'sistema': 'Poco importante'},
                      'Para redes sociales': {'precio': 'Algo importante', 'bateria': 'Importante', 'camara': 'Muy importante',
                                'pantalla': 'Algo importante', 'memoria': 'Algo importante', 'tamaño': 'Algo importante',
                                'velocidad': 'Importante', 'sonido': 'Poco importante', 'diseño': 'Algo importante',
                                'sistema': 'Poco importante'},
                      'Para comunicación': {'precio': 'Muy importante', 'bateria': 'No es importante', 'camara': 'Poco importante',
                                       'pantalla': 'Poco importante', 'memoria': 'No es importante', 'tamaño': 'Importante',
                                       'velocidad': 'No es importante', 'sonido': 'Importante', 'diseño': 'Poco importante',
                                       'sistema': 'Importante'},
                      }
    }

    #'tv': {'monitor': {'precio': 'Importante', 'imagen': 'Muy importante', 'sonido': 'Importante',
    #                   'sistema': 'Poco importante', 'control': 'Poco importante', 'tamaño': 'No es importante',
    #                   'velocidad': 'Algo importante', 'diseño': 'Algo importante', 'conexion': 'Importante'}},
    #'smartband': {} # deporte # Complemento del celular

    # Si el producto no tiene usos definidos
    if product not in d_usos.keys():
        return None

    return d_usos[product]

def get_attrs_technical_importance(df_cust_needs, df_relation_matrix):
    """
    Obtiene la importancia tecnica de cada atributo del producto
    :param df_cust_needs: Dataframe. Unidad de analisis: Customer need. Columnas: customer need de 1 palabra (index),
    customer need de 3 palabras y peso de la customer need.
    :param df_relation_matrix: Dataframe. Filas: customer need de producto. Columnas: atributos o campos especificos
    del producto. Celdas: indica relacion entre customer need  i y atributo j
    :return: Diccionario. Key: atributo del producto. Value: importancia tecnica del atributo.
    """
    # Defino variables
    d = {}  # inicializo diccionario a retornar

    # POR ATRIBUTO
    for atributo in df_relation_matrix.columns:

        # Reinicio variable de importancia tecnica
        imp_tecnica = 0

        # POR CUSTOMER NEED
        for customer_need in list(df_relation_matrix.index):

            # defino variables
            relacion = df_relation_matrix.loc[customer_need, atributo]  # Relacion entre atributo y customer need
            peso = df_cust_needs.loc[customer_need, 'Peso']  # Peso de customer need

            # CALCULO IMPORTANCIA TECNICA
            imp_tecnica += peso * relacion

        # GUARDO IMPORTANCIA TECNICA
        d[atributo] = imp_tecnica
    return d

def get_alts_final_value(df_alt, df_attr_alt_sent, df_attr_value_sent, d_attrs_tech_imp):
    """
    Obtiene valoracion final de cada alternativa del producto
    :param df_alt: Dataframe alternativas. Unidad de analisis: alternativa del producto. Columnas: id_alternativa y una
    por atributo del producto.
    :param df_attr_alt_sent: Dataframe. Unidad de analisis: alternativa del producto. Columnas: id_alternativa, atributo
    (ficticio), numero de opiniones en que basa su sentiment y su sentiment.
    :param df_attr_value_sent: Unidad de analisis: valor de atributo del producto. Columnas: valor, atributo al que
    pertenece, numero de opiniones en que basa su sentiment y su sentiment.
    :param d_attrs_tech_imp: Diccionario. Keys: atributo del producto. Values: importancia tecnica de atributo
    :return: Dataframe. Unidad de analisis: alternativa del producto. Columnas: id_alternativa, una por atributo del
    producto y valoracion final
    """
    # Defino variables
    l_atributos = list(df_attr_value_sent['atributo'].unique()) + list(df_attr_alt_sent['atributo'].unique())

    # POR ALTERNATIVA
    for i in df_alt.index:

        # Defino variables
        val_fin_alt = 0  # Reinicio suma de valoracion final por cada alternativa
        id_alt = df_alt.loc[i, 'id_alternativa']  # Id de alternativa
        print("ALTERNATIVA Nº: {}".format(i).center(120))

        # POR ATRIBUTO
        for atributo in l_atributos:

            # OBTENGO EL SENTIMENT DEL ATRIBUTO PARA LA ALTERNATIVA
            # (1) Si el atributo no es ficticio (no lo cree artificialmente sino que lo extraje de Meli, tiene valores)
            if atributo in df_attr_value_sent['atributo'].unique():

                # Defino variable
                valor = df_alt.loc[i, atributo]  # Valor que toma el atributo en la alternativa

                # Si el valor no es NaN (la alternativa puede no tener valor para el atributo)
                if str(valor) != 'nan':

                    # Obtengo sentiment del valor
                    sent = float(df_attr_value_sent[(df_attr_value_sent['atributo'] == atributo) & (df_attr_value_sent['valor'] == valor)]['sent'])

                # Si el valor es NaN
                else:
                    # Obtengo el peor sentiment del atributo
                    sent = df_attr_value_sent[df_attr_value_sent['atributo'] == atributo]["sent"].min()
                    print("El modelo Nº{} tiene valor NaN en atributo {}, por lo cual, le asigno el peor sentiment {} de"
                        "los valores de dicho atributo".format(i, atributo, sent))

            # (2) Si el atributo es ficticio (Creado artificialmente para ser relacionado con una customer need, no tiene valores)
            else:
                # Obtengo sentiment del atributo
                sent = float(df_attr_alt_sent[(df_attr_alt_sent['atributo'] == atributo) & (df_attr_alt_sent['id_alternativa'] == id_alt)]['sent'])

            # CALCULO APORTE DEL ATRIBUTO A VALORACION FINAL
            # Si el sentiment no es NaN
            if str(sent) != 'nan':
                # Calculo aporte del atributo a valoracion final
                val_fin_alt += sent * d_attrs_tech_imp[atributo]  # print(sent, d_attrs_tech_imp[atributo], val_fin_alt)
            # Si el sentiment es NaN
            else:
                # No hago nada
                pass

        # GUARDO ALTERNATIVA Y SU VALORACION FINAL
        df_alt.loc[i, 'val_final'] = val_fin_alt
    return df_alt

def create_recomendation_table(df_alt, df_alt_val_final):
    """
    Obtiene el porcentaje de recomendacion de cada alternativa
    :param df_alt: Dataframe alternativas. Unidad de analisis: alternativa del producto. Columnas: id_alternativa y una
    por atributo del producto. # deberia mostrar los valores reales de los modelos antes de limpiarlos... (y sin id_publicacion)
    :param df_alt_val_final: Dataframe. Unidad de analisis: alternativa del producto. Columnas: id_alternativa, una por
    atributo del producto y valoracion final
    :return: Dataframe. Unidad de analisis: alternativa del producto. Columnas: id_alternativa, una por atributo del
    producto y porcentaje de recomendacion (ordenados descendientemente segun esta)
    """
    # Defino variable
    val_max = df_alt_val_final['val_final'].dropna().max()  # Valoracion final maxima considerando todas las alternativas

    # POR ALTERNATIVA
    for i in df_alt.index:

        # Defino variables
        idx = df_alt_val_final.index[df_alt_val_final['id_alternativa'] == df_alt.loc[i, 'id_alternativa']][0]  # Indice de alternativa en df_alt_val_fin

        # OBTENGO SU VALORACION FINAL
        val_alt = df_alt_val_final.loc[idx, 'val_final']

        # CALCULO PORCENTAJE DE RECOMENDACION
        porc_recom = round(val_alt / val_max * 100, 1)

        # GUARDO PORCENTAJE DE RECOMENDACION
        df_alt.loc[i, "porcentaje_recomendacion"] = porc_recom
        print(val_alt, val_max, porc_recom)

    # ORDENO ALTERNATIVAS POR PORCENTAJE DE RECOMENDACION
    df_alt = df_alt.sort_values('porcentaje_recomendacion', ascending=False)
    df_alt.index = range(1, len(df_alt) + 1)  # df_alt = df_alt.set_index(range(1, len(df_alt)+1))     # df_alt = df_alt.reset_index(drop=True)
    return df_alt


if __name__ == '__main__':
    main()


# col1, col2 = st.columns(2)
# col1.metric(label="Posicion", value="1")
# col2.metric(label="Alternativa", value=df_alt.loc[1])
# col2.metric("Wind", "9 mph", "-8%")


# st.write('En la **etapa 1**, **conoceremos a cada grupo de alternativas** del producto. Para ello, veremos: ')
# st.write('- cuantos grupos hay y que nombres tienen')
# st.write('- cuantas alternativas tiene cada uno')
# st.write('- cual es la alternativa promedio de cada grupo')
# st.write('- posicion de cada grupo en cada necesidad del cliente')

# st.write('En la **etapa 2**, veremos la distribucion de cada marca entre los distintos grupos. Habiendo obtenido un profundo conocimiento de cada grupo en la etapa 1, podremos sacar conclusiones como:')
# st.write('- ¿Que necesidades del cliente prioriza la marca?')
# st.write('- ¿La marca ofrece calidad al menor precio posible?')
# st.write('- ¿Que marcas estan mejor posicionadas?')
