# Importo librerias
import pandas as pd

# Levanto los dataframes
path = '/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/extraccion_datos/df_opiniones_celulares.xlsx'
path2 = '/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/extraccion_datos/df_modelos_celulares.xlsx'

df_opiniones = pd.read_excel(path)
df_modelos = pd.read_excel(path2)

print(df_opiniones)
print(df_modelos)


def checkValores(df):

    for columna in df_modelos.columns:
        print("Campo al cual ver valores unicos:", columna)
        val_col = list(df_modelos[columna].value_counts())
        print(val_col)




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