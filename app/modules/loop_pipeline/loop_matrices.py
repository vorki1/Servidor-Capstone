from ..pipeline.pipeline_service import actualizar_tabla_ultimas_alertas
from ..pipeline import pipeline_state

from app.modules.alertas.alerta_service import obtener_dashboard_alertas
from app.infrastructure.aws.aws_publisher import enviar_datos_alertas_por_tamano
from app.db.database import SessionLocal

from datetime import datetime
import asyncio

from app.core.logger import crear_logger


logger = crear_logger("Loop")

ESPERA_ACTUALIZAR_ALERTAS = 600

async def loop_pipeline():

    while True:

        try:
            inicio = datetime.now()

            logger.info(
                "===== Inicio ciclo pipeline ====="
            )

            if pipeline_state.MATRIZ_B_EN_PROCESO:

                logger.info(
                    "Matriz B en proceso. Se omite actualización de alertas."
                )

            else:

                await actualizar_tabla_ultimas_alertas()

                db = SessionLocal()

                try:

                    datos_alertas = obtener_dashboard_alertas(
                        db
                    )

                    enviar_datos_alertas_por_tamano(
                        datos_alertas
                    )

                finally:

                    db.close()

            fin = datetime.now()

            duracion = (
                fin - inicio
            ).total_seconds()

            logger.info(
                f"===== Ciclo pipeline finalizado en {duracion:.2f} segundos ====="
            )

        except Exception as e:

            logger.error(
                f"Error pipeline: {e}"
            )

        logger.info(
            f"Esperando {ESPERA_ACTUALIZAR_ALERTAS} segundos antes del próximo ciclo"
        )

        await asyncio.sleep(
            ESPERA_ACTUALIZAR_ALERTAS
        )