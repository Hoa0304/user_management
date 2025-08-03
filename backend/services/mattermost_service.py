import os
import requests
from dotenv import load_dotenv

load_dotenv()

MATTERMOST_URL = os.getenv("MATTERMOST_URL")
TOKEN = os.getenv("MATTERMOST_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def get_team_by_name(name):
    res = requests.get(f"{MATTERMOST_URL}/api/v4/teams/name/{name}", headers=HEADERS)
    return res.json() if res.status_code == 200 else None

def get_channel_by_name(team_id, channel_name):
    res = requests.get(f"{MATTERMOST_URL}/api/v4/teams/{team_id}/channels/name/{channel_name}", headers=HEADERS)
    return res.json() if res.status_code == 200 else None

def create_mattermost_user(username, email, password, config):
    # config expects: servername, team, role, default_channels
    team_name = config.get("team")
    role = config.get("role")
    default_channels = config.get("default_channels", [])

    # 1. Create user
    payload = {"email": email, "username": username, "password": password}
    res = requests.post(f"{MATTERMOST_URL}/api/v4/users", headers=HEADERS, json=payload)
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
            headers=HEADERS,
            json={"team_id": team_id, "user_id": user_id}
        )

        # 3. Assign role
        if role:
            requests.put(
                f"{MATTERMOST_URL}/api/v4/teams/{team_id}/members/{user_id}/roles",
                headers=HEADERS,
                json={"roles": f"{role}"}
            )

        # 4. Add to default channels
        for ch_name in default_channels:
            ch = get_channel_by_name(team_id, ch_name)
            if ch:
                requests.post(
                    f"{MATTERMOST_URL}/api/v4/channels/{ch['id']}/members",
                    headers=HEADERS,
                    json={"user_id": user_id}
                )

    return {
        "id": user_id,
        "username": username,
        "email": email
    }

def update_mattermost_user(user_id, update_data):
    url = f"{MATTERMOST_URL}/api/v4/users/{user_id}"
    res = requests.put(url, headers=HEADERS, json=update_data)
    return res.json()

def delete_mattermost_user(user_id):
    url = f"{MATTERMOST_URL}/api/v4/users/{user_id}"
    res = requests.delete(url, headers=HEADERS)
    return {"status": res.status_code}

def add_user_to_team(user_id: str, team_name: str):
    team = get_team_by_name(team_name)
    if not team:
        return {"error": f"Team '{team_name}' not found"}
    team_id = team["id"]
    res = requests.post(
        f"{MATTERMOST_URL}/api/v4/teams/{team_id}/members",
        headers=HEADERS,
        json={"team_id": team_id, "user_id": user_id}
    )
    return res.json()

def update_user_team_role(user_id: str, team_name: str, role: str):
    team = get_team_by_name(team_name)
    if not team:
        return {"error": f"Team '{team_name}' not found"}
    team_id = team["id"]
    res = requests.put(
        f"{MATTERMOST_URL}/api/v4/teams/{team_id}/members/{user_id}/roles",
        headers=HEADERS,
        json={"roles": f"{role} Member"}
    )
    return res.json()

def remove_user_from_team(user_id: str, team_name: str):
    team = get_team_by_name(team_name)
    if not team:
        return {"error": f"Team '{team_name}' not found"}
    team_id = team["id"]
    res = requests.delete(
        f"{MATTERMOST_URL}/api/v4/teams/{team_id}/members/{user_id}",
        headers=HEADERS
    )
    return {"status": res.status_code}
