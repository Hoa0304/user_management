import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

from dotenv import load_dotenv

load_dotenv()

#-----NextCloud------#

NEXTCLOUD_BASE_URL = os.getenv("NEXTCLOUD_BASE_URL")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

OCS_HEADERS = {
    "OCS-APIRequest": "true",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json"
}

#-----GitLab------#

GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
if not GITLAB_TOKEN:
    raise Exception("Missing GITLAB_TOKEN in environment variables")

GITLAB_API_BASE = os.getenv("GITLAB_URL")

HEADERS_GITLAB = {
    "Private-Token": GITLAB_TOKEN
}

#-----Mattermost------#

MATTERMOST_URL = os.getenv("MATTERMOST_URL")
TOKEN = os.getenv("MATTERMOST_TOKEN")

HEADERS_MATTERMOST = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

#-----Google Drive------#

SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "service_account.json")
SCOPES = ["https://www.googleapis.com/auth/drive"]

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

drive_service = build("drive", "v3", credentials=credentials)
