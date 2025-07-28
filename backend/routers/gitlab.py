from utils.roles import map_role_to_access_level
from fastapi import APIRouter, HTTPException
from schemas.user import GitLabRemoveAccess, GitLabUpdateRole, UpdateUserRequest, UserCreate, UserOut
from models.user import User
from db import SessionLocal
from services import gitlab_service
from utils.security import hash_password
from datetime import datetime

router = APIRouter(
    tags=["GitLab Management"]
)

@router.post("/users/add", response_model=UserOut)
def add_user(user_data: UserCreate):
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
                    user.platforms["gitlab"] = gitlab_service.add_account(gitlab_config)
                else:
                    raise HTTPException(status_code=400, detail="GitLab user not found")

        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()

@router.put("/users/{user_id}/role")
def update_gitlab_role(user_id: int, body: GitLabUpdateRole):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if "gitlab" not in user.platforms:
        raise HTTPException(status_code=400, detail="GitLab info not found")

    gitlab_id = user.platforms["gitlab"]["user_id"]
    access_level = map_role_to_access_level(body.role)
    gitlab_service.update_user_role(gitlab_id, body.group_id, body.repo_access or [], access_level)

    # Update local DB
    user.platforms["gitlab"]["role"] = body.role
    db.commit()
    return {"detail": "Role updated"}


@router.post("/users/{user_id}/remove")
def remove_gitlab_access(user_id: int, body: GitLabRemoveAccess):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if "gitlab" not in user.platforms:
        raise HTTPException(status_code=400, detail="GitLab info not found")

    gitlab_id = user.platforms["gitlab"]["user_id"]
    gitlab_service.remove_user_access(gitlab_id, body.group_id, body.repo_access or [])

    return {"detail": "Access removed"}


@router.put("/users/{user_id}")
def update_user(user_id: int, body: UpdateUserRequest):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if body.email:
        user.email = body.email
    if body.password:
        user.set_password(body.password)
    if body.platforms:
        user.platforms = body.platforms

    db.commit()
    return {"detail": "User updated"}


@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if "gitlab" in user.platforms:
        gitlab_info = user.platforms["gitlab"]
        gid = gitlab_info.get("group_id")
        uid = gitlab_info.get("user_id")  
        repos = gitlab_info.get("repo_access", [])
        
        if uid is not None: 
            gitlab_service.remove_user_access(uid, gid, repos)

    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}

@router.post("/users/create", response_model=UserOut)
def create_gitlab_user_and_local(user_data: UserCreate):
    db = SessionLocal()
    try:
        if db.query(User).filter(User.username == user_data.username).first():
            raise HTTPException(status_code=400, detail="User already exists")

        hashed_pw = hash_password(user_data.password)

        # Create new user on GitLab
        gitlab_user = gitlab_service.create_gitlab_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password
        )
        gitlab_user_id = gitlab_user["id"]

        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_pw,
            created_at=datetime.utcnow(),
            platforms={
                "gitlab": {
                    "user_id": gitlab_user_id,
                    "role": "developer",
                    "group_id": None,
                    "repo_access": []
                }
            }
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()
        
@router.get("/users", response_model=list[UserOut])
def get_all_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return users
    finally:
        db.close()
