from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi import Query
from typing import Optional, List
from services.mattermost_service import *

router = APIRouter(tags=["Mattermost Integration"])

class UserCreateRequest(BaseModel):
    username: str
    email: str
    password: str
    config: Optional[dict] = {}

class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

class TeamActionRequest(BaseModel):
    team_name: str
    role: Optional[str] = None

@router.post("/users")
def create_user(payload: UserCreateRequest):
    try:
        return create_mattermost_user(
            username=payload.username,
            email=payload.email,
            password=payload.password,
            config=payload.config
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/users/{user_id}")
def update_user(user_id: str, payload: UserUpdateRequest):
    try:
        return update_mattermost_user(user_id, payload.dict(exclude_none=True))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/{user_id}")

def delete_user(user_id: str, permanent: bool = Query(False)):
    try:
        return delete_mattermost_user(user_id, permanent)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/{user_id}/teams")
def add_user_to_team_api(user_id: str, payload: TeamActionRequest):
    return add_user_to_team(user_id, payload.team_name)

@router.put("/users/{user_id}/teams")
def update_user_team_role_api(user_id: str, payload: TeamActionRequest):
    return update_user_team_role(user_id, payload.team_name, payload.role or "team_user")

@router.delete("/users/{user_id}/teams")
def remove_user_from_team_api(user_id: str, payload: TeamActionRequest):
    return remove_user_from_team(user_id, payload.team_name)
