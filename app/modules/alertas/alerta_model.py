# app/modules/alertas/alerta_model.py

from datetime import datetime, timezone
from sqlalchemy import Integer, String, Boolean, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class AlertaInstrumento(Base):
    __tablename__ = "alertas_instrumentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)

    identificador: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    
    tipo_alerta: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    nivel_alerta: Mapped[str] = mapped_column(String(50), nullable=False)

    nombre_tag: Mapped[str] = mapped_column(String(255), nullable=True)

    descripcion: Mapped[str] = mapped_column(String(500), nullable=True)

    unidad_de_ingenieria: Mapped[str] = mapped_column(String(100), nullable=True)

    area: Mapped[str] = mapped_column(String(100),nullable=True)

    subarea: Mapped[str] = mapped_column(String(100),nullable=True)

    sistema: Mapped[str] = mapped_column(String(100),nullable=True)

    fecha_inicio: Mapped[datetime] = mapped_column(DateTime,default=lambda: datetime.now(timezone.utc),nullable=False)

    fecha_ultima_actualizacion: Mapped[datetime] = mapped_column(DateTime,default=lambda: datetime.now(timezone.utc),nullable=False)

    fecha_fin: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    ciclos: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "identificador",
            "tipo_alerta",
            "activa",
            name="uq_alerta_activa_por_tipo"
        ),
    )