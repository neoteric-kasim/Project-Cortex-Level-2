from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

from app.routes import files  # import after env is loaded

app = FastAPI(title="Project Cortex API")

app.include_router(files.router, prefix="/api/v1/files")