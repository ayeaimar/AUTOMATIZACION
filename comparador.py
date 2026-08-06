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

archivo_anterior = os.path.join(carpeta_anterior, sys.argv[1].strip())
archivo_nuevo_path = os.path.join(carpeta_nuevo, sys.argv[2].strip())

if not os.path.exists(archivo_anterior):
    raise Exception(f"No existe el archivo viejo: {archivo_anterior}")

if not os.path.exists(archivo_nuevo_path):
    raise Exception(f"No existe el archivo nuevo: {archivo_nuevo_path}")

df_anterior = extraer_tabla(archivo_anterior)
df_nuevo = extraer_tabla(archivo_nuevo_path)

resultado = comparar(df_anterior, df_nuevo)

fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
excel_path = os.path.join(carpeta_resultados, f"Comparacion_{fecha}.xlsx")

if not resultado.empty:
    resultado.to_excel(excel_path, index=False)

if not resultado.empty and "Estado" in resultado.columns:
    agregadas = len(resultado[resultado["Estado"] == "AGREGADA"])
    modificadas = len(resultado[resultado["Estado"] == "MODIFICADA"])
    eliminadas = len(resultado[resultado["Estado"] == "ELIMINADA"])
    df_cambios = resultado[resultado["Estado"].isin(["AGREGADA", "MODIFICADA", "ELIMINADA"])]
else:
    agregadas = modificadas = eliminadas = 0
    df_cambios = resultado

detalle_completo = ""
if not df_cambios.empty:
    for _, fila in df_cambios.iterrows():
        detalle_completo += (
            f"• Estado: {fila['Estado']}\n"
            f"  Proceso: {fila.get('Proceso', 'General')}\n"
            f"  Tarea: {fila.get('Tarea', 'General')}\n"
            f"  Detalle/Impacto: {fila.get('Detalle', 'Sin detalle')}\n\n"
        )

doc = Document()
doc.add_heading('Informe de Comparación de Procedimientos', level=1)
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

texto_para_ia = detalle_completo.strip() if detalle_completo.strip() else "Sin cambios detectados entre ambas versiones."

print(f"""
Procesos/Tareas Agregadas: {agregadas}
Procesos/Tareas Modificadas: {modificadas}
Procesos/Tareas Eliminadas: {eliminadas}

DETALLE DE CAMBIOS DETECTADOS:
{texto_para_ia}
""")
