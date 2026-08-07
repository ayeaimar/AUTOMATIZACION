@app.post("/comparar")
def comparar(data: ComparacionRequest):
    os.makedirs(HISTORIAL_VIEJO, exist_ok=True)
    os.makedirs(HISTORIAL_NUEVO, exist_ok=True)
    os.makedirs(RESULTADOS_DIR, exist_ok=True)

    path_viejo = os.path.join(HISTORIAL_VIEJO, "documento_viejo.docx")
    path_nuevo = os.path.join(HISTORIAL_NUEVO, "documento_nuevo.docx")

    with open(path_viejo, "wb") as f:
        f.write(base64.b64decode(data.contenido_viejo_base64))

    with open(path_nuevo, "wb") as f:
        f.write(base64.b64decode(data.contenido_nuevo_base64))

    resultado = subprocess.run(
        ["python", "ejecutar_comparacion.py", "documento_viejo.docx", "documento_nuevo.docx"],
        capture_output=True,
        text=True
    )

    # Recortar el texto de detalle si es extremadamente largo
    detalle_texto = resultado.stdout if resultado.stdout else resultado.stderr
    if len(detalle_texto) > 10000:
        detalle_texto = detalle_texto[:10000] + "\n...[Detalle truncado por longitud]"

    return {
        "estado": "ok",
        "archivo_viejo": data.nombre_viejo,
        "archivo_nuevo": data.nombre_nuevo,
        "detalle": detalle_texto
    }
