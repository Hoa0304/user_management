import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load credentials
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "service_account.json")
SCOPES = ["https://www.googleapis.com/auth/drive"]

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# Build the Drive API client
drive_service = build("drive", "v3", credentials=credentials)


def grant_folder_access(shared_folder_id: str, user_email: str, role: str):
    """
    Grant access role to a user on the shared folder.

    Args:
        shared_folder_id (str): The ID of the Google Drive folder.
        user_email (str): The email of the user to grant access to.
        role (str): The access role ("reader", "writer", "commenter").

    Returns:
        dict: The role ID created for the user.
    """
    permission = {
        "type": "user",
        "role": role,
        "emailAddress": user_email,
    }

    result = drive_service.permissions().create(
        fileId=shared_folder_id,
        body=permission,
        fields="id",
        sendNotificationEmail=False,
    ).execute()

    return {"permission_id": result["id"]}


def revoke_folder_access(shared_folder_id: str, permission_id: str):
    """
    Revoke a user's permission using their permission ID.

    Args:
        folder_id (str): The ID of the folder.
        permission_id (str): The permission ID to revoke.

    Returns:
        dict: API response.
    """
    return drive_service.permissions().delete(
        fileId=shared_folder_id, permissionId=permission_id
    ).execute()


def list_permissions(shared_folder_id: str):
    """
    List all current permissions of a folder.

    Args:
        folder_id (str): The ID of the folder.

    Returns:
        dict: A dictionary containing the list of permissions.
    """
    return drive_service.permissions().list(fileId=shared_folder_id).execute()


def update_permission(shared_folder_id: str, permission_id: str, new_role: str):
    """
    Update the role of an existing permission.

    Args:
        folder_id (str): The ID of the folder.
        permission_id (str): The ID of the permission to update.
        new_role (str): The new role ("reader", "writer", etc.).

    Returns:
        dict: API response.
    """
    return drive_service.permissions().update(
        fileId=shared_folder_id,
        permissionId=permission_id,
        body={"role": new_role}
    ).execute()
