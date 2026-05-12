from fastapi import APIRouter
from .pipeline_service import (matriz_b, matriz_datos_c, diferencia_metricas, actualizar_datos_matriz_c)

router = APIRouter(
    prefix="/matriz",
    tags=["matriz"]
)

@router.get("/matriz-b")#Endpoint que se ejecutara cada 1 mes, actualiza la matriz B
async def obtener_matriz_b():
    return await matriz_b()
@router.get("/matriz-c")
async def construccion_matriz_c():
    data = await matriz_datos_c()
    return data.to_dict(orient="records")
@router.get("/matriz-c-periodica")#Endpoint que se solicitara periodicamente cada 5 seg
async def actualizar_matriz_c():
    return await actualizar_datos_matriz_c()
@router.get("/diferencia-metricas-matrices")
async def diferencia_metricas_matrices():
    return await diferencia_metricas()