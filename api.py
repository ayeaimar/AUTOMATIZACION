from fastapi import FastAPI
from pydantic import BaseModel
import base64
import os
import subprocess
import glob
import json

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

    path_viejo = os.path.join(HISTORIAL_VIEJO, "documento_viejo.docx")
    path_nuevo = os.path.join(HISTORIAL_NUEVO, "documento_nuevo.docx")

    with open(path_viejo, "wb") as f:
        f.write(base64.b64decode(data.contenido_viejo_base64))

    with open(path_nuevo, "wb") as f:
        f.write(base64.b64decode(data.contenido_nuevo_base64))

    resultado = subprocess.run(
        ["python", "ejecutar_comparacion.py", "documento_viejo.docx", "documento_nuevo.docx"],
        capture_output=True,
        text=True
    )

    # Leemos el archivo excel temporal que genera ejecutar_comparacion.py para devolver las filas exactas
    exceles = glob.glob(os.path.join(RESULTADOS_DIR, "*.xlsx"))
    filas = []
    if exceles:
        import pandas as pd
        ultimo_excel = max(exceles, key=os.path.getmtime)
        df = pd.read_excel(ultimo_excel)
        filas = df.to_dict(orient="records")

    return {
        "estado": "ok",
        "cambios": filas,
        "detalle_texto": resultado.stdout
    }
