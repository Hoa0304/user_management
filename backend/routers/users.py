import logging
from services.user_service import create_user_with_platforms, delete_user_and_cleanup, update_user_with_platforms
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from db import SessionLocal
from models.user import User
from schemas.user import UserCreate, UserOut, UserUpdate

router = APIRouter()

@router.post("/users", response_model=UserOut)
def create_user(user_data: UserCreate):
    db: Session = SessionLocal()
    try:
        return create_user_with_platforms(db, user_data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        logging.error(f"User creation failed: {e}")
        db.rollback()
        raise

    finally:
        db.close()

@router.get("/all_users", response_model=list[UserOut])
def get_all_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return [
            UserOut(
                id=user.id,
                username=user.username,
                email=user.email,
                created_at=user.created_at,
                platforms=user.platforms if user.platforms else []
            )
            for user in users
        ]
    finally:
        db.close()

@router.patch("/users/{username}", response_model=UserOut)
def update_user(username: str, user_update: UserUpdate):
    db: Session = SessionLocal()
    try:
        return update_user_with_platforms(db, username, user_update)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.delete("/users/{username}", response_model=dict)
def delete_user(username: str):
    db: Session = SessionLocal()
    try:
        delete_user_and_cleanup(db, username)
        return {"message": f"User '{username}' deleted successfully."}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
