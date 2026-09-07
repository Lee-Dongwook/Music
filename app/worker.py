import os
import time
from celery import Celery
from app.database import SessionLocal
from app.models import MusicTaskModel
from app.schemas import TaskStatus
from app.services.audio_engine import get_audio_engine

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "music_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)
audio_engine = None

@celery_app.task(name="generate_music_task")
def process_music_generation_task(task_id: str):
    global audio_engine
    if audio_engine is None:
        audio_engine = get_audio_engine()

    db = SessionLocal()
    try:
        task = db.query(MusicTaskModel).filter(MusicTaskModel.id == task_id).first()
        if not task:
            return
        
        task.status = TaskStatus.PROCESSING
        db.commit()

        storage_dir = "storage"
        os.makedirs(storage_dir, exist_ok=True)
        filename = f"{task.id}.wav"
        file_path = os.path.join(storage_dir, filename)

        audio_engine.generate(prompt=task.prompt, output_path=file_path)
        task.status = TaskStatus.COMPLETED
        task.audio_url = f"http://localhost:8000/static/{filename}"
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
