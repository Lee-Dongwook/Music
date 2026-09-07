import os
import time
from celery import Celery
from app.database import SessionLocal
from app.models import MusicTaskModel
from app.schemas import TaskStatus

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "music_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.config.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Seoul",
    enable_utc=True
)

@celery_app.task(name="generate_music_task")
def process_music_generation_task(task_id: str):
    db = SessionLocal()
    try:
        task = db.query(MusicTaskModel).filter(MusicTaskModel.id == task_id).first()
        if not task:
            return
        
        task.status = TaskStatus.PROCESSING
        db.commit()

        time.sleep(10)

        task.status = TaskStatus.COMPLETED
        task.audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
        task.cover_image_url = "https://picsum.photos/400/400"
        db.commit()
        
    except Exception as e:
        db.rollback()
        task = db.query(MusicTaskModel).filter(MusicTaskModel.id == task_id).first()
        if task:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            db.commit()
    finally:
        db.close()
