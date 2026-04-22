from pydantic import BaseModel

class InstrumentoI(BaseModel):
    id: int
    nombre: str
    tipo: str
    valor: float