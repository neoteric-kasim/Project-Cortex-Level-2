from pydantic import BaseModel
from typing import List

class UploadResponse(BaseModel):
    status: str
    message: str
    path: str

class FileListResponse(BaseModel):
    status: str
    files: List[str]