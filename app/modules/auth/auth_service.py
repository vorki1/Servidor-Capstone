from datetime import datetime, timedelta

from jose import jwt
from pwdlib import PasswordHash

from app.core.config import settings
from .auth_repository import obtener_usuario_por_username


password_hash = PasswordHash.recommended()


def hashear_password(password: str) -> str:
    return password_hash.hash(password)


def verificar_password(password_plano: str, password_hash_guardado: str) -> bool:
    return password_hash.verify(password_plano, password_hash_guardado)


def autenticar_usuario(db, username: str, password: str):
    usuario = obtener_usuario_por_username(db, username)

    if not usuario:
        return None

    if not usuario.activo:
        return None

    if not verificar_password(password, usuario.password_hash):
        return None

    return usuario


def crear_access_token(data: dict):
    datos_token = data.copy()

    expiracion = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    datos_token.update({"exp": expiracion})

    return jwt.encode(
        datos_token,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )