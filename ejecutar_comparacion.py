import os
import sys
from datetime import datetime
from docx import Document
from extractor import extraer_tabla
from comparador import comparar

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Carpetas
carpeta_anterior = os.path.join(BASE_DIR, "Historial_Viejo")
carpeta_nuevo = os.path.join(BASE_DIR, "Historial_Nuevo")
carpeta_resultados = os.path.join(BASE_DIR, "Resultados")

os.makedirs(carpeta_resultados, exist_ok=True)

# Buscar DOCX
archivos_viejos = [
    os.path.join(carpeta_anterior, f)
    for f in os.listdir(carpeta_anterior)
    if f.lower().endswith(".docx")
]

archivos_nuevos = [
    os.path.join(carpeta_nuevo, f)
    for f in os.listdir(carpeta_nuevo)
    if f.lower().endswith(".docx")
]

if not archivos_viejos:
    raise Exception("No existen archivos en Historial_Viejo")

if not archivos_nuevos:
    raise Exception("No existen archivos en Historial_Nuevo")

# Archivos recibidos desde Power Automate
if len(sys.argv) < 3:
    raise Exception("Debe recibir archivo_viejo y archivo_nuevo")

archivo_viejo = sys.argv[1]
archivo_nuevo = sys.argv[2]

archivo_anterior = os.path.join(carpeta_anterior, archivo_viejo)
archivo_nuevo = os.path.join(carpeta_nuevo, archivo_nuevo)

if not os.path.exists(archivo_anterior):
    raise Exception(f"No existe el archivo viejo: {archivo_anterior}")

if not os.path.exists(archivo_nuevo):
    raise Exception(f"No existe el archivo nuevo: {archivo_nuevo}")

print(f"VIEJO: {os.path.basename(archivo_anterior)}")
print(f"NUEVO: {os.path.basename(archivo_nuevo)}")

# Extraer información
df_anterior = extraer_tabla(archivo_anterior)
df_nuevo = extraer_tabla(archivo_nuevo)

# Comparar
resultado = comparar(df_anterior, df_nuevo)

print("COLUMNAS:")
print(resultado.columns.tolist())

print("RESULTADO:")
print(resultado.head())

# Timestamp
fecha = datetime.now().strftime("%Y%m%d_%H%M%S")

# Archivos de salida
excel_path = os.path.join(carpeta_resultados, f"Comparacion_{fecha}.xlsx")

# Guardar resultados
resultado.to_excel(excel_path, index=False)

# Métricas (Alineadas sin espacios extra)
agregadas = len(resultado[resultado["Estado"] == "AGREGADO"])
modificadas = len(resultado[resultado["Estado"] == "MODIFICADO"])
eliminadas = len(resultado[resultado["Estado"] == "ELIMINADO"])

# Imprimir en consola la cantidad de filas que detectó la comparación
print(f"Total filas en resultado: {len(resultado)}")
if "Estado" in resultado.columns:
    print(resultado["Estado"].value_counts())

# Detalle de cambios
detalle_completo = ""
# Filtra solo las filas que tengan cambios reales
df_cambios = resultado[resultado["Estado"].isin(["AGREGADO", "MODIFICADO", "ELIMINADO"])]
for _, fila in resultado.iterrows():
    detalle_completo += (
        f"Estado: {fila['Estado']}\n"
        f"Proceso: {fila['Proceso']}\n"
        f"Tarea: {fila['Tarea']}\n"
        f"Detalle: {fila['Detalle']}\n\n"
    )

# Crear Word
doc = Document()

doc.add_heading('Informe de Comparación de Procedimientos', level=1)
doc.add_paragraph(f'Documento anterior: {os.path.basename(archivo_anterior)}')
doc.add_paragraph(f'Documento nuevo: {os.path.basename(archivo_nuevo)}')
doc.add_paragraph(f'Agregadas: {agregadas}')
doc.add_paragraph(f'Modificadas: {modificadas}')
doc.add_paragraph(f'Eliminadas: {eliminadas}')

doc.add_heading('Cambios detectados', level=2)

if detalle_completo.strip():
    doc.add_paragraph(detalle_completo)
else:
    doc.add_paragraph('No se detectaron cambios entre ambas versiones.')

# Guardar word
docx_path = os.path.join(carpeta_resultados, f"Informe_Comparacion_{fecha}.docx")
doc.save(docx_path)

# Salida para FastAPI
print(f"""
VIEJO: {os.path.basename(archivo_anterior)}
NUEVO: {os.path.basename(archivo_nuevo)}

Agregadas: {agregadas}
Modificadas: {modificadas}
Eliminadas: {eliminadas}

Cambios detectados:

{detalle_completo}
""")
