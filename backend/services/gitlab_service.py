from typing import List, Optional
import requests

from config import GITLAB_API_BASE, HEADERS_GITLAB
from utils.roles import map_role_to_access_level

def add_account(config):
    """
    Add an existing GitLab user to a group and/or projects.

    Args:
        config (dict): Configuration dictionary containing:
            - username (str): GitLab username.
            - email (str): GitLab user email.
            - group_id (int): GitLab group ID to add the user to.
            - role (str): Role to assign (e.g., "Developer").
            - repo_access (list): List of project IDs to grant access to.

    Returns:
        dict: Summary of user setup and access information.
    """
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
        "platform": "gitlab",
        "user_id": user_id,
        "group_id": group_id,
        "role": role,
        "repo_access": repo_access
    }

def add_user_to_group(user_id: int, group_id: int, access_level: int):
    """
    Add a user to a GitLab group.

    Args:
        user_id (int): ID of the GitLab user.
        group_id (int): ID of the GitLab group.
        access_level (int): Access level to assign (e.g., 30 for Developer).
    """
    url = f"{GITLAB_API_BASE}/groups/{group_id}/members"
    payload = {"user_id": user_id, "access_level": access_level}
    res = requests.post(url, headers=HEADERS_GITLAB, data=payload)

    if res.status_code == 409:
        print(f"[Info] User {user_id} already in group {group_id}")
    elif res.status_code != 201:
        raise Exception(f"[Error] Failed to add user to group: {res.status_code} - {res.text}")

def add_user_to_project(user_id: int, project_id: int, access_level: int):
    """
    Add a user to a GitLab project.

    Args:
        user_id (int): ID of the GitLab user.
        project_id (int): ID of the GitLab project.
        access_level (int): Access level to assign.
    """
    url = f"{GITLAB_API_BASE}/projects/{project_id}/members"
    payload = {"user_id": user_id, "access_level": access_level}
    res = requests.post(url, headers=HEADERS_GITLAB, data=payload)

    if res.status_code == 409:
        print(f"[Info] User {user_id} already in project {project_id}")
    elif res.status_code != 201:
        raise Exception(f"[Error] Failed to add user to project: {res.status_code} - {res.text}")

def find_gitlab_user_by_email(email: str):
    """
    Search for a GitLab user by email.

    Args:
        email (str): Email address.

    Returns:
        int or None: User ID if found, otherwise None.
    """
    if not email:
        return None
    url = f"{GITLAB_API_BASE}/users?search={email}"
    res = requests.get(url, headers=HEADERS_GITLAB)
    if res.status_code == 200 and res.json():
        return res.json()[0]["id"]
    return None

def find_gitlab_user_by_username(username: str):
    """
    Search for a GitLab user by username.

    Args:
        username (str): GitLab username.

    Returns:
        int or None: User ID if found, otherwise None.
    """
    if not username:
        return None
    url = f"{GITLAB_API_BASE}/users?username={username}"
    res = requests.get(url, headers=HEADERS_GITLAB)
    if res.status_code == 200 and res.json():
        return res.json()[0]["id"]
    return None

def update_user_role(user_id: int, group_id: Optional[int], repo_ids: List[int], access_level: int):
    """
    Update the user's role in a group and/or list of projects.

    Args:
        user_id (int): ID of the GitLab user.
        group_id (int or None): GitLab group ID.
        repo_ids (List[int]): List of project IDs.
        access_level (int): New access level.
    """
    if group_id:
        url = f"{GITLAB_API_BASE}/groups/{group_id}/members/{user_id}"
        res = requests.put(url, headers=HEADERS_GITLAB, data={"access_level": access_level})
        if res.status_code not in [200, 201]:
            raise Exception(f"Update group failed: {res.text}")
    
    for repo_id in repo_ids:
        url = f"{GITLAB_API_BASE}/projects/{repo_id}/members/{user_id}"
        res = requests.put(url, headers=HEADERS_GITLAB, data={"access_level": access_level})
        if res.status_code not in [200, 201]:
            print(f"[Error] Response: {res.status_code} - {res.text}")
            raise Exception(f"Update project failed: {res.text}")

def remove_user_access(user_id: int, group_id: Optional[str], repo_ids: List[int]):
    """
    Remove a user's access from a group and list of projects.

    Args:
        user_id (int): ID of the user to remove.
        group_id (str or None): GitLab group ID.
        repo_ids (List[int]): List of project IDs.
    """
    if group_id:
        group_url = f"{GITLAB_API_BASE}/groups/{group_id}/members/{user_id}"
        response = requests.delete(group_url, headers=HEADERS_GITLAB)
        print(f"Remove from group {group_id}: {response.status_code}")

    for repo_id in repo_ids:
        repo_url = f"{GITLAB_API_BASE}/projects/{repo_id}/members/{user_id}"
        response = requests.delete(repo_url, headers=HEADERS_GITLAB)
        print(f"Remove from repo {repo_id}: {response.status_code}")

def create_gitlab_user(username, email, password):
    """
    Create a new GitLab user.

    Args:
        username (str): Username for the new user.
        email (str): Email address.
        password (str): Password.

    Returns:
        dict: User details if created successfully.

    Raises:
        Exception: If user creation fails.
    """
    url = f"{GITLAB_API_BASE}/users"
    payload = {
        "username": username,
        "email": email,
        "name": username,
        "password": password,
        "skip_confirmation": True
    }

    response = requests.post(url, json=payload, headers=HEADERS_GITLAB)
    
    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Failed to create GitLab user: {response.status_code} {response.text}")

def delete_gitlab_user(user_id: int):
    """
    Delete a GitLab user by ID.

    Args:
        user_id (int): ID of the user to delete.

    Returns:
        dict: Deletion status.

    Raises:
        Exception: If deletion fails or user not found.
    """
    url = f"{GITLAB_API_BASE}/users/{user_id}"
    response = requests.delete(url, headers=HEADERS_GITLAB)

    if response.status_code == 204:
        return {"status": "deleted"}
    elif response.status_code == 404:
        raise Exception("User not found.")
    else:
        raise Exception(f"Failed to delete GitLab user: {response.status_code} {response.text}")

def get_gitlab_user_id(username: str) -> Optional[int]:
    """
    Get a GitLab user ID by username.

    Args:
        username (str): GitLab username.

    Returns:
        int or None: User ID if found, else None.
    """
    url = f"{GITLAB_API_BASE}/users?username={username}"
    
    response = requests.get(url, headers=HEADERS_GITLAB)
    if response.status_code == 200:
        users = response.json()
        if users:
            return users[0]["id"]
    return None
