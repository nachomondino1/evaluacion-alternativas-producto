import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


def getPublicacionOpinions(driver):
    """
    Extrae opiniones de una publicacion

    :return: Dataframe cuya unidad de analisis es la opinion y sus columnas son titulo, content, rate, fecha, likes, dislikes

    Notas:
    Las opiniones estan en dentro de tag unico div#class=infinite-scroll-component
    """

    # Creo el dataframe
    df = pd.DataFrame(columns=['id','title', 'content', 'rate','likes','dislikes'])
    idx = 0

    # Tendre que implementar extraccion de id o bien pasarlo como parametro


    # Extraigo opiniones
    # Obtengo los XPATH donde se ubican los parrafos de cada una de las opiniones
    # Por opinion (recorda que cada publicacion tiene varias opiniones) Ojo que por ahi va solo al primer article y no a todos...
    opiniones_publicacion = driver.find_elements(By.XPATH, '//div[@class="infinite-scroll-component "]/article')

    for opinion in opiniones_publicacion:
        title = getOpinionTitle(opinion)
        content = getOpinionContent(opinion)
        rate = getOpinionRate(opinion)
        likes, dislikes = getOpinionLikes(opinion)

        # Cargo nueva fila al df
        df.loc[idx] = [id,title,content,rate,likes,dislikes]
        idx += 1

    return df


def ClickVerTodasLasOpiniones(driver):
    # Busco link de "Ver todas las opiniones" y hago click
    # El boton "ver todas las opiniones" esta dentro de un tag unico div#class=ui-pdp-reviews__actions__container

    try:
        link_opiniones = driver.find_element(By.XPATH,'//div[@class="ui-pdp-reviews__actions__container"]/a').get_attribute("href")
        driver.get(link_opiniones)
        resp = True
    except:
        resp = None

    return resp


def verificationNewOpinions(driver, df):
    """

    :param driver:
    :param df: dataframe cuya unidad de analisis es una opinion y las columnas son titulo, content, rate, fecha, likes, dislikes
    :return: True si son opiniones ya extraidas o False en caso que sean nuevas
    """
    # Preasumo que la opinion es nueva
    bool = True

    # Extraigo la primera opinion
    prim_opinion = driver.find_element(By.XPATH, '//div[@class="infinite-scroll-component "]/article/p').text

    # Veo si la primera opinion ya fue extraida
    if prim_opinion in df["content"]:
        bool = False

    return bool


def getOpinionTitle(opinion):
    title = opinion.find_element_by_xpath('.//h2').text
    return title


def getOpinionRate(opinion):
    """

    :param opinion: tag article con rate, content, titulo, likes y dislikes
    :return: Numero de estrellas de la opinion
    """
    n = 0
    stars = opinion.find_elements_by_class_name("ui-review-view__comments__review-comment__rating__star")
    # print(stars)

    for star in stars:
        # print(star.find_element_by_tag_name("path").get_attribute("fill"))
        # print(type(star.find_element_by_tag_name("path").get_attribute("fill")))
        # print(star.find_elements_by_class_name("fill"))

        if star.find_element_by_tag_name("path").get_attribute("fill") == "#3483FA":
            n += 1
        else:
            break
    return n


def getOpinionContent(opinion):
    try:
        content = opinion.find_element_by_xpath('.//p').text
    except:
        pass
    return content


def getOpinionLikes(opinion):
    # falta implementar handle exception
    likes = int(opinion.find_element_by_xpath('.//a[@data-testid="like-button"]').text)
    dislikes = int(opinion.find_element_by_xpath('.//a[@data-testid="dislike-button"]').text)
    return likes, dislikes