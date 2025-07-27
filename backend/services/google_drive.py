import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = "credentials/credentials.json"
SCOPES = ['https://www.googleapis.com/auth/drive']

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build('drive', 'v3', credentials=credentials)

def grant_folder_access(folder_id: str, user_email: str, role: str = "writer"):
    permission = {
        'type': 'user',
        'role': role,  # 'reader', 'writer', 'commenter', 'owner'
        'emailAddress': user_email,
    }
    return drive_service.permissions().create(
        fileId=folder_id,
        body=permission,
        fields='id',
        sendNotificationEmail=False
    ).execute()

def revoke_folder_access(folder_id: str, permission_id: str):
    return drive_service.permissions().delete(
        fileId=folder_id,
        permissionId=permission_id
    ).execute()

def list_permissions(folder_id: str):
    return drive_service.permissions().list(fileId=folder_id).execute()

def update_permission(folder_id: str, permission_id: str, new_role: str):
    return drive_service.permissions().update(
        fileId=folder_id,
        permissionId=permission_id,
        body={"role": new_role}
    ).execute()
