# Importo librerias
from urllib.request import urlopen
from bs4 import BeautifulSoup

# Cargo en una variable el codigo HTML del website a scrapear
html = urlopen('http://en.wikipedia.org/wiki/Kevin_Bacon')

# Creo objeto BeautifulSoup para poder operar el codigo HTML
bs = BeautifulSoup(html.read(), 'html.parser')

# Extraigo todos los links de la pagina y los guardo en una lista
links = bs.find_all("a")

# Obtengo link de cada tag "a"
for link in links:

    # algunos tags "a" no tienen atributo "href"
    if "href" in link.attrs:
        print(link.attrs["href"])


    """
    La de arriba es la propuesta del libro, la siguiente es la mia:
    try:
        print(link.attrs["href"])
    except:
        pass
    """


