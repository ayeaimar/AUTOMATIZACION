import os
import sys
from datetime import datetime
from docx import Document
from extractor import extraer_tabla
from comparador import comparar

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

carpeta_anterior = os.path.join(BASE_DIR, "Historial_Viejo")
carpeta_nuevo = os.path.join(BASE_DIR, "Historial_Nuevo")
carpeta_resultados = os.path.join(BASE_DIR, "Resultados")

os.makedirs(carpeta_resultados, exist_ok=True)

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

# Extraer información y comparar
df_anterior = extraer_tabla(archivo_anterior)
df_nuevo = extraer_tabla(archivo_nuevo)

resultado = comparar(df_anterior, df_nuevo)

fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
excel_path = os.path.join(carpeta_resultados, f"Comparacion_{fecha}.xlsx")
resultado.to_excel(excel_path, index=False)

# Métricas (Sincronizadas en femenino con comparador.py)
if not resultado.empty and "Estado" in resultado.columns:
    agregadas = len(resultado[resultado["Estado"] == "AGREGADA"])
    modificadas = len(resultado[resultado["Estado"] == "MODIFICADA"])
    eliminadas = len(resultado[resultado["Estado"] == "ELIMINADA"])
else:
    agregadas = modificadas = eliminadas = 0

# Filtrar únicamente los cambios reales (Femenino)
if not resultado.empty and "Estado" in resultado.columns:
    df_cambios = resultado[resultado["Estado"].isin(["AGREGADA", "MODIFICADA", "ELIMINADA"])]
else:
    df_cambios = resultado

# Detalle completo con el contenido original vs nuevo
detalle_completo = ""
if not df_cambios.empty:
    for _, fila in df_cambios.iterrows():
        detalle_completo += (
            f"• Estado: {fila['Estado']}\n"
            f"  Proceso: {fila.get('Proceso', 'N/A')}\n"
            f"  Tarea: {fila.get('Tarea', 'N/A')}\n"
            f"  Detalle/Impacto: {fila.get('Detalle', 'N/A')}\n\n"
        )

# Crear documento Word
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

docx_path = os.path.join(carpeta_resultados, f"Informe_Comparacion_{fecha}.docx")
doc.save(docx_path)

# Salida formateada explícitamente para el Prompt de Power Automate / AI Builder
texto_para_ia = detalle_completo.strip() if detalle_completo.strip() else "Sin cambios detectados entre ambas versiones."

print(f"""
VIEJO: {os.path.basename(archivo_anterior)}
NUEVO: {os.path.basename(archivo_nuevo)}

Procesos/Tareas Agregadas: {agregadas}
Procesos/Tareas Modificadas: {modificadas}
Procesos/Tareas Eliminadas: {eliminadas}

DETALLE DE CAMBIOS DETECTADOS:
{texto_para_ia}
""")
