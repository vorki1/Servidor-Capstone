from fastapi import APIRouter
from .instrumento_service import obtener_datos, all_instrumentos, obtener_csv

router = APIRouter(
    prefix="/instrumento",
    tags=["instrumento"]
)

@router.get("/")
def obtener_instrumento():
    instrumento = obtener_datos()
    return {"mensaje": "Instrumento creado correctamente", "instrumento": instrumento}

@router.get("/datos")
def obtener_instrumentos():
    instrumentos = all_instrumentos()
    return {"mensaje": "Datos obtenidos correctamente", "instrumentos": instrumentos}

@router.get("/csv")
def obtener_csv_def():
    csv_data = obtener_csv()
    #return {"mensaje": "CSV obtenido correctamente", "csv_data": csv_data}
    return {"mensaje": "CSV obtenido correctamente"}