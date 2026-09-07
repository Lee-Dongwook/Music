import asyncio
import uuid
from datetime import datetime
from typing import Dict
from app.schemas import TaskStatus, MusicTaskResponse, LyricsGenerateResponse

class AIService:
    def __init__(self):
        self.tasks: Dict[str, dict] = {}
    
    async def generate_lyrics(self, topic:str, genre: str) -> LyricsGenerateResponse:
        """LLM 엔진 : 가사 및 프롬포트 시퀀스 생성"""
        await asyncio.sleep(1)

        sample_lyrics = (
            f"[Verse 1]\n{topic} 속을 달려가는 밤\n선명해지는 너의 기억\n\n"
            f"[Chorus]\n{genre} 리듬에 몸을 맡겨봐\n멈추지 않는 이 순간\n\n"
            f"[Outro]\n고요해지는 밤하늘 속으로"
        )
        tags = [genre.lower(), "upbeat", "synthwave", "melodic"]

        return LyricsGenerateResponse(
            prompt=f"{genre} style track about {topic}",
            lyrics=sample_lyrics,
            style_tags=tags
        )

    def create_task(self, prompt: str, lyrics: str | None, title: str) -> str:
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            "task_id": task_id,
            "status": TaskStatus.PENDING,
            "title": title,
            "prompt": prompt,
            "lyrics": lyrics,
            "audio_url": None,
            "cover_image_url": None,
            "created_at": datetime.now(),
            "error_message": None
        }
        return  task_id

    async def process_music_generation(self, task_id: str):
        task = self.tasks.get(task_id)
        if not task:
            return
        
        try:
            task["status"] = TaskStatus.PROCESSING

            await asyncio.sleep(10)

            task["status"] = TaskStatus.COMPLETED
            task["audio_url"] = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
            task["cover_image_url"] = "https://picsum.photos/400/400"
        except Exception as e:
            task["status"] = TaskStatus.FAILED
            task["error_message"] = str(e)

    def get_task(self, task_id: str) -> dict | None:
        return self.tasks.get(task_id)

    def get_all_tasks(self):
        return list(self.tasks.values())

ai_service = AIService()
