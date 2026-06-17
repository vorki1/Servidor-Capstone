from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from .auth_dependencies import obtener_usuario_actual
from .auth_schema import LoginRequest, TokenResponse, UsuarioResponse
from .auth_service import autenticar_usuario, crear_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/login", response_model=TokenResponse)
def login(
    datos_login: LoginRequest,
    db: Session = Depends(get_db)
):
    usuario = autenticar_usuario(
        db=db,
        username=datos_login.username,
        password=datos_login.password
    )

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos"
        )

    access_token = crear_access_token(
        data={
            "sub": usuario.username,
            "rol": usuario.rol
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": usuario
    }

@router.get("/me", response_model=UsuarioResponse)
def obtener_mi_usuario(
    usuario_actual=Depends(obtener_usuario_actual)
):
    return usuario_actual