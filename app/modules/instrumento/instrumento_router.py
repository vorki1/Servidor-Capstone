from fastapi import APIRouter
from .instrumento_service import historico_instrumento, procesamiento_matriz_b, quality_code, matriz_b

router = APIRouter(
    prefix="/instrumento",
    tags=["instrumento"]
)

@router.get("/datos")
def obtener_instrumentos():
    instrumentos = historico_instrumento()
    return instrumentos

@router.get("/procesamiento-matriz-b")
def procesamiento_df_matriz_b():
    procesamiento_matriz_b()
    csv_data = "Holaa"
    return {"mensaje": "CSV obtenido correctamente", "csv_data": csv_data}

@router.get("/quality-code")
def obtener_quality_code():
    quality_code_json = quality_code()
    return quality_code_json

@router.get("/matriz-b")
def obtener_matriz_b():
    return matriz_b()