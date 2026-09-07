from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime

class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class LyricsGenerateRequest(BaseModel):
    topic: str = Field(..., description = "곡 주제 또는 무드 (예: 야간 드라이브, 신나는 팝)")
    genre: Optional[str] = Field("K-Pop", description="음악 장르")

class LyricsGenerateResponse(BaseModel):
    prompt: str
    lyrics: str
    style_tags: List[str]

class MusicGenerateRequest(BaseModel):
    prompt: str = Field(..., description="스타일 및 분위기 설명")
    lyrics: Optional[str] = Field(None, description="[Verse], [Chorus] 형태의 가사")
    instrumental: bool = Field(False, description="보컬 없는 반주곡 여부")
    title: Optional[str] = Field("Untitled Track", description="트랙 제목")

class MusicTaskResponse(BaseModel):
    task_id: str
    status: TaskStatus
    title: str
    prompt: str
    lyrics: Optional[str] = None
    audio_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    created_at: datetime
    error_message: Optional[str] = None
