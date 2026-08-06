import pandas as pd


def comparar(df_anterior, df_nuevo):

    resultado = []

    anterior = {
        (r["Proceso"], r["Tarea"]): r["Contenido"]
        for _, r in df_anterior.iterrows()
    }

    nuevo = {
        (r["Proceso"], r["Tarea"]): r["Contenido"]
        for _, r in df_nuevo.iterrows()
    }

    for clave, contenido_nuevo in nuevo.items():

        proceso, tarea = clave

        if clave not in anterior:

            resultado.append({
                "Proceso": proceso,
                "Tarea": tarea,
                "Estado": "AGREGADA",
                "Detalle": "Nueva tarea"
            })

        else:

            contenido_viejo = anterior[clave]

            if str(contenido_viejo) != str(contenido_nuevo):

                resultado.append({
                    "Proceso": proceso,
                    "Tarea": tarea,
                    "Estado": "MODIFICADA",
                    "Detalle": "Contenido actualizado"
                })

    for clave in anterior:

        if clave not in nuevo:

            proceso, tarea = clave

            resultado.append({
                "Proceso": proceso,
                "Tarea": tarea,
                "Estado": "ELIMINADA",
                "Detalle": "La tarea ya no existe"
            })

    return pd.DataFrame(resultado)