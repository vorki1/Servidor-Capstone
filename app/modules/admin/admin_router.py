from fastapi import APIRouter, UploadFile, File, Depends
from .admin_service import importar_excel_service, exportar_excel_service
from app.modules.auth.auth_dependencies import requiere_admin

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(requiere_admin)]
)


@router.post("/importar-excel")
async def importar_excel(archivo: UploadFile = File(...)):
    return await importar_excel_service(archivo)


@router.get("/exportar-excel")
async def exportar_excel():
    return await exportar_excel_service()