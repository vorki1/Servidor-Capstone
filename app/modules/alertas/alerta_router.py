from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.modules.alertas import alerta_service as service
from app.modules.alertas.alerta_schema import AlertaResponse


router = APIRouter(
    prefix="/alertas",
    tags=["Alertas"]
)


@router.get("/")
def obtener_alertas(solo_activas: bool = True,page: int = 1,limit: int = 100,db: Session = Depends(get_db)):
    return service.listar_alertas(db=db,solo_activas=solo_activas,page=page,limit=limit)