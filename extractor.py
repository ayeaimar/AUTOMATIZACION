from docx import Document
import pandas as pd

def extraer_tabla(archivo):
    doc = Document(archivo)

    datos = []
    proceso_actual = "General"
    tarea_actual = "Inicio Documento"
    contenido_actual = []

    for p in doc.paragraphs:
        texto = p.text.strip()
        if not texto:
            continue

        estilo = p.style.name.lower()

        # Soporta estilos en inglés ("heading 2") y en español ("título 2")
        is_h2 = "heading 2" in estilo or "título 2" in estilo or "titulo 2" in estilo
        is_h3 = "heading 3" in estilo or "título 3" in estilo or "titulo 3" in estilo

        if is_h2:
            if contenido_actual or tarea_actual != "Inicio Documento":
                datos.append({
                    "Proceso": proceso_actual,
                    "Tarea": tarea_actual,
                    "Contenido": "\n".join(contenido_actual)
                })

            proceso_actual = texto
            tarea_actual = "General"
            contenido_actual = []

        elif is_h3:
            if contenido_actual or tarea_actual != "Inicio Documento":
                datos.append({
                    "Proceso": proceso_actual,
                    "Tarea": tarea_actual,
                    "Contenido": "\n".join(contenido_actual)
                })

            tarea_actual = texto
            contenido_actual = []

        else:
            contenido_actual.append(texto)

    # Agregar el último bloque leído
    if contenido_actual:
        datos.append({
            "Proceso": proceso_actual,
            "Tarea": tarea_actual,
            "Contenido": "\n".join(contenido_actual)
        })

    return pd.DataFrame(datos)
