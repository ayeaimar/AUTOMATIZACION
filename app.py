import streamlit as st
import pandas as pd
import os
import pythoncom
import win32com.client

from extractor import extraer_tabla
from comparador import comparar

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(
    page_title="Control de Cambios",
    layout="wide"
)

st.title("Control de Cambios de Documentos")

# RUTAS
carpeta_anterior = os.path.join(
    BASE_DIR,
    "Historial_Viejo"
)

carpeta_nuevo = os.path.join(
    BASE_DIR,
    "Historial_Nuevo"
)

# BOTÓN PRINCIPAL
if st.button("Generar Comparación"):

    if not os.path.exists(carpeta_anterior):
        st.error(f"No existe la carpeta:\n{carpeta_anterior}")
        st.stop()

    if not os.path.exists(carpeta_nuevo):
        st.error(f"No existe la carpeta:\n{carpeta_nuevo}")
        st.stop()

    archivos_viejos = [
        os.path.join(carpeta_anterior, f)
        for f in os.listdir(carpeta_anterior)
        if f.lower().endswith(".docx")
    ]

    archivos_nuevos = [
        os.path.join(carpeta_nuevo, f)
        for f in os.listdir(carpeta_nuevo)
        if f.lower().endswith(".docx")
    ]

    if len(archivos_viejos) == 0:
        st.error("No hay archivos DOCX en Historial_Viejo")
        st.stop()

    if len(archivos_nuevos) == 0:
        st.error("No hay archivos DOCX en Historial_Nuevo")
        st.stop()

    archivo_anterior = max(
        archivos_viejos,
        key=os.path.getmtime
    )

    archivo_nuevo = max(
        archivos_nuevos,
        key=os.path.getmtime
    )

    df_anterior = extraer_tabla(archivo_anterior)
    df_nuevo = extraer_tabla(archivo_nuevo)

    resultado = comparar(
        df_anterior,
        df_nuevo
    )

    # GUARDAR EN MEMORIA
    st.session_state["archivo_anterior"] = archivo_anterior
    st.session_state["archivo_nuevo"] = archivo_nuevo
    st.session_state["resultado"] = resultado


# MOSTRAR RESULTADOS SI YA EXISTEN
if "resultado" in st.session_state:

    archivo_anterior = st.session_state["archivo_anterior"]
    archivo_nuevo = st.session_state["archivo_nuevo"]
    resultado = st.session_state["resultado"]

    st.success(
        f"Documento anterior: {os.path.basename(archivo_anterior)}"
    )

    st.success(
        f"Documento nuevo: {os.path.basename(archivo_nuevo)}"
    )

    agregadas = len(
        resultado[
            resultado["Estado"] == "AGREGADA"
        ]
    )

    modificadas = len(
        resultado[
            resultado["Estado"] == "MODIFICADA"
        ]
    )

    eliminadas = len(
        resultado[
            resultado["Estado"] == "ELIMINADA"
        ]
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Agregadas",
        agregadas
    )

    col2.metric(
        "Modificadas",
        modificadas
    )

    col3.metric(
        "Eliminadas",
        eliminadas
    )

    st.dataframe(
        resultado,
        use_container_width=True
    )

    resultado.to_excel(
        "resultado.xlsx",
        index=False
    )

    resultado.to_csv(
        "resultado.csv",
        index=False
    )

    with open("resultado.xlsx", "rb") as f:

        st.download_button(
            "Descargar Excel",
            f,
            "Comparacion.xlsx"
        )

    with open("resultado.csv", "rb") as f:

        st.download_button(
            "Descargar CSV",
            f,
            "Comparacion.csv"
        )

    st.divider()

    if st.button("Convertir Documento Nuevo a PDF"):

        st.info(
            f"Documento seleccionado: "
            f"{os.path.basename(archivo_nuevo)}"
        )

        try:

            pythoncom.CoInitialize()

            ruta_doc = os.path.abspath(
                st.session_state["archivo_nuevo"]
            )

            st.write("Ruta DOCX:", ruta_doc)

            pdf_path = (
                os.path.splitext(ruta_doc)[0]
                + ".pdf"
            )

            word = win32com.client.Dispatch(
                "Word.Application"
            )

            word.Visible = False
            word.DisplayAlerts = 0

            doc = word.Documents.Open(
                FileName=ruta_doc,
                ReadOnly=True
            )

            doc.ExportAsFixedFormat(
                OutputFileName=pdf_path,
                ExportFormat=17
            )

            doc.Close(False)
            word.Quit()

            pythoncom.CoUninitialize()

            st.success(
                "PDF generado correctamente"
            )

            with open(pdf_path, "rb") as pdf:

                st.download_button(
                    "Descargar PDF",
                    pdf,
                    os.path.basename(pdf_path),
                    mime="application/pdf"
                )

        except Exception as e:

            st.error(
                f"Error al generar PDF: {e}"
            )
