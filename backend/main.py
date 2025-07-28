# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import google_drive, gitlab
from db import Base, engine
from dotenv import load_dotenv

load_dotenv()
from models import user

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)

app.include_router(gitlab.router, prefix="/gitlab")
app.include_router(google_drive.router, prefix="/google-drive") 

# run: uvicorn main:app --reload