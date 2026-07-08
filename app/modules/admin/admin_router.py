from fastapi import APIRouter, UploadFile, File
from .admin_service import importar_excel_service, exportar_excel_service

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


@router.post("/importar-excel")
async def importar_excel(archivo: UploadFile = File(...)):
    return await importar_excel_service(archivo)


@router.get("/exportar-excel")
async def exportar_excel():
    return await exportar_excel_service()