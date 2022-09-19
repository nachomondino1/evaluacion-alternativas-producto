# Importo librerias
import streamlit as st
from PIL import Image

def main():
    # Defino variables
    st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="expanded", menu_items=None)

    # ELEMENTOS DEL SIDEBAR
    with st.sidebar:
        # + Info
        st.subheader("+ Info")
        st.info("Estas herramientas se enmarcan en el proyecto final de carrera de quien les habla, Ignacio Mondino. Espero "
                "que les sirva tanto como me sirvió a mí. Pueden contactarme en el siguiente mail: nachomondino1@gmail.com")

    # Imprimo titulo
    st.header('COMPRAR NUNCA FUE TAN FÁCIL')  # st.title('EVALUACION AUTOMATICA DE ALTERNATIVAS EN PROCESO DE COMPRA')

    # ESCRIBO INTRODUCCION AL PROBLEMA QUE RESUELVE LA HERRAMIENTA
    st.write("Quedate con la tranquilidad de elegir la opción óptima de un producto ahorrando mucho tiempo y estrés.")
    image_0 = Image.open('./p5_deployment/utils/prueba.png')
    st.image(image_0, use_column_width=True)
    st.markdown("---")

    st.write("Actualmente, disponemos de dos herramientas que facilitan la elección de una alternativa en la compra de "
             "un producto. Éstas son:")
    image_1 = Image.open('./p5_deployment/utils/alternativas_posibles.png')
    image_2 = Image.open('./p5_deployment/utils/posicion_mercado.jpeg')
    col1, col2, col3, col4, col5 = st.columns([0.2, 3.19, 0.2, 4, 0.2])
    col2.image(image_1, use_column_width=True, caption="Evaluador de alternativas")
    col4.image(image_2, use_column_width=True, caption="Evaluador de marcas")
    st.write(" ")

    st.write("A su vez, los productos relevados son:")
    image_3 = Image.open('./p5_deployment/utils/celular.jpeg')
    image_4 = Image.open('./p5_deployment/utils/smartband.jpeg')
    image_5 = Image.open('./p5_deployment/utils/tv.jpeg')
    col1, col2, col3, col4, col5, col6, col7 = st.columns([0.2, 2, 0.2, 2, 0.2, 2, 0.2])
    col2.image(image_3, use_column_width=True, caption="Celular")
    col4.image(image_4, use_column_width=True, caption="Smartband")
    col6.image(image_5, use_column_width=True, caption="Televisor")

    st.write(" ")


if __name__ == '__main__':
    main()
