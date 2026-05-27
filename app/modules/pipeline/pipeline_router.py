from fastapi import APIRouter
from .pipeline_service import (matriz_b, matriz_datos_c, tabla_ultimas_alertas)

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
@router.get("/tabla-alertas-instrumentos")
async def alertas_instrumentos():
    return await tabla_ultimas_alertas()