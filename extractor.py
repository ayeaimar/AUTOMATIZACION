from docx import Document
import pandas as pd

def extraer_tabla(archivo):
    doc = Document(archivo)
    datos = []
    
    proceso_actual = "General"
    tarea_actual = "Sección General"
    contenido_actual = []

    for p in doc.paragraphs:
        texto = p.text.strip()
        if not texto:
            continue

        estilo = p.style.name.lower()
        is_h1_h2 = "heading 1" in estilo or "heading 2" in estilo or "título 1" in estilo or "título 2" in estilo
        is_h3_h4 = "heading 3" in estilo or "heading 4" in estilo or "título 3" in estilo or "título 4" in estilo

        if is_h1_h2:
            if contenido_actual:
                datos.append({
                    "Proceso": proceso_actual,
                    "Tarea": tarea_actual,
                    "Contenido": "\n".join(contenido_actual)
                })
                contenido_actual = []
            proceso_actual = texto
            tarea_actual = "General"

        elif is_h3_h4:
            if contenido_actual:
                datos.append({
                    "Proceso": proceso_actual,
                    "Tarea": tarea_actual,
                    "Contenido": "\n".join(contenido_actual)
                })
                contenido_actual = []
            tarea_actual = texto

        else:
            contenido_actual.append(texto)

    # Capturar el último bloque
    if contenido_actual:
        datos.append({
            "Proceso": proceso_actual,
            "Tarea": tarea_actual,
            "Contenido": "\n".join(contenido_actual)
        })

    return pd.DataFrame(datos)
