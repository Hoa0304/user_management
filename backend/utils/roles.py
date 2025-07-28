def map_role_to_access_level(role: str) -> int:
    role_map = {
        "Guest": 10,
        "Reporter": 20,
        "Developer": 30,
        "Maintainer": 40,
        "Owner": 50,
    }
    return role_map.get(role, 30)
