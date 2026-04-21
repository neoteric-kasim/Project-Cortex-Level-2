from fastapi import FastAPI
from dotenv import load_dotenv
from app.services.rag import load_index
from app.routes import agent
from app.routes import files
from app.routes.agent import router as agent_router

load_dotenv()



app = FastAPI(title="Project Cortex API")

@app.on_event("startup")
async def startup_event():
    import asyncio
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, load_index)

@app.get("/")
def health_check():
    return {"status": "alive"}

app.include_router(files.router, prefix="/api/v1/files")
app.include_router(agent_router, prefix="/api/v1/agent")