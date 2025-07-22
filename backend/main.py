# main.py
from fastapi import FastAPI
from routers import users
from db import Base, engine
from dotenv import load_dotenv
load_dotenv()

from models import user

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(users.router, prefix="/api")

# run: uvicorn main:app --reload