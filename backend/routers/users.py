from fastapi import APIRouter, HTTPException
from schemas.user import UserCreate, UserOut
from models.user import User
from db import SessionLocal
from services import gitlab_service
from utils.security import hash_password
from datetime import datetime

router = APIRouter()

@router.post("/users", response_model=UserOut)
def create_user(user_data: UserCreate):
    db = SessionLocal()
    try:
        if db.query(User).filter(User.username == user_data.username).first():
            raise HTTPException(status_code=400, detail="User already exists")

        hashed_pw = hash_password(user_data.password)

        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_pw,
            created_at=datetime.utcnow()
        )

        if user_data.platforms:
            user.platforms = {}
            if "gitlab" in user_data.platforms:
                gitlab_config = user_data.platforms["gitlab"]
                gitlab_user_id = gitlab_service.find_gitlab_user_by_email(user_data.email)

                if gitlab_user_id:
                    gitlab_config["user_id"] = gitlab_user_id
                    user.platforms["gitlab"] = gitlab_service.create_account(gitlab_config)
                else:
                    raise HTTPException(status_code=400, detail="GitLab user not found")

        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()
