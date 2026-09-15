# Evaluación de alternativas de un producto en proceso de compra utilizando web scraping y análisis de sentimientos 

*Esta herramienta digital forma parte del catálogo de herramientas del **Banco Interamericano de Desarrollo**. Puedes conocer más sobre la iniciativa del BID en [code.iadb.org](https://code.iadb.org)*

<h1 align="center"> Evaluador de alternativas</h1>
<p align="center"> Logo e imagen o gif de la interfaz principal de la herramienta</p>
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
Esto es un archivo README. Debe contener la documentación de soporte uso de la herramienta digital. Las siguientes secciones son las secciones recomendadas que debes poner incluir en cualquier herramienta digital. Puedes descargar este archivo para que te sirva como plantilla.

Asegúrate de empezar este archivo con una breve descripción sobre las funcionalidades y contexto de la herramienta digital. Sé conciso y al grano.

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

## Guía de usuario
---
Explica los pasos básicos sobre cómo usar la herramienta digital. Es una buena sección para mostrar capturas de pantalla o gifs que ayuden a entender la herramienta digital.

## Autor/es
---
Nombra a el/los autor/es original/es. Consulta con ellos antes de publicar un email o un nombre personal. Una manera muy común es dirigirlos a sus cuentas de redes sociales.

## Información adicional
---
Esta es la sección que permite agregar más información de contexto al proyecto como alguna web de relevancia, proyectos similares o que hayan usado la misma tecnología.

## Licencia 
---

La licencia especifica los permisos y las condiciones de uso que el desarrollador otorga a otros desarrolladores que usen y/o modifiquen la herramienta digital.

Incluye en esta sección una nota con el tipo de licencia otorgado a esta herramienta digital. El texto de la licencia debe estar incluído en un archivo *LICENSE.md* o *LICENSE.txt* en la raíz del repositorio.

Si desconoces qué tipos de licencias existen y cuál es la mejor para cada caso, te recomendamos visitar la página https://choosealicense.com/.

Si la herramienta que estás publicando con la iniciativa Código para el Desarrollo ha sido financiada por el BID, te invitamos a revisar la [licencia oficial del banco para publicar software](https://github.com/EL-BID/Plantilla-de-repositorio/blob/master/LICENSE.md)

## Limitación de responsabilidades
Disclaimer: Esta sección es solo para herramientas financiadas por el BID.

El BID no será responsable, bajo circunstancia alguna, de daño ni indemnización, moral o patrimonial; directo o indirecto; accesorio o especial; o por vía de consecuencia, previsto o imprevisto, que pudiese surgir:

i. Bajo cualquier teoría de responsabilidad, ya sea por contrato, infracción de derechos de propiedad intelectual, negligencia o bajo cualquier otra teoría; y/o

ii. A raíz del uso de la Herramienta Digital, incluyendo, pero sin limitación de potenciales defectos en la Herramienta Digital, o la pérdida o inexactitud de los datos de cualquier tipo. Lo anterior incluye los gastos o daños asociados a fallas de comunicación y/o fallas de funcionamiento de computadoras, vinculados con la utilización de la Herramienta Digital.
