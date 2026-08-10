import base64
import io
import pandas as pd
from docx import Document
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class ComparacionRequest(BaseModel):
    nombre_viejo: str
    contenido_viejo_base64: str
    nombre_nuevo: str
    contenido_nuevo_base64: str


def extraer_tabla_docx(contenido_bytes: bytes) -> pd.DataFrame:
    """Lee el binario de Word en memoria y convierte sus tablas a DataFrame."""
    try:
        doc = Document(io.BytesIO(contenido_bytes))
        datos = []

        for tabla in doc.tables:
            if not tabla.rows:
                continue

            # Obtiene encabezados de la primera fila
            headers = [cell.text.strip() for cell in tabla.rows[0].cells]

            # Extrae las filas restantes
            for row in tabla.rows[1:]:
                valores = [cell.text.strip() for cell in row.cells]
                if len(valores) == len(headers):
                    datos.append(dict(zip(headers, valores)))

        df = pd.DataFrame(datos)
        return df.fillna("")
    except Exception as e:
        print(f"Error al extraer tabla del docx: {e}")
        return pd.DataFrame()


def comparar_procedimientos(
    df_anterior: pd.DataFrame, df_nuevo: pd.DataFrame
) -> list:
    """Compara procesos, tareas y contenidos entre dos versiones."""
    resultado = []

    # Validar presencia de columnas mínimas
    columnas_necesarias = {"Proceso", "Tarea", "Contenido"}
    if not columnas_necesarias.issubset(
        set(df_anterior.columns)
    ) or not columnas_necesarias.issubset(set(df_nuevo.columns)):
        return resultado

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

    # 1. Tareas Agregadas y Modificadas
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

    # 2. Tareas Eliminadas
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
def comparar(data: ComparacionRequest):
    try:
        # Decodificación en memoria
        bytes_viejo = base64.b64decode(data.contenido_viejo_base64)
        bytes_nuevo = base64.b64decode(data.contenido_nuevo_base64)

        # Conversión directa a DataFrames
        df_viejo = extraer_tabla_docx(bytes_viejo)
        df_nuevo = extraer_tabla_docx(bytes_nuevo)

        # Ejecución del comparador de diferencias
        filas_cambios = comparar_procedimientos(df_viejo, df_nuevo)

        # Formatear el resumen de texto para la IA (Run a prompt)
        if filas_cambios:
            lineas = [
                f"- [{c['Estado']}] Proceso: {c['Proceso']} | Tarea: {c['Tarea']} -> {c['Detalle']}"
                for c in filas_cambios
            ]
            detalle_texto = (
                f"Comparación entre '{data.nombre_viejo}' y '{data.nombre_nuevo}':\n"
                + "\n".join(lineas)
            )
        else:
            detalle_texto = f"Sin diferencias detectadas entre '{data.nombre_viejo}' y '{data.nombre_nuevo}'."

        # Retorno compatible con Parse JSON en Power Automate
        return {
            "estado": "ok",
            "cambios": filas_cambios,
            "detalle_texto": detalle_texto,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error en la API de comparación: {str(e)}"
        )
