import requests

from config import HEADERS_MATTERMOST, MATTERMOST_URL

def get_team_by_name(name):
    """
    Retrieve team information by name.

    Args:
        name (str): Team name.

    Returns:
        dict or None: Team information if found, otherwise None.
    """
    res = requests.get(f"{MATTERMOST_URL}/api/v4/teams/name/{name}", headers=HEADERS_MATTERMOST)
    return res.json() if res.status_code == 200 else None

def get_channel_by_name(team_id, channel_name):
    """
    Retrieve channel information by name within a team.

    Args:
        team_id (str): ID of the team.
        channel_name (str): Channel name.

    Returns:
        dict or None: Channel information if found, otherwise None.
    """
    res = requests.get(f"{MATTERMOST_URL}/api/v4/teams/{team_id}/channels/name/{channel_name}", headers=HEADERS_MATTERMOST)
    return res.json() if res.status_code == 200 else None

def create_mattermost_user(username, email, password, config):
    """
    Create a new Mattermost user, and optionally add them to a team and channels based on the config.

    Args:
        username (str): Username.
        email (str): User email.
        password (str): User password.
        config (dict): Configuration containing:
            - team (str): Team name to add the user to.
            - role (str): User role in the team ("Admin" or "Member").
            - default_channels (list): List of default channel names.

    Returns:
        dict: Created user information or detailed error message.
    """
    # config expects: servername, team, role, default_channels
    team_name = config.get("team")
    role = config.get("role")
    default_channels = config.get("default_channels", [])

    # 1. Create user
    payload = {"email": email, "username": username, "password": password}
    res = requests.post(f"{MATTERMOST_URL}/api/v4/users", headers=HEADERS_MATTERMOST, json=payload)
    if res.status_code != 201:
        return {"error": res.json(), "status": res.status_code}

    user = res.json()
    user_id = user["id"]

    # 2. Add to team
    if team_name:
        team = get_team_by_name(team_name)
        if not team:
            return {"error": f"Team '{team_name}' not found"}
        team_id = team["id"]

        # Add user to team
        requests.post(
            f"{MATTERMOST_URL}/api/v4/teams/{team_id}/members",
            headers=HEADERS_MATTERMOST,
            json={"team_id": team_id, "user_id": user_id}
        )

        # 3. Assign role
        if role:
            requests.put(
                f"{MATTERMOST_URL}/api/v4/teams/{team_id}/members/{user_id}/roles",
                headers=HEADERS_MATTERMOST,
                json={"roles": f"{role}"}
            )

        # 4. Add to default channels
        for ch_name in default_channels:
            ch = get_channel_by_name(team_id, ch_name)
            if ch:
                requests.post(
                    f"{MATTERMOST_URL}/api/v4/channels/{ch['id']}/members",
                    headers=HEADERS_MATTERMOST,
                    json={"user_id": user_id}
                )

    return {
        "id": user_id,
        "username": username,
        "email": email
    }

def update_mattermost_user(user_id, update_data):
    """
    Update Mattermost user information.

    Args:
        user_id (str): User ID.
        update_data (dict): Fields to update (email, username, password, etc.)

    Returns:
        dict: Updated user information.
    """
    url = f"{MATTERMOST_URL}/api/v4/users/{user_id}"
    res = requests.put(url, headers=HEADERS_MATTERMOST, json=update_data)
    return res.json()

def delete_mattermost_user(user_id, permanent=False):
    """
    Delete or deactivate a Mattermost user.

    Args:
        user_id (str): User ID.
        permanent (bool): If True, the user is permanently deleted. Otherwise, just deactivated.

    Returns:
        dict: Deletion status response.
    """
    url = f"{MATTERMOST_URL}/api/v4/users/{user_id}"
    if permanent:
        url += "?permanent=true"

    res = requests.delete(url, headers=HEADERS_MATTERMOST)
    return {"status": res.status_code, "detail": res.text}

def add_user_to_team(user_id: str, team_name: str):
    """
    Add a user to a team by name.

    Args:
        user_id (str): User ID.
        team_name (str): Name of the team.

    Returns:
        dict: API response.
    """
    team = get_team_by_name(team_name)
    if not team:
        return {"error": f"Team '{team_name}' not found"}
    team_id = team["id"]
    res = requests.post(
        f"{MATTERMOST_URL}/api/v4/teams/{team_id}/members",
        headers=HEADERS_MATTERMOST,
        json={"team_id": team_id, "user_id": user_id}
    )
    return res.json()

def update_user_team_role(user_id: str, team_name: str, role: str):
    """
    Update a user's role within a team.

    Args:
        user_id (str): User ID.
        team_name (str): Name of the team.
        role (str): Role to assign, only "Admin" or "Member" supported.

    Returns:
        dict: API response or error message.
    """
    role_mapping = {
        "Admin": "team_admin",
        "Member": "team_user"
    }
    mattermost_roles = role_mapping.get(role)
    if not mattermost_roles:
        return {"error": f"Invalid role: {role}"}

    team = get_team_by_name(team_name)
    if not team:
        return {"error": f"Team '{team_name}' not found"}
    
    team_id = team["id"]
    res = requests.put(
        f"{MATTERMOST_URL}/api/v4/teams/{team_id}/members/{user_id}/roles",
        headers=HEADERS_MATTERMOST,
        json={"roles": mattermost_roles}
    )
    return res.json()

def remove_user_from_team(user_id: str, team_name: str):
    """
    Remove a user from a team.

    Args:
        user_id (str): User ID.
        team_name (str): Name of the team.

    Returns:
        dict: Status of removal.
    """
    team = get_team_by_name(team_name)
    if not team:
        return {"error": f"Team '{team_name}' not found"}
    team_id = team["id"]
    res = requests.delete(
        f"{MATTERMOST_URL}/api/v4/teams/{team_id}/members/{user_id}",
        headers=HEADERS_MATTERMOST
    )
    return {"status": res.status_code}
