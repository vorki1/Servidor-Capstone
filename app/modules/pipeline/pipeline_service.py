from ..pipeline.matriz_b import construccion_matriz_b
from ..pipeline.matriz_c import matriz_c_builder, obtener_metricas_matriz_c, actualizar_datos_matriz_c
from ..pipeline.storage import (
    leer_metricas_matriz_b,
    leer_datos_matriz_c,
)
from ..alertas.criterios_alertas import tabla_alertas
from ..alertas.alertas_builder import procesar_y_obtener_alertas_activas

from app.core.logger import crear_logger

logger = crear_logger("Pipeline")


async def inicializar_archivos_pipeline():
    logger.info("Verificando archivos base del pipeline")

    metricas_matriz_b = leer_metricas_matriz_b()

    if metricas_matriz_b.empty:
        logger.warning("No existe Matriz B. Construyendo Matriz B inicial")

        info_b = await construccion_matriz_b()

        logger.info(f"Resultado Matriz B inicial: {info_b}")

        logger.info("Construyendo Matriz C inicial después de Matriz B")

        info_c = await matriz_c_builder()

        logger.info(f"Resultado Matriz C inicial: {info_c}")

        return

    datos_matriz_c = leer_datos_matriz_c()

    if datos_matriz_c.empty:
        logger.warning("Existe Matriz B, pero no existe Matriz C. Construyendo Matriz C inicial")

        info_c = await matriz_c_builder()

        logger.info(f"Resultado Matriz C inicial: {info_c}")

        return

    logger.info("Archivos base del pipeline encontrados correctamente")
async def matriz_b():
    info_b = await construccion_matriz_b()
    info_c = await matriz_c_builder()

    return {
        "matriz_b": info_b,
        "matriz_c": info_c
    }


async def actualizar_tabla_ultimas_alertas():
    await actualizar_datos_matriz_c()

    metricas_matriz_b = leer_metricas_matriz_b()

    if metricas_matriz_b.empty:
        logger.warning("No se actualizan alertas: métricas B vacías")
        return []

    metricas_matriz_c = await obtener_metricas_matriz_c()

    if metricas_matriz_c.empty:
        logger.warning("No se actualizan alertas: métricas C vacías")
        return []

    df_tabla_alertas = tabla_alertas(
        metricas_matriz_b,
        metricas_matriz_c
    )

    if df_tabla_alertas.empty:
        logger.info("No se detectaron alertas")
        return []

    df_tabla_alertas = procesar_y_obtener_alertas_activas(
        df_tabla_alertas
    )

    if df_tabla_alertas.empty:
        return []

    return df_tabla_alertas.to_dict(orient="records")