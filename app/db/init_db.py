from app.db.database import Base, engine

# importar todos los modelos
from app.modules.alertas.alerta_model import AlertaInstrumento

def create_tables():
    Base.metadata.create_all(bind=engine)