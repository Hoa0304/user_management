import requests

from config import ADMIN_PASSWORD, ADMIN_USERNAME, NEXTCLOUD_BASE_URL, OCS_HEADERS

# User Services
def create_user(userid: str, password: str, email: str = "", displayname: str = ""):
    url = f"{NEXTCLOUD_BASE_URL}/ocs/v1.php/cloud/users"
    payload = {
        "userid": userid,
        "password": password,
    }
    if email:
        payload["email"] = email
    if displayname:
        payload["displayname"] = displayname

    response = requests.post(url, auth=(ADMIN_USERNAME, ADMIN_PASSWORD), headers=OCS_HEADERS, data=payload)
    if response.status_code == 200:
        return {"message": "User created successfully."}
    raise Exception(response.text or "Failed to create user.")

def update_user(userid: str, key: str, value: str):
    url = f"{NEXTCLOUD_BASE_URL}/ocs/v1.php/cloud/users/{userid}"
    payload = {"key": key, "value": value}
    response = requests.put(url, auth=(ADMIN_USERNAME, ADMIN_PASSWORD), headers=OCS_HEADERS, data=payload)
    if response.status_code == 200:
        return {"message": "User updated successfully."}
    raise Exception(response.text or "Failed to update user.")

def delete_user(userid: str):
    url = f"{NEXTCLOUD_BASE_URL}/ocs/v1.php/cloud/users/{userid}"
    response = requests.delete(url, auth=(ADMIN_USERNAME, ADMIN_PASSWORD), headers=OCS_HEADERS)
    if response.status_code == 200:
        return {"message": "User deleted successfully."}
    raise Exception(response.text or "Failed to delete user.")


# Group (System group) Services
def create_group(groupid: str):
    url = f"{NEXTCLOUD_BASE_URL}/ocs/v1.php/cloud/groups"
    payload = {"groupid": groupid}
    response = requests.post(url, auth=(ADMIN_USERNAME, ADMIN_PASSWORD), headers=OCS_HEADERS, data=payload)
    if response.status_code == 200:
        return {"message": f"Group '{groupid}' created successfully."}
    raise Exception(response.text or "Failed to create group.")

def add_member_to_group(userid: str, groupid: str):
    # Endpoint: /ocs/v1.php/cloud/users/{userid}/groups
    url = f"{NEXTCLOUD_BASE_URL}/ocs/v1.php/cloud/users/{userid}/groups"
    payload = {"groupid": groupid}
    response = requests.post(url, auth=(ADMIN_USERNAME, ADMIN_PASSWORD), headers=OCS_HEADERS, data=payload)
    if response.status_code == 200:
        return {"message": f"User '{userid}' added to group '{groupid}'."}
    raise Exception(response.text or "Failed to add user to group.")

def remove_member_from_group(userid: str, groupid: str):
    # Endpoint: /ocs/v1.php/cloud/groups/{groupid}/users/{userid}
    url = f"{NEXTCLOUD_BASE_URL}/ocs/v1.php/cloud/groups/{groupid}/users/{userid}"
    response = requests.delete(url, auth=(ADMIN_USERNAME, ADMIN_PASSWORD), headers=OCS_HEADERS)
    if response.status_code == 200:
        return {"message": f"User '{userid}' removed from group '{groupid}'."}
    raise Exception(response.text or "Failed to remove user from group.")


# Folder Sharing Services
def share_folder(folder_path: str, userid: str, permission: int):
    url = f"{NEXTCLOUD_BASE_URL}/ocs/v2.php/apps/files_sharing/api/v1/shares"
    payload = {
        "path": folder_path,
        "shareType": 0,  # 0 = share with user (1 = group)
        "shareWith": userid,
        "permissions": permission
    }
    response = requests.post(url, auth=(ADMIN_USERNAME, ADMIN_PASSWORD), headers=OCS_HEADERS, data=payload)
    try:
        res_data = response.json()
    except Exception:
        res_data = {}
    if response.status_code == 200 and res_data.get("ocs", {}).get("meta", {}).get("status") == "ok":
        share_id = res_data.get("ocs", {}).get("data", {}).get("id")
        return {"message": f"Folder '{folder_path}' shared with '{userid}'.", "share_id": share_id}
    raise Exception(response.text or "Failed to share folder.")

def update_folder_permission_all_user(share_id: int, new_permission: int):
    url = f"{NEXTCLOUD_BASE_URL}/ocs/v2.php/apps/files_sharing/api/v1/shares/{share_id}"
    payload = {"permissions": new_permission}
    response = requests.put(url, auth=(ADMIN_USERNAME, ADMIN_PASSWORD), headers=OCS_HEADERS, data=payload)
    if response.status_code == 200:
        return {"message": "Folder permission updated successfully."}
    raise Exception(response.text or "Failed to update permission.")

def unshare_folder_by_share_id(share_id: int):
    url = f"{NEXTCLOUD_BASE_URL}/ocs/v2.php/apps/files_sharing/api/v1/shares/{share_id}"
    response = requests.delete(url, auth=(ADMIN_USERNAME, ADMIN_PASSWORD), headers=OCS_HEADERS)
    if response.status_code == 200:
        return {"message": "Folder unshared successfully."}
    raise Exception(response.text or "Failed to unshare folder.")

def unshare_folder_by_user(folder_path: str, userid: str):
    list_url = f"{NEXTCLOUD_BASE_URL}/ocs/v2.php/apps/files_sharing/api/v1/shares"
    response = requests.get(list_url, auth=(ADMIN_USERNAME, ADMIN_PASSWORD), headers=OCS_HEADERS)
    if response.status_code != 200:
        raise Exception("Failed to list shares.")

    shares = response.json().get("ocs", {}).get("data", [])
    for share in shares:
        if share["path"] == folder_path and share["share_with"] == userid:
            share_id = share["id"]
            return unshare_folder_by_share_id(share_id)
    raise Exception("Matching share not found.")

