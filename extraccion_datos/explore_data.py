import pandas as pd
# Levanto los data
path = '/df_extraccion_datos/df_opiniones_celulares.xlsx'
path2 = '/Users/nachomondino/Documents/GitHub/evaluacion-compra-automatica/df_extraccion_datos/df_modelos_celulares.xlsx'

df_opiniones = pd.read_excel(path)
df_modelos = pd.read_excel(path2)

print(df_opiniones)
print(df_modelos)

# lo termine implementando en excel...