from sqlalchemy.orm import Session

from .auth_model import Usuario


def obtener_usuario_por_username(db: Session, username: str):
    return (
        db.query(Usuario)
        .filter(Usuario.username == username)
        .first()
    )
