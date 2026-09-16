# Importo librerias
import streamlit as st

RENDER_URL = "https://evaluacion-alternativas-producto.onrender.com"


def main():
    st.set_page_config(page_title="Nos mudamos", page_icon="🔀", layout="centered")
    st.markdown(f'<meta http-equiv="refresh" content="3;url={RENDER_URL}">', unsafe_allow_html=True)

    st.title("¡Nos mudamos!")
    st.write("Esta herramienta se movió a un nuevo lugar. Si no te redirige solo en unos segundos, entrá manualmente:")
    st.markdown(f"### [Ir a Evaluador de alternativas]({RENDER_URL})")


if __name__ == '__main__':
    main()
