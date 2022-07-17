# Importo librerias
import streamlit as st
from PIL import Image

def main():
    # Defino variables
    st.set_page_config(page_title=None, page_icon=None, layout="centered", initial_sidebar_state="collapsed", menu_items=None)

    # ELEMENTOS DEL SIDEBAR
    with st.sidebar:
        # + Info
        st.subheader("+ Info")
        st.info("Esta herramienta se enmarca en el proyecto final de carrera de quien les habla, Ignacio Mondino. Espero "
                "que les sirva tanto como me sirvió a mí. Pueden contactarme en el siguiente mail: nachomondino1@gmail.com")

    st.header('LA OPCION IDEAL DEL PRODUCTO PARA VOS')  # imprimo titulo  # # st.title('EVALUACION AUTOMATICA DE ALTERNATIVAS EN PROCESO DE COMPRA')

    # ESCRIBO INTRODUCCION AL PROBLEMA QUE RESUELVE LA HERRAMIENTA
    st.write("Quedate con la tranquilidad de elegir la opcion optima de un producto para vos ahorrando mucho tiempo y "
             "estres.")
    st.markdown("---")

    st.write("Actualmente, disponemos de dos herramientas que facilitan la elección de una alternativa en la compra de "
             "un producto. Estas son:")
    image_1 = Image.open('./p5_deployment/utils/alternativas_posibles.png') # Imagen de persona antes ≠ alternativas
    image_2 = Image.open('./p5_deployment/utils/posicion_mercado.jpeg') # Imagen de persona antes ≠ alternativas
    col1, col2, col3, col4, col5 = st.columns([0.2, 3.19, 0.2, 4, 0.2])
    col2.image(image_1, use_column_width=True, caption="Evaluación de alternativas")
    col4.image(image_2, use_column_width=True, caption="Posicionamiento de marcas")
    st.write(" ")

    st.write("A su vez, los productos relevados son:")
    image_3 = Image.open('./p5_deployment/utils/producto_celulares.jpeg')  # Imagen de persona antes ≠ alternativas
    image_4 = Image.open('./p5_deployment/utils/producto_smartband.jpeg')  # Imagen de persona antes ≠ alternativas
    image_5 = Image.open('./p5_deployment/utils/producto_tv.webp')  # Imagen de persona antes ≠ alternativa
    col1, col2, col3, col4, col5, col6, col7 = st.columns([0.2, 3, 0.2, 2, 0.2, 3.7, 0.2])
    col2.image(image_3, use_column_width=True, caption="Celular")
    col4.image(image_4, use_column_width=True, caption="Smartband")
    col6.image(image_5, use_column_width=True, caption="Televisor")

    st.write(" ")


if __name__ == '__main__':
    main()
