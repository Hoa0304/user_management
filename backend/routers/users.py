import logging
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from datetime import datetime
import os
import time
from db import SessionLocal
from models.user import User
from schemas.user import NextCloudConfig, UserCreate, UserOut, MattermostConfig, GitLabConfig, UserUpdate
from utils.security import hash_password
from services import gitlab_service, mattermost_service, nextcloud_service

router = APIRouter()

@router.post("/users", response_model=UserOut)
def create_user(user_data: UserCreate):
    db: Session = SessionLocal()
    try:
        if db.query(User).filter(User.username == user_data.username).first():
            raise HTTPException(status_code=400, detail="User already exists")

        hashed_pw = hash_password(user_data.password)

        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_pw,
            created_at=datetime.utcnow(),
            platforms=[]  # ✅ list, không phải dict
        )

        platforms = user_data.platforms or []

        for platform_config in platforms:
            if platform_config.platform == "gitlab":
                gitlab_config: GitLabConfig = platform_config
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

                gitlab_config_dict["username"] = user_data.username
                gitlab_config_dict["email"] = user_data.email
                gitlab_config_dict["platform"] = "gitlab"

                result = gitlab_service.add_account(gitlab_config_dict)
                user.platforms.append(result)

            elif platform_config.platform == "mattermost":
                mm_config: MattermostConfig = platform_config
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
                user.platforms.append(mm_config_dict)  # ✅

            elif platform_config.platform == "nextcloud":
                nc_config: NextCloudConfig = platform_config

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
                    permission_map = {
                        "viewer": 1,
                        "editor": 15,
                    }

                    nextcloud_service.share_folder(
                        folder_path=nc_config.shared_folder_id,
                        userid=user_data.username,
                        permission=permission_map.get(nc_config.permission or "viewer", 1)
                    )

                user.platforms.append(nc_config.model_dump()) 

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
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.get("/all_users", response_model=list[UserOut])
def get_all_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return [
            UserOut(
                id=user.id,
                username=user.username,
                email=user.email,
                created_at=user.created_at,
                platforms=user.platforms if user.platforms else []
            )
            for user in users
        ]
    finally:
        db.close()
        
@router.patch("/users/{username}", response_model=UserOut)
def update_user(username: str, user_update: UserUpdate):
    print(f"Update data: {user_update}")
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        platforms = user.platforms or {}

        # Update email and password
        if user_update.email:
            user.email = user_update.email
        if user_update.password:
            from utils.security import hash_password
            user.password_hash = hash_password(user_update.password)

        # Convert platforms list → dict by platform name for easier lookup
        platform_map = {p.platform: p for p in user_update.platforms or []}

        ### GITLAB UPDATE ###
        if "gitlab" in platforms and "gitlab" in platform_map:
            gl_conf = platforms["gitlab"]
            gl_update = platform_map["gitlab"]

            gitlab_user_id = gl_conf.get("user_id")
            if not gitlab_user_id:
                raise HTTPException(status_code=400, detail="Missing GitLab user ID")

            new_role = getattr(gl_update, "role", None)
            new_group_id = getattr(gl_update, "group_id", None)

            if new_role and new_group_id:
                gitlab_service.update_user_role(
                    user_id=gitlab_user_id,
                    group_id=new_group_id,
                    role=new_role
                )

            if "gitlab" not in user.platforms:
                user.platforms["gitlab"] = {}

            user.platforms["gitlab"].update(gl_update.dict(exclude_unset=True))
            flag_modified(user, "platforms")


        ### MATTTERMOST UPDATE ###
        if "mattermost" in platforms and "mattermost" in platform_map:
            mm_conf = platforms["mattermost"]
            mm_user_id = mm_conf.get("user_id")
            if not mm_user_id:
                raise HTTPException(status_code=400, detail="Missing Mattermost user ID")

            mm_update = platform_map["mattermost"]

            update_fields = {}
            if user_update.email:
                update_fields["email"] = user_update.email
            if user_update.username:
                update_fields["username"] = user_update.username

            if update_fields:
                mattermost_service.update_mattermost_user(mm_user_id, update_fields)

            # Role/team update
            new_role = getattr(mm_update, "role", None)
            team_name = mm_conf.get("team")
            if new_role and team_name:
                mattermost_service.update_user_team_role(
                    user_id=mm_user_id,
                    team_name=team_name,
                    role=new_role
                )

            if "mattermost" not in user.platforms:
                user.platforms["mattermost"] = {}

            user.platforms["mattermost"].update(mm_update.dict(exclude_unset=True))
            flag_modified(user, "platforms")

        ### NEXTCLOUD UPDATE ###
        if "nextcloud" in platforms and "nextcloud" in platform_map:
            nc_conf = platforms["nextcloud"]
            nc_update = platform_map["nextcloud"]
            username_nc = user.username

            if user_update.email:
                nextcloud_service.update_user(username_nc, "email", user_update.email)
            if user_update.password:
                nextcloud_service.update_user(username_nc, "password", user_update.password)

            if nc_update.storage_limit:
                nextcloud_service.set_user_quota(username_nc, f"{nc_update.storage_limit} MB")

            old_group = nc_conf.get("group_id")
            new_group = nc_update.group_id
            if new_group and old_group != new_group:
                if old_group:
                    nextcloud_service.remove_member_from_group(username_nc, old_group)
                nextcloud_service.add_member_to_group(username_nc, new_group)

            old_folder = nc_conf.get("shared_folder_id")
            new_folder = nc_update.shared_folder_id
            new_permission = nc_update.permission or "viewer"

            if old_folder and old_folder != new_folder:
                try:
                    nextcloud_service.unshare_folder_by_user(old_folder, username_nc)
                except:
                    pass

            if new_folder:
                permission_map = {
                    "viewer": 1,
                    "editor": 15,
                }
                nextcloud_service.share_folder(
                    folder_path=new_folder,
                    userid=username_nc,
                    permission=permission_map.get(new_permission, 1)
                )

            if "nextcloud" not in user.platforms:
                user.platforms["nextcloud"] = {}

            user.platforms["nextcloud"].update(nc_update.dict(exclude_unset=True))
            flag_modified(user, "platforms")

        if user_update.platforms:
            flag_modified(user, "platforms")

        db.commit()
        db.refresh(user)
        return user

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


        
@router.delete("/users/{username}", response_model=dict)
def delete_user(username: str):
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # --- Optional cleanup on platforms ---
        platforms = user.platforms or {}

        # Mattermost cleanup
        if "mattermost" in platforms:
            mm_user_id = platforms["mattermost"].get("user_id")
            if mm_user_id:
                try:
                    mattermost_service.delete_mattermost_user(mm_user_id)
                except Exception as e:
                    print(f"[Mattermost] Deactivation failed: {e}")

        # NextCloud cleanup
        if "nextcloud" in platforms:
            try:
                nextcloud_service.delete_user(username)
            except Exception as e:
                print(f"[NextCloud] Delete failed: {e}")

        db.delete(user)
        db.commit()

        return {"message": f"User '{username}' deleted successfully."}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
