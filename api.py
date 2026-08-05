from fastapi import FastAPI
from pydantic import BaseModel

import subprocess
import os
import glob
import base64

app = FastAPI()

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

RESULTADOS_DIR = os.path.join(
    BASE_DIR,
    "Resultados"
)

class ComparacionRequest(BaseModel):
    archivo_viejo: str
    archivo_nuevo: str

@app.post("/comparar")
def comparar(data: ComparacionRequest):

    resultado = subprocess.run(
        [
            "python",
            "ejecutar_comparacion.py",
            data.archivo_viejo,
            data.archivo_nuevo
        ],
        capture_output=True,
        text=True
    )

    exceles = glob.glob(
        os.path.join(
            RESULTADOS_DIR,
            "*.xlsx"
        )
    )
 
    docxs = glob.glob(
        os.path.join(
            RESULTADOS_DIR,
            "*.docx"
        )
    )

    ultimo_docx = max(
        docxs,
        key=os.path.getmtime
    ) if docxs else ""

    ultimo_excel = max(
        exceles,
        key=os.path.getmtime
    ) if exceles else ""

    excel_base64 = ""

    if ultimo_excel:
        with open(
            ultimo_excel,
            "rb"
        ) as f:
            excel_base64 = base64.b64encode(
                f.read()
            ).decode("utf-8")

    return {
        "estado": "ok",
        "archivo_viejo": data.archivo_viejo,
        "archivo_nuevo": data.archivo_nuevo,
        "archivo_excel": ultimo_excel,
        "excel_base64": excel_base64,
        "detalle": resultado.stdout if resultado.stdout else resultado.stderr,
        "error": resultado.stderr,
        "archivo_docx": ultimo_docx

    }