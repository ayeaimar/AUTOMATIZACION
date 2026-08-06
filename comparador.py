import pandas as pd

def comparar(df_anterior, df_nuevo):
    resultado = []

    anterior = {
        (r["Proceso"], r["Tarea"]): r["Contenido"].strip()
        for _, r in df_anterior.iterrows()
    }

    nuevo = {
        (r["Proceso"], r["Tarea"]): r["Contenido"].strip()
        for _, r in df_nuevo.iterrows()
    }

    # Detectar AGREGADAS y MODIFICADAS
    for clave, contenido_nuevo in nuevo.items():
        proceso, tarea = clave

        if clave not in anterior:
            resultado.append({
                "Proceso": proceso,
                "Tarea": tarea,
                "Estado": "AGREGADA",
                "Detalle": f"Se agregó contenido nuevo en esta sección: '{contenido_nuevo[:150]}...'"
            })
        else:
            contenido_viejo = anterior[clave]
            if contenido_viejo != contenido_nuevo:
                resultado.append({
                    "Proceso": proceso,
                    "Tarea": tarea,
                    "Estado": "MODIFICADA",
                    "Detalle": f"El contenido cambió de:\n'{contenido_viejo[:100]}...'\na:\n'{contenido_nuevo[:100]}...'"
                })

    # Detectar ELIMINADAS
    for clave, contenido_viejo in anterior.items():
        if clave not in nuevo:
            proceso, tarea = clave
            resultado.append({
                "Proceso": proceso,
                "Tarea": tarea,
                "Estado": "ELIMINADA",
                "Detalle": f"Se eliminó el contenido previo de esta sección: '{contenido_viejo[:150]}...'"
            })

    return pd.DataFrame(resultado)
