from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services import nextcloud_service
from schemas.user import (
    FolderAccessRequest,
    GroupCreateRequest,
    GroupMemberRequest,
    UnshareByUserRequest,
    UpdatePermissionRequest,
    UpdateUserRequest,
    UserCreateRequest,
    UserDeleteRequest
)

router = APIRouter(tags=["NextCloud"])

# ----- USER ENDPOINTS -----
@router.post("/users/create")
def create_user(data: UserCreateRequest):
    try:
        return nextcloud_service.create_user(data.userid, data.password, data.email)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/users/update")
def update_user(data: UpdateUserRequest):
    try:
        return nextcloud_service.update_user(data.userid, data.key, data.value)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/users/delete")
def delete_user(data: UserDeleteRequest):
    try:
        return nextcloud_service.delete_user(data.userid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ----- SYSTEM GROUP ENDPOINTS -----
@router.post("/groups/create")
def create_group(data: GroupCreateRequest):
    try:
        return nextcloud_service.create_group(data.groupid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/groups/add_member")
def add_member(data: GroupMemberRequest):
    try:
        return nextcloud_service.add_member_to_group(data.userid, data.groupid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/groups/remove_member")
def remove_member(data: GroupMemberRequest):
    try:
        return nextcloud_service.remove_member_from_group(data.userid, data.groupid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ----- FOLDER SHARING ENDPOINTS -----
@router.post("/folders/share")
def share_folder(data: FolderAccessRequest):
    try:
        return nextcloud_service.share_folder(data.folder_path, data.userid, data.permission)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/folders/update_permission")
def update_folder_permission(data: UpdatePermissionRequest):
    try:
        return nextcloud_service.update_folder_permission_all_user(data.share_id, data.new_permission)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/folders/unshare/{share_id}")
def unshare_folder(share_id: int):
    try:
        return nextcloud_service.unshare_folder_by_share_id(share_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/folders/unshare_by_user")
def unshare_folder_by_user(data: UnshareByUserRequest):
    try:
        return nextcloud_service.unshare_folder_by_user(data.folder_path, data.userid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
