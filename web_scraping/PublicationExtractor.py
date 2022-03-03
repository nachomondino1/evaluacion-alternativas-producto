import pandas as pd
import random
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import OpinionsExtractor as oe
import LinksExtractor as le
import WebScrapingActions

# Puedo hacer un buscador de atributos... que busque en publicaciones hasta que encuentre en alguna un cuadro comparativo de publicaciones entonces saco la primera columna de la tabla
# o bien, en la seccion que dice "Caracteristicas de ..." aunque veo que es poco (por ej, en celulares falta sistema operativo, memoria ram, etc)

def PublicationExtractor(driver):

    """Nota: los datos en las ≠ public estan en un div#class="ui-pdp-container ui-pdp-container--pdp".
    Por que hafo un try?
    Publicaciones de celulares tienen datos en column center y objetos como roperos, banco de pesas en column right
    De aqui extraigo: nombre_publicacion ; precio ; envio gratis? ; estado (nuevo o usado) ; devolucion?

    NO HACE FALTA HACER UN TRY PUES LOS TAGS SON UNICOS MAS ALLA DE SI ESTAN EN UNA COLUMNA U OTRA POR LO QUE,
    NO IMPORTAN.
    """

    # Estado. Esta en un lugar unico tanto para usados como nuevos div#class="ui-pdp-header__subtitle"
    driver.find_element(By.XPATH, '//div[@class="ui-pdp-header__subtitle"]/span]').text

    # Nombre publicacion. Esta en un lugar unico tanto para usados como nuevos h1#class="ui - pdp - title"
    driver.find_element(By.XPATH, '//h1[@class="ui - pdp - title"]').text

    # Precio.
    driver.find_element(By.XPATH, '//div[@class="ui - pdp - price__second - line"]'
                                      '/span[@class="andes-money-amount__fraction"]').text
    # Envio. Hago try porque puede que no lo tengan si no es envio gratis...
    envio = getEnvio(driver)

    # Devolucion
    devolucion = getDevolucion(driver)

    # Compra protegida





    """
    Faltaria extraer: marca ; modelo
    Por que hago un try?
    Por que los celularers tienen marca y modelo en el nombre de la seccion "Caracteristicas de ...".
    En cambio, los roperos y los bancos de pesas dice "caracteristicas principales" y dentro de esta, hay una tabla
    donde especifica marca, linea y modelo.
    """



"""
Este sera un ciclo que recorra publicaciones hasta que encuentre la primera que tenga la info.
Extraigo atributos del producto atrib_prod_1 ; atrib_prod_2 ; ... ; atrib_prodn
Por que hago un try?
Porque los celulares tienen datos de atributos en columncenter (tendre que ver como extraerlos) OJO! NO USO TABLA COMPARATIVA PORQUE SON ATRIBUTOS IRRELEVANTES
En cambio los roperos y bancos de pesas los tienen en la seccion "otras caracteristicas"
"""


def getEnvio(driver):
    # envio = 1 es que es gratis, 0 si no.
    try:
        texto = driver.find_element(By.XPATH,
                                    '//div[@class="ui-pdp-container__row ui-pdp-container__row--shipping-summary"] or'
                                    '[@class="ui-pdp-media ui-pdp-shipping ui-pdp-shipping--md mb-20 ui-pdp-color--GREEN"]'
                                    '//p[@class="ui-pdp-color--GREEN ui-pdp-family--REGULAR ui-pdp-media__title ui-pdp-media__title--on-hover"]').text

        # Usan "Llega gratis" o "Envio gratis a todo el pais"
        if "gratis" in texto:
            envio = 1

    except:
        envio = 0
    return envio


def getDevolucion(driver):
    try:
        driver.find_element(By.XPATH, '//div[@class="class="ui-pdp-container__row"]//p[contains("Devolución gratis")]')
        devolucion = 1
    except:
        devolucion = 0
    return devolucion


def getCompraProtegida(driver):
