# Importo librerias
import pandas as pd
import streamlit as st
from PIL import Image

def get_attrs_technical_importance(df_cust_needs, df_relation_matrix):
    """
    Obtiene la importancia tecnica de cada atributo del producto
    :param df_cust_needs: Dataframe con peso
    :param relation_matrix: Dataframe
    :return: Diccionario cuyas keys son cada atributo y sus values son la importancia tecnica de cada atributo
    """
    # Defino variables
    l_atributos = df_relation_matrix.columns  # Lista de atributos del producto
    l_customer_needs = list(df_relation_matrix.index)  # Lista de customer needs de 1 palabra del producto
    d = {}  # inicializo diccionario a retornar

    # POR ATRIBUTO
    for atributo in l_atributos:

        # Reinicio variable de importancia tecnica
        imp_tecnica = 0

        # POR CUSTOMER NEED
        for customer_need in l_customer_needs:

            # defino relacion entre atributo y customer need
            relacion = df_relation_matrix.loc[customer_need, atributo]

            # CALCULO IMPORTANCIA TECNICA
            imp_tecnica += df_cust_needs.loc[customer_need, 'Peso'] * relacion

        # GUARDO IMPORTANCIA TECNICA
        d[atributo] = imp_tecnica
    return d

def get_alts_final_value(df_alt, df_attr_alt_sent, df_attr_value_sent, d_attrs_tech_imp):
    """
    Obtiene valoracion final de cada alternativa del producto
    :param df_alt: Dataframe alternativas. Unidad de analisis: alternativa. Columnas: atributos del producto.
    :param df_attr_value_sent: Dataframe. Unidad de analisis: valor de un atributo. Columnas: valor, atributo al que pertence
     y sentiment del valor.
    :param d_attrs_tech_imp: Diccionario. Keys: atributo del producto. Values: importancia tecnica de atributo
    :return: Dataframe. Unidad de analisis: alternativa. Columnas: atributos del producto + columna de valoracion final
    """
    # Defino variables
    df = df_alt.copy()
    l_val_fin_alts = []
    l_atributos = list(df_attr_value_sent['atributo'].unique()) + list(df_attr_alt_sent['atributo'].unique())

    # POR ALTERNATIVA
    for i in range(len(df_alt)):

        # Defino variables
        val_fin_alt = 0  # Reinicio suma de valoracion final por cada alternativa
        id_alt = df_attr_alt_sent.loc[i, 'id_alternativa']  # Id de alternativa
        print("ALTERNATIVA Nº: {}".format(i).center(120))

        # POR ATRIBUTO
        for atributo in l_atributos:

            # OBTENGO EL SENTIMENT DEL ATRIBUTO PARA LA ALTERNATIVA
            # (1) Si el atributo no es ficticio (no lo cree artificialmente sino que lo extraje de Meli, tiene valores)
            if atributo in df_attr_value_sent['atributo'].unique():

                # Obtengo el valor que toma el atributo en la alternativa
                valor = df_alt.loc[i, atributo]

                # SI EL VALOR NO ES NAN (la alternativa puede no tener valor para el atributo)
                if str(valor) != 'nan':

                    # OBTENGO SENTIMENT DEL VALOR
                    sent = float(df_attr_value_sent[(df_attr_value_sent['atributo'] == atributo) & (df_attr_value_sent['valor'] == valor)]['sent'])

                # SI EL VALOR ES NAN
                else:
                    # OBTENGO EL PEOR SENTIMENT DEL ATRIBUTO
                    sent = df_attr_value_sent[df_attr_value_sent['atributo'] == atributo]["sent"].min()
                    print("El modelo Nº{} tiene valor NaN en atributo {}, por lo cual, le asigno el peor sentiment {} de"
                        "los valores de dicho atributo".format(i, atributo, sent))

            # (2) Si el atributo es ficticio (Creado artificialmente para ser relacionado con una customer need, no tiene valores)
            else:
                # OBTENGO SENTIMENT DEL ATRIBUTO
                sent = float(df_attr_alt_sent[(df_attr_alt_sent['atributo'] == atributo) & (df_attr_alt_sent['id_alternativa'] == id_alt)]['sent'])

            # SI EL SENTIMENT NO ES NAN
            if str(sent) != 'nan':

                # CALCULO VALORACION FINAL DEL ATRIBUTO
                val_fin_alt += sent * d_attrs_tech_imp[atributo]  # print(sent, d_attrs_tech_imp[atributo], val_fin_alt)

            # SI EL SENTIMENT ES NAN
            else:
                # NO HAGO NADA
                pass

        # GUARDO ALTERNATIVA Y SU VALORACION FINAL
        l_val_fin_alts.append(val_fin_alt)

    # Agrego columna al dataframe alternativas
    df['val_final'] = l_val_fin_alts
    print(l_val_fin_alts)
    return df

def create_recomendation_table(df_alt, df_alt_val_final):
    """
    Obtiene porcentaje de recomendacion de cada alternativa
    :param df_alt:# deberia mostrar los valores reales de los modelos antes de limpiarlos... (y sin id_publicacion)
    :param df_alt_val_final:
    :return: Dataframe alternativas con columna porcentaje de recomendacion y ordenado segun esta
    """
    # Defino variables
    val_max = df_alt_val_final['val_final'].dropna().max()  # Valoracion final maxima considerando todas las alternativas
    df_alt['porcentaje_recomendacion'] = None  # Creo la columna "porcenta_recomendacion" en df_alt

    # POR ALTERNATIVA
    for id_alt in df_alt['id_alternativa']: # for id_alt in df_alt_val_final['id_alternativa']:  # con df_alt sin importar to client       # for i in range(len(df_alt)):

        idx_id_en_df_alt = df_alt.index[df_alt['id_alternativa'] == id_alt][0]
        idx_id_en_df_alt_val_final = df_alt_val_final.index[df_alt_val_final['id_alternativa'] == id_alt][0]

        # OBTENGO SU VALORACION FINAL
        val_alt = df_alt_val_final.loc[idx_id_en_df_alt_val_final, 'val_final']

        # CALCULO PORCENTAJE DE RECOMENDACION
        porc_recom = round(val_alt / val_max * 100, 1)

        # GUARDO PORCENTAJE DE RECOMENDACION
        df_alt.loc[idx_id_en_df_alt, "porcentaje_recomendacion"] = porc_recom
        print(val_alt, val_max, porc_recom)

    # Ordeno alternativas por porcentaje de recomendacion
    df_alt = df_alt.sort_values('porcentaje_recomendacion', ascending=False)
    df_alt.index = range(1, len(df_alt) + 1)  # df_alt = df_alt.set_index(range(1, len(df_alt)+1))     # df_alt = df_alt.reset_index(drop=True)
    return df_alt

def main():
    # (1) SOLICITO INGRESO DE DATOS EN SIDEBAR (tipo de cliente y producto a relevar)
    st.header('EVALUACION AUTOMATICA DE ALTERNATIVAS EN PROCESO DE COMPRA')  # imprimo titulo  # # st.title('EVALUACION AUTOMATICA DE ALTERNATIVAS EN PROCESO DE COMPRA')
    st.sidebar.write('# Cambiar tipo de cliente')  # titulo 1 de sidebar
    l_client_options = ['Usuario final', 'Empresa']  # Usuario define si es empresa o usuario final
    client_help = "Si sos un consumidor final como la gran mayoria tu opcion es 'Usuario final'. Solo si sos empresario y queres conocer la posicion de tu empresa en el mercado, la opcion correcta es 'Empresa'"
    client = st.sidebar.radio(label='¿Que tipo de cliente sos?', options=l_client_options, help=client_help)  # client = st.sidebar.selectbox('1) ¿Que tipo de cliente eres?', client_options)
    product_options = ['', 'Celulares', 'Smartband', 'TV']  # ['Auriculares', 'Celulares', 'Fundas de celular', 'Notebook', 'Smartband', 'Suplementos','Tablets', 'TV']  # Lista de productos

    # SI EL CLIENTE ES UN USUARIO FINAL
    if client == 'Usuario final':

        st.write("Antes de comprar cualquier producto que deseamos, solemos **evaluar las distintas alternativas** posibles. "
                 "Tipicamente buscamos informacion en internet, por ejemplo, leemos opiniones, vemos videos que hagan "
                 "una reseña, entre otros.")

        image_1 = Image.open('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/p5_deployment/investigar_alternativas.jpeg') # Imagen de persona antes ≠ alternativas
        col1, col2, col3 = st.columns([0.2, 5, 0.2])
        col2.image(image_1, use_column_width=True)

        st.write("Hoy en dia, cada vez hay mas alternativas lo que hace que la eleccion de una sola sea un proceso "
                 "extramadamente desgastante. Es muy probable que consumamos mucho de nuestro valioso tiempo y encima no "
                 "terminemos escogiendo la alternativa ideal para nosotros.")

        image_2 = Image.open('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/p5_deployment/alternativas_posibles.png')
        col1, col2, col3 = st.columns([0.2, 5, 0.2])
        col2.image(image_2, use_column_width=True)

        st.write("Afortundamente, podras facilitar este proceso utilizando la siguiente herramienta pensada para "
                 "encontrar **la mejor alternativa para vos** en solo 3 pasos")

        st.write('### PASO 1 DE 3: ELEGI TU PRODUCTO')
        product = st.selectbox('¿Que producto desea evaluar?', product_options)  # product = st.sidebar.selectbox('2) ¿Que producto desea evaluar?', product_options)
        product = product.lower()

        # Si seleccion producto
        if product != '':
            # IMPORTO ARCHIVOS UNA VEZ SELECCIONADO EL PRODUCTO
            # Archivos de (2) Data preparation
            df_alt_to_client = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_alt_cleaned_to_client.xlsx'.format(product))  # df_alt = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/{}/df_alt.xlsx'.format(product))  # correct_price
            df_alt_cleaned = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_alt_cleaned.xlsx'.format(product))
            df_cust_needs = pd.read_excel("/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_cust_needs.xlsx".format(product), index_col=0)
            # Archivos de (3) Modelling
            df_attr_alt_sent = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/atribucion/{}/df_attr_alt_sent.xlsx'.format(product))
            df_value_sent = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/atribucion/{}/df_attr_values_sent.xlsx'.format(product))
            df_relation_matrix = pd.read_excel("/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_relation_matrix.xlsx".format(product), index_col=0)

            # (2) SOLICITO PESOS DE LAS CUSTOMER NEEDS
            # Imprimo titulo
            st.write('### PASO 2 DE 3: IMPORTANCIA DE CADA NECESIDAD DEL CLIENTE'.format(product))
            # st.write('Ingrese la importancia que tiene para vos cada necesidad del cliente tipica de {}'.format(product))
            st.write('Ya elegiste el producto! Ya estas en el paso 2 de 3, yo le diria a Usain Bolt que se empiece a preocupar!')
            st.write("Ahora, tenes que asignar la importancia para vos de cada necesidad del cliente tipica de {}. Bueno, "
                     "seguramente mas de uno se esta preguntando 'y como hago eso?' (tal vez usando alguna palabrita mas)".format(product))
            st.write("Es muy sencillo! A continuacion, habra una barra por cada necesidad del cliente del producto. "
                     "Podes cambiar el valor de cada barra segun la importancia que tiene para vos cada necesidad del cliente!")
            st.write("Una vez que hayas asignado los pesos, clikea el boton 'Procesar' abajo de todo.")

            # Solicito pesos al cliente
            df_cust_needs_with_weight = set_weigths(df_cust_needs, product)

            # SI EL CLIENTE DA CLICK A BOTON "PROCESAR"
            if st.button('Procesar'):

                # (3) CALCULO IMPORTANCIA TECNICA DE CADA ATRIBUTO (SEGUN PESOS DE NECESIDADES DEL CLIENTE)
                d_attrs_tech_imp = get_attrs_technical_importance(df_cust_needs_with_weight, df_relation_matrix)
                # print(d_attrs_tech_imp) # st.write("Verifico (3): ",d_attrs_tech_imp)

                # (4) CALCULO VALORACION FINAL DE CADA ALTERNATIVA
                df_alts_val_fin = get_alts_final_value(df_alt_cleaned, df_attr_alt_sent, df_value_sent, d_attrs_tech_imp)
                # st.write("Verifico (4): ", df_alts_val_fin)

                # (5) IMPRIMO RESULTADOS
                # 5.1) Muestro tabla de recomendacion
                st.write('### PASO 3 DE 3: ELECCION DE ALTERNATIVA')
                st.write('Llegaste al ultimo paso! Aca te presentamos las 10 alternativas que mejor se ajustan a lo que '
                         'buscas, solo tendras que elegir entre alguna de las 10. Y quedate tranquil@, analizamos todas '
                         'las alternativas posibles (y si, podes decir que lo hiciste todo vos!).')
                # st.write('Dada la importancia que le da a cada necesidad del cliente, buscamos las alternativas mas idoneas para vos')

                st.write('#### Las 10 alternativas que mas te recomendamos')

                # Calculo porcentaje de recomendacion de cada alternativa
                df_alts_recommend = create_recomendation_table(df_alt_to_client, df_alts_val_fin)   # OJO! DF_ALT TIENE ALTS QUE DF_ALT_CLEANED NO Y POR ENDE EL INDICE ES ≠

                # Selecciono las 10 alternativas de mayor porcentaje de recomendacion
                df_top_ten = df_alts_recommend.iloc[0:10, 1:]  # df_top_ten = pd.DataFrame(columns=['Marca', "Modelo", "precio", 'porcentaje_recomendacion'])
                st.dataframe(df_top_ten)

                st.balloons()

                with st.expander("Ver todas las alternativas tenidas en cuenta en el analisis"):
                    st.write("Aquí, podra ver todas las alternativas que con las que trabajo la herramienta. Así, puede "
                             "verificar que no falta ninguna alternativa")
                    st.dataframe(df_alts_recommend.iloc[:, 1:])

    # SI EL CLIENTE ES UNA EMPRESA
    else:
        st.write('La herramienta tiene como objetivo identificar el **posicionamiento de las marcas de un producto '
                 'en el mercado**. Para ello, llevamos a cabo un analisis en el que agrupamos las alternativas '
                 'de un producto segun la similaridad de sus caracteristicas.')

        image_3 = Image.open('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/p5_deployment/posicion_mercado.jpeg')
        col1, col2, col3 = st.columns([0.2, 5, 0.2])
        col2.image(image_3, use_column_width=True)

        st.write('###  Escoge tu producto')
        product = st.selectbox('¿Que producto desea evaluar?', product_options)  # product = st.sidebar.selectbox('2) ¿Que producto desea evaluar?', product_options)
        product = product.lower()

        # Si seleccion producto
        if product != '':
            # Importar archivos
            df_alt_to_client_clust = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/clustering/{}/df_alt_to_client_clust.xlsx'.format(product), index_col=0)
            df_alt_per_clust = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/clustering/{}/df_alt_per_clust.xlsx'.format(product), index_col=0)
            df_centroids_values = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/clustering/{}/df_centroids_values.xlsx'.format(product), index_col=0)
            df_brand_per_cluster = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/clustering/{}/df_brand_per_cluster.xlsx'.format(product), index_col=0)
            df_best_brand_per_cust_need = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/clustering/{}/df_best_brand_per_cust_need.xlsx'.format(product),index_col=0)

            # Le muestro resultados al cliente
            st.write('Los resultados fueron:')
            st.write("* Nº GRUPOS: {}".format(len(df_alt_per_clust)))
            st.write("* NOMBRES DE GRUPOS:  {}".format("  -  ".join(list(df_alt_per_clust.index))))

            st.write('Conozcamos que hay dentro de cada uno de estos grupos!')

            st.write('### Tabla 1: Número de alternativas por grupo')
            st.write("Podemos ver la cantidad de alternativas dentro de cada uno de estos grupos.")
            # st.bar_chart(df_alt_per_clust)
            image_5 = Image.open('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/p5_deployment/cant_alt_{}.png'.format(product))
            col1, col2, col3 = st.columns([0.2, 5, 0.2])
            col2.image(image_5, use_column_width=True)

            st.write('### Tabla 2: Ejemplo típico de cada grupo')  #  CENTROIDES DE CLUSTERS SEGUN VALORES DE ATRIBUTOS
            st.write('En la siguiente tabla, se responde a la pregunta "¿Como es la alternativa tipica de cada grupo?"')
            st.write(df_centroids_values)

            st.write('### Tabla 3: Número de alternativas por grupo y marca')
            st.write("Tal como en la tabla 1, podemos ver cuantas alternativas hay por grupo. Pero ahora, le sumaremos "
                     "la variable marca. Así, veremos como se distribuye cada marca en los distintos grupos")
            st.write(df_brand_per_cluster)

            st.write('Un grafico suele ayudar a visualizar mejor los resultados, veamos la tabla anterior en el siguiente '
                     'grafico')
            image_4 = Image.open('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/p5_deployment/brand_{}.png'.format(product))
            col1, col2, col3 = st.columns([0.2, 5, 0.2])
            col2.image(image_4, use_column_width=True)

            with st.expander("Ayuda en interpretacion del grafico", expanded=False):
                st.write('* Marcas con mayor cantidad de verde -->  marcas con mejor relacion precio-calidad')
                st.write('* Marcas con mayor cantidad de amarillo - naranja -->  marcas con relacion precio-calidad media')
                st.write('* Marcas con mayor cantidad de rojo -->  marcas con peor relacion precio-calidad')

            # Agregar cantidad de modelos totales???

            st.write('### Tabla 4: Mejores marcas por necesidad del cliente')
            st.write("A continuación, podra ver las mejores marcas por necesidad del cliente")
            st.dataframe(df_best_brand_per_cust_need)

            with st.expander("Ver todas las alternativas tenidas en cuenta en el análisis"):
                st.write("Aquí, podra ver todas las alternativas que con las que trabajo la herramienta. Así, puede "
                         "verificar que no falta ninguna alternativa")
                st.dataframe(df_alt_to_client_clust.iloc[:, 1:])

def set_weigths(df_cust_needs, product):
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
    temp_options = ["No es importante", 'Poco importante', 'Algo importante', 'Importante', 'Muy importante']
    d = {"No es importante": 1, 'Poco importante': 2, 'Algo importante': 3, 'Importante': 4, 'Muy importante': 5}  # antes: -10, -2.5, 0, 2.5, 10 --> no esta bien que neutral sea 0

    # SI EL PRODUCTO TIENE USOS CON PESOS PREDETERMINADOS
    # Obtengo usos del producto con pesos predeterminados
    d_usos = get_usos(product)  # Diccionario con usos del producto como keys y pesos como values
    # Si el producto tiene usos especificados
    if d_usos is not None:
        # Coloco container para que el cliente pueda seleccionar un uso
        col1, col2 = st.columns([2, 0.6])
        uso_selected = col2.selectbox('AYUDA: Orientacion de importancias segun uso', ['Ninguno'] + list(d_usos.keys()))
    # Si el producto no tiene usos especificados
    else:
        # No coloco container para que el cliente pueda seleccionar un uso
        uso_selected = 'Ninguno'

    # POR CUSTOMER NEED
    for i in range(len(l_cust_needs_three_words)):

        # Defino variables
        label = '{}) {}:'.format(i + 1, l_cust_needs_three_words[i].upper())  # titulo de cada slider
        help = get_help_button(l_cust_needs_one_word[i], product)  # Texto help de cada slider

        # SI EL CLIENTE NO SELECCIONO UN USO, O BIEN, EL PRODUCTO NO LOS TIENE ESPECIFICADOS
        if uso_selected == "Ninguno":
            # SETEO SLIDER INICIALMENTE EN PESO "ALGO IMPORTANTE"
            peso = st.select_slider(label=label, options=temp_options, value="Algo importante", help=help)  # puedo agregarle help y sus palabras relacionadas por ej
        # SI EL CLIENTE SELECCIONO UN USO
        else:
            # SETEO SLIDER CON PESOS PREDETERMINADO DEL USO
            uso = d_usos[uso_selected]
            peso = st.select_slider(label=label, options=temp_options, value=uso[l_cust_needs_one_word[i]], help=help)  # puedo agregarle help y sus palabras relacionadas por ej

        # GUARDO PESO NUMERICO
        df_cust_needs.loc[l_cust_needs_one_word[i], 'Peso'] = d[peso]

    return df_cust_needs

def get_help_button(cust_need, producto):
    """
    Texto de ayuda por cada customer need de cada producto
    :param cust_need: String. Customer need
    :param producto: String. Nombre de producto
    :return: String. Texto 'help' que explica el significado de la customer need para dicho producto.
    """
    d = {'celulares':
             {'precio': "Precio y marca del dispositivo. Aclaracion: Generalmente, a mayor importancia, se buscaran "
                        "precios mas bajos (aunque siempre se priorizara una alta relacion precio-calidad)",
              'bateria': 'Duracion de la bateria',
              'camara': 'Resoluciones de foto y video tanto de la camara frontal como de la camara trasera',
              'diseño': "Estetica y resistencia (caidas, agua y polvo)",
              'memoria': "Capacidad de almacenamiento interna",
              'pantalla': 'Calidad de imagen de la pantalla',
              'sistema': 'Facilidad de uso, cantidad y calidad de funciones y frecuencia de actualizaciones del sistema operativo',
              'sonido': 'Calidad del sonido, cantidad de parlantes y ubicacion de los mismos',
              'tamaño': 'Tamaño de pantalla y peso del dispositivo. Aclaracion: A mayor importancia, se priorizaran tamaños '
                        'mas grandes pero sin dejar de perder comodidad en la mano ni que sea tan pesado',
              'velocidad': 'Velocidad de procesamiento del dispositivo'
              },
         # TV
         'tv':{ 'control': "Sencillez del control remoto y comando por voz",
                'conexion': "Estabilidad en las distintas conexiones (internet, ethernet y bluetooth) y  cantidad de "
                            "entradas/puertos",
                'diseño': 'Estetica y calidad de materiales',
                'imagen': 'Calidad de imagen de la pantalla',
                'precio': 'Precio y marca del dispositivo. Aclaracion: Generalmente, a mayor importancia, se buscaran '
                          'precios mas bajos (aunque siempre se priorizara una alta relacion precio-calidad)',
                'sistema': 'Facilidad de uso y cantidad y calidad tanto de aplicaciones (que tiene o que se pueden instalar) como de '
                           'funciones,',
                'sonido': 'Calidad de sonido',
                'tamaño': 'Tamaño de la pantalla y peso',
                'velocidad': 'Velocidad de procesamiento'},
         # SMARTBAND
         'smartband':{'conecta': 'Alcance y velocidad de conexion con celular',
                      'bateria': 'Duracion de bateria',
                      'diseño': 'Estetica y resistencia (golpes y agua)',
                      'facil': 'Facilidad de uso y nivel de personalizacion',
                      'funciones': 'Cantidad y precision de funciones (cuenta pasos, estres, etcetera)',
                      'pantalla': 'Calidad de imagen de la pantalla y tamaño de esta',
                      'precio': 'Precio y marca del dispositivo. Aclaracion: Generalmente, a mayor importancia, se '
                                'buscaran precios mas bajos (aunque siempre se priorizara una alta relacion precio-calidad)'}
         }

    return d[producto][cust_need]

def get_usos(product):
    # Pasar a funcion aparte?
    # INTENTO AGREGAR PERFILES DE CLIENTES --> QUE SETEEN PESOS PREDETERMINADOS

    d_usos = {
        'celulares': {'Jugar': {'precio': 'Algo importante', 'bateria': 'Importante', 'camara': 'Poco importante',
                                'pantalla': 'Importante', 'memoria': 'Algo importante', 'tamaño': 'Algo importante',
                                'velocidad': 'Muy importante', 'sonido': 'Algo importante', 'diseño': 'Poco importante',
                                'sistema': 'Poco importante'},
                      'Trabajar': {'precio': 'Muy importante', 'bateria': 'Importante', 'camara': 'Algo importante',
                                   'pantalla': 'Algo importante', 'memoria': 'Importante', 'tamaño': 'Poco importante',
                                   'velocidad': 'Muy importante', 'sonido': 'Poco importante', 'diseño': 'Algo importante',
                                   'sistema': 'Poco importante'},
                      'Redes': {'precio': 'Algo importante', 'bateria': 'Importante', 'camara': 'Muy importante',
                                'pantalla': 'Algo importante', 'memoria': 'Algo importante', 'tamaño': 'Algo importante',
                                'velocidad': 'Importante', 'sonido': 'Poco importante', 'diseño': 'Algo importante',
                                'sistema': 'Poco importante'},
                      'Comunicacion': {'precio': 'Muy importante', 'bateria': 'No es importante', 'camara': 'Poco importante',
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


if __name__ == '__main__':
    main()





# col1, col2 = st.columns(2)
# col1.metric(label="Posicion", value="1")
# col2.metric(label="Alternativa", value=df_alt.loc[1])
# col2.metric("Wind", "9 mph", "-8%")


