# Importo librerias
import pandas as pd
import streamlit as st
#from st_aggrid import AgGrid, GridOptionsBuilder
#from st_aggrid.shared import GridUpdateMode


def get_attrs_technical_importance(df_cust_needs, df_relation_matrix):
    """
    Obtiene la importancia tecnica de cada atributo del producto
    :param df_cust_needs: Dataframe con peso
    :param relation_matrix: Dataframe
    :return: Diccionario
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

def get_alts_final_value(df_alt, df_value_sent, d_attrs_tech_imp):
    """
    Obtienen valoracion final de cada alternativa del producto
    :param df_alt: Dataframe
    :param df_value_sent: Dataframe
    :param d_attrs_tech_imp: Diccionario
    :return: Dataframe alternativas con columna adicional de valoracion final
    """
    # valoración final = sum por cada resp técnica de una alternativa (importancia tecnica j * sentiment de respuesta técnica {segun el valor que toma dicha resp técnica}
    # return df con modelo y su valoracion final
    # Defino variables
    df = df_alt.copy()
    val_fin_alts = []
    atributos = df_value_sent['atributo'].unique()

    # POR ALTERNATIVA
    for i in range(len(df_alt)):
        print("ALTERNATIVA Nº: {}".format(i).center(120))

        # Defino variables
        sum_val_fin_alt = 0  # Reinicio suma de valoracion final por cada alternativa
        n_val_sent_nan = 0  # Reinicio numero de valores cuyo sentiment es nan

        # POR ATRIBUTO
        for atributo in atributos:  # ingreso solo a atributos que tienen al menos una relacion

            imp_tecnica_attr = d_attrs_tech_imp[atributo]

            # NO DEBERIA HACER UN IF IMPORTANCIA TECNICA DEL ATTR > 0????? PUES AL TENER IMP TEC 0 AFRCTA VALORACION FINAL
            if imp_tecnica_attr > 0: # prueba

                # OBTENGO VALOR DEL ATRIBUTO
                valor = df_alt.loc[i, atributo]

                print("ATRIBUTO: {} , VALOR: {}".format(atributo, valor))

                # SI EL VALOR NO ES NAN (la alternativa puede no tener valor para el atributo)
                if str(valor) != 'nan':

                    # OBTENGO SENTIMENT DEL VALOR
                    sent_valor = float(df_value_sent[(df_value_sent['atributo'] == atributo) & (df_value_sent['valor'] == valor)]['sent'])

                    # SI EL SENTIMENT DEL VALOR NO ES NAN
                    if str(sent_valor) != 'nan':


                        # CALCULO VALORACION FINAL DEL ATRIBUTO
                        sum_val_fin_alt += sent_valor * d_attrs_tech_imp[atributo]
                        # print(sent, importancia_tecnica[atributo], valor_final)

                        print(sent_valor,d_attrs_tech_imp[atributo], sum_val_fin_alt)


                    # SI EL SENTIMENT DEL VALOR ES NAN
                    else:  # DEBO PENSAR SI DEJAR SENT NAN O ASIGNARLES SENT MIN PORQUE AL SER VALORACIONES NEGATIVAS FAVOREZCO LAS ALT QUE TIENE VALORES QUE TIENEN SENT NAN
                        # SUMO 1 A CANTIDAD DE VALORES SIN SENTIMENT DE LA ALTERNATIVA
                        n_val_sent_nan += 1

                        # PRUEBA: QUE PASA SI ASIGNO SENTIMENT MIN A LOS VALORES CUYO SENT ES NAN
                        worst_sent = df_value_sent[df_value_sent['atributo'] == atributo]["sent"].min()
                        sum_val_fin_alt += worst_sent * d_attrs_tech_imp[atributo]

                        print(worst_sent,d_attrs_tech_imp[atributo], sum_val_fin_alt)

                        print("El atributo {} toma valor {} y este tiene sentiment NaN".format(atributo, valor))

                # SI EL VALOR ES NAN
                else:
                    # OBTENGO EL PEOR SENTIMENT DEL ATRIBUTO
                    worst_sent = df_value_sent[df_value_sent['atributo'] == atributo]["sent"].min()
                    print("El modelo Nº{} tiene valor NaN en atributo {}, por lo cual, le asigno el peor sentiment {} de"
                          "los valores de dicho atributo".format(i, atributo, worst_sent))

                    # CALCULO VALORACION FINAL DEL ATRIBUTO
                    sum_val_fin_alt += worst_sent * d_attrs_tech_imp[atributo]

                    print(worst_sent, d_attrs_tech_imp[atributo], sum_val_fin_alt)

        # PONDERO VALORACION FINAL DE LA ALTERNATIVA SEGUN CANTIDAD DE VALORES NAN
        val_fin_alt = sum_val_fin_alt #/ (len(atributos) - n_val_sent_nan)

        # print('Valor final =', val_fin_alt, ' Cantidad de valores =', len(atributos),'Cantidad de valores sin sent =', n_val_sent_nan, 'Valor final / (cant valores - cant val nan) = ', val_fin_alt) #_2

        # GUARDO ALTERNATIVA Y SU VALORACION FINAL
        val_fin_alts.append(val_fin_alt)

    # Agrego columna al dataframe alternativas
    df['val_final'] = val_fin_alts
    print(val_fin_alts)

    return df

def recommend_table(df_alt, df_alt_val_final):  # FUNCIONA MAL, EL DF_ALT_VAL_FINAL ESTA ORDENADO POR VAL FINAL...
    """
    Obtiene porcentaje de recomendacion de cada alternativa
    :param df_alt:# deberia mostrar los valores reales de los modelos antes de limpiarlos... (y sin id_publicacion)
    :param df_alt_val_final:
    :return: Dataframe alternativas con columna porcentaje de recomendacion y ordenado segun esta
    """
    # Defino variables
    val_max = df_alt_val_final['val_final'].dropna().max()
    l_porc_recom = []

    df_alt['porcentaje_recomendacion'] = None

    # POR ALTERNATIVA
    # for i in range(len(df_alt)):
    for id_alt in df_alt_val_final['id_alternativa']:

        idx_1 = df_alt.index[df_alt['id_alternativa'] == id_alt][0]
        idx_2 = df_alt_val_final.index[df_alt_val_final['id_alternativa'] == id_alt][0]

        val_alt = df_alt_val_final.loc[idx_2, 'val_final']

        # OBTENGO SU VALORACION FINAL
        # val_fin = df_alt_val_final.loc[i, 'val_final']

        # CALCULO PORCENTAJE DE RECOMENDACION
        # Si la valoracion maxima es positiva
        if val_max > 0:
            # Calculo porcentaje de recomendacion de alternaitva con ecuacion
            porc_recom = round(val_alt / val_max * 100, 1)  # 3 / 5 = 0.6
        # Si la valoracion maxima es negativa
        else:
            # Calculo porcentaje de recomendacion de alternaitva con otra ecuacion
            porc_recom = round(val_max / val_alt * 100, 1)  # -3 / -5 = -0.6 pero -5 no puede ser val_max sino que seria el -3, en ese caso, -5 / -3 = 1.66

        # l_porc_recom.append(porc_recom)
        # df_alt.loc[i, "porcentaje_recomendacion"] = porc_recom
        df_alt.loc[idx_1, "porcentaje_recomendacion"] = porc_recom
        print(val_alt, val_max, porc_recom)

    # GUARDO PORCENTAJES DE RECOMENDACION DE LAS ALTERNITVAS
    # df_alt['porcentaje_recomendacion'] = l_porc_recom
    df_alt = df_alt.sort_values('porcentaje_recomendacion', ascending=False)
    st.write(df_alt)

    return df_alt

'''
def aggrid_interactive_table(df: pd.DataFrame):
    """
    Creates an st-aggrid interactive table based on a dataframe.
    :param df: Source dataframe
    :return:         # dict: The selected row
    """
    # https://share.streamlit.io/streamlit/example-app-interactive-table/main
    options = GridOptionsBuilder.from_dataframe(df, enableRowGroup=True, enableValue=True, enablePivot=True)

    options.configure_side_bar()

    options.configure_selection("single")
    selection = AgGrid(df, enable_enterprise_modules=True, gridOptions=options.build(), theme="light",
                       update_mode=GridUpdateMode.MODEL_CHANGED, allow_unsafe_jscode=True)
    return selection
'''


def main():
    # (1) SOLICITO INGRESO DE DATOS EN SIDEBAR (tipo de cliente y producto a relevar)
    st.title('EVALUACION AUTOMATICA DE ALTERNATIVAS EN PROCESO DE COMPRA')  # imprimo titulo
    st.sidebar.write('# Ingrese los siguientes datos')  # titulo 1 de sidebar
    client_options = ['Usuario final', 'Empresa']  # Usuario define si es empresa o usuario final
    product_options = ['Auriculares', 'Celulares', 'Fundas de celular', 'Notebook', 'Smartband', 'Suplementos','Tablets', 'TV']  # Lista de productos
    client = st.sidebar.selectbox('1) ¿Que tipo de cliente eres?', client_options)  #  client = st.sidebar.radio('1) ¿Que tipo de cliente eres?', client_options)
    product = st.sidebar.selectbox('2) ¿Que producto desea evaluar?', product_options)  # product = st.sidebar.radio('2) ¿Que producto desea evaluar?', product_options)
    product = product.lower()

    # IMPORTO ARCHIVOS UNA VEZ SELECCIONADO EL PRODUCTO
    # Archivos de (2) Data preparation
    df_alt = pd.read_excel('evaluacion-compra-automatica/data/collect_initial_data/{}/df_alt_formated.xlsx'.format(product))  # correct_price
    df_alt = pd.read_excel('//data/data_preparation/{}/df_alt_formated.xlsx'.format(product)) # correct_price
    df_alt_cleaned = pd.read_excel('//data/data_preparation/{}/df_alt_cleaned.xlsx'.format(product))
    df_cust_needs = pd.read_excel("//data/data_preparation/{}/df_cust_needs.xlsx".format(product), index_col=0)
    # Si funciona l_cust_needs, borro estas lineas pues no hace falta exportar cust needs sino que las obtengo de matriz de relaciones...  --> necesito si o si las cust needs de 3 palabras y e esas no estan en matriz de relaciones
    # Archivos de (3) Modelling
    df_relation_matrix = pd.read_excel("//data/data_preparation/{}/df_relation_matrix.xlsx".format(product), index_col=0)
    df_alt_clust = pd.read_excel('//data/modelling/clustering/{}/df_alt_clust.xlsx'.format(product), index_col=0)
    df_alt_per_clust = pd.read_excel('//data/modelling/clustering/{}/df_alt_per_clust.xlsx'.format(product), index_col=0)
    df_centroids_values = pd.read_excel('//data/modelling/clustering/{}/df_centroids_values.xlsx'.format(product), index_col=0)
    df_brand_per_cluster = pd.read_excel('//data/modelling/clustering/{}/df_brand_per_cluster.xlsx'.format(product), index_col=0)

    # l_cust_needs = list(df_relation_matrix.index)
    df_value_sent = pd.read_excel('//data/modelling/atribucion/{}/df_attr_values_sent.xlsx'.format(product))

    print(df_alt.shape)
    # Selecciono ids de alternativas que no han sido borradas
    ids_cleaned = df_alt_cleaned["id_alternativa"].unique()
    # Filtro dataframe alternativas por ids
    df_alt = df_alt[df_alt.id_alternativa.isin(ids_cleaned)]
    df_alt = df_alt.reset_index(drop=True)  # el dropna me borra una fila y los indices quedan mal...
    print(df_alt.shape)


    # SI EL CLIENTE ES UN USUARIO FINAL
    if client == 'Usuario final':

        # (2) SOLICITO PESOS DE LAS CUSTOMER NEEDS
        # Imprimo titulo
        st.sidebar.write('## Ingrese la importancia que usted le da a cada necesidad del cliente tipica de {}'.format(product))

        # Por customer need
        l_cust_needs_three_words = list(df_cust_needs['cust_needs_three_words'])  # hace falta hacerles una variable? En caso de que si, las dejo aca?
        l_cust_needs_one_word = list(df_cust_needs.index)
        df_cust_needs['Peso'] = None  # inicializo columna peso de customer needs
        temp_options = ["No es importante", 'Poco importante', 'Algo importante', 'Importante', 'Muy importante']
        d = {"No es importante": 0, 'Poco importante': 1, 'Algo importante': 3, 'Importante': 5, 'Muy importante': 7}

        for i in range(len(l_cust_needs_three_words)):
            # pido peso y lo guardo
            # peso = st.sidebar.slider(l_cust_needs_three_words[i].title(), min_value=0, max_value=10, value=0, step=1)
            peso = st.select_slider(label=l_cust_needs_three_words[i], options=temp_options)
            df_cust_needs.loc[l_cust_needs_one_word[i], 'Peso'] = d[peso]
            # d_cust_needs_weights[l_cust_needs_three_words[i]] = peso  # df = pd.DataFrame(d_cust_needs_weights, index=[0])  # por algun motivo no se hace bien... aunque el dic si
        # st.write("Verifico (2): ",d_cust_needs_weights)
        # st.write("Verifico (2): ", df_cust_needs)
        st.write("Verifico (2):")
        st.dataframe(df_cust_needs)

        """
        col1, col2 = st.columns(2)
        col1.metric(label="Posicion", value="1")
        col2.metric(label="Alternativa", value=df_alt.loc[1])
        # col2.metric("Wind", "9 mph", "-8%")
        """

        # (3) CALCULO IMPORTANCIA TECNICA DE CADA ATRIBUTO (SEGUN PESOS DE NECESIDADES DEL CLIENTE)
        d_attrs_tech_imp = get_attrs_technical_importance(df_cust_needs, df_relation_matrix)
        print(d_attrs_tech_imp)
        st.write("Verifico (3): ",d_attrs_tech_imp)

        # (4) CALCULO VALORACION FINAL DE CADA ALTERNATIVA
        df_alts_val_fin = get_alts_final_value(df_alt_cleaned, df_value_sent, d_attrs_tech_imp)
        # df.to_excel('/Users/nachomondino/Desktop/df_valoracion_final.xlsx', 'Hoja de datos', index=False)
        st.write("Verifico (4): ", df_alts_val_fin)

        # (5) IMPRIMO RESULTADOS
        # 5.1) Muestro tabla de recomendacion
        st.write('## Tabla de recomendaciones')
        st.write('Dada la importancia que le da a cada necesidad del cliente, buscamos las alternativas mas idoneas para usted')
        st.write('#### Las 10 alternativas que mas le recomendamos')

        # Calculo porcentaje de recomendacion de cada alternativa
        df_alts_recommend = recommend_table(df_alt, df_alts_val_fin)   # OJO! DF_ALT TIENE ALTS QUE DF_ALT_CLEANED NO Y POR ENDE EL INDICE ES ≠
        # df2.to_excel('/Users/nachomondino/Desktop/df_valoracion_final_recommend.xlsx', 'Hoja de datos', index=False)

        # Selecciono las 10 alternativas de mayor porcentaje de recomendacion
        # df_top_ten = pd.DataFrame(columns=['Marca', "Modelo", "precio", 'porcentaje_recomendacion'])
        idxs_top_ten = df_alts_recommend.index[:10]
        aggrid_interactive_table(df=df_alts_recommend.loc[idxs_top_ten]) #['Marca', "Modelo", "precio", 'porcentaje_recomendacion']]) --> falla para fundas de celular

        # 5.2) Muestro tabla completa de alternartivas
        st.write('#### Todas las alternativas')
        aggrid_interactive_table(df=df_alts_recommend)

    # SI EL CLIENTE ES UNA EMPRESA
    else:
        # Le muestro resultados al cliente
        st.write('## Tabla 1: Numero de alternativas por cluster')
        st.write(df_alt_per_clust)

        st.write('## Tabla 2: Valor tipico de cada cluster')  #  CENTROIDES DE CLUSTERS SEGUN VALORES DE ATRIBUTOS
        st.write(df_centroids_values)

        st.write('## Tabla 3: Numero de marcas por cluster')
        st.write(df_brand_per_cluster)

        st.write('## Tabla 4: Todas las alternativas y su clister')  # Alternativas por grupo
        st.write(df_alt_clust)


if __name__ == '__main__':
    main()



''' Ex funcion cuado retornaba diccionario y usaba customer_needs_translation...
def get_attrs_technical_importance(d_cust_needs_weights, df_relation_matrix):
    """
    Obtiene la importancia tecnica de cada atributo del producto
    :param customer_needs_weights: Diccionario
    :param relation_matrix: Dataframe
    :return: Diccionario
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
            # print(customer_need, atributo)

            # defino relacion entre atributo y customer need
            # idx_customer_need = customer_needs.index(customer_need)
            # idx_attr = relation_matrix.columns.get_loc(atributo) # agrega flexibilidad pues puedo pasarle el df_opiniones enterro e igual usa solo "opiniones"
            # print(idx_customer_need, idx_attr)
            # relacion = relation_matrix.iloc[idx_customer_need, idx_attr]
            relacion = df_relation_matrix.loc[customer_need, atributo]

            # CALCULO IMPORTANCIA TECNICA
            customer_need_three_words = customer_needs_translation(d_cust_needs_weights.keys(), customer_need)
            # print(customer_need_three_words)
            # print(customer_needs_weights[customer_need_three_words])
            # print("relacion:", relacion)
            imp_tecnica += d_cust_needs_weights[customer_need_three_words] * relacion  # deeberia ser contains(customer_need) pues una es de 1 palabra y la otra de 3.

        # GUARDO IMPORTANCIA TECNICA
        d[atributo] = imp_tecnica

    return d
    
    
def customer_needs_translation(l_cust_needs, cust_need):  # no se que enombre ponerle, busca relacion entre customer needs de 3 palabras y las de 1...
    """
    Traduce customer need de 1 palabra a customer need de 3 palabras
    :param customer_needs: Lista de customer needs de 3 palabras
    :param customer_needs_substring: String. Customer need de 1 palabra.
    :return:
    """
    # POR CUSTOMER NEED DE 3 PALABRAS
    for customer_need in l_cust_needs:

        # SI CUSTOMER NEED DE 1 PALABRA ESTA EN CUSTOMER NEED DE 3 PALABRAS
        if cust_need in customer_need:
            return customer_need  # retorno customer need de 3 palabras
'''



"""
   # IMPORTO ARCHIVOS UNA VEZ SELECCIONADO EL PRODUCTO
    # Archivos de (2) Data preparation
    df_alt = pd.read_excel('./data/data_preparation/{}/df_alt_formated.xlsx'.format(product))  # correct_price
    df_alt = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_alt_formated.xlsx'.format(product)) # correct_price
    df_alt_cleaned = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_alt_cleaned.xlsx'.format(product))
    df_cust_needs = pd.read_excel("/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_cust_needs.xlsx".format(product), index_col=0)
    # Si funciona l_cust_needs, borro estas lineas pues no hace falta exportar cust needs sino que las obtengo de matriz de relaciones...  --> necesito si o si las cust needs de 3 palabras y e esas no estan en matriz de relaciones
    # Archivos de (3) Modelling
    df_relation_matrix = pd.read_excel("/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_relation_matrix.xlsx".format(product), index_col=0)
    df_alt_clust = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/clustering/{}/df_alt_clust.xlsx'.format(product), index_col=0)
    df_alt_per_clust = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/clustering/{}/df_alt_per_clust.xlsx'.format(product), index_col=0)
    df_centroids_values = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/clustering/{}/df_centroids_values.xlsx'.format(product), index_col=0)
    df_brand_per_cluster = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/clustering/{}/df_brand_per_cluster.xlsx'.format(product), index_col=0)

    # l_cust_needs = list(df_relation_matrix.index)
    df_value_sent = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/modelling/atribucion/{}/df_attr_values_sent.xlsx'.format(product))

    print(df_alt.shape)
    # Selecciono ids de alternativas que no han sido borradas
    ids_cleaned = df_alt_cleaned["id_alternativa"].unique()
    # Filtro dataframe alternativas por ids
    df_alt = df_alt[df_alt.id_alternativa.isin(ids_cleaned)]
    df_alt = df_alt.reset_index(drop=True)  # el dropna me borra una fila y los indices quedan mal...
    print(df_alt.shape)

"""