from fastapi import FastAPI
from .modules.instrumento.instrumento_router import router as instrumento_router
from .modules.pipeline.pipeline_router import router as pipeline_router
from .modules.loop_pipeline.loop_matrices import loop_pipeline
from fastapi.middleware.cors import CORSMiddleware
from app.db.init_db import create_tables
from contextlib import asynccontextmanager
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):

    create_tables()

    #asyncio.create_task(loop_pipeline())

    yield

app = FastAPI(lifespan=lifespan)
app.include_router(instrumento_router)
app.include_router(pipeline_router)
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
