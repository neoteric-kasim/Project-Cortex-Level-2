from fastapi import FastAPI
from dotenv import load_dotenv
from app.services.rag import load_index
from app.routes import files
from app.routes.agent import router as agent_router
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

load_dotenv()

app = FastAPI(title="Project Cortex API")

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Load RAG index
@app.on_event("startup")
async def startup_event():
    import asyncio
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, load_index)

# ===============================
# 📦 STATIC PATH SETUP
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Serve static assets (JS/CSS)
app.mount(
    "/assets",
    StaticFiles(directory=os.path.join(STATIC_DIR, "assets")),
    name="assets"
)

# ===============================
# 🔌 API ROUTES (MUST COME FIRST)
# ===============================
app.include_router(files.router, prefix="/api/v1/files")
app.include_router(agent_router, prefix="/api/v1/agent")

# ===============================
# 🌐 FRONTEND ROUTES (LAST)
# ===============================

# Root → React app
@app.get("/")
def serve_frontend():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

# Catch-all → React routing
@app.get("/{full_path:path}")
def serve_react_app(full_path: str):
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))