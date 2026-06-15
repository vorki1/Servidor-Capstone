from pathlib import Path
from fastapi import UploadFile, HTTPException
from fastapi.responses import FileResponse
import shutil
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
EXCEL_PATH = DATA_DIR / "TagsCNN_area_seca.xlsx"
print(EXCEL_PATH)

async def importar_excel_service(archivo: UploadFile):
    if not archivo.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser un Excel .xlsx o .xls"
        )

    columnas_requeridas = [
        "Identificador",
        "Nombre_TAG",
        "Descripcion",
        "TAG_OPC",
        "Area",
        "Subarea",
        "Sistema",
        "Unidad_de_Ingenieria",
        "Criticidad"
    ]

    try:
        df = pd.read_excel(archivo.file)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="No se pudo leer el archivo Excel"
        )

    faltantes = [
        columna
        for columna in columnas_requeridas
        if columna not in df.columns
    ]

    if faltantes:
        raise HTTPException(
            status_code=400,
            detail={
                "mensaje": "El Excel no tiene la estructura esperada",
                "columnas_faltantes": faltantes
            }
        )

    if df.empty:
        raise HTTPException(
            status_code=400,
            detail="El Excel está vacío"
        )

    if df["Identificador"].dropna().empty:
        raise HTTPException(
            status_code=400,
            detail="El Excel no contiene identificadores válidos"
        )

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    archivo.file.seek(0)

    with open(EXCEL_PATH, "wb") as buffer:
        shutil.copyfileobj(archivo.file, buffer)

    try:
        from app.modules.pipeline import data_loader

        data_loader._df_instrumentos_mapeados = None
        data_loader._df_matriz_a = None
        data_loader._ids_booleanos = None

    except Exception as e:
        print(f"No se pudieron limpiar los cachés: {e}")

    return {
        "mensaje": "Excel validado e importado correctamente",
        "archivo_original": archivo.filename,
        "archivo_guardado": "TagsCNN_area_seca.xlsx",
        "filas": len(df),
        "columnas": list(df.columns)
    }

async def exportar_excel_service():
    if not EXCEL_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="No existe el archivo Excel para exportar"
        )

    return FileResponse(
        path=EXCEL_PATH,
        filename="TagsCNN_area_seca.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )