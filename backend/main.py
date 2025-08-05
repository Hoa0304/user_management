from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import google_drive, gitlab, nextcloud, mattermost, users
from db import Base, engine
from dotenv import load_dotenv

load_dotenv()
from models import user

app = FastAPI()
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={"Access-Control-Allow-Origin": "*"},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
        headers={"Access-Control-Allow-Origin": "*"},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers={"Access-Control-Allow-Origin": "*"},
    )

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
app.include_router(nextcloud.router, prefix="/nextcloud")
app.include_router(mattermost.router, prefix="/mattermost") 
app.include_router(users.router, prefix="/api")

# run: uvicorn main:app --reload