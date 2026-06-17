from app.db.database import SessionLocal, Base, engine
from app.modules.auth.auth_model import Usuario
from app.modules.auth.auth_service import hashear_password
from app.core.config import settings


USUARIOS_INICIALES = [
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


def crear_usuarios_iniciales():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        for usuario_data in USUARIOS_INICIALES:
            usuario_existente = (
                db.query(Usuario)
                .filter(Usuario.username == usuario_data["username"])
                .first()
            )

            if usuario_existente:
                print(f"El usuario '{usuario_data['username']}' ya existe")
                continue

            nuevo_usuario = Usuario(
                username=usuario_data["username"],
                nombre=usuario_data["nombre"],
                password_hash=hashear_password(usuario_data["password"]),
                rol=usuario_data["rol"],
                activo=True
            )

            db.add(nuevo_usuario)

            print(f"Usuario '{usuario_data['username']}' creado correctamente")

        db.commit()

    finally:
        db.close()


if __name__ == "__main__":
    crear_usuarios_iniciales()