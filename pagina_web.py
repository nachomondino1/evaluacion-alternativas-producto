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
    # Es para cada propiedad del producto. Para cada propiedad del producto j: Suma por cada req del cliente i de (Valoracion del cliente de requisito i * relacion entre req i y prop j)
    # return Diccionario con atributo
    # Defino variables
    atributos = df_relation_matrix.columns  # Atributos del producto
    customer_needs = list(df_relation_matrix.index)  # Customer needs de 1 palabra del producto
    d = {}  # inicializo diccionario a retornar

    # POR ATRIBUTO
    for atributo in atributos:

        # Reinicio variable de importancia tecnica
        imp_tecnica = 0

        # POR CUSTOMER NEED
        for customer_need in customer_needs:

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
    # valoración final = sum por cada resp técnica de una alternativa (importancia tecnica j * sentiment de respuesta técnica {segun el valor que toma dicha resp técnica}
    # Defino variables
    df = df_alt.copy()
    l_val_fin_alts = []
    l_atributos = list(df_attr_value_sent['atributo'].unique()) + list(df_attr_alt_sent['atributo'].unique())

    # POR ALTERNATIVA
    for i in range(len(df_alt)):

        # Defino variables
        val_fin_alt = 0  # Reinicio suma de valoracion final por cada alternativa
        id_alt = df_attr_alt_sent.loc[i, 'id_alternativa']
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
                # NO HAGO NADA --> justif en NDV
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
    st.sidebar.write('# Ingrese los siguientes datos')  # titulo 1 de sidebar
    client_options = ['Usuario final', 'Empresa']  # Usuario define si es empresa o usuario final
    product_options = ['Celulares', 'Smartband', 'TV']  # ['Auriculares', 'Celulares', 'Fundas de celular', 'Notebook', 'Smartband', 'Suplementos','Tablets', 'TV']  # Lista de productos
    client = st.sidebar.radio('1) ¿Que tipo de cliente eres?', client_options)  # client = st.sidebar.selectbox('1) ¿Que tipo de cliente eres?', client_options)
    product = st.sidebar.radio('2) ¿Que producto desea evaluar?', product_options)  # product = st.sidebar.selectbox('2) ¿Que producto desea evaluar?', product_options)
    product = product.lower()

    # IMPORTO ARCHIVOS UNA VEZ SELECCIONADO EL PRODUCTO
    # Archivos de (2) Data preparation
    df_alt_to_client = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_alt_cleaned_to_client.xlsx'.format(product))  # df_alt = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/{}/df_alt.xlsx'.format(product))  # correct_price
    df_alt_cleaned = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_alt_cleaned.xlsx'.format(product))
    df_cust_needs = pd.read_excel("/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_cust_needs.xlsx".format(product), index_col=0)
    # Archivos de (3) Modelling
    df_attr_alt_sent =  pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/atribucion/{}/df_attr_alt_sent.xlsx'.format(product))
    df_value_sent = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/atribucion/{}/df_attr_values_sent.xlsx'.format(product))
    df_relation_matrix = pd.read_excel("/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_relation_matrix.xlsx".format(product), index_col=0)
    df_alt_to_client_clust = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/clustering/{}/df_alt_to_client_clust.xlsx'.format(product), index_col=0)
    df_alt_per_clust = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/clustering/{}/df_alt_per_clust.xlsx'.format(product), index_col=0)
    df_centroids_values = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/clustering/{}/df_centroids_values.xlsx'.format(product), index_col=0)
    df_brand_per_cluster = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/clustering/{}/df_brand_per_cluster.xlsx'.format(product), index_col=0)

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
                 "encontrar **la mejor alternativa para usted**")

        # (2) SOLICITO PESOS DE LAS CUSTOMER NEEDS
        # Imprimo titulo
        st.write('###  Importancia de cada necesidad del cliente'.format(product))
        st.write('Ingrese la importancia que tiene para usted cada necesidad del cliente tipica de {}'.format(product))

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
            st.write('### Tabla de recomendaciones')
            st.write('Dada la importancia que le da a cada necesidad del cliente, buscamos las alternativas mas idoneas para usted')
            st.write('#### Las 10 alternativas que mas le recomendamos')
            # Calculo porcentaje de recomendacion de cada alternativa
            df_alts_recommend = create_recomendation_table(df_alt_to_client, df_alts_val_fin)   # OJO! DF_ALT TIENE ALTS QUE DF_ALT_CLEANED NO Y POR ENDE EL INDICE ES ≠

            # Selecciono las 10 alternativas de mayor porcentaje de recomendacion
            df_top_ten = df_alts_recommend.iloc[0:10, 1:]  # df_top_ten = pd.DataFrame(columns=['Marca', "Modelo", "precio", 'porcentaje_recomendacion'])
            st.dataframe(df_top_ten)

            with st.expander("Ver todas las alternativas y su grupo"):
                st.write("""La tabla de abajo muestra todas las alternativas tenidas en cuenta en el analisis.""")
                st.dataframe(df_alts_recommend)

    # SI EL CLIENTE ES UNA EMPRESA
    else:
        st.write('La herramienta tiene como objetivo identificar el **posicionamiento de las marcas de un producto '
                 'en el mercado**. Para ello, llevamos a cabo un analisis en el que agrupamos las alternativas '
                 'del producto (en este caso, {}) segun la similaridad de sus caracteristicas.'.format(product))

        image_3 = Image.open('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/p5_deployment/posicion_mercado.jpeg')
        col1, col2, col3 = st.columns([0.2, 5, 0.2])
        col2.image(image_3, use_column_width=True)

        # Le muestro resultados al cliente
        st.write('Los resultados fueron:')
        st.write("   * Nº GRUPOS: {}".format(len(df_alt_per_clust)))
        st.write("   * NOMBRES DE GRUPOS: {}".format(" - ".join(list(df_alt_per_clust.index))))

        st.write('Conozcamos que hay dentro de cada uno de estos grupos!')

        st.write('### Tabla 1: Numero de alternativas por grupo')
        st.write(" A continuacion vemos la cantidad de alternativas dentro de cada uno de estos grupos.")
        # st.bar_chart(df_alt_per_clust)
        image_5 = Image.open('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/p5_deployment/cant_alt_{}.png'.format(product))
        col1, col2, col3 = st.columns([0.2, 5, 0.2])
        col2.image(image_5, use_column_width=True)

        st.write('### Tabla 2: Numero de alternativas por grupo y marca')
        st.write(df_brand_per_cluster)

        st.write('Para visualizarlo mejor, tenemos el siguiente grafico:')
        image_4 = Image.open('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/p5_deployment/brand_{}.png'.format(product))
        col1, col2, col3 = st.columns([0.2, 5, 0.2])
        col2.image(image_4, use_column_width=True)

        st.write('### Tabla 3: Ejemplo tipico de cada grupo')  #  CENTROIDES DE CLUSTERS SEGUN VALORES DE ATRIBUTOS
        st.write(df_centroids_values)

        with st.expander("Ver todas las alternativas y su grupo"):
            st.write("""La tabla de abajo muestra todas las alternativas tenidas en cuenta en el analisis y su correspondiente grupo""")
            st.dataframe(df_alt_to_client_clust)


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
    l_cust_needs_three_words = list(df_cust_needs['cust_needs_three_words'])  # hace falta hacerles una variable? En caso de que si, las dejo aca?
    l_cust_needs_one_word = list(df_cust_needs.index)
    df_cust_needs['Peso'] = None  # Inicializo columna peso de customer needs
    temp_options = ["No es importante", 'Poco importante', 'Algo importante', 'Importante', 'Muy importante']
    d = {"No es importante": -4, 'Poco importante': 1, 'Algo importante': 4, 'Importante': 7, 'Muy importante': 12}  # antes: -10, -2.5, 0, 2.5, 10 --> no esta bien que neutral sea 0

    d_usos = get_usos(product)  # Usos del producto

    if d_usos is not None:
        col1, col2 = st.columns([2, 0.6])
        uso_selected = col2.selectbox('AYUDA: Orientacion de importancias segun uso', ['Ninguno'] + list(d_usos.keys()))
    else:
        uso_selected = 'Ninguno'

    # Si no eligio perfil de cliente
    for i in range(len(l_cust_needs_three_words)):
        # pido peso y lo guardo # peso = st.sidebar.slider(l_cust_needs_three_words[i].title(), min_value=-10, max_value=10, value=0, step=5)
        label = '{}) {}:'.format(i + 1, l_cust_needs_three_words[i].upper())
        help = get_help_button(l_cust_needs_one_word[i], product)

        # Si no se asigno un uso
        if uso_selected == "Ninguno":
            # Seteo peso en "Algo importante"
            peso = st.select_slider(label=label, options=temp_options, value="Algo importante", help=help)  # puedo agregarle help y sus palabras relacionadas por ej
        # Si se asigno uso
        else:
            # Setea pesos de uso
            uso = d_usos[uso_selected]
            peso = st.select_slider(label=label, options=temp_options, value=uso[l_cust_needs_one_word[i]], help=help)  # puedo agregarle help y sus palabras relacionadas por ej

        # Guardo peso numerico
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


