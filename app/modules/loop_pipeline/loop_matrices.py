from ..pipeline.pipeline_service import actualizar_tabla_ultimas_alertas
from ..pipeline import pipeline_state

from datetime import datetime
import asyncio

from app.core.logger import crear_logger


logger = crear_logger("Loop")


ESPERA_ACTUALIZAR_ALERTAS = 6000


async def loop_pipeline():
    while True:
        try:
            inicio = datetime.now()

            logger.info("===== Inicio ciclo pipeline =====")

            if pipeline_state.MATRIZ_B_EN_PROCESO:
                logger.info(
                    "Matriz B en proceso. Se omite actualización de alertas."
                )
            else:
                await actualizar_tabla_ultimas_alertas()

            fin = datetime.now()
            duracion = (fin - inicio).total_seconds()

            logger.info(
                f"===== Ciclo pipeline finalizado en {duracion:.2f} segundos ====="
            )

        except Exception as e:
            logger.error(f"Error pipeline: {e}")

        logger.info(
            f"Esperando {ESPERA_ACTUALIZAR_ALERTAS} segundos antes del próximo ciclo"
        )

        await asyncio.sleep(ESPERA_ACTUALIZAR_ALERTAS)