# Importo librerias
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode


def c(customer_needs, customer_needs_substring):
    for customer_need in customer_needs:

        if customer_needs_substring in customer_need:
            return customer_need

def calculate_importancia_tecnica(customer_needs_weights, relation_matrix):
    # Es para cada propiedad del producto. Para cada propiedad del producto j: Suma por cada req del cliente i de (Valoracion del cliente de requisito i * relacion entre req i y prop j)
    # return Diccionario con atributo

    # Defino variables
    attributes = relation_matrix.columns
    customer_needs = list(relation_matrix.index)  # Son customer needs de 1 sola palabra
    d = {}

    # Por atributo
    for atributo in attributes:

        # Reinicio variable de importancia tecnica
        imp_tecnica = 0

        # Por customer need
        for customer_need in customer_needs:
            # print(customer_need, atributo)

            # defino relacion entre atributo y customer need
            idx_customer_need = customer_needs.index(customer_need)
            idx_attr = relation_matrix.columns.get_loc(atributo) # agrega flexibilidad pues puedo pasarle el df_opiniones enterro e igual usa solo "opiniones"
            # print(idx_customer_need, idx_attr)
            relacion = relation_matrix.iloc[idx_customer_need, idx_attr]

            # calculo importancia tecnica
            customer_need_three_words = c(customer_needs_weights.keys(), customer_need)
            # print(customer_need_three_words)
            # print(customer_needs_weights[customer_need_three_words])
            # print("relacion:", relacion)
            imp_tecnica += customer_needs_weights[customer_need_three_words] * relacion  # deeberia ser contains(customer_need) pues una es de 1 palabra y la otra de 3.

        d[atributo] = imp_tecnica

    return d

def calculate_valoracion_final(df_modelos, df_sent_attr_val, importancia_tecnica):
    # valoración final = sum por cada resp técnica de una alternativa (importancia tecnica j * sentiment de respuesta técnica {segun el valor que toma dicha resp técnica}
    # return df con modelo y su valoracion final

    # Defino variables
    df = df_modelos.copy()
    valores_fin = []

    # Por la cantidad de modelos de haya
    for i in range(len(df_modelos)):
        print("CAMBIO DE MODELO. Nº:", i)

        # defino valoracion final
        valor_final = 0
        valores_nan = 0

        # Por atributo
        # for atributo in importancia_tecnica.keys():
        for atributo in df_sent_attr_val['campo_especifico'].unique():  # ingreso solo a atributos que tienen al menos una relacion
            print("ATRIBUTO:", atributo)

            # Obtengo valor para ese atributo de ese modelo
            idx_atrib = df_modelos.columns.get_loc(atributo)  # es una idea aplicable a varias funciones que ya hice
            valor_attr = df_modelos.iloc[i, idx_atrib]

            # si el atributo tiene valor nan
            if str(valor_attr) == 'nan':
                # Obtengo el sentiment minimo para dicho atributo
                min_prom_sent = df_sent_attr_val[df_sent_attr_val['campo_especifico'] == atributo]["prom_sent"].min()

                print("El modelo Nº{} tiene valor NaN en atributo {}, por lo cual, le asigno el peor sentiment {} de"
                      "los valores de dicho atributo".format(i, atributo, min_prom_sent))

                # Calculo valoracion final
                valor_final += min_prom_sent * importancia_tecnica[atributo]

            # si el atributo tiene valor
            else:
                # Obtengo sentiment del valor del atributo
                df_sent_attr_val_filtrado = df_sent_attr_val[(df_sent_attr_val['campo_especifico'] == atributo) &
                                        (df_sent_attr_val['valor'] == valor_attr)]
                print(df_sent_attr_val_filtrado)

                # Calculo valoracion final parcial
                # si el valor no tiene score
                idx_prom_sent = df_sent_attr_val.columns.get_loc("prom_sent")  # agrega flexibilidad pues puedo pasarle el df_opiniones enterro e igual usa solo "opiniones"
                if str(df_sent_attr_val_filtrado.iloc[0,idx_prom_sent]) == 'nan':
                    valores_nan += 1

                # si el valor tiene score
                else:  #adentro hacia un try-except pero al parecer ya no lo necesito

                    sent = df_sent_attr_val_filtrado.iloc[0,idx_prom_sent]
                    valor_final += sent * importancia_tecnica[atributo]
                    # print(sent * importancia_tecnica[atributo], valor_final)
                    # print(sent, importancia_tecnica[atributo], valor_final)

        # Guardo modelo y su valoracion final
        a = valor_final / (len(df_sent_attr_val['campo_especifico'].unique()) - valores_nan)
        print('Valor final =', valor_final, ' Cantidad de valores =', len(df_sent_attr_val['campo_especifico'].unique()),
              'Cantidad de valores nan = ',valores_nan, 'Valor final / (cant valores - cant val nan) = ', a)
        valores_fin.append(a)

    # Agrego columna al dataframe modelos
    df['val_final'] = valores_fin
    print(valores_fin)

    return df

def recommend_table(df_mod_original, df_mod_val_final):

    # deberia mostrar los valores reales de los modelos antes de limpiarlos... (y sin id_publicacion)

    # Ordeno los dataframes del mismo modo
    df_mod_original = df_mod_original.sort_values(by=['id_publicacion'])
    df_mod_val_final = df_mod_val_final.sort_values(by=['id_publicacion'])
    print(df_mod_original)
    print(df_mod_val_final)

    val_max = df_mod_val_final['val_final'].max()
    idx = df_mod_val_final.columns.get_loc('val_final')
    l_porc_recom = []

    for i in range(len(df_mod_val_final)):
        val_fin = df_mod_val_final.iloc[i, idx]
        porc_recom = round(val_fin / val_max * 100, 1)
        l_porc_recom.append(porc_recom)

    df_mod_original['val_final'] = l_porc_recom
    df_mod_original = df_mod_original.sort_values('val_final', ascending=False)

    return df_mod_original

def aggrid_interactive_table(df: pd.DataFrame):
    # https://share.streamlit.io/streamlit/example-app-interactive-table/main
    """Creates an st-aggrid interactive table based on a dataframe.

    Args:
        df (pd.DataFrame]): Source dataframe

    Returns:
        dict: The selected row
    """
    options = GridOptionsBuilder.from_dataframe(
        df, enableRowGroup=True, enableValue=True, enablePivot=True
    )

    options.configure_side_bar()

    options.configure_selection("single")
    selection = AgGrid(
        df,
        enable_enterprise_modules=True,
        gridOptions=options.build(),
        theme="light",
        update_mode=GridUpdateMode.MODEL_CHANGED,
        allow_unsafe_jscode=True,
    )

    return selection

def main():
    customer_needs_weights = {}

    # titulo
    st.title('EVALUACION AUTOMATICA DE ALTERNATIVAS EN PROCESO DE COMPRA')

    st.sidebar.write('# Ingrese los siguientes datos')

    # Ingreso de datos del cliente: tipo de cliente y producto a relevar
    client_options = ['Usuario final', 'Empresa']  # Usuario define si es empresa o usuario final
    product_options = ['Celulares', 'TV', 'Smartband']  # Lista de productos

    client = st.sidebar.radio('1) ¿Que tipo de cliente eres?', client_options)  # client = st.sidebar.selectbox('¿Que tipo de cliente eres?', client_options)

    product = st.sidebar.radio('2) ¿Que producto desea evaluar?', product_options)  # product = st.sidebar.selectbox('¿Que producto desea evaluar?', product_options)

    # Abrir archivo de sentiment segun producto

    # Si el cliente es usuario final
    if client == 'Usuario final':

        # SOLICITO PESOS DE LAS CUSTOMER NEEDS
        # Imprimo titulo
        # st.sidebar.write('## Ingrese la importancia que usted le da a cada necesidad del cliente tipica de {}'.format(product.lower()))
        st.write('## Ingrese la importancia que usted le da a cada necesidad del cliente tipica de {}'.format(product.lower()))

        # Importar customer needs segun producto
        customer_needs = ['relacion precio calidad','bateria dura mucho','tiene buena camara','tiene buena memoria',
                          'tiene buen tamaño', 'pantalla ve bien', 'tiene buena resolucion']

        # Por customer need
        for i in range(len(customer_needs)):
            # pido un peso y lo guardo
            peso = st.slider(customer_needs[i].title(), min_value=0, max_value=10, value=0, step=1)
            customer_needs_weights[customer_needs[i]] = peso
        df = pd.DataFrame(customer_needs_weights, index=[0])  # por algun motivo no se hace bien... aunque el dic si
        # st.write(df)

        # PROCESAMIENTO DE PESOS Y DATOS
        # importar matriz de relaciones
        # relation_matrix = pd.read_excel('/Users/nachomondino/Desktop/relations_matrixes.xlsx')  # dsp la importare desde otro lugar
        # relation_matrix = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/relation_matrix.xlsx', index_col=0)  # dsp la importare desde otro lugar
        relation_matrix = pd.read_excel('/Users/nachomondino/Desktop/relations_matrixes.xlsx', index_col=0)  # dsp la importare desde otro lugar
        print(relation_matrix)

        # Calculo importancia tecnica de cada atributo segun necesidades del cliente
        imp_tecnica_attr = calculate_importancia_tecnica(customer_needs_weights, relation_matrix)
        print(imp_tecnica_attr)

        # Importo archivos
        df_modelos = pd.read_excel('/Users/nachomondino/Desktop/df_modelos_cleaned.xlsx')
        print(df_modelos)
        # df_sent_attr_val = pd.read_excel('/Users/nachomondino/Desktop/df_attr_value_sent.xlsx', index_col=0)
        df_sent_attr_val = pd.read_excel('/Users/nachomondino/Desktop/df_ponderado.xlsx', index_col=0)
        print(df_sent_attr_val)

        # Calculo valoracion final de cada alternativa
        df = calculate_valoracion_final(df_modelos, df_sent_attr_val, imp_tecnica_attr)
        # df.to_excel('/Users/nachomondino/Desktop/df_valoracion_final.xlsx', 'Hoja de datos', index=False)

        # Presentación de resultados dinámicos
        # Muestro tabla de recomendacion
        st.write('## Tabla de recomendaciones')
        st.write('Dada la importancia que le da a cada necesidad del cliente, buscamos las alternativas mas idoneas '
                 'para usted')

        df_modelos_original = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_modelos_celulares.xlsx', 'Hoja de datos')
        # df_modelos_original['precio'] = show_correct_price(df_modelos_original['precio'])
        df2 = recommend_table(df_modelos_original, df)
        # df2.to_excel('/Users/nachomondino/Desktop/df_valoracion_final_recommend.xlsx', 'Hoja de datos', index=False)

        # Aca mostraria los 10 mas recomendados...
        st.write('#### Las 10 alternativas que mas le recomendamos')
        st.write(df2.loc[:,['Marca', "precio",'val_final']])

        # Aca mostraria los resultados completos
        st.write('#### Todas las alternativas')
        selection = aggrid_interactive_table(df=df2)

    # si es empresa
    else:
        # Importo resultados de clustering
        # df_clustering = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_clustering_labels.xlsx', 'Hoja de datos')

        # Le muestro resultados al cliente
        st.write('## Tabla 1: Promedio de scores por grupo')
        df_clustering = pd.read_excel('/Users/nachomondino/Desktop/df_clustering_prueba.xlsx',index_col=0)
        st.write(df_clustering)

        st.write('## Tabla 2: Promedio de valores por grupo')

        st.write('## Tabla 3: Marcas por grupo')

        st.write('## Tabla 4: Alternativas por grupo')



        # st.write(df_clustering)
        pass












def show_correct_price(col_precio):  #seguro la saco...
    """
    Corrige columna precio dado que el punto es entendido como una coma (Por ejemplo, 20.000 los entiende como 20)
    :param col_precio: Columna precio
    :return: Columna precio corregida
    """
    l_precios = []

    # Por cada valor de columna precio
    for i in range(len(col_precio)):

         # Intento corregir el valor
        try:
            # Saco el punto
            correct_value = int(col_precio.iloc[i]) * 1000 #siempre use espacio en blanco

            l_precios.append(correct_value)

        # Excepto que es nan
        except ValueError:  # cannot convert float NaN to integer
            # No corrigo nada
            l_precios.append(0)  # asigno 0 en lugar de None pues sino si o si seria dtype float64 pues el NaN es un float64 y mostraria mal los numeros enteeros..

    # Guardo nueva columna precio
    new_col_precio = pd.Series(l_precios)  #si o si sera dtype float64 pues el NaN es un float64
    print("Se corrigio el precio correctamente ")
    return new_col_precio #antes devolcia col_precio

if __name__ == '__main__':
    main()
