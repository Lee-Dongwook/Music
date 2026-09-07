from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import MusicTaskModel
from app.schemas import (
    MusicGenerateRequest, 
    MusicTaskResponse, 
    LyricsGenerateRequest, 
    LyricsGenerateResponse
)
from app.service import ai_service
from app.worker import process_music_generation_task

router = APIRouter(prefix="/api/v1/music", tags=["Music Generation"])

@router.post("/lyrics", response_model=LyricsGenerateResponse)
async def generate_lyrics(req: LyricsGenerateRequest):
    return await ai_service.generate_lyrics(req.topic, req.genre)

@router.post("/generate", response_model=MusicTaskResponse)
def generate_music(req: MusicGenerateRequest, db: Session = Depends(get_db)):
    new_task = MusicTaskModel(
        title=req.title or "Untitled Track",
        prompt=req.prompt,
        lyrics=req.lyrics
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    process_music_generation_task.delay(new_task.id)

    return new_task

@router.get("/tasks/{task_id}", response_model=MusicTaskResponse)
async def get_task_status(task_id: str, db: Session = Depends(get_db)):
    task = db.query(MusicTaskModel).filter(MusicTaskModel.id == task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/history", response_model=List[MusicTaskResponse])
async def get_music_history(db: Session = Depends(get_db)):
    return db.query(MusicTaskModel).order_by(MusicTaskModel.created_at.desc()).all()
