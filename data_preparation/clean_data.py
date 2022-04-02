# Importo librerias
import pandas as pd

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


def delete_none_values(df):
    print(df)

    # Columna

    # Fila
    porc_max_none = 0.01

    cant_col = len(df.columns)

    # Recorro cada fila del df
    for i in range(len(df)):
        cont = 0

        # Recorro cada columna del df
        for j in range(cant_col):

            # si la celda tiene el valor None
            if df.iloc[i, j]== "NaN": # No esta entrando aca... el problema es que dice nan
                print(df.iloc[i, j]) # se deberian imprimir los nan

                # Sumo 1 al contador de None
                cont = 1

        # Terminado de recorrer las columnas de una fila, defino porcentaje de None de dicha fila
        porc_none = cont / cant_col

        # Si hay mas None de los tolerados
        if porc_none > porc_max_none:

            # Elimino fila
            df = df.drop(df.iloc[i:])

    print(df)
    return df


def main(): # esto lo implemento en main.py, dsp de terminar el archivo, la paso...
    # Levanto el dataframe
    path = '/data/df_extraccion_datos/df_modelos_celulares.xlsx'

    df_modelos= pd.read_excel(path)

    print(df_modelos)

    # Imprimo frecuencia de valores
    for atributo in df_modelos.columns:
        print(df_modelos[atributo].value_counts())

    # checkValores(df_modelos) # tengo que decirle que no se fije en precio, id_pub, marca ni modelo.
    delete_none_values(df_modelos)

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