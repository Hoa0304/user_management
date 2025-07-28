from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.google_drive import grant_folder_access, revoke_folder_access, update_permission, list_permissions

router = APIRouter(
    tags=["Google Drive Integration"]
)

class AccessRequest(BaseModel):
    folder_id: str
    user_email: str
    role: str

@router.post("/grant-access")
def api_grant_access(
    folder_id: str,
    user_email: str,
    role: str  # "reader", "writer", "commenter"
):
    try:
        result = grant_folder_access(folder_id, user_email, role)
        return {"permission_id": result['id']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/revoke-access")
def api_revoke_access(folder_id: str, permission_id: str):
    try:
        revoke_folder_access(folder_id, permission_id)
        return {"status": "revoked"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update-access")
def api_update_access(folder_id: str, permission_id: str, new_role: str):
    try:
        update_permission(folder_id, permission_id, new_role)
        return {"status": "updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/permissions")
def api_list_permissions(folder_id: str):
    try:
        return list_permissions(folder_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
