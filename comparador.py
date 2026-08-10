import base64
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Importamos el extractor corregido que lee Títulos, Párrafos e Imágenes
from extractor import extraer_tabla

app = FastAPI()


class RequestComparacion(BaseModel):
    nombre_viejo: str
    contenido_viejo_base64: str
    nombre_nuevo: str
    contenido_nuevo_base64: str


def comparar_dfs(df_anterior: pd.DataFrame, df_nuevo: pd.DataFrame) -> list:
    resultado = []

    # Validar columnas necesarias
    for df in [df_anterior, df_nuevo]:
        for col in ["Proceso", "Tarea", "Contenido"]:
            if col not in df.columns:
                df[col] = ""

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
                    "Detalle": f"Se agregó la sección/tarea con contenido: '{contenido_nuevo}'",
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
                        "Detalle": f"Se modificó el contenido. Antes: '{contenido_viejo}' | Ahora: '{contenido_nuevo}'",
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
                    "Detalle": f"Se eliminó la sección/tarea (Contenido previo: '{contenido_viejo}')",
                }
            )

    return resultado


@app.post("/comparar")
async def comparar_archivos(payload: RequestComparacion):
    try:
        # Decodificación binaria de los Base64 de Power Automate
        bytes_viejo = base64.b64decode(payload.contenido_viejo_base64)
        bytes_nuevo = base64.b64decode(payload.contenido_nuevo_base64)

        # Extracción procesando directamente en memoria mediante extractor.py
        df_viejo = extraer_tabla(bytes_viejo)
        df_nuevo = extraer_tabla(bytes_nuevo)

        # Ejecución de la comparación
        lista_cambios = comparar_dfs(df_viejo, df_nuevo)

        # Construcción del texto consolidado
        if lista_cambios:
            lineas_resumen = [
                f"- [{c['Estado']}] Proceso: {c['Proceso']} | Tarea: {c['Tarea']} -> Detalle: {c['Detalle']}"
                for c in lista_cambios
            ]
            detalle_texto = "\n".join(lineas_resumen)
        else:
            detalle_texto = "Sin diferencias detectadas entre las versiones del documento."

        return {
            "estado": "OK",
            "cambios": lista_cambios,
            "detalle_texto": detalle_texto,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error en la comparación: {str(e)}"
        )
