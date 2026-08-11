import base64
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from extractor import extraer_tabla

app = FastAPI()


class ComparacionRequest(BaseModel):
    nombre_viejo: str
    contenido_viejo_base64: str
    nombre_nuevo: str
    contenido_nuevo_base64: str


def comparar_procedimientos(df_anterior, df_nuevo):
    resultado = []

    for df in [df_anterior, df_nuevo]:
        if df.empty:
            continue

        for col in ["Proceso", "Tarea", "Contenido"]:
            if col not in df.columns:
                df[col] = ""

    anterior = (
        {
            (
                str(r["Proceso"]).strip(),
                str(r["Tarea"]).strip(),
            ): str(r["Contenido"]).strip()
            for _, r in df_anterior.iterrows()
        }
        if not df_anterior.empty
        else {}
    )

    nuevo = (
        {
            (
                str(r["Proceso"]).strip(),
                str(r["Tarea"]).strip(),
            ): str(r["Contenido"]).strip()
            for _, r in df_nuevo.iterrows()
        }
        if not df_nuevo.empty
        else {}
    )

    # AGREGADAS Y MODIFICADAS
    for clave, contenido_nuevo in nuevo.items():
        proceso, tarea = clave

        if clave not in anterior:
            resultado.append(
                {
                    "Proceso": proceso,
                    "Tarea": tarea,
                    "Estado": "AGREGADA",
                    "Detalle": f"Se agregó contenido: {contenido_nuevo}",
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
                        "Detalle": (
                            f"Antes: {contenido_viejo} | "
                            f"Ahora: {contenido_nuevo}"
                        ),
                    }
                )

    # ELIMINADAS
    for clave, contenido_viejo in anterior.items():
        if clave not in nuevo:
            proceso, tarea = clave

            resultado.append(
                {
                    "Proceso": proceso,
                    "Tarea": tarea,
                    "Estado": "ELIMINADA",
                    "Detalle": f"Contenido eliminado: {contenido_viejo}",
                }
            )

    return resultado


@app.post("/comparar")
async def comparar_archivos(payload: ComparacionRequest):
    try:
        bytes_viejo = base64.b64decode(payload.contenido_viejo_base64)
        bytes_nuevo = base64.b64decode(payload.contenido_nuevo_base64)

        # USA TU extractor.py
        df_viejo = extraer_tabla(bytes_viejo)
        df_nuevo = extraer_tabla(bytes_nuevo)

        # DEBUG
        print("FILAS VIEJO:", len(df_viejo))
        print("FILAS NUEVO:", len(df_nuevo))

        lista_cambios = comparar_procedimientos(
            df_viejo,
            df_nuevo,
        )

        if lista_cambios:
            detalle_texto = "\n".join(
                [
                    (
                        f"[{c['Estado']}] "
                        f"Proceso: {c['Proceso']} | "
                        f"Tarea: {c['Tarea']} | "
                        f"Detalle: {c['Detalle']}"
                    )
                    for c in lista_cambios
                ]
            )
        else:
            detalle_texto = "Sin diferencias detectadas."

        return {
            "estado": "ok",
            "cambios": lista_cambios,
            "detalle_texto": detalle_texto,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en la comparación: {str(e)}",
        )
