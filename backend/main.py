# main.py
from fastapi import FastAPI
from routers import users, google_drive
from db import Base, engine
from dotenv import load_dotenv

load_dotenv()
from models import user

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(users.router, prefix="/api")
app.include_router(google_drive.router, prefix="/google-drive") 

# run: uvicorn main:app --reload