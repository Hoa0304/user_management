from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import os

from db import SessionLocal
from models.user import User
from schemas.user import UserCreate, UserOut, MattermostConfig, GitLabConfig
from utils.security import hash_password
from services import gitlab_service, mattermost_service

router = APIRouter()

@router.post("/users", response_model=UserOut)
def create_user(user_data: UserCreate):
    db: Session = SessionLocal()
    try:
        if db.query(User).filter(User.username == user_data.username).first():
            raise HTTPException(status_code=400, detail="User already exists")

        hashed_pw = hash_password(user_data.password)

        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_pw,
            created_at=datetime.utcnow(),
            platforms={}
        )

        platforms = user_data.platforms or {}

        # --- Handle GitLab ---
        if "gitlab" in platforms:
            gitlab_config: GitLabConfig = platforms["gitlab"]
            gitlab_config_dict = gitlab_config.dict()

            gitlab_user_id = gitlab_service.find_gitlab_user_by_email(user_data.email)
            if not gitlab_user_id:
                raise HTTPException(status_code=400, detail="GitLab user not found")

            gitlab_config_dict["user_id"] = gitlab_user_id
            user.platforms["gitlab"] = gitlab_service.add_account(gitlab_config_dict)

        # --- Handle Mattermost ---
        if "mattermost" in platforms:
            mm_config: MattermostConfig = platforms["mattermost"]
            mm_config_dict = mm_config.dict()

            # Load from .env
            mm_config_dict["server_url"] = os.getenv("MATTERMOST_SERVER_URL")
            mm_config_dict["admin_token"] = os.getenv("MATTERMOST_ADMIN_TOKEN")

            # Optional override from server_name
            if mm_config.server_name:
                mm_config_dict["server_url"] = f"https://{mm_config.server_name}"

            mm_user = mattermost_service.create_mattermost_user(
                username=user_data.username,
                email=user_data.email,
                password=user_data.password,
                config=mm_config_dict
            )

            if not isinstance(mm_user, dict) or "id" not in mm_user:
                raise HTTPException(status_code=500, detail=f"Invalid Mattermost response: {mm_user}")

            mm_config_dict["user_id"] = mm_user["id"]
            user.platforms["mattermost"] = mm_config_dict

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.get("/all_users", response_model=list[UserOut])
def get_all_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return users
    finally:
        db.close()
        