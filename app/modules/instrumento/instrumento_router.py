from fastapi import APIRouter
from .instrumento_service import (historico_instrumento,
                                  areas_unicas,
                                  subareas_de_area,
                                  instrumentos_por_subarea, 
                                  datos_historicos_por_id,
                                  informacion_instrumento)

router = APIRouter(
    prefix="/instrumento",
    tags=["instrumento"]
)

@router.get("/areas")#Endpoint de todas las areas
async def todas_las_areas():
    return await areas_unicas()
@router.get("/subareas")#Endpoint de todas las subareas de un area
async def todas_las_subareas_de_area(area:int):
    return await subareas_de_area(area)
@router.get("/instrumentos")#Endpoint de todos los instrumentos de una subarea
async def obtener_instrumentos_de_subarea(subarea:str):
    return await instrumentos_por_subarea(subarea)
@router.get("/info-instrumento")
async def info_instrumento(id:int):
    return await informacion_instrumento(id)
@router.get("/histogram")#Endpoint del historial de tiempo de un instrumento
async def datos_historicos_por_instrumento(id:int,minutos:int):
    return await datos_historicos_por_id(id,minutos)