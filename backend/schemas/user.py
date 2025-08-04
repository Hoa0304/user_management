from datetime import datetime

from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Union, Optional, Dict, List, Annotated

class GitLabConfig(BaseModel):
    platform: Literal["gitlab"]
    group_id: Optional[int]
    repo_access: Optional[List[int]]
    role: str

class MattermostConfig(BaseModel):
    platform: Literal["mattermost"]
    server_name: str
    team: str
    role: str
    default_channels: List[str]

class NextCloudConfig(BaseModel):
    platform: Literal["nextcloud"]
    group_id: str
    storage_limit: Optional[float] = None
    shared_folder_id: str
    permission: str

PlatformConfig = Annotated[
    Union[GitLabConfig, MattermostConfig, NextCloudConfig],
    Field(discriminator="platform")
]

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
    email: str

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

class MattermostUpdateConfig(BaseModel):
    role: Optional[str]

class NextCloudUpdateConfig(BaseModel):
    group_id: Optional[str]
    shared_folder_id: Optional[str]
    storage_limit: Optional[int]
    permission: Optional[str]

class UserUpdate(BaseModel):
    email: Optional[str]
    password: Optional[str]
    username: Optional[str]
    platforms: Optional[Dict[str, Union[dict, MattermostUpdateConfig, NextCloudUpdateConfig]]]
