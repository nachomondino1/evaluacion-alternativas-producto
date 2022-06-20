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
    # st.title('EVALUACION AUTOMATICA DE ALTERNATIVAS EN PROCESO DE COMPRA')  # imprimo titulo
    st.header('EVALUACION AUTOMATICA DE ALTERNATIVAS EN PROCESO DE COMPRA')  # imprimo titulo
    st.sidebar.write('# Ingrese los siguientes datos')  # titulo 1 de sidebar
    client_options = ['Usuario final', 'Empresa']  # Usuario define si es empresa o usuario final
    product_options = ['Celulares', 'Smartband', 'TV']  # ['Auriculares', 'Celulares', 'Fundas de celular', 'Notebook', 'Smartband', 'Suplementos','Tablets', 'TV']  # Lista de productos
    client = st.sidebar.radio('1) ¿Que tipo de cliente eres?', client_options)  # client = st.sidebar.selectbox('1) ¿Que tipo de cliente eres?', client_options)
    product = st.sidebar.radio('2) ¿Que producto desea evaluar?', product_options)  # product = st.sidebar.selectbox('2) ¿Que producto desea evaluar?', product_options)
    product = product.lower()

    # IMPORTO ARCHIVOS UNA VEZ SELECCIONADO EL PRODUCTO
    # Archivos de (2) Data preparation
    df_alt = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/collect_initial_data/{}/df_alt.xlsx'.format(product))  # correct_price
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


    # VER DONDE METER (saco alternativas eliminadas en Data prepartion de df_alt)
    print(df_alt.shape)
    # Selecciono ids de alternativas que no han sido borradas
    ids_cleaned = df_alt_cleaned["id_alternativa"].unique()
    # Filtro dataframe alternativas por ids
    df_alt = df_alt[df_alt.id_alternativa.isin(ids_cleaned)]
    df_alt = df_alt.reset_index(drop=True)  # el dropna me borra una fila y los indices quedan mal...
    print(df_alt.shape)
    st.write(df_alt)

    # ESTA BUENA LA IDEA PERO AUN NO FUNCIONA... (si funciona saco lo de arriba)
    df_alt_to_client = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/data_preparation/{}/df_alt_cleaned_to_client.xlsx'.format(product))
    st.write(df_alt_to_client)

    cont = 0
    for id_alt in list(df_alt_to_client["id_alternativa"]):
        if id_alt not in list(df_alt_cleaned['id_alternativa']):
            cont += 1
            st.write(id_alt)

    st.write(cont)
    # hay 29 alternativas que estan en df_alt_to_client y no en df_alt_cleaned  # como puede ser? Efectivamente, son alt que tienen un valor mal cargado y sin embarrgo estan en df_alt_to_client... Claramente algo falla en la eliminacion dee alts..


    # SI EL CLIENTE ES UN USUARIO FINAL
    if client == 'Usuario final':

        st.write("Antes de comprar cualquier producto que deseamos, solemos **evaluar las distintas alternativas** posibles. "
                 "Por ejemplo, queremos comprar un celular y empezamos a leer opiniones, ver videos que hagan una reseña"
                 " e tenemo ")

        image_1 = Image.open('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/p5_deployment/1.jpeg')
        st.image(image_1)  # Imagen de persona antes ≠ alternativas

        st.write("Hoy en dia, cada vez hay mas alternativas lo que hace que la eleccion de una sola sea un proceso "
                 "extramadamente desgastante. Es muy probable que consumamos mucho de nuestro valioso tiempo y encima no "
                 "terminemos escogiendo la alternativa ideal para nosotros.")

        image_2 = Image.open('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/p5_deployment/2.jpeg')
        st.image(image_2, use_column_width='always')

        st.write("Normalmente, para ver si una alternativa es buena o no ver un video que haga una reseña, leer un articulo "
                 "en la web, escuchar la recomendacion de un amigo, leer opiniones, etcetera. Pero si, todo eso solo para"
                 "una alternativa cuando en el mercado hay cientos")

        st.write("Lamentablemente, en muchos casos, esto puede consumirnos mucho tiempo ademas de que es probable que no "
                 "terminemos comprando la alternativa que mas se ajusta con lo que buscamos. "
                 "Para facilitar este proceso, podras utilizar la siguiente herramienta pensada para encontrar la "
                 "alternativa mas idonea segun las necesidades de cada cliente")


        # (2) SOLICITO PESOS DE LAS CUSTOMER NEEDS
        # Imprimo titulo
        st.write('###  Importancia de cada necesidad del cliente'.format(product))
        st.write('Ingrese la importancia que tiene para usted cada necesidad del cliente tipica de {}'.format(product))

        # Por customer need
        l_cust_needs_three_words = list(df_cust_needs['cust_needs_three_words'])  # hace falta hacerles una variable? En caso de que si, las dejo aca?
        l_cust_needs_one_word = list(df_cust_needs.index)
        df_cust_needs['Peso'] = None  # inicializo columna peso de customer needs

        temp_options = ["No es importante", 'Poco importante', 'Neutral', 'Importante', 'Muy importante']
        d = {"No es importante": -10, 'Poco importante': -2.5, 'Neutral': 0, 'Importante': 2.5, 'Muy importante': 10}  # Pensar si dejo asi los pesos...


        # set_weigths()
        # Pasar a funcion aparte?
        # INTENTO AGREGAR PERFILES DE CLIENTES --> QUE SETEEN PESOS PREDETERMINADOS
        d_usos = {
            'celulares': {'Jugar': {'precio': 'Neutral', 'bateria': 'Importante', 'camara': 'Poco importante',
                                'pantalla': 'Importante', 'memoria': 'Neutral', 'tamaño': 'Neutral',
                                'velocidad': 'Muy importante', 'sonido': 'Neutral', 'diseño': 'Neutral',
                                'sistema': 'Neutral'},
                          'Trabajar': {'precio': 'Muy importante', 'bateria': 'Importante', 'camara': 'Neutral',
                                 'pantalla': 'Neutral', 'memoria': 'Importante', 'tamaño': 'Neutral',
                                 'velocidad': 'Muy importante', 'sonido': 'Neutral', 'diseño': 'Neutral',
                                       'sistema': 'Poco importante'},
                          'Redes':  {'precio': 'Neutral', 'bateria': 'Importante', 'camara': 'Muy importante',
                                 'pantalla': 'Neutral', 'memoria': 'Neutral', 'tamaño': 'Neutral',
                                 'velocidad': 'Muy importante', 'sonido': 'Neutral', 'diseño': 'Importante',
                                 'sistema': 'Poco importante'},
                          'Comunicacion':  {'precio': 'Muy importante', 'bateria': 'Importante', 'camara': 'Neutral',
                                 'pantalla': 'Neutral', 'memoria': 'Importante', 'tamaño': 'Muy importante',
                                 'velocidad': 'Neutral', 'sonido': 'Muy importante', 'diseño': 'Neutral',
                                 'sistema': 'Muy importante'},
                      },
            'tv': {'monitor': {'precio': 'Importante', 'imagen': 'Muy importante', 'sonido': 'Importante',
                                'sistema': 'Poco importante', 'control': 'Poco importante', 'tamaño': 'No es importante',
                                'velocidad': 'Neutral', 'diseño': 'Neutral', 'conexion': 'Importante'}},
            'smartband': {}
            # 'auriculares': {}
        }

        option = st.selectbox('AYUDA: Recomendacion de importancias segun el uso', [' '] + list(d_usos[product].keys())) #(d_perfil_cliente[product])+ [

        # Si no eligio perfil de cliente
        for i in range(len(l_cust_needs_three_words)):
            # pido peso y lo guardo # peso = st.sidebar.slider(l_cust_needs_three_words[i].title(), min_value=-10, max_value=10, value=0, step=5)
            label = '{}) {}:'.format(i+1, l_cust_needs_three_words[i].upper())

            if option == " ":
                peso = st.select_slider(label=label, options=temp_options, value="Neutral") # puedo agregarle help y sus palabras relacionadas por ej

            else:
                perfil = d_usos[product][option]
                peso = st.select_slider(label=label, options=temp_options, value=perfil[l_cust_needs_one_word[i]]) # puedo agregarle help y sus palabras relacionadas por ej

            # Guardo peso numerico
            df_cust_needs.loc[l_cust_needs_one_word[i], 'Peso'] = d[peso]
            # d_cust_needs_weights[l_cust_needs_three_words[i]] = peso  # df = pd.DataFrame(d_cust_needs_weights, index=[0])  # por algun motivo no se hace bien... aunque el dic si
        #st.write("Verifico (2):") # st.dataframe(df_cust_needs)

        # SI EL CLIENTE DA CLICK A BOTON "PROCESAR"
        if st.button('Procesar'):

            # (3) CALCULO IMPORTANCIA TECNICA DE CADA ATRIBUTO (SEGUN PESOS DE NECESIDADES DEL CLIENTE)
            d_attrs_tech_imp = get_attrs_technical_importance(df_cust_needs, df_relation_matrix)
            # print(d_attrs_tech_imp) # st.write("Verifico (3): ",d_attrs_tech_imp)

            # (4) CALCULO VALORACION FINAL DE CADA ALTERNATIVA
            df_alts_val_fin = get_alts_final_value(df_alt_cleaned, df_attr_alt_sent, df_value_sent, d_attrs_tech_imp)
            # df.to_excel('/Users/nachomondino/Desktop/df_valoracion_final.xlsx', 'Hoja de datos', index=False)
            # st.write("Verifico (4): ", df_alts_val_fin)

            # (5) IMPRIMO RESULTADOS
            # 5.1) Muestro tabla de recomendacion
            st.write('### Tabla de recomendaciones')
            st.write('Dada la importancia que le da a cada necesidad del cliente, buscamos las alternativas mas idoneas para usted')
            st.write('#### Las 10 alternativas que mas le recomendamos')
            # Calculo porcentaje de recomendacion de cada alternativa
            df_alts_recommend = create_recomendation_table(df_alt_to_client, df_alts_val_fin)   # OJO! DF_ALT TIENE ALTS QUE DF_ALT_CLEANED NO Y POR ENDE EL INDICE ES ≠
            # df2.to_excel('/Users/nachomondino/Desktop/df_valoracion_final_recommend.xlsx', 'Hoja de datos', index=False)
            # st.dataframe(df_alts_recommend)

            # Selecciono las 10 alternativas de mayor porcentaje de recomendacion
            df_top_ten = df_alts_recommend.iloc[0:10, 1:]  # df_top_ten = pd.DataFrame(columns=['Marca', "Modelo", "precio", 'porcentaje_recomendacion'])
            st.dataframe(df_top_ten)

            with st.expander("Ver todas las alternativas y su grupo"):
                st.write("""
                    La tabla de abajo muestra todas las alternativas tenidas en cuenta en el analisis.
                """)
                st.dataframe(df_alts_recommend)

            aggrid_interactive_table(df_alts_recommend)
            # idxs_top_ten = df_alts_recommend.index[:10]
            #aggrid_interactive_table(df=df_alts_recommend.loc[idxs_top_ten]) #['Marca', "Modelo", "precio", 'porcentaje_recomendacion']]) --> falla para fundas de celular

    # SI EL CLIENTE ES UNA EMPRESA
    else:
        # Le muestro resultados al cliente
        st.write('Llevamos a cabo un analisis en el que agrupamos las alternativas de {} que tengan caracteristicas similares. Los resultados fueron:'.format(product))
        st.write("\t * Nº GRUPOS: {}".format(len(df_alt_per_clust)))
        st.write("\t * NOMBRES DE GRUPOS: {}".format( " - ".join(list(df_alt_per_clust.index))))

        st.write('Conozcamos que hay dentro de cada uno de estos grupos!')

        st.write('### Tabla 1: Numero de alternativas por grupo')
        st.write(" A continuacion vemos la cantidad de alternativas dentro de cada uno de estos grupos.")
        chart_data = pd.DataFrame(data=df_alt_per_clust)
        st.bar_chart(chart_data)  # st.write(df_alt_per_clust)

        st.write('### Tabla 2: Numero de alternativas por grupo y marca')
        st.write(df_brand_per_cluster)

        st.write('### Tabla 3: Ejemplo tipico de cada grupo')  #  CENTROIDES DE CLUSTERS SEGUN VALORES DE ATRIBUTOS
        st.write(df_centroids_values)

        # st.write('### Tabla 4: Todas las alternativas y su grupo')  # Alternativas por grupo
        # st.write(df_alt_clust)

        with st.expander("Ver todas las alternativas y su grupo"):
            st.write("""
            La tabla de abajo muestra todas las alternativas tenidas en cuenta en el analisis y su correspondiente grupo
            """)
            st.dataframe(df_alt_to_client_clust)




if __name__ == '__main__':
    main()


def set_weigths():
    pass



'''
col1, col2 = st.columns(2)
col1.metric(label="Posicion", value="1")
col2.metric(label="Alternativa", value=df_alt.loc[1])
# col2.metric("Wind", "9 mph", "-8%")
'''

''' Funcion get_alts_final_value() con dos ciclos for (uno para cada tipo de atributo, ficticio y no ficticio) lo que lleva a repeticion de lineas
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
    l_atributos = df_attr_alt_sent['atributo'].unique() + df_attr_value_sent['atributo'].unique()

    # POR ALTERNATIVA
    for i in range(len(df_alt)):
        print("ALTERNATIVA Nº: {}".format(i).center(120))

        # Defino variables
        val_fin_alt = 0  # Reinicio suma de valoracion final por cada alternativa
        id_alt = df_attr_alt_sent.loc[i, 'id_alternativa']

        # SI EL ATRIBUTO ES FICTICIO (Creado artificialmente para ser relacionado con una customer need, no tiene valores)
        for atributo in df_attr_alt_sent['atributo'].unique():

            # Obtengo importancia tecnica del atributo
            imp_tecnica_attr = d_attrs_tech_imp[atributo]

            # NO DEBERIA HACER UN IF IMPORTANCIA TECNICA DEL ATTR > 0????? PUES AL TENER IMP TEC 0 AFRCTA VALORACION FINAL --> pa mi no afecta, no hace nada pues es una suma, pero si mejora eficiencia en procesamiento (reduce calculo al pedo)
            # if imp_tecnica_attr > 0: # prueba

            # OBTENGO SENTIMENT DEL ATRIBUTO
            sent_valor = float(df_attr_alt_sent[(df_attr_alt_sent['atributo'] == atributo) & (df_attr_alt_sent['id_alternativa'] == id_alt)]['sent'])

            # SI EL SENTIMENT DEL VALOR NO ES NAN
            if str(sent_valor) != 'nan':
                # CALCULO VALORACION FINAL DEL ATRIBUTO
                val_fin_alt += sent_valor * d_attrs_tech_imp[atributo]
                print(sent_valor, d_attrs_tech_imp[atributo], val_fin_alt)

            # SI EL SENTIMENT DEL VALOR ES NAN, NO HAGO NADA --> justif en NDV

        # SI EL ATRIBUTO NO ES FICTICIO (no lo cree artificialmente sino que lo extraje de Meli, tiene valores)
        # POR ATRIBUTO
        for atributo in df_attr_value_sent['atributo'].unique():  # ingreso solo a atributos que tienen al menos una relacion

            # Obtengo importancia tecnica del atributo
            imp_tecnica_attr = d_attrs_tech_imp[atributo]

            # NO DEBERIA HACER UN IF IMPORTANCIA TECNICA DEL ATTR > 0????? PUES AL TENER IMP TEC 0 AFRCTA VALORACION FINAL
            # if imp_tecnica_attr > 0: # prueba

            # OBTENGO VALOR DEL ATRIBUTO
            valor = df_alt.loc[i, atributo]
            print("ATRIBUTO: {} , VALOR: {}".format(atributo, valor))

            # SI EL VALOR NO ES NAN (la alternativa puede no tener valor para el atributo)
            if str(valor) != 'nan':

                # OBTENGO SENTIMENT DEL VALOR
                sent_valor = float(df_attr_value_sent[(df_attr_value_sent['atributo'] == atributo) & (df_attr_value_sent['valor'] == valor)]['sent'])

                # SI EL SENTIMENT DEL VALOR NO ES NAN
                if str(sent_valor) != 'nan':

                    # CALCULO VALORACION FINAL DEL ATRIBUTO
                    val_fin_alt += sent_valor * d_attrs_tech_imp[atributo]
                    print(sent_valor, d_attrs_tech_imp[atributo], val_fin_alt)

                # SI EL SENTIMENT DEL VALOR ES NAN, NO HAGO NADA --> justif en NDV

            # SI EL VALOR ES NAN
            else:
                # OBTENGO EL PEOR SENTIMENT DEL ATRIBUTO
                worst_sent = df_attr_value_sent[df_attr_value_sent['atributo'] == atributo]["sent"].min()
                print("El modelo Nº{} tiene valor NaN en atributo {}, por lo cual, le asigno el peor sentiment {} de"
                      "los valores de dicho atributo".format(i, atributo, worst_sent))

                # CALCULO VALORACION FINAL DEL ATRIBUTO
                val_fin_alt += worst_sent * d_attrs_tech_imp[atributo]
                print(worst_sent, d_attrs_tech_imp[atributo], val_fin_alt)

        # GUARDO ALTERNATIVA Y SU VALORACION FINAL
        l_val_fin_alts.append(val_fin_alt)

    # Agrego columna al dataframe alternativas
    df['val_final'] = l_val_fin_alts
    print(l_val_fin_alts)
    return df

'''