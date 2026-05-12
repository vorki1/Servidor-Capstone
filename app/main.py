from fastapi import FastAPI
from .modules.instrumento.instrumento_router import router as instrumento_router
from .modules.pipeline.pipeline_router import router as pipeline_router

app = FastAPI()
app.include_router(instrumento_router)
app.include_router(pipeline_router)

@app.get("/")
def root():
    return {"mensaje": "API funcionando correctamente"}