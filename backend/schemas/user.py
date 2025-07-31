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

# Schemas for Users and Groups
class UserCreateRequest(BaseModel):
    userid: str
    password: str
    email: str = ""
    display_name: str = ""

class UpdateUserRequest(BaseModel):
    userid: str
    key: str
    value: str

class UserDeleteRequest(BaseModel):
    userid: str

class GroupMemberRequest(BaseModel):
    groupid: str
    userid: str

class GroupCreateRequest(BaseModel):
    groupid: str

# Schemas for Folder Sharing
class FolderAccessRequest(BaseModel):
    folder_path: str
    userid: str
    permission: int  # 1=view, 2= update, 4=create,8= delete, 15=all (view/edit/delete) 

class UpdatePermissionRequest(BaseModel):
    share_id: int
    new_permission: int

class UnshareByUserRequest(BaseModel):
    folder_path: str
    userid: str
    