from fastapi import APIRouter
from .instrumento_service import (historico_instrumento,
                                  quality_code, matriz_b, 
                                  areas_unicas,
                                  subareas_de_area,
                                  instrumentos_por_subarea, 
                                  datos_historicos_por_id,
                                  matriz_datos_c,
                                  diferencia_metricas,
                                  actualizar_datos_matriz_c)

router = APIRouter(
    prefix="/instrumento",
    tags=["instrumento"]
)

@router.get("/datos")
def obtener_instrumentos():
    instrumentos = historico_instrumento()
    return instrumentos

@router.get("/quality-code")
def obtener_quality_code():
    quality_code_json = quality_code()
    return quality_code_json

@router.get("/matriz-b")
async def obtener_matriz_b():
    return await matriz_b()

@router.get("/areas")#Endpoint de todas las areas
async def todas_las_areas():
    return await areas_unicas()

@router.get("/subareas")#Endpoint de todas las subareas de un area
async def todas_las_subareas_de_area(area:int):
    return await subareas_de_area(area)

@router.get("/instrumentos")#Endpoint de todos los instrumentos de una subarea
async def obtener_instrumentos_de_subarea(subarea:str):
    return await instrumentos_por_subarea(subarea)

@router.get("/histogram")#Endpoint del historial de tiempo de un instrumento
async def datos_historicos_por_instrumento(id:int,minutos:int):
    return await datos_historicos_por_id(id,minutos)

@router.get("/matriz-c")
async def construccion_matriz_c():
    data = await matriz_datos_c()
    return data.to_dict(orient="records")
@router.get("/matriz-c-periodica")
async def actualizar_matriz_c():
    return await actualizar_datos_matriz_c()
@router.get("/diferencia-metricas-matrices")
async def diferencia_metricas_matrices():
    return await diferencia_metricas()