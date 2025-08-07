from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Literal, Union, Optional, Dict, List, Annotated

class GitLabConfig(BaseModel):
    platform: Literal["gitlab"]
    group_id: str
    repo_access: Optional[List[int]]
    role: str

class MattermostConfig(BaseModel):
    platform: Literal["mattermost"]
    server_name: str
    team: str
    role: str
    # default_channels: List[str]

class DriveConfig(BaseModel):
    platform: Literal["drive"]
    shared_folder_id: str
    role: Optional[str] = "writer"

class NextCloudConfig(BaseModel):
    platform: Literal["nextcloud"]
    group_id: str
    storage_limit: Optional[float] = None
    shared_folder_id: str
    permission: str

PlatformConfig = Annotated[
    Union[GitLabConfig, MattermostConfig, NextCloudConfig, DriveConfig],
    Field(discriminator="platform")
]

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    platforms: Optional[List[PlatformConfig]] = None
    
class DriveOutConfig(BaseModel):
    platform: Literal["drive"] = "drive"
    shared_folder_id: str
    user_email: str
    role: str
    permission_id: Optional[str] = None

class GitLabOutConfig(BaseModel):
    platform: Literal["gitlab"] = "gitlab"
    user_id: int
    group_id: str
    role: Optional[str] = None
    repo_access: Optional[List[int]] = []

class MattermostOutConfig(BaseModel):
    platform: Literal["mattermost"] = "mattermost"
    user_id: str
    team: Optional[str] = None
    role: Optional[str] = None
    server_name: str

class NextCloudOutConfig(BaseModel):
    platform: Literal["nextcloud"] = "nextcloud"
    group_id: str
    shared_folder_id: Optional[str] = None
    permission: Optional[str] = None
    storage_limit: Optional[float] = None


class UpdateUserRequest(BaseModel):
    email: Optional[str]
    password: Optional[str]
    platforms: Optional[Dict[str, PlatformConfig]]

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    created_at: Optional[datetime] = None
    platforms: List[Union[GitLabOutConfig, MattermostOutConfig, NextCloudOutConfig, DriveOutConfig]] = []

    model_config = {
        "from_attributes": True
    }

class GitLabRemoveAccess(BaseModel):
    group_id: Optional[int]
    repo_access: Optional[List[int]]

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

class BasePlatformUpdate(BaseModel):
    platform: str

class GitLabUpdateRole(BasePlatformUpdate):
    platform: Literal["gitlab"]
    group_id: Optional[str]
    repo_access: Optional[List[int]]
    role: str

class MattermostUpdateConfig(BasePlatformUpdate):
    platform: Literal["mattermost"]
    role: Optional[str]
    team: Optional[str]
    server_name: Optional[str]
    # default_channels: Optional[List[str]]

class NextCloudUpdateConfig(BasePlatformUpdate):
    platform: Literal["nextcloud"]
    group_id: Optional[str]
    shared_folder_id: Optional[str]
    storage_limit: Optional[int]
    permission: Optional[str]

class DriveUpdateConfig(BasePlatformUpdate):
    platform: Literal["drive"]
    shared_folder_id: str
    role: Optional[str]
    user_email: str
    permission_id: str

PlatformUnion = Annotated[
    Union[
        GitLabUpdateRole,
        MattermostUpdateConfig,
        NextCloudUpdateConfig,
        DriveUpdateConfig
    ],
    Field(discriminator="platform")
]

platform_model_map = {
    "gitlab": GitLabUpdateRole,
    "mattermost": MattermostUpdateConfig,
    "nextcloud": NextCloudUpdateConfig,
    "drive": DriveUpdateConfig
}

class UserUpdate(BaseModel):
    email: Optional[str]
    password: Optional[str] = None 
    username: Optional[str]
    platforms: Optional[List[PlatformUnion]] = Field(default_factory=list)

    @field_validator("password", mode="before")
    def empty_string_to_none(cls, v):
        return v or None