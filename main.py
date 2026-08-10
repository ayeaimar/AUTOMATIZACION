import os
import pandas as pd
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sharepoint import SharePointManager
from comparator import compare_documents

app = FastAPI(title="Control de Cambios de Documentos")
templates = Jinja2Templates(directory="templates")

# Almacenamiento temporal
TEMP_DIR = "temp_files"
os.makedirs(TEMP_DIR, exist_ok=True)

# Guardar último dataframe generado en memoria para descargas
CURRENT_DF = pd.DataFrame()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "doc_viejo": None,
        "doc_nuevo": None,
        "counts": {"agregadas": 0, "modificadas": 0, "eliminadas": 0},
        "items": []
    })

@app.post("/api/comparar")
async def comparar_documentos_api():
    global CURRENT_DF
    sp = SharePointManager()
    
    path_viejo = os.path.join(TEMP_DIR, "viejo.docx")
    path_nuevo = os.path.join(TEMP_DIR, "nuevo.docx")
    
    name_viejo = sp.get_latest_file_from_folder("Control_Cambios/Historial_Viejo", path_viejo)
    name_nuevo = sp.get_latest_file_from_folder("Control_Cambios/Historial_Nuevo", path_nuevo)
    
    df, counts = compare_documents(path_viejo, path_nuevo)
    CURRENT_DF = df
    
    # Guardar Excel localmente para que se pueda descargar vía HTTP
    excel_path = os.path.join(TEMP_DIR, "Resultado_Comparacion.xlsx")
    df.to_excel(excel_path, index=False)
    
    return {
        "status": "success",
        "doc_viejo": name_viejo,
        "doc_nuevo": name_nuevo,
        "counts": counts,
        "items": df.to_dict(orient="records") if not df.empty else []
    }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/excel")
async def download_excel():
    if CURRENT_DF.empty:
        raise HTTPException(status_code=400, detail="No hay datos de comparación disponibles.")
    file_path = os.path.join(TEMP_DIR, "Resultado_Comparacion.xlsx")
    CURRENT_DF.to_excel(file_path, index=False)
    return FileResponse(file_path, filename="Resultado_Comparacion.xlsx")

@app.get("/api/download/csv")
async def download_csv():
    if CURRENT_DF.empty:
        raise HTTPException(status_code=400, detail="No hay datos de comparación disponibles.")
    file_path = os.path.join(TEMP_DIR, "Resultado_Comparacion.csv")
    CURRENT_DF.to_csv(file_path, index=False, encoding="utf-8-sig")
    return FileResponse(file_path, filename="Resultado_Comparacion.csv")
