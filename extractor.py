import io
import pandas as pd
from docx import Document

def extraer_tabla(archivo):
    if isinstance(archivo, bytes):
        archivo = io.BytesIO(archivo)

    doc = Document(archivo)
    datos = []

    proceso_actual = ""
    tarea_actual = ""
    contenido_actual = []
    imagenes_count = 0

    def guardar_bloque():
        nonlocal tarea_actual, contenido_actual, imagenes_count
        if proceso_actual and (contenido_actual or imagenes_count > 0):
            # Si hay contenido pero no hay Título 3, asigna "General"
            nombre_tarea = tarea_actual if tarea_actual else "General"
            
            if imagenes_count > 0:
                contenido_actual.append(f"[IMAGENES DETECTADAS: {imagenes_count}]")

            datos.append({
                "Proceso": proceso_actual,
                "Tarea": nombre_tarea,
                "Contenido": "\n".join(contenido_actual)
            })

    for p in doc.paragraphs:
        num_imgs = len(p._element.xpath(".//a:blip"))
        if num_imgs > 0:
            imagenes_count += num_imgs

        texto = p.text.strip()
        if not texto and num_imgs == 0:
            continue

        estilo = p.style.name.strip()
        is_heading_2 = estilo in ["Heading 2", "Título 2", "Heading2", "Título2"]
        is_heading_3 = estilo in ["Heading 3", "Título 3", "Heading3", "Título3"]

        if is_heading_2:
            guardar_bloque()
            proceso_actual = texto
            tarea_actual = ""
            contenido_actual = []
            imagenes_count = 0

        elif is_heading_3:
            guardar_bloque()
            tarea_actual = texto
            contenido_actual = []
            imagenes_count = 0

        else:
            if proceso_actual:
                contenido_actual.append(texto)

    guardar_bloque()
    return pd.DataFrame(datos)
