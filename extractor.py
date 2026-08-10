import io
import pandas as pd
from docx import Document


def extraer_tabla(archivo):
    # Si viene en bytes o Base64 decodificado, lo convertimos a BytesIO
    if isinstance(archivo, bytes):
        archivo = io.BytesIO(archivo)

    doc = Document(archivo)
    datos = []

    proceso_actual = ""
    tarea_actual = ""
    contenido_actual = []

    for p in doc.paragraphs:
        texto = p.text.strip()
        if not texto:
            continue

        # Normalizamos el nombre del estilo
        estilo = p.style.name.strip()

        # Detección de Proceso (Título 2 o Heading 2)
        is_heading_2 = estilo in ["Heading 2", "Título 2", "Heading2", "Título2"]
        # Detección de Tarea (Título 3 o Heading 3)
        is_heading_3 = estilo in ["Heading 3", "Título 3", "Heading3", "Título3"]

        if is_heading_2:
            # Si ya veníamos armando una tarea previa, guardarla
            if tarea_actual:
                datos.append(
                    {
                        "Proceso": proceso_actual,
                        "Tarea": tarea_actual,
                        "Contenido": "\n".join(contenido_actual),
                    }
                )

            proceso_actual = texto
            tarea_actual = ""
            contenido_actual = []

        elif is_heading_3:
            # Guardar la tarea anterior
            if tarea_actual:
                datos.append(
                    {
                        "Proceso": proceso_actual,
                        "Tarea": tarea_actual,
                        "Contenido": "\n".join(contenido_actual),
                    }
                )

            tarea_actual = texto
            contenido_actual = []

        else:
            # Es un párrafo de texto normal dentro de una tarea
            if tarea_actual:
                contenido_actual.append(texto)

    # Guardar el último bloque leído
    if tarea_actual:
        datos.append(
            {
                "Proceso": proceso_actual,
                "Tarea": tarea_actual,
                "Contenido": "\n".join(contenido_actual),
            }
        )

    return pd.DataFrame(datos)
