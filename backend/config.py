import os
from dotenv import load_dotenv

load_dotenv()

NEXTCLOUD_BASE_URL = os.getenv("NEXTCLOUD_BASE_URL")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

OCS_HEADERS = {
    "OCS-APIRequest": "true",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json"
}
