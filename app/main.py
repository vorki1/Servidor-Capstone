from fastapi import FastAPI
from .modules.instrumento.instrumento_router import router as instrumento_router

app = FastAPI()
app.include_router(instrumento_router)

@app.get("/")
def root():
    return {"mensaje": "API funcionando correctamente"}