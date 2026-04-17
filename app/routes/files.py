from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.adls_service import ADLSService
from app.models.schemas import UploadResponse
from app.models.schemas import FileListResponse

router = APIRouter()


@router.post("/upload",response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    try:
        adls_service = ADLSService() 

        content = await file.read()

        if not content:
            raise HTTPException(status_code=400, detail="Empty file")

        file_path = adls_service.upload_file(file.filename, content)

        return {
            "status": "success",
            "message": "File uploaded successfully",
            "path": file_path
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list",response_model=FileListResponse)
def list_files():
    try:
        adls_service = ADLSService() 

        files = adls_service.list_files("Kasim/Gold")

        return {
            "status": "success",
            "files": files
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))