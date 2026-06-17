from sqlalchemy.orm import Session

from app.modules.auth.auth_model import Usuario
from app.modules.auth.auth_service import hashear_password
from app.core.config import settings

def crear_usuarios_iniciales(db: Session):
    usuarios_iniciales = [
        {
            "username": settings.ADMIN_USERNAME,
            "nombre": settings.ADMIN_NAME,
            "password": settings.ADMIN_PASSWORD,
            "rol": "admin"
        },
        {
            "username": settings.USUARIO_USERNAME,
            "nombre": settings.USUARIO_NAME,
            "password": settings.USUARIO_PASSWORD,
            "rol": "usuario"
        }
    ]

    for usuario_data in usuarios_iniciales:
        if not usuario_data["username"] or not usuario_data["password"]:
            continue

        usuario_existente = (
            db.query(Usuario)
            .filter(Usuario.username == usuario_data["username"])
            .first()
        )

        if usuario_existente:
            continue

        nuevo_usuario = Usuario(
            username=usuario_data["username"],
            nombre=usuario_data["nombre"],
            password_hash=hashear_password(usuario_data["password"]),
            rol=usuario_data["rol"],
            activo=True
        )

        db.add(nuevo_usuario)

    db.commit()