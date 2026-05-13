from ..pipeline.pipeline_service import actualizar_datos_matriz_c, diferencia_metricas
from ..criterios_de_alertas.criterios_alertas import criterios_anomalias
import asyncio 
from app.core.logger import crear_logger

logger = crear_logger("Loop")

async def loop_pipeline():
    while True:
        try:
            print("===== Inicio ciclo pipeline =====")
            # 1. Actualizar matriz C
            await actualizar_datos_matriz_c() #String de exito
            # 2. Comparar matrices
            diferencias = await diferencia_metricas() #df matriz B, matriz C y diferencia
            # 3. Detectar alertas
            criterios_de_anomalias = criterios_anomalias(diferencias)
            print("===== Fin ciclo pipeline =====")

        except Exception as e:
            logger.error(f"Error pipeline: {e}")
        await asyncio.sleep(5)