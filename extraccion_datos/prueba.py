from MercadoLibreApi import MercadoLibreApi
import pandas as pd

api = MercadoLibreApi()
df_categorias = api.getCategoriasID()

l = []

for id in df_categorias['id_subcategoria'] :
    l.append(api.getAtributosSubcategoria(id))

df_categorias['atributos'] = l
# print(df_categorias)

# df_categorias.to_excel('/Users/nachomondino/Desktop/df_categorias_completo.xlsx', 'Hoja de datos', index=False)

