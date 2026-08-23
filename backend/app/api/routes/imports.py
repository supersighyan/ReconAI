from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.imports.import_service import preview_import

router = APIRouter(prefix="/imports", tags=["imports"])


@router.post("/preview")
async def imports_preview(file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict[str, object]:
    content = await file.read()
    if not content: raise HTTPException(status_code=400, detail="CSV file is empty")
    return preview_import(db, content, file.filename or "upload.csv")
