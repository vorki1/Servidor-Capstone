from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.modules.alertas import alerta_service as service
from app.modules.auth.auth_dependencies import obtener_usuario_actual


router = APIRouter(
    prefix="/alertas",
    tags=["Alertas"],
    dependencies=[Depends(obtener_usuario_actual)]
)


@router.get("/")
def obtener_alertas(solo_activas: bool = True,page: int = 1,limit: int = 100,db: Session = Depends(get_db)):
    return service.listar_alertas(db=db,solo_activas=solo_activas,page=page,limit=limit)

@router.get("/tabla-alertas-instrumentos")
def tabla_alertas_instrumentos(db: Session = Depends(get_db)):
    return service.listar_alertas_activas(db)

@router.get("/estadisticas")
def obtener_estadisticas(
    db: Session = Depends(get_db)
):
    return service.obtener_estadisticas_dashboard(db)