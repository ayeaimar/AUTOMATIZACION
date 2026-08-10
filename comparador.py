import base64
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Importamos el extractor corregido
from extractor import extraer_tabla

app = FastAPI()


class RequestComparacion(BaseModel):
    nombre_viejo: str
    contenido_viejo_base64: str
    nombre_nuevo: str
    contenido_nuevo_base64: str


def comparar_dfs(df_anterior: pd.DataFrame, df_nuevo: pd.DataFrame) -> list:
    resultado = []

    # Asegurar que existan las columnas necesarias
    for df in [df_anterior, df_nuevo]:
        if df.empty:
            continue
        for col in ["Proceso", "Tarea", "Contenido"]:
            if col not in df.columns:
                df[col] = ""

    # Si ambos DataFrames están vacíos, no hay nada que comparar
    if df_anterior.empty and df_nuevo.empty:
        return resultado

    anterior = {}
    if not df_anterior.empty:
        anterior = {
            (
                str(r.get("Proceso", "")).strip(),
                str(r.get("Tarea", "")).strip(),
            ): str(r.get("Contenido", "")).strip()
            for _, r in df_anterior.iterrows()
        }

    nuevo = {}
    if not df_nuevo.empty:
        nuevo = {
            (
                str(r.get("Proceso", "")).strip(),
                str(r.get("Tarea", "")).strip(),
            ): str(r.get("Contenido", "")).strip()
            for _, r in df_nuevo.iterrows()
        }

    # 1. Detectar Agregados y Modificados
    for clave, contenido_nuevo in nuevo.items():
        proceso, tarea = clave

        if clave not in anterior:
            resultado.append(
                {
                    "Proceso": proceso if proceso else "General",
                    "Tarea": tarea if tarea else "General",
                    "Estado": "AGREGADA",
                    "Detalle": f"Se agregó contenido: '{contenido_nuevo}'",
                }
            )
        else:
            contenido_viejo = anterior[clave]
            if contenido_viejo != contenido_nuevo:
                resultado.append(
                    {
                        "Proceso": proceso if proceso else "General",
                        "Tarea": tarea if tarea else "General",
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
                    "Proceso": proceso if proceso else "General",
                    "Tarea": tarea if tarea else "General",
                    "Estado": "ELIMINADA",
                    "Detalle": f"Se eliminó contenido (Anterior: '{contenido_viejo}')",
                }
            )

    return resultado


@app.post("/comparar")
async def comparar_archivos(payload: RequestComparacion):
    try:
        bytes_viejo = base64.b64decode(payload.contenido_viejo_base64)
        bytes_nuevo = base64.b64decode(payload.contenido_nuevo_base64)

        df_viejo = extraer_tabla(bytes_viejo)
        df_nuevo = extraer_tabla(bytes_nuevo)

        lista_cambios = comparar_dfs(df_viejo, df_nuevo)

        if lista_cambios:
            lineas_resumen = [
                f"- [{c['Estado']}] Proceso: {c['Proceso']} | Tarea: {c['Tarea']} -> Detalle: {c['Detalle']}"
                for c in lista_cambios
            ]
            detalle_texto = "\n".join(lineas_resumen)
        else:
            detalle_texto = f"Sin diferencias detectadas entre '{payload.nombre_viejo}' y '{payload.nombre_nuevo}'."

        return {
            "estado": "ok",
            "cambios": lista_cambios,
            "detalle_texto": detalle_texto,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error en la comparación: {str(e)}"
        )
