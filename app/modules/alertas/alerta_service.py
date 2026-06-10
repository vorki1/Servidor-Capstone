from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.modules.alertas.alerta_model import AlertaInstrumento
from app.modules.alertas import alerta_repository as repo
import math

TIPOS_ALERTA = {
    "Alerta_Cambio_Brusco": "CAMBIO_BRUSCO",
    "Alerta_Oscilacion": "OSCILACION",
    "Alerta_Senal_Congelada": "SENAL_CONGELADA",
    "Alerta_Todos_Cero": "TODOS_CERO",
    "Alerta_Media_Congelada": "MEDIA_CONGELADA",
    "Alerta_Senal_Recuperada": "SENAL_RECUPERADA",
}


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

def cerrar_alertas_ausentes_del_ciclo(db: Session, df_alertas):
    now = datetime.now(timezone.utc)

    ids_ciclo = set(
        df_alertas["Identificador"]
        .dropna()
        .astype(int)
        .tolist()
    )

    tipos_ciclo = list(TIPOS_ALERTA.values())

    alertas_activas = (
        db.query(AlertaInstrumento)
        .filter(AlertaInstrumento.activa == True)
        .filter(AlertaInstrumento.tipo_alerta.in_(tipos_ciclo))
        .all()
    )

    for alerta in alertas_activas:
        if alerta.identificador not in ids_ciclo:
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
        alerta_activa.nivel_alerta = nivel_alerta
        alerta_activa.nombre_tag = nombre_tag
        alerta_activa.descripcion = descripcion
        alerta_activa.unidad_de_ingenieria = unidad_de_ingenieria
        alerta_activa.area = area
        alerta_activa.subarea = subarea
        alerta_activa.sistema = sistema
        alerta_activa.fecha_ultima_actualizacion = now
        alerta_activa.ciclos += 1

        db.commit()
        db.refresh(alerta_activa)

        return alerta_activa

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
        ciclos=1,
        activa=True
    )

    db.add(nueva_alerta)
    db.commit()
    db.refresh(nueva_alerta)

    return nueva_alerta