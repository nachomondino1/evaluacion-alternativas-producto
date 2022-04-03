# Importo librerias
import pandas as pd


def delete_repeated_rows(df):  #
    """
     La funcion debe obteneer los indices de las filas a borrar

    :param df: Dataframe al cual revisar valores duplicados
    :return: Lista de indices de las filas del dataframe a borrar
    """
    # Defino lista donde guardar los indices de las filas a borrar
    idx = []

    # Defino cantidad de filas
    cant_filas = df.shape[0]
    print("Originalmente el dataframe tenia {} filas.".format(cant_filas), end=" ")

    # Elimino filas duplicadas
    df = df.drop_duplicates()

    for i in range(len(df)):
        if i not in df.index:
            idx.append(i)

    # Defino nueva cantidad de filas
    cant_filas = df.shape[0]
    print("Tras eliminar las filas duplicadas, el dataframe tiene {} filas".format(cant_filas))

    return idx

def check_numeric_columns():

    # Por cada columna (campo especifico) de las columnas del df
        # Por cada valor de la columna
            # ver si tiene numeros

    pass

def categorize_numeric(): # esta funcion deberia recibir una columna y discretizarla (teniendo en cuentas las unidades)

    pass


def delete_attr_x_values(df):

    cant_atributos = len(df.columns)
    cant_valores_posibles = len(df)

    # Defino parametros:
    porc_pocos_val = 0.2
    porc_muchos_val = 0.75

    # Por cada atributo
    for atributo in df.columns:

        # Obtengo lista de frecuencia de sus valores
        val_col = list(df[atributo].value_counts())
        # print("Campo al cual ver valores unicos:", atributo)
        # print(val_col)

        # Si el atributo tiene un unico valor para todos los modelos
        if len(val_col) < 3:

            # Recorro cada frecuencia
            for valor in val_col:

                # si alguna frecuencia es predominante
                if valor > 0.9 * sum(val_col):

                    # Elimino el atributo
                    print("Elimino atributo {} por tener muy pocos valores y uno muy predominante".format(atributo))
                    df = df.drop([atributo], axis=1)

        # Si el atributo tiene muchos valores
        elif len(val_col) > porc_muchos_val * cant_valores_posibles:

            # Intento convertir la variable a numerica
            try:
                # Pruebo con el primer elemento
                int(df[atributo][0])
                print("Entendio el atributo {} como numero".format(atributo))


            except:

                # Si el valor mas frecuente tiene una frecuencia aceptable
                if val_col[0] > 0.1 * cant_valores_posibles:
                    pass

                else:
                    # Elimino el atributo
                    print("Elimino atributo {} por tener muchos valores y de frecuencia baja".format(atributo))
                    df = df.drop([atributo], axis=1)

        else:
            pass

    print(df)
    return df


def main(): # esto lo implemento en main.py, dsp de terminar el archivo, la paso...
    # Levanto el dataframe
    df_modelos = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_modelos_celulares.xlsx')
    df_opiniones = pd.read_excel('/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/data/df_extraccion_datos/df_opiniones_celulares.xlsx')

    # 1) ELIMINO NONE VALUES
    # ver si implemento borrado de campos especificos con muchos none value o no... a priori, no lo hago.
    df_opiniones.dropna() # solo borraria alguna fila por si no tiene title...

    # 2) ELIMINO FILAS REPETIDAS --> ojo que tiene que ser sin id...
    df_opiniones = df_opiniones.drop(delete_repeated_rows(df_opiniones['content']))  # elimino duplicados teniendo en cuenta solo la columna content que es la que contiene opiniones propiamente
    df_modelos = df_modelos.drop(delete_repeated_rows(df_modelos.iloc[:, 2:]))  # elimino duplicados sin tener en cuenta las columna de id y precio
    print(df_opiniones.shape)
    print(df_modelos.shape)

    # 3) CATEGORIZO VARIABLES NUMERICAS
    # categorize_numeric()


    # 4) ELIMINO CAMPOS ESPECIFICOS SEGUN CANTIDAD DE VALORES Y CANTIDAD DE OPINIONES POR VALOR
    # delete_attr_x_values(df_modelos)


main()







"""
Verificar unicidad de filas desde marca en adelante
Contar None values. 
    1.- Si una FILA tiene menos del x% de atrib entonces la sacaria. 
    2.- Si una columna tiene menos del x% de atrib la sacaria

Contar valores unicos de columnas.
    1.- Si tiene muchos valores unicos (mas de x por ej): --> (no incluir id_pub, precio, marca ni modelo)
        1.1.- Si la variable es numerica, convertirla en categorica (por ej, capacidad de la bateria, en cambio, modelo del procesador no puedo)
        1.2.- Si no es numerica, (Por ej, "Modelo del procesador" quien toma muchos valores ≠ y con poca frec cada uno)
            Si el mas frecuente, tiene una frec muy chica, entonces eliminar.
            Si el mas frecuente tiene una frec aceptable, no eliminar
            
    2.- Si tiene muy pocos valores unicos:
        2.1.- y predomina uno por mucho, entonces no tener en cuenta el atributo. Por ej, atrib "Con camara" hay 71 Si y 2 No. Es practicamente cte en los modelos y encima el "No" se basa en pocas opiniones..
    Pero que hago con los modelos que son el caso particular que no lo tiene? 
        2.2.- 
    
    3.- Si tiene un solo valor, eliminar atributo. No hay diferencial entre modelos. Por ej, atributo "Con teclado QWERTY físico" que solo toma el valor "No".


Ver si precio lo entiende como int o como str. 
"""


''' ANTES DE DECIDIR QUE NO IBA A BORRAR FILAS DEL DF_MODELOS
def delete_none_values(df):
    # ELIMINO FILAS CON MUCHOS NONE VALUES
    df_copia = df.copy()  #tuve que haceer copia porque quedaba out of bounds

    porc_max_none = 0.20
    cant_col = len(df.columns)

    # Recorro cada fila del df
    for i in range(len(df)):
        none_values_fila = 0
        print("Nueva fila, numero {}".format(i))

        # Recorro cada columna del df
        for j in range(cant_col):

            # si la celda tiene el valor None
            if str(df.iloc[i, j]) == 'nan':
                print(df.iloc[i, j])  # se deberian imprimir los nan

                # Sumo 1 al contador de None
                none_values_fila += 1

        # Terminado de recorrer las columnas de una fila, defino porcentaje de None de dicha fila
        porc_none = none_values_fila / cant_col

        # Si hay mas None de los tolerados
        if porc_none > porc_max_none:
            # Elimino fila
            print("Elimino fila numero {} pues tienen el {:.0f}% de sus valores None".format(i, porc_none*100))
            df_copia = df_copia.drop(i, axis=0)
            print(df_copia.shape)

    # ELIMINO COLUMNAS CON MUCHOS NONE VALUES
    # falta implementar
    return df


'''