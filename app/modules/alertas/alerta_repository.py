from sqlalchemy.orm import Session

from app.modules.alertas.alerta_model import AlertaInstrumento


def obtener_activa_por_identificador_y_tipo(
    db: Session,
    identificador: int,
    tipo_alerta: str
):
    return (
        db.query(AlertaInstrumento)
        .filter(
            AlertaInstrumento.identificador == identificador,
            AlertaInstrumento.tipo_alerta == tipo_alerta,
            AlertaInstrumento.activa == True
        )
        .first()
    )


def obtener_activas(db: Session):
    return (
        db.query(AlertaInstrumento)
        .filter(AlertaInstrumento.activa == True)
        .order_by(AlertaInstrumento.fecha_ultima_actualizacion.desc())
        .all()
    )


def obtener_activas_por_tipos(
    db: Session,
    tipos_alerta: list[str]
):
    return (
        db.query(AlertaInstrumento)
        .filter(AlertaInstrumento.activa == True)
        .filter(AlertaInstrumento.tipo_alerta.in_(tipos_alerta))
        .all()
    )


def obtener_historicas(db: Session):
    return (
        db.query(AlertaInstrumento)
        .filter(AlertaInstrumento.activa == False)
        .order_by(AlertaInstrumento.fecha_ultima_actualizacion.desc())
        .all()
    )


def obtener_todas(db: Session):
    return (
        db.query(AlertaInstrumento)
        .order_by(AlertaInstrumento.fecha_ultima_actualizacion.desc())
        .all()
    )


def obtener_por_id(
    db: Session,
    alerta_id: int
):
    return (
        db.query(AlertaInstrumento)
        .filter(AlertaInstrumento.id == alerta_id)
        .first()
    )


def obtener_alertas(
    db: Session,
    solo_activas: bool = True,
    skip: int = 0,
    limit: int = 100
):
    query = db.query(AlertaInstrumento)

    if solo_activas:
        query = query.filter(
            AlertaInstrumento.activa == True
        )

    total = query.count()

    alertas = (
        query
        .order_by(
            AlertaInstrumento.fecha_ultima_actualizacion.desc()
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

    return total, alertas