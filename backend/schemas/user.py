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

PlatformConfig = Annotated[
    Union[GitLabConfig, MattermostConfig],
    Field(discriminator="platform")
]

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    platforms: Optional[Dict[str, PlatformConfig]] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr]
    password: Optional[str]
    platforms: Optional[Dict[str, PlatformConfig]]

class UpdateUserRequest(BaseModel):
    email: Optional[str]
    password: Optional[str]
    platforms: Optional[Dict[str, PlatformConfig]]

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    created_at: Optional[datetime] = None
    platforms: Optional[Dict[str, PlatformConfig]]

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
