from fastapi import APIRouter, Depends
from .instrumento_service import (historico_instrumento,
                                  areas_unicas,
                                  subareas_de_area,
                                  datos_historicos_por_id,
                                  informacion_instrumento,
                                  sistemas_por_subarea,
                                  instrumentos_por_sistema
                                  )
from app.modules.auth.auth_dependencies import obtener_usuario_actual

router = APIRouter(
    prefix="/instrumento",
    tags=["instrumento"],
    dependencies=[Depends(obtener_usuario_actual)]
)

@router.get("/datos")
def obtener_historico_instrumento():
    return historico_instrumento()
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
@router.get("/{id}")
async def info_instrumento(id:int):
    return await informacion_instrumento(id)
@router.get("/{id}/historico")
async def datos_historicos_por_instrumento(id: int, minutos: int):
    return await datos_historicos_por_id(id, minutos)
