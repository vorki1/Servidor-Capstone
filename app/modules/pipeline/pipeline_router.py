from fastapi import APIRouter, Depends
from threading import Thread
import asyncio

from . import pipeline_state
from .pipeline_service import (
    matriz_b,
    actualizar_tabla_ultimas_alertas,
)
from .storage import obtener_fecha_actualizacion_metricas_matriz_b

router = APIRouter(
    prefix="/matriz",
    tags=["matriz"],
)


def ejecutar_matriz_b_thread():
    try:
        asyncio.run(matriz_b())
    finally:
        pipeline_state.MATRIZ_B_EN_PROCESO = False

@router.post("/matriz-b")
async def ejecutar_matriz_b():
    if pipeline_state.MATRIZ_B_EN_PROCESO:
        return {
            "estado": "en_proceso",
            "mensaje": "La matriz B ya se está construyendo"
        }

    pipeline_state.MATRIZ_B_EN_PROCESO = True

    thread = Thread(
        target=ejecutar_matriz_b_thread,
        daemon=True
    )

    thread.start()

    return {
        "estado": "iniciada",
        "mensaje": "Matriz B iniciada en segundo plano"
    }

@router.get("/matriz-b/estado")
async def estado_matriz_b():
    return {
        "matriz_b_en_proceso": pipeline_state.MATRIZ_B_EN_PROCESO
    }

@router.get("/metricas-matriz-base/ultima-actualizacion")
async def obtener_fecha_actualizacion_matriz_base():
    return obtener_fecha_actualizacion_metricas_matriz_b()

@router.get("/actualizar-tabla-alertas-activas")#Endpoint que hay que eliminar (Esta en el loop de pipeline)
async def alertas_instrumentos():
    return await actualizar_tabla_ultimas_alertas()