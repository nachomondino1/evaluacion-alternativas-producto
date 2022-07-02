# Importo librerias
from time import sleep
import random

""" La idea de esta clase es implementar un crawler que haga acciones que sirvan para CUALQUIER PROYECTO de web scraping
Asi, no pongo las acciones especificas que puedo hacer en mercado libre por ejemplo
Podria implementar cosas como ingresar un usuario, hacer un kampachatca, cerrar una ad, etc
."""


class Crawler():
    """ Attempt to model a Crawler for every web scraping's project """

    def __init__(self, driver):
        """ Inicialize driver attribute """
        self.driver = driver


    def ScrollDown(self):
        """
        Carga todos los elementos en una pagina al deslizar el driver hacia abajo hasta el final

        :return:
        """
        # Get scroll height
        # Defino tiempo de pausa aleatorio entre 1 y 2 segundos para evitar banneo de IP
        SCROLL_PAUSE_TIME = random.uniform(1, 2)

        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                break
            last_height = new_height


''' INTENTO INICIALIZER EL DRIVER DESDE CRAWLER.PY PERO FALLO
    def initializeDriver(self, driver):
        """
        Define web browser a utilizar

        :param driver: Nombre del web browser que se desea utilizar, por ejemplo, "Chrome".
        :return:
        """

        if driver == "Chrome":
            # Defino a Chrome como Web Browser
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')  # Hace que no se abra un web browser en tu compu
            self.driver = webdriver.Chrome(
                executable_path='/Users/nachomondino/PycharmProjects/Utils/web_scraping_browsers/chromedriver',
                options=options)

        elif driver == "Firefox":
            pass
            
        
def inicializedriver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Hace que no se abra un web browser en tu compu
    return webdriver.Chrome(
        executable_path='/Users/nachomondino/PycharmProjects/Utils/web_scraping_browsers/chromedriver',
        options=options)

'''