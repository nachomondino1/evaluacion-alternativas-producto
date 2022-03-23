# Importo librerias
import pandas as pd

# Levanto los dataframes
path = '/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/extraccion_datos/df_opiniones_celulares.xlsx'
path2 = '/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/extraccion_datos/df_modelos_celulares.xlsx'

df_opiniones = pd.read_excel(path)
df_modelos = pd.read_excel(path2)

print(df_opiniones)
print(df_modelos)

# Veo los valores de cada columna del Dataframe
for columna in df_opiniones.columns:
    print(df_opiniones[columna].value_counts())

