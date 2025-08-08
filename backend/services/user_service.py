import logging
from fastapi import HTTPException
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.orm import Session
from datetime import datetime
import os
from models.user import User
from schemas.user import (
    DriveConfig, DriveOutConfig, NextCloudConfig, MattermostConfig,
    GitLabConfig, UserCreate, UserOut, UserUpdate, platform_model_map
)
from utils.security import hash_password
from utils.roles import map_role_to_access_level
from services import gitlab_service, mattermost_service, nextcloud_service, google_drive

def create_user_with_platforms(db: Session, user_data: UserCreate) -> UserOut:
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_pw = hash_password(user_data.password)

    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_pw,
        created_at=datetime.utcnow(),
        platforms=[]
    )

    platforms = user_data.platforms or []

    for platform_config in platforms:
        if platform_config.platform == "gitlab":
            _add_gitlab_user(user, user_data, platform_config)
        elif platform_config.platform == "mattermost":
            _add_mattermost_user(user, user_data, platform_config)
        elif platform_config.platform == "nextcloud":
            _add_nextcloud_user(user, user_data, platform_config)
        elif platform_config.platform == "drive":
            _add_drive_user(user, user_data, platform_config)

    db.add(user)
    db.commit()
    db.refresh(user)
    logging.warning("User platforms data: %s", user.platforms)

    return UserOut(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at,
        platforms=user.platforms
    )

# ---- Helper functions ----
def _add_gitlab_user(user, user_data, gitlab_config: GitLabConfig):
    gitlab_config_dict = gitlab_config.model_dump()

    gitlab_user_id = gitlab_service.find_gitlab_user_by_email(user_data.email)
    if not gitlab_user_id:
        created = gitlab_service.create_gitlab_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password
        )
        if not created or "id" not in created:
            raise HTTPException(status_code=500, detail="Failed to create GitLab user")
        gitlab_user_id = created["id"]

    gitlab_config_dict.update({
        "username": user_data.username,
        "email": user_data.email,
        "platform": "gitlab"
    })

    result = gitlab_service.add_account(gitlab_config_dict)
    user.platforms.append(result)

def _add_mattermost_user(user, user_data, mm_config: MattermostConfig):
    mm_config_dict = mm_config.model_dump()
    mm_config_dict["server_url"] = os.getenv("MATTERMOST_SERVER_URL")
    mm_config_dict["admin_token"] = os.getenv("MATTERMOST_ADMIN_TOKEN")

    if mm_config.server_name:
        mm_config_dict["server_url"] = f"https://{mm_config.server_name}"

    mm_user = mattermost_service.create_mattermost_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        config=mm_config_dict
    )

    if not isinstance(mm_user, dict) or "id" not in mm_user:
        raise HTTPException(status_code=500, detail=f"Invalid Mattermost response: {mm_user}")

    mm_config_dict["user_id"] = mm_user["id"]
    user.platforms.append(mm_config_dict)

def _add_nextcloud_user(user, user_data, nc_config: NextCloudConfig):
    nextcloud_service.create_user(
        userid=user_data.username,
        password=user_data.password,
        email=user_data.email,
    )

    nextcloud_service.wait_for_user_ready(user_data.username)

    if nc_config.group_id:
        nextcloud_service.add_member_to_group(user_data.username, nc_config.group_id)

    if nc_config.storage_limit:
        nextcloud_service.set_user_quota(user_data.username, f"{nc_config.storage_limit} MB")

    if nc_config.shared_folder_id:
        permission_map = {"viewer": 1, "editor": 15}
        nextcloud_service.share_folder(
            folder_path=nc_config.shared_folder_id,
            userid=user_data.username,
            permission=permission_map.get(nc_config.permission or "viewer", 1)
        )

    user.platforms.append(nc_config.model_dump()) 

def _add_drive_user(user, user_data, drive_config: DriveConfig):
    result = google_drive.grant_folder_access(
        shared_folder_id=drive_config.shared_folder_id,
        user_email=user_data.email,
        role=drive_config.role
    )

    permission_id = result["permission_id"]

    user.platforms.append(DriveOutConfig(
        platform="drive",
        shared_folder_id=drive_config.shared_folder_id,
        user_email=user_data.email,
        role=drive_config.role,
        permission_id=permission_id
    ).dict())

def update_user_with_platforms(db, username: str, user_update: UserUpdate):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    platforms_list = user.platforms or []
    platforms = {p.get("platform"): p for p in platforms_list if isinstance(p, dict)}

    # Update email / password
    if user_update.email:
        user.email = user_update.email
    if user_update.password:
        user.password_hash = hash_password(user_update.password)

    # Normalize payload into dict {platform: model}
    typed_platforms = []
    for item in user_update.platforms or []:
        if isinstance(item, dict):
            model = platform_model_map.get(item.get("platform"))
            if model:
                typed_platforms.append(model(**item))
        else:
            typed_platforms.append(item)
    platform_map = {p.platform: p for p in typed_platforms}

    all_platforms = ["gitlab", "mattermost", "nextcloud", "drive"]

    for p_name in all_platforms:
        in_db = p_name in platforms
        in_payload = p_name in platform_map

        if in_db and in_payload:
            # Case 1: In DB and still on => update
            if p_name == "gitlab":
                _update_gitlab(platforms, platform_map, user_update)
            elif p_name == "mattermost":
                _update_mattermost(platforms, platform_map, user_update)
            elif p_name == "nextcloud":
                _update_nextcloud(platforms, platform_map, user)
            elif p_name == "drive":
                _update_drive(platforms, platform_map, user)

        elif in_db and not in_payload:
            # Case 2: In DB but toggle off => remove
            _remove_platform_account(p_name, platforms[p_name], user)
            del platforms[p_name]

        elif not in_db and in_payload:
            # Case 3: Not yet but toggle on => add
            if p_name == "gitlab":
                _add_gitlab_user(user, user_update, platform_map["gitlab"])
            elif p_name == "mattermost":
                _add_mattermost_user(user, user_update, platform_map["mattermost"])
            elif p_name == "nextcloud":
                _add_nextcloud_user(user, user_update, platform_map["nextcloud"])
            elif p_name == "drive":
                _add_drive_user(user, user_update, platform_map["drive"])
            platforms[p_name] = user.platforms[-1]

    user.platforms = list(platforms.values())
    flag_modified(user, "platforms")
    db.commit()
    db.refresh(user)
    return user

def _remove_platform_account(platform_name: str, config: dict, user: User):
    """Call API/process account deletion on platform when toggle OFF"""
    if platform_name == "gitlab":
        gitlab_service.delete_gitlab_user(config.get("user_id"))
    elif platform_name == "mattermost":
        mattermost_service.delete_mattermost_user(config.get("user_id"))
    elif platform_name == "nextcloud":
        nextcloud_service.delete_user(user.username)
    elif platform_name == "drive":
        if config.get("permission_id"):
            google_drive.revoke_folder_access(config["shared_folder_id"], config["permission_id"])

# --- Helper functions ---
def _update_gitlab(platforms, platform_map, user_update):
    gl_conf = platforms["gitlab"]
    gl_update = platform_map["gitlab"]

    gitlab_user_id = gl_conf.get("user_id")
    if not gitlab_user_id:
        raise HTTPException(status_code=400, detail="Missing GitLab user ID")

    if not gl_update.role:
        raise HTTPException(status_code=400, detail="Missing role")

    access_level = map_role_to_access_level(gl_update.role)
    new_group_id = getattr(gl_update, "group_id", None)

    if access_level and new_group_id:
        gitlab_service.update_user_role(
            user_id=gitlab_user_id,
            group_id=new_group_id,
            repo_ids=getattr(gl_update, "repo_access", []),
            access_level=access_level,
        )

    platforms["gitlab"].update(gl_update.dict(exclude_unset=True))

def _update_mattermost(platforms, platform_map, user_update):
    mm_conf = platforms.get("mattermost", {})
    mm_user_id = mm_conf.get("user_id")
    if not mm_user_id:
        raise HTTPException(status_code=400, detail="Missing Mattermost user ID")

    mm_update = platform_map["mattermost"]

    # --- Update email & username ---
    update_fields = {}
    if user_update.email:
        update_fields["email"] = user_update.email
    if user_update.username:
        update_fields["username"] = user_update.username

    if update_fields:
        mattermost_service.update_mattermost_user(mm_user_id, update_fields)

    # --- Update role ---
    new_role = getattr(mm_update, "role", None)
    team_name = getattr(mm_update, "team", None) or mm_conf.get("team")
    if new_role and team_name:
        # Capitalize role để match mapping
        role_cap = new_role.capitalize()
        res = mattermost_service.update_user_team_role(
            user_id=mm_user_id,
            team_name=team_name,
            role=role_cap
        )
        if "error" in res:
            raise HTTPException(status_code=400, detail=res["error"])

    # --- Merge config ---
    platforms["mattermost"] = {**mm_conf, **mm_update.dict(exclude_unset=True)}

def _update_nextcloud(platforms, platform_map, user):
    nc_conf = platforms.get("nextcloud", {})
    nc_update = platform_map["nextcloud"]
    username_nc = user.username

    if user.email:
        nextcloud_service.update_user(username_nc, "email", user.email)
    if user.password_hash:
        nextcloud_service.update_user(username_nc, "password", user.password_hash)

    if nc_update.storage_limit is not None:
        nextcloud_service.set_user_quota(username_nc, f"{nc_update.storage_limit} MB")

    old_group = nc_conf.get("group_id")
    new_group = nc_update.group_id
    if new_group and old_group != new_group:
        if old_group:
            nextcloud_service.remove_member_from_group(username_nc, old_group)
        nextcloud_service.add_member_to_group(username_nc, new_group)

    old_folder = nc_conf.get("shared_folder_id")
    new_folder = nc_update.shared_folder_id
    new_permission = (nc_update.permission).lower()

    if old_folder and old_folder != new_folder:
        try:
            nextcloud_service.unshare_folder_by_user(old_folder, username_nc)
        except:
            pass

    if new_folder:
        permission_map = {"viewer": 1, "editor": 15}
        new_perm_val = permission_map.get(new_permission, 1)

        if new_folder == old_folder:
            try:
                share_id = nextcloud_service.get_share_id_by_user(new_folder, username_nc)
                nextcloud_service.update_folder_permission_all_user(share_id, new_perm_val)
            except Exception as e:
                print("Failed to update permission:", e)
        else:
            nextcloud_service.share_folder(
                folder_path=new_folder,
                userid=username_nc,
                permission=new_perm_val
            )

    platforms["nextcloud"] = {**nc_conf, **nc_update.dict(exclude_unset=True)}

def _update_drive(platforms, platform_map, user):
    drive_conf = platforms.get("drive", {})
    drive_update = platform_map["drive"]

    folder_id = drive_update.shared_folder_id
    role = drive_update.role.lower()
    user_email = drive_update.user_email or user.email
    permission_id = drive_update.permission_id

    VALID_ROLES = {"reader", "writer", "commenter"}
    if role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid Drive role: {role}")

    try:
        if permission_id:
            google_drive.update_permission(folder_id, permission_id, role)
        else:
            result = google_drive.grant_folder_access(
                shared_folder_id=folder_id,
                user_email=user_email,
                role=role
            )
            permission_id = result["permission_id"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drive role error: {str(e)}")

    platforms["drive"] = {
        **drive_conf,
        **drive_update.dict(exclude_unset=True),
        "user_email": user_email,
        "platform": "drive",
        "permission_id": permission_id,
    }

def delete_mattermost_user(mm_config):
    mm_user_id = mm_config.get("user_id") 
    if mm_user_id:
        try:
            mattermost_service.delete_mattermost_user(mm_user_id)
        except Exception as e:
            logging.error(f"[Mattermost] Deactivation failed: {e}")

def delete_nextcloud_user(username):
    try:
        nextcloud_service.delete_user(username)
    except Exception as e:
        logging.error(f"[NextCloud] Delete failed: {e}")

def delete_gitlab_user(username, gitlab_config):
    group_id = gitlab_config.get("group_id")
    repo_ids = gitlab_config.get("repo_access", [])
    gitlab_user_id = gitlab_config.get("user_id")

    if not gitlab_user_id:
        try:
            gitlab_user_id = gitlab_service.get_gitlab_user_id(username)
        except Exception as e:
            logging.error(f"[GitLab] Could not find GitLab user_id for username {username}: {e}")
            return

    if gitlab_user_id:
        try:
            gitlab_service.remove_user_access(
                user_id=gitlab_user_id,
                group_id=group_id,
                repo_ids=repo_ids
            )
            gitlab_service.delete_gitlab_user(gitlab_user_id)
        except Exception as e:
            logging.error(f"[GitLab] Error delete user_id {gitlab_user_id}: {e}")
    else:
        logging.warning(f"[GitLab] Cannot delete user because user_id from username is not found {username}")

def delete_user_and_cleanup(db: Session, username: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    platforms = user.platforms or []

    if mm_conf := next((p for p in platforms if p.get("platform") == "mattermost"), None):
        delete_mattermost_user(mm_conf)

    if nc_conf := next((p for p in platforms if p.get("platform") == "nextcloud"), None):
        delete_nextcloud_user(username)

    if gl_conf := next((p for p in platforms if p.get("platform") == "gitlab"), None):
        delete_gitlab_user(username, gl_conf)

    db.delete(user)
    db.commit()