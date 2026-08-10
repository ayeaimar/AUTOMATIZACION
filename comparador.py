import base64
import io
import pandas as pd
from docx import Document
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class RequestComparacion(BaseModel):
    nombre_viejo: str
    contenido_viejo_base64: str
    nombre_nuevo: str
    contenido_nuevo_base64: str


def extraer_tabla_docx(contenido_bytes: bytes) -> pd.DataFrame:
    """Lee un binario .docx y extrae la tabla principal a Dataframe."""
    doc = Document(io.BytesIO(contenido_bytes))
    datos = []

    for tabla in doc.tables:
        headers = [cell.text.strip() for cell in tabla.rows[0].cells]
        for row in tabla.rows[1:]:
            valores = [cell.text.strip() for cell in row.cells]
            if len(valores) == len(headers):
                datos.append(dict(zip(headers, valores)))

    df = pd.DataFrame(datos)
    # Limpieza básica de espacios y nulos
    return df.fillna("")


def comparar_dfs(df_anterior: pd.DataFrame, df_nuevo: pd.DataFrame) -> list:
    resultado = []

    anterior = {
        (str(r["Proceso"]).strip(), str(r["Tarea"]).strip()): str(
            r["Contenido"]
        ).strip()
        for _, r in df_anterior.iterrows()
    }

    nuevo = {
        (str(r["Proceso"]).strip(), str(r["Tarea"]).strip()): str(
            r["Contenido"]
        ).strip()
        for _, r in df_nuevo.iterrows()
    }

    # 1. Detectar Agregados y Modificados
    for clave, contenido_nuevo in nuevo.items():
        proceso, tarea = clave

        if clave not in anterior:
            resultado.append(
                {
                    "Proceso": proceso,
                    "Tarea": tarea,
                    "Estado": "AGREGADA",
                    "Detalle": f"Se agregó la tarea con contenido: '{contenido_nuevo}'",
                }
            )
        else:
            contenido_viejo = anterior[clave]
            if contenido_viejo != contenido_nuevo:
                resultado.append(
                    {
                        "Proceso": proceso,
                        "Tarea": tarea,
                        "Estado": "MODIFICADA",
                        "Detalle": f"Antes: '{contenido_viejo}' | Ahora: '{contenido_nuevo}'",
                    }
                )

    # 2. Detectar Eliminados
    for clave, contenido_viejo in anterior.items():
        if clave not in nuevo:
            proceso, tarea = clave
            resultado.append(
                {
                    "Proceso": proceso,
                    "Tarea": tarea,
                    "Estado": "ELIMINADA",
                    "Detalle": f"Se eliminó la tarea (Contenido previo: '{contenido_viejo}')",
                }
            )

    return resultado


@app.post("/comparar")
async def comparar_archivos(payload: RequestComparacion):
    try:
        # Decodificación binaria directa
        bytes_viejo = base64.b64decode(payload.contenido_viejo_base64)
        bytes_nuevo = base64.b64decode(payload.contenido_nuevo_base64)

        # Extracción a DataFrames
        df_viejo = extraer_tabla_docx(bytes_viejo)
        df_nuevo = extraer_tabla_docx(bytes_nuevo)

        # Ejecución del comparador
        lista_cambios = comparar_dfs(df_viejo, df_nuevo)

        # Generación del texto consolidado para el Prompt de IA
        if lista_cambios:
            lineas_resumen = [
                f"- [{c['Estado']}] Proceso: {c['Proceso']} | Tarea: {c['Tarea']} -> Detalle: {c['Detalle']}"
                for c in lista_cambios
            ]
            detalle_texto = "\n".join(lineas_resumen)
        else:
            detalle_texto = "No se detectaron diferencias entre las versiones del documento."

        # Retorno en el formato exacto que espera Parse JSON en Power Automate
        return {
            "estado": "OK",
            "cambios": lista_cambios,
            "detalle_texto": detalle_texto,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error en la comparación: {str(e)}"
        )
