from fastapi import FastAPI
from pydantic import BaseModel
import base64
import os
import subprocess
import glob

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORIAL_VIEJO = os.path.join(BASE_DIR, "Historial_Viejo")
HISTORIAL_NUEVO = os.path.join(BASE_DIR, "Historial_Nuevo")
RESULTADOS_DIR = os.path.join(BASE_DIR, "Resultados")

class ComparacionRequest(BaseModel):
    nombre_viejo: str
    contenido_viejo_base64: str
    nombre_nuevo: str
    contenido_nuevo_base64: str

@app.post("/comparar")
def comparar(data: ComparacionRequest):
    os.makedirs(HISTORIAL_VIEJO, exist_ok=True)
    os.makedirs(HISTORIAL_NUEVO, exist_ok=True)
    os.makedirs(RESULTADOS_DIR, exist_ok=True)

    # Nombres fijos de trabajo en el servidor para evitar fallas de encoding/espacios
    path_viejo = os.path.join(HISTORIAL_VIEJO, "documento_viejo.docx")
    path_nuevo = os.path.join(HISTORIAL_NUEVO, "documento_nuevo.docx")

    # Guardar archivos binarios en disco
    with open(path_viejo, "wb") as f:
        f.write(base64.b64decode(data.contenido_viejo_base64))

    with open(path_nuevo, "wb") as f:
        f.write(base64.b64decode(data.contenido_nuevo_base64))

    # Ejecutar script con los nombres fijos creados
    resultado = subprocess.run(
        ["python", "ejecutar_comparacion.py", "documento_viejo.docx", "documento_nuevo.docx"],
        capture_output=True,
        text=True
    )

    exceles = glob.glob(os.path.join(RESULTADOS_DIR, "*.xlsx"))
    docxs = glob.glob(os.path.join(RESULTADOS_DIR, "*.docx"))

    ultimo_docx = max(docxs, key=os.path.getmtime) if docxs else ""
    ultimo_excel = max(exceles, key=os.path.getmtime) if exceles else ""

    excel_base64 = ""
    if ultimo_excel:
        with open(ultimo_excel, "rb") as f:
            excel_base64 = base64.b64encode(f.read()).decode("utf-8")

    return {
        "estado": "ok",
        "archivo_viejo": data.nombre_viejo,
        "archivo_nuevo": data.nombre_nuevo,
        "archivo_excel": ultimo_excel,
        "excel_base64": excel_base64,
        "detalle": resultado.stdout if resultado.stdout else resultado.stderr,
        "error": resultado.stderr,
        "archivo_docx": ultimo_docx
    }
