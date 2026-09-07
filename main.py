import os
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import music

app = FastAPI(title="Music AI Backend", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("storage", exist_ok=True)
app.mount("/static", StaticFiles(directory="storage"), name="static")

app.include_router(music.router)

@app.get("/")
def read_root():
    return {"message": "Music AI generation API is running"}
