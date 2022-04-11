"""
Pseudocodigo de lo que quisiera que haga para un usuario final:
# Búsqueda del cliente
# Le muestro customer needs al cliente (ya extraidas) para que establezca el peso a cada una.
# Llamara a algoritmo que haga el calculo de la importancia tecnica, luego calcule la valoracion final de cada publicacion
# Otro algoritmo calculara el % de recomendacion y le mostrará en formato tabla los resultados (dicha tabla tendra filtros para que el cliente pueda interactuar con precio, estado, etc)
"""


# Importo librerias
# import streamlit as st antes hacer pip install streamlit (hacerlo dsp de virtual env)
import pandas as pd
import streamlit as st

def main():
    data = {}

    # titulo
    st.title('EVALUACION AUTOMATICA DE ALTERNATIVAS EN PROCESO DE COMPRA')

    # titulo de sidebar
    st.sidebar.header('Entrada de datos de usuario')

    # Usuario define si es empresa o usuario final
    client_options = ['Usuario final', 'Empresa']
    client = st.sidebar.selectbox('¿Que tipo de cliente eres?', client_options)

    # Lista de productos
    product_options = ['Celulares', 'TV', 'Smartband']
    product = st.sidebar.selectbox('¿Que producto desea evaluar?', product_options)

    # Abrir archivo de sentiment segun producto

    # Solicito peso de customer needs if cliente es usuario final
    if client == 'Usuario final':

        st.sidebar.subheader('Ingrese cuan de acuerdo esta con cada necesidad del cliente')

        # Abrir archivo de customer needs segun producto
        customer_needs = ['relacion precio calidad','bateria dura mucho','tiene buena camara','tiene buena memoria',
                          'tiene buen tamaño', 'pantalla ve bien', 'tiene buena resolucion']

        for i in range(len(customer_needs)):
            peso = st.sidebar.slider(customer_needs[i].title(), 0, 10,1)
            data[customer_needs[i]] = peso

        df = pd.DataFrame(data, index=[0])
        st.subheader(data)
        st.subheader(df)

    # def processing

    # importar matriz de relaciones

    def importancia_tecnica(customer_needs_weights, relation_matrix):
        # Es para cada propiedad del producto. Para cada propiedad del producto j: Suma por cada req del cliente i de (Valoracion del cliente de requisito i * relacion entre req i y prop j)
        # return Diccionario con atributo

        attributes = relation_matrix.columns
        customer_needs = relation_matrix.index

        d = {}

        # Por atributo
        for atributo in attributes:

            # defino variable de importancia tecnica
            imp_tecnica = 0

            for customer_need in customer_needs:

                # defino relacion entre atributo y customer need
                relacion = relation_matrix.loc[customer_need, atributo]

                # calculo importancia tecnica
                prod = customer_needs_weights[customer_need] * relacion # deeberia ser contains(customer_need) pues una es de 1 palabra y la otra de 3.

            imp_tecnica += prod
            d[atributo] = imp_tecnica

        return d

    # importar df_sent por valor de atrib

    def calculate_valoracion_final(df_modelo, df_sent, importancia_tecnica):
        # valoración final = sum por cada resp técnica de una alternativa (importancia tecnica j * sentiment de respuesta técnica {segun el valor que toma dicha resp técnica}
        # return df con modelo y su valoracion final
        df = df_modelo.copy()
        df['val_final'] = 0  # agrego columna de valoracion final

        # Por modelo o alternativa
        for i in range(len(df_modelo)):

            # defino valoracion final
            val_final = 0

            # Agarro un modelo
            modelo = df_modelo.iloc[i]

            # Por atributo
            for atributo in importancia_tecnica.keys():
                idx_atrib = df_modelo.columns.get_loc(atributo)  # es una idea aplicable a varias funciones que ya hice

                # Obtengo valor del atributo
                valor = df_modelo.iloc[i, idx_atrib]

                # Obtengo sentiment del valor del atributo
                df_sent_filtro = df_sent[df_sent['atributo'==atributo]]
                df_sent_filtro2 = df_sent_filtro[df_sent_filtro['valor'==valor]]
                cant_opi = df_sent_filtro['cant_opi']
                sent = df_sent_filtro['sentiment']

                val_final += sent * importancia_tecnica[atributo]

            # Guardo modelo y su valoracion final
            idx_val_final = df_modelo.columns.get_loc('val_final')  # es una idea aplicable a varias funciones que ya hice
            df.iloc[i, idx_val_final] = val_final

        return df

    # si es cliente
    if client == 'Usuario final':

        # Calculo importancia tecnica de cada atributo segun necesidades del cliente
        imp_tecnica = importancia_tecnica(data, relation_matrix)

        # Calculo valoracion final de cada alternativa
        calculate_valoracion_final(df_modelo, df_sent, imp_tecnica)

        # Muestro tabla de recomendacion


    # si es empresa
    else:
        # clustering() --> ojo que solo usa dataframe atribuido a customer needs
        # Debera agrupar sentiment de una misma alternativa o modelo y luego agrupare las alternativas qie se asemejan

        # show results
        pass


if __name__ == '__main__':
    main()