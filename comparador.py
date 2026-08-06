import pandas as pd


def comparar(df_anterior, df_nuevo):
    resultado = []

    # 1. Armamos diccionarios con las claves (Proceso, Tarea)
    anterior = {
        (r["Proceso"], r["Tarea"]): str(r["Contenido"]).strip()
        for _, r in df_anterior.iterrows()
    }

    nuevo = {
        (r["Proceso"], r["Tarea"]): str(r["Contenido"]).strip()
        for _, r in df_nuevo.iterrows()
    }

    # 2. Detectar AGREGADAS y MODIFICADAS
    for clave, contenido_nuevo in nuevo.items():
        proceso, tarea = clave

        if clave not in anterior:
            resultado.append({
                "Proceso": proceso,
                "Tarea": tarea,
                "Estado": "AGREGADA",
                "Detalle": f"Nueva tarea agregada. Contenido: '{contenido_nuevo[:200]}...'"
            })
        else:
            contenido_viejo = anterior[clave]
            if contenido_viejo != contenido_nuevo:
                resultado.append({
                    "Proceso": proceso,
                    "Tarea": tarea,
                    "Estado": "MODIFICADA",
                    "Detalle": f"Texto anterior: '{contenido_viejo[:100]}...' | Texto nuevo: '{contenido_nuevo[:100]}...'"
                })

    # 3. Detectar ELIMINADAS
    for clave, contenido_viejo in anterior.items():
        if clave not in nuevo:
            proceso, tarea = clave
            resultado.append({
                "Proceso": proceso,
                "Tarea": tarea,
                "Estado": "ELIMINADA",
                "Detalle": f"Tarea eliminada. Texto previo: '{contenido_viejo[:200]}...'"
            })

    return pd.DataFrame(resultado)
