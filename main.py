import uuid
import asyncio
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Music AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tasks = {}

class GenerateRequest(BaseModel):
    prompt: str
    lyrics: str | None = None

async def mock_generate_audio(task_id: str):
    tasks[task_id]["status"] = "processing"
    await asyncio.sleep(5)
    tasks[task_id]["status"] = "completed"
    tasks[task_id]["audio_url"] = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"

@app.post("/api/generate")
async def generate_music(req: GenerateRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "status": "pending",
        "prompt": req.prompt,
        "audio_url": None
    }
    background_tasks.add_task(mock_generate_audio, task_id)
    return {"task_id": task_id, "status": "pending"}

@app.get("/api/status/{task_id}")
async def get_status(task_id: str):
    task = tasks.get(task_id)
    if not task:
        return {"error": "Task not found"}, 404
    return task
