from fastapi import APIRouter
from .instrumento_service import obtener_datos, all_instrumentos

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