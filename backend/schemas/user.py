from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    platforms: Optional[Dict[str, Dict[str, Any]]] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr]
    password: Optional[str]
    platforms: Optional[Dict[str, Dict[str, Any]]]

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    created_at: Optional[datetime] = None
    platforms: Optional[Dict[str, Any]]

    model_config = {
        "from_attributes": True
    }

class GitLabUpdateRole(BaseModel):
    group_id: Optional[int]
    repo_access: Optional[List[int]]
    role: str


class GitLabRemoveAccess(BaseModel):
    group_id: Optional[int]
    repo_access: Optional[List[int]]


class UpdateUserRequest(BaseModel):
    email: Optional[str]
    password: Optional[str]
    platforms: Optional[dict]
