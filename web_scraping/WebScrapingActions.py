# Importo librerias
from time import sleep
import random
import LinksExtractor as le
from selenium.webdriver.common.by import By


# Podria implementar cosas como ingresar un usuario, hacer un kampachatca, cerrrar un ad, etc

def ScrollDown(driver):
    # Get scroll height
    # Defino tiempo de pausa aleatorio entre 1 y 2 segundos para evitar banneo de IP
    SCROLL_PAUSE_TIME = random.uniform(1, 2)

    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break
        last_height = new_height


