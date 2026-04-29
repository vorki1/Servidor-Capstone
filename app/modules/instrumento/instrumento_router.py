from fastapi import APIRouter
from .instrumento_service import historico_instrumento, obtener_csv

router = APIRouter(
    prefix="/instrumento",
    tags=["instrumento"]
)

@router.get("/datos")
def obtener_instrumentos():
    instrumentos = historico_instrumento()
    return {"mensaje": "Datos obtenidos correctamente", "instrumentos": instrumentos}

@router.get("/csv")
def obtener_csv_def():
    obtener_csv()
    csv_data = "Holaa"
    return {"mensaje": "CSV obtenido correctamente", "csv_data": csv_data}