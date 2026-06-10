from fastapi import FastAPI
from .modules.instrumento.instrumento_router import router as instrumento_router
from .modules.pipeline.pipeline_router import router as pipeline_router
from .modules.alertas.alerta_router import router as alerta_router
from .modules.loop_pipeline.loop_matrices import loop_pipeline
from fastapi.middleware.cors import CORSMiddleware
from app.db.init_db import create_tables
from contextlib import asynccontextmanager
import asyncio
import threading


def iniciar_loop_pipeline():
    asyncio.run(loop_pipeline())


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()

    thread_pipeline = threading.Thread(
        target=iniciar_loop_pipeline,
        daemon=True
    )
    thread_pipeline.start()

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(instrumento_router)
app.include_router(pipeline_router)
app.include_router(alerta_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"mensaje": "API funcionando correctamente"}