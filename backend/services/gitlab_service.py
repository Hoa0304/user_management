import requests
import os

GITLAB_API_BASE = "https://gitlab.com/api/v4"
HEADERS = {
    "Private-Token": GITLAB_TOKEN
}

def create_account(config):
    username = config.get("username")
    email = config.get("email")
    group_id = config.get("group_id")
    role = config.get("role", "Developer")
    repo_access = config.get("repo_access", [])

    # Lookup user ID via email or username
    user_id = find_gitlab_user_by_email(email) or find_gitlab_user_by_username(username)
    if not user_id:
        raise Exception("GitLab user not found")

    # Add to group
    if group_id:
        add_user_to_group(user_id, group_id, access_level_from_role(role))

    # Add to repos/projects
    for project_id in repo_access:
        add_user_to_project(user_id, project_id, access_level_from_role(role))

    return {
        "user_id": user_id,
        "group_id": group_id,
        "role": role,
        "repo_access": repo_access
    }

# === Helpers ===
def add_user_to_group(user_id: int, group_id: int, access_level: int):
    url = f"{GITLAB_API_BASE}/groups/{group_id}/members"
    payload = {
        "user_id": user_id,
        "access_level": access_level
    }
    res = requests.post(url, headers=HEADERS, data=payload)
    if res.status_code == 409:
        print(f"[Info] User {user_id} already in group {group_id}")
    elif res.status_code != 201:
        raise Exception(f"[Error] Failed to add user to group: {res.status_code} - {res.text}")

def add_user_to_project(user_id: int, project_id: int, access_level: int):
    url = f"{GITLAB_API_BASE}/projects/{project_id}/members"
    payload = {
        "user_id": user_id,
        "access_level": access_level
    }
    res = requests.post(url, headers=HEADERS, data=payload)
    if res.status_code == 409:
        print(f"[Info] User {user_id} already in project {project_id}")
    elif res.status_code != 201:
        raise Exception(f"[Error] Failed to add user to project: {res.status_code} - {res.text}")

def access_level_from_role(role: str) -> int:
    mapping = {
        "Guest": 10,
        "Reporter": 20,
        "Developer": 30,
        "Maintainer": 40,
        "Owner": 50
    }
    return mapping.get(role, 30)

def find_gitlab_user_by_email(email: str):
    if not email:
        return None
    url = f"{GITLAB_API_BASE}/users?search={email}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200 and res.json():
        return res.json()[0]["id"]
    return None

def find_gitlab_user_by_username(username: str):
    if not username:
        return None
    url = f"{GITLAB_API_BASE}/users?username={username}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200 and res.json():
        return res.json()[0]["id"]
    return None
