# Evaluación de alternativas de un producto en proceso de compra utilizando web scraping y análisis de sentimientos 

<h1 align="center"> Evaluador de alternativas</h1>
<p align="center"><img src="https://nachomondino1-evaluacion-compra-automatica-my-appinicio-leworg.streamlit.app/~/+/media/364f7e86abe7e50f00933cae2fb2e014acb5032e99d8433f969098ce.jpeg"/></p>

## Tabla de contenidos:
---

- [Descripción y contexto](#descripción-y-contexto)
- [Guía de usuario](#guía-de-usuario)
- [Autor/es](#autores)
- [Información adicional](#información-adicional)
- [Licencia](#licencia)

## Descripción y contexto
---
Elegir entre alternativas de un mismo producto (qué celular comprar, qué smartband, qué TV) es un proceso lento: implica leer decenas de opiniones dispersas en distintas publicaciones y compararlas a mano. **Evaluador de alternativas** automatiza ese proceso: scrapea publicaciones y opiniones de compradores en MercadoLibre, les aplica análisis de sentimiento por atributo (precio, calidad, batería, etc.) y agrupa las alternativas por similitud, para que el usuario pueda comparar opciones según lo que a él o ella le importa, en lugar de tener que leer todo manualmente.

La herramienta ofrece dos vistas sobre estos mismos datos:

- **Evaluador de alternativas**: el usuario pondera qué tan importante es cada atributo del producto para su decisión de compra, y la herramienta le recomienda la alternativa que mejor se ajusta a esas prioridades.
- **Evaluador de marcas**: agrupa las alternativas en clusters según similitud de atributos y muestra qué marcas están mejor posicionadas en cada grupo, para responder qué marca prioriza qué característica y quién ofrece más calidad al menor precio.

Por ahora cubre tres categorías de producto: celulares, smartbands y TVs.

Nació como proyecto final de carrera y hoy sigue en desarrollo activo.

## Instalación y ejecución local
---
Para correr la app de Streamlit en tu máquina (Python 3.10 recomendado, ya que algunas dependencias no compilan en versiones más nuevas):

```bash
# 1) Crear y activar un entorno virtual
python3.10 -m venv venv
source venv/bin/activate

# 2) Instalar las dependencias necesarias para la app (streamlit)
pip install -r requirements.txt

# 3) Correr la app (desde la raíz del repo, no desde /my_app)
streamlit run my_app/Inicio.py
```

Esto abre la app en `http://localhost:8501`.

`requirements.txt` (en la raíz) tiene solo lo necesario para correr la app — es el mismo archivo que usa el deploy en Streamlit Community Cloud. Si en cambio necesitás el pipeline completo de scraping/NLP/modelado (`p1_data_understanding`, `p2_data_preparation`, `p3_modelling`), instalá `requirements-pipeline.txt`:

```bash
pip install -r requirements-pipeline.txt
```

## Despliegue en Render
---
El repo incluye [`render.yaml`](render.yaml), así que el deploy es automático:

1. Entrá a [render.com](https://render.com) y logueate con tu cuenta de GitHub.
2. `New` → `Blueprint`, elegí este repositorio.
3. Render lee `render.yaml` solo y crea el servicio (`evaluacion-alternativas-producto`), con el build (`pip install -r requirements.txt`) y el comando de arranque (`streamlit run my_app/Inicio.py`) ya configurados. Confirmá y esperá el primer deploy.
4. La URL final queda como `https://evaluacion-alternativas-producto.onrender.com` (Render agrega un sufijo si ese nombre ya está tomado).

En el plan free, el servicio se duerme tras 15 minutos de inactividad y tarda ~30-60s en volver a arrancar con la primera visita.

## Guía de usuario
---
1. Entrá a la app ([demo online](https://nachomondino1-evaluacion-compra-automatica-my-appinicio-leworg.streamlit.app/) o corriéndola localmente, ver sección anterior).
2. En la pantalla de inicio, elegí una de las dos herramientas: **Evaluador de alternativas** o **Evaluador de marcas**.
3. Seleccioná el producto que querés evaluar (celulares, smartband o TV).
4. **Si elegiste Evaluador de alternativas**: para cada atributo del producto (precio, calidad, batería, etc.), indicá con el slider qué tan importante es para vos — podés arrancar de un uso predefinido si el producto lo tiene, o ajustarlo manualmente. La herramienta te devuelve la alternativa que mejor se ajusta a esas prioridades.
5. **Si elegiste Evaluador de marcas**: seguí los tres pasos guiados — (1) elegís el producto, (2) explorás los grupos de alternativas similares que armó la herramienta, (3) ves qué marca está mejor posicionada en cada grupo, para comparar precio vs. calidad entre marcas.

## Autor/es
---
[Ignacio Mondino](https://github.com/nachomondino1) — nachomondino1@gmail.com

## Información adicional
---
- Demo online: https://nachomondino1-evaluacion-compra-automatica-my-appinicio-leworg.streamlit.app/
- Stack: Python, Selenium/BeautifulSoup (scraping de MercadoLibre), NLP para análisis de sentimiento por atributo, clustering (KMeans) para agrupar alternativas similares, Streamlit para la interfaz.
- Estructura del repo: `p1_data_understanding` (scraping y exploración), `p2_data_preparation` (limpieza y armado del dataset), `p3_modelling` (clustering y atribución de sentimiento), `p5_deployment`/`my_app` (la app de Streamlit).

## Licencia 
---
Este proyecto está bajo licencia MIT — ver [LICENSE.md](LICENSE.md).
