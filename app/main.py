from fastapi import FastAPI
from .modules.instrumento.instrumento_router import router as instrumento_router
from .modules.pipeline.pipeline_router import router as pipeline_router
import asyncio
from .modules.loop_pipeline.loop_matrices import loop_pipeline

app = FastAPI()
app.include_router(instrumento_router)
app.include_router(pipeline_router)
'''
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(loop_pipeline())
'''
@app.get("/")
def root():
    return {"mensaje": "API funcionando correctamente"}