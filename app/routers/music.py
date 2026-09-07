from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import List
from app.schemas import (
    MusicGenerateRequest, 
    MusicTaskResponse, 
    LyricsGenerateRequest, 
    LyricsGenerateResponse
)
from app.service import ai_service

router = APIRouter(prefix="/api/v1/music", tags=["Music Generation"])

@router.post("/lyrics", response_model=LyricsGenerateResponse)
async def generate_lyrics(req: LyricsGenerateRequest):
    return await ai_service.generate_lyrics(req.topic, req.genre)

@router.post("/generate", response_model=MusicTaskResponse)
async def generate_music(req: MusicGenerateRequest, background_tasks: BackgroundTasks):
    task_id = ai_service.create_task(
        prompt=req.prompt,
        lyrics=req.lyrics,
        title=req.title or "Untitled Track"
    )

    background_tasks.add_task(ai_service.process_music_generation, task_id)

    task_data = ai_service.get_task(task_id)
    return task_data

@router.get("/tasks/{task_id}", response_model=MusicTaskResponse)
async def get_task_status(task_id: str):
    task = ai_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/history", response_model=List[MusicTaskResponse])
async def get_music_history():
    return ai_service.get_all_tasks()
