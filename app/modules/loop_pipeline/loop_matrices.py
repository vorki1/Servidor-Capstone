from ..pipeline.pipeline_service import tabla_ultimas_alertas
import asyncio 
from app.core.logger import crear_logger

logger = crear_logger("Loop")

async def loop_pipeline():
    while True:
        try:
            print("===== Inicio ciclo pipeline =====")
            
            print("===== Fin ciclo pipeline =====")

        except Exception as e:
            logger.error(f"Error pipeline: {e}")
        await asyncio.sleep(5)