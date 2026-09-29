import requests
import json
import time
from app.core.logger import crear_logger
from app.core.config import settings
from datetime import datetime, date

logger = crear_logger("AWS Publisher")

URL_API_AWS = settings.URL_API_AWS

LIMITE_KB = 50
LIMITE_BYTES = LIMITE_KB * 1024


def serializar_json(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    return str(obj)


def calcular_tamano_json_bytes(contenido: dict) -> int:
    payload_json = json.dumps(
        contenido,
        ensure_ascii=False,
        default=serializar_json
    )

    return len(payload_json.encode("utf-8"))


def calcular_tamano_json_kb(contenido: dict) -> float:
    return calcular_tamano_json_bytes(contenido) / 1024


def enviar_json_a_aws(nombre_archivo: str, contenido: dict, limite_kb: int = LIMITE_KB):
    payload = {
        "nombre": nombre_archivo,
        **contenido
    }

    tamano_kb = calcular_tamano_json_kb(payload)

    logger.info(
        f"JSON {nombre_archivo} pesa {tamano_kb:.2f} KB"
    )

    if tamano_kb > limite_kb:
        logger.error(
            f"{nombre_archivo} supera el límite de prueba de {limite_kb} KB. "
            f"Tamaño actual: {tamano_kb:.2f} KB"
        )
        return False

    try:
        payload_json = json.dumps(
            payload,
            ensure_ascii=False,
            default=serializar_json
        )

        inicio = time.time()

        response = requests.post(
            URL_API_AWS,
            data=payload_json.encode("utf-8"),
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        duracion = time.time() - inicio

        logger.info("========== REPORTE AWS ==========")
        logger.info(f"Archivo enviado: {nombre_archivo}")
        logger.info(f"Tamaño enviado: {tamano_kb:.2f} KB")
        logger.info(f"Status HTTP: {response.status_code}")
        logger.info(f"OK HTTP: {response.ok}")
        logger.info(f"URL final: {response.url}")
        logger.info(f"Tiempo respuesta: {duracion:.2f} segundos")
        logger.info(f"Headers respuesta: {dict(response.headers)}")
        logger.info(f"Texto respuesta: {response.text}")
        logger.info("=================================")

        if not response.ok:
            logger.error(
                f"Error HTTP al enviar {nombre_archivo}. "
                f"Status: {response.status_code}. "
                f"Respuesta: {response.text}"
            )
            return False

        try:
            respuesta_json = response.json()
        except Exception:
            logger.error(
                f"AWS no devolvió JSON válido para {nombre_archivo}"
            )
            return False

        status_interno = respuesta_json.get("statusCode")

        if status_interno != 200:
            logger.error(
                f"AWS rechazó {nombre_archivo}. "
                f"Status interno: {status_interno}. "
                f"Respuesta completa: {respuesta_json}"
            )
            return False

        body_raw = respuesta_json.get("body", "{}")

        try:
            body_json = json.loads(body_raw)
        except Exception:
            body_json = {}

        archivo_guardado = body_json.get("archivo")
        ssm_status = body_json.get("ssm_status")
        ssm_command_id = body_json.get("ssm_command_id")

        logger.info(
            f"{nombre_archivo} aceptado por AWS. "
            f"Archivo destino: {archivo_guardado}. "
            f"SSM status: {ssm_status}. "
            f"Command ID: {ssm_command_id}"
        )

        logger.info(
            "Esperando 60 segundos antes del siguiente envío AWS"
        )

        time.sleep(60)

        return True

    except Exception as e:
        logger.error(
            f"Excepción al enviar {nombre_archivo} a AWS: {e}"
        )
        return False


def dividir_lista_por_tamano(
    nombre_base: str,
    clave_lista: str,
    lista: list,
    max_kb: int = LIMITE_KB
):
    partes = []
    parte_actual = []

    limite_bytes = max_kb * 1024

    for item in lista:
        prueba = parte_actual + [item]

        contenido_prueba = {
            "parte": 1,
            "total_partes": 1,
            clave_lista: prueba
        }

        payload_prueba = {
            "nombre": f"{nombre_base}_temp.json",
            **contenido_prueba
        }

        tamano = calcular_tamano_json_bytes(
            payload_prueba
        )

        if tamano > limite_bytes and parte_actual:
            partes.append(parte_actual)
            parte_actual = [item]
        else:
            parte_actual = prueba

    if parte_actual:
        partes.append(parte_actual)

    if not partes:
        partes = [[]]

    return partes


def enviar_lista_json_por_tamano(
    nombre_base: str,
    clave_lista: str,
    lista: list,
    limite_kb: int = LIMITE_KB
):
    partes = dividir_lista_por_tamano(
        nombre_base=nombre_base,
        clave_lista=clave_lista,
        lista=lista,
        max_kb=limite_kb
    )

    total_partes = len(partes)

    logger.info(
        f"{nombre_base}: límite {limite_kb} KB, "
        f"total registros {len(lista)}, total partes {total_partes}"
    )

    for index, parte in enumerate(partes, start=1):
        contenido = {
            "parte": index,
            "total_partes": total_partes,
            clave_lista: parte
        }

        nombre_archivo = f"{nombre_base}_{index}.json"

        logger.info(
            f"Enviando {nombre_archivo}: parte {index}/{total_partes}, "
            f"registros en parte: {len(parte)}"
        )

        enviado = enviar_json_a_aws(
            nombre_archivo=nombre_archivo,
            contenido=contenido
        )

        if not enviado:
            logger.error(
                f"Prueba fallida con límite {limite_kb} KB en {nombre_archivo}"
            )
            return False

    logger.info(
        f"Prueba exitosa con límite {limite_kb} KB para {nombre_base}"
    )

    return True


def enviar_datos_alertas_por_tamano(datos_alertas: dict):
    estadisticas = datos_alertas.get("estadisticas", {})
    alertas = datos_alertas.get("alertas", [])

    enviado_estadisticas = enviar_json_a_aws(
        nombre_archivo="datos_alertas_estadisticas.json",
        contenido={
            "estadisticas": estadisticas
        }
    )

    if not enviado_estadisticas:
        logger.error(
            "No se pudo enviar datos_alertas_estadisticas.json"
        )
        return False

    return enviar_lista_json_por_tamano(
        nombre_base="datos_alertas",
        clave_lista="alertas",
        lista=alertas
    )