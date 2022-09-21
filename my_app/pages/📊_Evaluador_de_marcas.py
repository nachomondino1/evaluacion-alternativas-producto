# Importo librerias
import pandas as pd
import streamlit as st
from PIL import Image

# Configuración de hoja
st.set_page_config(page_title=None, page_icon=None, layout="centered", initial_sidebar_state="collapsed",
                   menu_items=None)
st.cache()

# ELEMENTOS DEL SIDEBAR
with st.sidebar:
    # Glosario
    st.subheader("Glosario")
    st.write('- *Alternativas:* las distintas opciones que tiene el cliente a la hora de comprar un producto')
    st.write('- *Necesidad del cliente:* las expresiones que los clientes utilizan para describir los productos y '
             'sus características deseables')

    # + info
    st.subheader("+ Info")
    st.info("Esta herramienta se enmarca en el proyecto final de carrera de quien les habla, Ignacio Mondino. Espero "
            "que les sirva tanto como me sirvió a mí. Pueden contactarme en el siguiente mail: nachomondino1@gmail.com")

# (1) INTRODUCCIÓN A ANALISIS
st.title('EVALUADOR DE MARCAS')  # imprimo titulo
st.write('La herramienta tiene como objetivo identificar el **posicionamiento de las marcas de un producto en el mercado**. '
         'Al final del análisis podrás contestar preguntas como:')
st.write('- ¿Qué marcas están mejor posicionadas para el consumidor?')
st.write('- ¿Qué características del producto prioriza cada marca?')
st.write('- La *marca x* ¿ofrece calidad al menor precio posible?')

image_3 = Image.open('./p5_deployment/utils/posicion_mercado.jpeg')
col1, col2, col3 = st.columns([0.2, 0.8, 0.2])
col2.image(image_3, use_column_width=True)

st.write('En dos simples pasos, podrás conocer el posicionamiento de las marcas en el mercado. Primero, seleccionás un '
         'producto y luego te mostramos los resultados.')
st.write(" ")
st.write(" ")

# (2) SOLICITO PRODUCTO
st.write('### PASO 1: ELEGÍ TU PRODUCTO')
product_options = ['', 'Celulares', 'Smartband', 'TV']  # ['Auriculares', 'Celulares', 'Fundas de celular', 'Notebook', 'Smartband', 'Suplementos','Tablets', 'TV']  # Lista de productos
product = st.selectbox('¿Qué producto deseás evaluar?',product_options)  # product = st.sidebar.selectbox('2) ¿Que producto desea evaluar?', product_options)
product = product.lower()
st.write(" ")
st.write(" ")

# SI SELECCIONO UN PRODUCTO
if product != '':
    # IMPORTO ARCHIVOS DE CLUSTERING
    df_alt_cleaned_cluster = pd.read_excel('./data/modelling/clustering/{}/df_alt_cleaned_cluster.xlsx'.format(product),index_col=0)
    df_alt_per_clust = pd.read_excel('./data/modelling/clustering/{}/df_alt_per_clust.xlsx'.format(product),index_col=0)
    df_centroids_values = pd.read_excel('./data/modelling/clustering/{}/df_centroids_values.xlsx'.format(product),index_col=0)
    df_brand_per_cluster = pd.read_excel('./data/modelling/clustering/{}/df_brand_per_cluster.xlsx'.format(product),index_col=0)
    df_best_cluster_per_cust_need = pd.read_excel('./data/modelling/clustering/{}/df_best_cluster_per_cust_need.xlsx'.format(product), index_col=0)

    # (3) MUESTRO RESULTADOS
    # Numero de grupos y sus nombres
    st.write('### PASO 2: ANÁLISIS DE RESULTADOS')

    st.write("Agrupamos todas las alternativas del producto {} según lo parecidas que son. Conociendo profundamente cada grupo "
             "y con qué grupo se identifica mayormente una marca, podremos responder a las preguntas anteriores.".format(product))
    st.write(" ")

    st.write("#### 2.1. CONOCIMIENTO DE LOS GRUPOS DE ALTERNATIVAS")
    st.write('##### Cantidad de grupos y sus nombres')
    st.write("* Nº GRUPOS: {}".format(len(df_alt_per_clust)))
    st.write("* NOMBRES DE GRUPOS:  {}".format("  -  ".join(list(df_alt_per_clust.index))))
    st.write(" ")

    # Numero de alternativas por grupo
    st.write('##### Cantidad de alternativas por grupo')  # st.write('##### Tabla 1: Número de alternativas por grupo')
    st.write("Podemos ver la cantidad de alternativas dentro de cada uno de estos grupos.")
    image_5 = Image.open('./p5_deployment/utils/cant_alt_{}.png'.format(product))  # st.bar_chart(df_alt_per_clust)
    col1, col2, col3 = st.columns([0.2, 5, 0.2])
    col2.image(image_5, use_column_width=True)
    st.write(" ")

    # Ejemplo tipico de cada grupo
    st.write('##### Alternativa típica por grupo')  #  CENTROIDES DE CLUSTERS SEGUN VALORES DE ATRIBUTOS
    st.write('En la siguiente tabla, se responde a la pregunta "¿Cómo es la alternativa típica de cada grupo?"')
    st.write(df_centroids_values)
    st.write(" ")

    st.write('##### Posición de cada grupo en las necesidades del cliente')  # st.write('##### Tabla 4: Mejores marcas por necesidad del cliente')
    # Mejores marcas por necesidad del cliente
    st.write("A continuación, podrá ver las mejores marcas por necesidad del cliente")
    st.dataframe(df_best_cluster_per_cust_need)
    st.write(" ")
    st.write(" ")

    st.write("#### 2.2. DISTRIBUCIÓN DE MARCAS EN GRUPOS")
    # Distribucion de marcas en grupos
    st.write('¿Con qué grupo se identifica más cada marca?')

    # Tabla y Grafico
    tab1, tab2 = st.tabs(["Tabla", "Gráfico"])
    with tab1:
        st.write(df_brand_per_cluster)
    with tab2:
        image_4 = Image.open('./p5_deployment/utils/brand_{}.png'.format(product))
        col1, col2, col3 = st.columns([0.2, 5, 0.2])
        col2.image(image_4, use_column_width=True)

        with st.expander("Ayuda en interpretacion del gráfico", expanded=False):
            st.write('* Marcas con mayor cantidad de verde -->  marcas con mejor relación precio-calidad')
            st.write('* Marcas con mayor cantidad de amarillo - naranja -->  marcas con relación precio-calidad media')
            st.write('* Marcas con mayor cantidad de rojo -->  marcas con peor relación precio-calidad')

    # Listado de todas las alternativas tenidas en cuenta en el analisis
    with st.expander("Ver todas las alternativas tenidas en cuenta en el análisis"):
        st.write("Acá, podrás ver todas las alternativas con las que trabajó la herramienta para que puedas"
                 "verificar que no falta ninguna.")
        st.dataframe(df_alt_cleaned_cluster.iloc[:, 1:])