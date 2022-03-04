"""
Pseudocodigo de lo que quisiera que haga:
# Búsqueda del cliente
# Le muestro customer needs al cliente (ya extraidas) para que establezca el peso a cada una.
# Llamara a algoritmo que haga el calculo de la importancia tecnica, luego calcule la valoracion final de cada publicacion
# Otro algoritmo calculara el % de recomendacion y le mostrará en formato tabla los resultados (dicha tabla tendra filtros para que el cliente pueda interactuar con precio, estado, etc)

"""
# Importo librerias
from selenium import webdriver
from web_scraping import LinksExtractor as le
from selenium.webdriver.chrome.options import Options


# Defino a Chrome como Web Browser
opts = Options()
opts.add_argument(
    "USER_AGENT=Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543a Safari/419.3")
driver = webdriver.Chrome('/Users/nachomondino/Desktop/chromedriver', chrome_options=opts)


# Pedido al usuario de producto a buscar
busqueda = str(input("Ingrese busqueda: "))

# Valido la busqueda (para que no sea tan amplia)
while le.validacionBusqueda(driver, busqueda) == False:
    print("Por favor sea mas especifico en su busqueda")
    busqueda = str(input("Ingrese busqueda: "))
