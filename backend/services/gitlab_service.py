from typing import List, Optional
import requests
import os

from utils.roles import map_role_to_access_level
from dotenv import load_dotenv
import os

load_dotenv()

GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
if not GITLAB_TOKEN:
    raise Exception("Missing GITLAB_TOKEN in environment variables")

GITLAB_API_BASE = "https://gitlab.ikya.dev/api/v4"
HEADERS = {
    "Private-Token": GITLAB_TOKEN
}

def add_account(config):
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
        add_user_to_group(user_id, group_id, map_role_to_access_level(role))

    # Add to repos/projects
    for project_id in repo_access:
        add_user_to_project(user_id, project_id, map_role_to_access_level(role))

    return {
        "user_id": user_id,
        "group_id": group_id,
        "role": role,
        "repo_access": repo_access
    }

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

def update_user_role(user_id: int, group_id: Optional[int], repo_ids: List[int], access_level: int):
    if group_id:
        url = f"{GITLAB_API_BASE}/groups/{group_id}/members/{user_id}"
        res = requests.put(url, headers=HEADERS, data={"access_level": access_level})
        if res.status_code not in [200, 201]:
            raise Exception(f"Update group failed: {res.text}")
    
    for repo_id in repo_ids:
        url = f"{GITLAB_API_BASE}/projects/{repo_id}/members/{user_id}"
        res = requests.put(url, headers=HEADERS, data={"access_level": access_level})
        if res.status_code not in [200, 201]:
            print(f"[Error] Response: {res.status_code} - {res.text}")
            raise Exception(f"Update group failed: {res.text}")


def remove_user_access(user_id: int, group_id: Optional[int], repo_ids: List[int]):
    if group_id:
        requests.delete(f"{GITLAB_API_BASE}/groups/{group_id}/members/{user_id}", headers=HEADERS)
    
    for repo_id in repo_ids:
        requests.delete(f"{GITLAB_API_BASE}/projects/{repo_id}/members/{user_id}", headers=HEADERS)

def create_gitlab_user(username, email, password):
    url = f"{GITLAB_API_BASE}/users"
    payload = {
        "username": username,
        "email": email,
        "name": username,
        "password": password,
        "skip_confirmation": True
    }
    headers = {"Private-Token": GITLAB_TOKEN}
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Failed to create GitLab user: {response.status_code} {response.text}")
