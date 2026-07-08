from fastapi import APIRouter
from .instrumento_service import (historico_instrumento,
                                  areas_unicas,
                                  subareas_de_area,
                                  datos_historicos_por_id,
                                  informacion_instrumento,
                                  sistemas_por_subarea,
                                  instrumentos_por_sistema,
                                  obtener_jerarquia_planta,
                                  instrumentos_matriz_a,
                                  analisis_matriz_a
                                  )

router = APIRouter(
    prefix="/instrumento",
    tags=["instrumento"],
)

@router.get("/datos")
def obtener_historico_instrumento():
    return historico_instrumento()
@router.post("/matriz-a")
def obtener_matriz_a():
    return instrumentos_matriz_a()
@router.post("/jerarquia")
async def obtener_jerarquia():
    return await obtener_jerarquia_planta()
@router.get("/areas")#Endpoint de todas las areas
async def todas_las_areas():
    return await areas_unicas()
@router.get("/areas/{area}/subareas")#Endpoint de todas las subareas de un area
async def todas_las_subareas_de_area(area:str):
    return await subareas_de_area(area)

@router.get("/subareas/{subarea}/sistemas")
async def obtener_sistemas(subarea: str):
    return await sistemas_por_subarea(subarea)
@router.get("/sistemas/{sistema}/instrumentos")
async def obtener_instrumentos_de_sistema(sistema: str):
    return await instrumentos_por_sistema(sistema)

@router.get("/{id}/historico")
async def datos_historicos_por_instrumento(id: int, minutos: int):
    return await datos_historicos_por_id(id, minutos)

@router.get("/analisis-matriz-a")
async def obtener_analisis_matriz_a():
    return await analisis_matriz_a()

@router.get("/{id}")
async def info_instrumento(id:int):
    return await informacion_instrumento(id)