from datetime import datetime, timezone
import math

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.modules.instrumento.instrumento_service import datos_matriz_a
from app.modules.alertas.alerta_model import AlertaInstrumento
from app.modules.alertas import alerta_repository as repo
from .alerta_constants import TIPOS_ALERTA


def listar_alertas_activas(db: Session):
    alertas = repo.obtener_activas(db)

    return [
        {
            "Identificador": alerta.identificador,
            "Nombre_TAG": alerta.nombre_tag,
            "Descripcion": alerta.descripcion,
            "Unidad_de_Ingenieria": alerta.unidad_de_ingenieria,
            "Area": alerta.area,
            "Subarea": alerta.subarea,
            "Sistema": alerta.sistema,
            "Tipo_Alerta": alerta.tipo_alerta,
            "Nivel_Alerta": alerta.nivel_alerta,
            "Fecha_Inicio_Alarma": alerta.fecha_inicio,
            "Fecha_Ultima_Actualizacion": alerta.fecha_ultima_actualizacion,
            "Fecha_Fin": alerta.fecha_fin,
            "Ciclos_Alarma": alerta.ciclos,
            "Alarma_Activa": alerta.activa,
        }
        for alerta in alertas
    ]


def listar_alertas_historicas(db: Session):
    return repo.obtener_historicas(db)


def listar_todas_las_alertas(db: Session):
    return repo.obtener_todas(db)


def listar_alertas(
    db: Session,
    solo_activas: bool = True,
    page: int = 1,
    limit: int = 100
):
    if page < 1:
        page = 1

    if limit < 1:
        limit = 100

    if limit > 500:
        limit = 500

    skip = (page - 1) * limit

    total, alertas = repo.obtener_alertas(
        db=db,
        solo_activas=solo_activas,
        skip=skip,
        limit=limit
    )

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": math.ceil(total / limit),
        "data": alertas
    }


def construir_alertas_presentes_del_ciclo(df_alertas):
    alertas_presentes = set()

    for _, fila in df_alertas.iterrows():
        identificador = int(fila["Identificador"])

        for columna_df, tipo_alerta in TIPOS_ALERTA.items():
            if columna_df not in df_alertas.columns:
                continue

            nivel_alerta = str(fila[columna_df]).strip().upper()

            if nivel_alerta != "NORMAL":
                alertas_presentes.add(
                    (identificador, tipo_alerta)
                )

    return alertas_presentes


def cerrar_alertas_ausentes_del_ciclo(db: Session, df_alertas):
    now = datetime.now(timezone.utc)

    alertas_presentes = construir_alertas_presentes_del_ciclo(
        df_alertas
    )

    tipos_ciclo = list(TIPOS_ALERTA.values())

    alertas_activas = repo.obtener_activas_por_tipos(
        db=db,
        tipos_alerta=tipos_ciclo
    )

    for alerta in alertas_activas:
        clave_alerta = (
            alerta.identificador,
            alerta.tipo_alerta
        )

        if clave_alerta not in alertas_presentes:
            alerta.activa = False
            alerta.fecha_fin = now
            alerta.fecha_ultima_actualizacion = now

    db.commit()


def procesar_alertas_dataframe(db: Session, df_alertas):
    alertas_procesadas = []

    for _, fila in df_alertas.iterrows():
        identificador = int(fila["Identificador"])

        for columna_df, tipo_alerta in TIPOS_ALERTA.items():
            if columna_df not in df_alertas.columns:
                continue

            nivel_alerta = str(fila[columna_df]).strip().upper()

            alerta = procesar_alerta_individual(
                db=db,
                identificador=identificador,
                tipo_alerta=tipo_alerta,
                nivel_alerta=nivel_alerta,
                nombre_tag=fila.get("Nombre_TAG"),
                descripcion=fila.get("Descripcion"),
                unidad_de_ingenieria=fila.get("Unidad_de_Ingenieria"),
                area=fila.get("Area"),
                subarea=fila.get("Subarea"),
                sistema=fila.get("Sistema"),
            )

            if alerta is not None:
                alertas_procesadas.append(alerta)

    cerrar_alertas_ausentes_del_ciclo(db, df_alertas)

    return alertas_procesadas


def ajustar_nivel_por_ciclos(
    tipo_alerta: str,
    nivel_alerta: str,
    ciclos: int
):
    if tipo_alerta == "SENAL_CONGELADA":
        if ciclos >= 10:
            return "CRITICO"

        return "PREVENTIVO"

    return nivel_alerta


def procesar_alerta_individual(
    db: Session,
    identificador: int,
    tipo_alerta: str,
    nivel_alerta: str,
    nombre_tag: str | None = None,
    descripcion: str | None = None,
    unidad_de_ingenieria: str | None = None,
    area: str | None = None,
    subarea: str | None = None,
    sistema: str | None = None,
):
    now = datetime.now(timezone.utc)

    alerta_activa = repo.obtener_activa_por_identificador_y_tipo(
        db=db,
        identificador=identificador,
        tipo_alerta=tipo_alerta
    )

    if nivel_alerta == "NORMAL":
        if alerta_activa:
            alerta_activa.activa = False
            alerta_activa.fecha_fin = now
            alerta_activa.fecha_ultima_actualizacion = now

            db.commit()
            db.refresh(alerta_activa)

            return alerta_activa

        return None

    if alerta_activa:
        alerta_activa.ciclos += 1

        nivel_alerta = ajustar_nivel_por_ciclos(
            tipo_alerta=tipo_alerta,
            nivel_alerta=nivel_alerta,
            ciclos=alerta_activa.ciclos
        )

        alerta_activa.nivel_alerta = nivel_alerta
        alerta_activa.nombre_tag = nombre_tag
        alerta_activa.descripcion = descripcion
        alerta_activa.unidad_de_ingenieria = unidad_de_ingenieria
        alerta_activa.area = area
        alerta_activa.subarea = subarea
        alerta_activa.sistema = sistema
        alerta_activa.fecha_ultima_actualizacion = now

        db.commit()
        db.refresh(alerta_activa)

        return alerta_activa

    ciclos_iniciales = 1

    nivel_alerta = ajustar_nivel_por_ciclos(
        tipo_alerta=tipo_alerta,
        nivel_alerta=nivel_alerta,
        ciclos=ciclos_iniciales
    )

    nueva_alerta = AlertaInstrumento(
        identificador=identificador,
        tipo_alerta=tipo_alerta,
        nivel_alerta=nivel_alerta,
        nombre_tag=nombre_tag,
        descripcion=descripcion,
        unidad_de_ingenieria=unidad_de_ingenieria,
        area=area,
        subarea=subarea,
        sistema=sistema,
        fecha_inicio=now,
        fecha_ultima_actualizacion=now,
        fecha_fin=None,
        ciclos=ciclos_iniciales,
        activa=True
    )

    db.add(nueva_alerta)
    db.commit()
    db.refresh(nueva_alerta)

    return nueva_alerta


def obtener_estadisticas_dashboard(db):

    df_instrumentos = datos_matriz_a()

    total_sensores = len(df_instrumentos)

    sensores_con_fallas = (
        db.query(
            func.count(
                func.distinct(
                    AlertaInstrumento.identificador
                )
            )
        )
        .filter(
            AlertaInstrumento.activa == True
        )
        .scalar()
    )

    porcentaje_con_fallas = round(
        (sensores_con_fallas / total_sensores) * 100,
        2
    ) if total_sensores > 0 else 0

    alertas_por_nivel = (
        db.query(
            AlertaInstrumento.nivel_alerta,
            func.count().label("cantidad")
        )
        .filter(
            AlertaInstrumento.activa == True
        )
        .group_by(
            AlertaInstrumento.nivel_alerta
        )
        .all()
    )

    preventivas = 0
    criticas = 0
    emergencias = 0

    for nivel, cantidad in alertas_por_nivel:

        nivel = nivel.upper()

        if nivel == "PREVENTIVO":
            preventivas = cantidad

        elif nivel == "CRITICO":
            criticas = cantidad

        elif nivel == "EMERGENCIA":
            emergencias = cantidad

    sistema_mas_alertas = (
        db.query(
            AlertaInstrumento.sistema,
            func.count().label("cantidad")
        )
        .filter(
            AlertaInstrumento.activa == True
        )
        .group_by(
            AlertaInstrumento.sistema
        )
        .order_by(
            func.count().desc()
        )
        .first()
    )

    return {
        "sensores": {
            "total": total_sensores,
            "con_fallas": sensores_con_fallas,
            "porcentaje_con_fallas": porcentaje_con_fallas
        },
        "cantidad_alertas": {
            "preventivas": preventivas,
            "criticas": criticas,
            "emergencias": emergencias
        },
        "sistema_mas_alertas": {
            "sistema": sistema_mas_alertas[0] if sistema_mas_alertas else None,
            "cantidad_alertas": sistema_mas_alertas[1] if sistema_mas_alertas else 0
        }
    }


def obtener_dashboard_alertas(db: Session):

    estadisticas = obtener_estadisticas_dashboard(db)
    alertas = listar_alertas_activas(db)

    return {
        "estadisticas": estadisticas,
        "alertas": alertas
    }