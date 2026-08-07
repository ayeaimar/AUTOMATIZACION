import os
import sys

from datetime import datetime

import pandas as pd

from docx import Document

from extractor import extraer_tabla
from comparador import comparar


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

carpeta_anterior = os.path.join(
    BASE_DIR,
    "Historial_Viejo"
)

carpeta_nuevo = os.path.join(
    BASE_DIR,
    "Historial_Nuevo"
)

carpeta_resultados = os.path.join(
    BASE_DIR,
    "Resultados"
)

os.makedirs(
    carpeta_resultados,
    exist_ok=True
)

if len(sys.argv) < 3:

    raise Exception(
        "Debe recibir archivo_viejo y archivo_nuevo"
    )

nombre_archivo_viejo = sys.argv[1]
nombre_archivo_nuevo = sys.argv[2]

archivo_anterior = os.path.join(
    carpeta_anterior,
    nombre_archivo_viejo
)

archivo_nuevo = os.path.join(
    carpeta_nuevo,
    nombre_archivo_nuevo
)

if not os.path.exists(archivo_anterior):

    raise Exception(
        f"No existe el archivo viejo: {archivo_anterior}"
    )

if not os.path.exists(archivo_nuevo):

    raise Exception(
        f"No existe el archivo nuevo: {archivo_nuevo}"
    )

print(
    f"VIEJO: {os.path.basename(archivo_anterior)}"
)

print(
    f"NUEVO: {os.path.basename(archivo_nuevo)}"
)

df_anterior = extraer_tabla(
    archivo_anterior
)

df_nuevo = extraer_tabla(
    archivo_nuevo
)

resultado = comparar(
    df_anterior,
    df_nuevo
)

fecha = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

excel_path = os.path.join(
    carpeta_resultados,
    f"Comparacion_{fecha}.xlsx"
)

resultado.to_excel(
    excel_path,
    index=False
)

agregadas = len(
    resultado[
        resultado["Estado"] == "AGREGADA"
    ]
) if not resultado.empty else 0

modificadas = len(
    resultado[
        resultado["Estado"] == "MODIFICADA"
    ]
) if not resultado.empty else 0

eliminadas = len(
    resultado[
        resultado["Estado"] == "ELIMINADA"
    ]
) if not resultado.empty else 0

detalle_completo = ""

if not resultado.empty:

    for _, fila in resultado.iterrows():

        detalle_completo += (
            f"Estado: {fila['Estado']}\n"
            f"Proceso: {fila['Proceso']}\n"
            f"Tarea: {fila['Tarea']}\n"
            f"Detalle: {fila['Detalle']}\n\n"
        )

doc = Document()

doc.add_heading(
    "Informe de Comparación de Procedimientos",
    level=1
)

doc.add_paragraph(
    f"Documento anterior: "
    f"{os.path.basename(archivo_anterior)}"
)

doc.add_paragraph(
    f"Documento nuevo: "
    f"{os.path.basename(archivo_nuevo)}"
)

doc.add_paragraph(
    f"Agregadas: {agregadas}"
)

doc.add_paragraph(
    f"Modificadas: {modificadas}"
)

doc.add_paragraph(
    f"Eliminadas: {eliminadas}"
)

doc.add_heading(
    "Cambios detectados",
    level=2
)

if detalle_completo.strip():

    doc.add_paragraph(
        detalle_completo
    )

else:

    doc.add_paragraph(
        "No se detectaron cambios entre ambas versiones."
    )

docx_path = os.path.join(
    carpeta_resultados,
    f"Informe_Comparacion_{fecha}.docx"
)

doc.save(docx_path)

print(
    f"""
VIEJO: {os.path.basename(archivo_anterior)}
NUEVO: {os.path.basename(archivo_nuevo)}

Agregadas: {agregadas}
Modificadas: {modificadas}
Eliminadas: {eliminadas}

Cambios detectados:

{detalle_completo}
"""
)
