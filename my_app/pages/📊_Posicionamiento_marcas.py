# Importo librerias
import pandas as pd
import streamlit as st
from PIL import Image

# ELEMENTOS DEL SIDEBAR
with st.sidebar:
    # + info
    st.subheader("+ Info")
    st.info("Esta herramienta se enmarca en el proyecto final de carrera de quien les habla, Ignacio Mondino. Espero "
            "que les sirva tanto como me sirvió a mí. Pueden contactarme en el siguiente mail: nachomondino1@gmail.com")

# (1) INTRODUCCIÓN A ANALISIS
st.header('POSICIONAMIENTO DE MARCAS')  # imprimo titulo
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
product_options = ['', 'Celulares', 'Smartband', 'TV']  # ['Auriculares', 'Celulares', 'Fundas de celular', 'Notebook', 'Smartband', 'Suplementos','Tablets', 'TV']  # Lista de productos
product = st.selectbox('¿Que producto desea evaluar?',product_options)  # product = st.sidebar.selectbox('2) ¿Que producto desea evaluar?', product_options)
product = product.lower()

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
    st.write('##### Alternativa tipica por grupo')  #  CENTROIDES DE CLUSTERS SEGUN VALORES DE ATRIBUTOS
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