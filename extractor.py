from docx import Document
import pandas as pd


def extraer_tabla(archivo):
    doc = Document(archivo)

    datos = []

    proceso_actual = ""
    tarea_actual = ""
    contenido_actual = []

    for p in doc.paragraphs:

        texto = p.text.strip()

        if not texto:
            continue

        estilo = p.style.name

        if estilo == "Heading 2":

            if tarea_actual:
                datos.append({
                    "Proceso": proceso_actual,
                    "Tarea": tarea_actual,
                    "Contenido": "\n".join(contenido_actual)
                })

            proceso_actual = texto
            tarea_actual = ""
            contenido_actual = []

        elif estilo == "Heading 3":

            if tarea_actual:
                datos.append({
                    "Proceso": proceso_actual,
                    "Tarea": tarea_actual,
                    "Contenido": "\n".join(contenido_actual)
                })

            tarea_actual = texto
            contenido_actual = []

        else:

            if tarea_actual:
                contenido_actual.append(texto)

    if tarea_actual:

        datos.append({
            "Proceso": proceso_actual,
            "Tarea": tarea_actual,
            "Contenido": "\n".join(contenido_actual)
        })

    return pd.DataFrame(datos)