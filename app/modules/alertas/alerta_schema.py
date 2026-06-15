from datetime import datetime
from pydantic import BaseModel


class AlertaBase(BaseModel):
    identificador: int
    tipo_alerta: str
    nivel_alerta: str
    nombre_tag: str | None = None
    descripcion: str | None = None
    unidad_de_ingenieria: str | None = None
    area: str | None = None
    subarea: str | None = None
    sistema: str | None = None


class AlertaCreate(AlertaBase):
    pass


class AlertaUpdate(BaseModel):
    nivel_alerta: str | None = None
    nombre_tag: str | None = None
    descripcion: str | None = None
    unidad_de_ingenieria: str | None = None
    area: str | None = None
    subarea: str | None = None
    sistema: str | None = None
    fecha_ultima_actualizacion: datetime | None = None
    fecha_fin: datetime | None = None
    ciclos: int | None = None
    activa: bool | None = None


class AlertaResponse(AlertaBase):
    id: int
    fecha_inicio: datetime
    fecha_ultima_actualizacion: datetime
    fecha_fin: datetime | None = None
    ciclos: int
    activa: bool

    class Config:
        from_attributes = True