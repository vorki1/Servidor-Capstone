from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime

from app.db.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True, index=True, nullable=False)
    nombre = Column(String, nullable=False)

    password_hash = Column(String, nullable=False)

    rol = Column(String, nullable=False, default="usuario")

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(DateTime, default=datetime.utcnow)