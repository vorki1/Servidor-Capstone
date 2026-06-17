from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from app.db.init_db import create_tables
from app.db.database import SessionLocal

from app.modules.auth.auth_seed import crear_usuarios_iniciales

from .modules.instrumento.instrumento_router import router as instrumento_router
from .modules.pipeline.pipeline_router import router as pipeline_router
from .modules.alertas.alerta_router import router as alerta_router
from .modules.auth.auth_router import router as auth_router
from app.modules.pipeline.pipeline_service import inicializar_archivos_pipeline
from .modules.loop_pipeline.loop_matrices import loop_pipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()

    db = SessionLocal()

    try:
        crear_usuarios_iniciales(db)
    finally:
        db.close()
    await inicializar_archivos_pipeline()
    asyncio.create_task(loop_pipeline())

    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(instrumento_router)
app.include_router(pipeline_router)
app.include_router(alerta_router)