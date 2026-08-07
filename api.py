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

    docx_base64 = ""

    if ultimo_docx:

        with open(
            ultimo_docx,
            "rb"
        ) as f:

            docx_base64 = base64.b64encode(
                f.read()
            ).decode("utf-8")

    return {
        "estado": "ok",
        "archivo_viejo": data.archivo_viejo,
        "archivo_nuevo": data.archivo_nuevo,
        "archivo_docx": ultimo_docx,
        "docx_base64": docx_base64,
        "detalle": resultado.stdout,
        "error": resultado.stderr
    }
