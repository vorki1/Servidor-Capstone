# app/modules/alertas/alerta_model.py

from datetime import datetime, timezone

from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class AlertaInstrumento(Base):
    __tablename__ = "alertas_instrumentos"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True
    )
    identificador: Mapped[int] = mapped_column(
        Integer,
        index=True,
        nullable=False
    )
    nombre_tag: Mapped[str] = mapped_column(
        String(255),
        nullable=True
    )
    descripcion: Mapped[str] = mapped_column(
        String(500),
        nullable=True
    )
    unidad_de_ingenieria: Mapped[str] = mapped_column(
        String(100),
        nullable=True
    )
    timestamp_alarma: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    ciclos: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )
    alerta_cambio_brusco: Mapped[str] = mapped_column(
        String(50),
        default="NORMAL",
        nullable=False
    )
    alerta_oscilacion: Mapped[str] = mapped_column(
        String(50),
        default="NORMAL",
        nullable=False
    )
    alerta_senal_congelada: Mapped[str] = mapped_column(
        String(50),
        default="NORMAL",
        nullable=False
    )