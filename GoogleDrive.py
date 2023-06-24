from turtle import update
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload

import os

GOOGLE_OAUTH_SCOPES = [
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/drive.appdata",
    "https://www.googleapis.com/auth/drive.file",
]

NEXT_GOOGLE_ACCOUNT_ID = 0


class GoogleDrive:
    primary_account = None
    number_of_accounts = 0

    def is_valid(self):
        if self.token_status == 0:
            return True
        else:
            return False

    def is_not_valid(self):
        if self.token_status == 0:
            return False
        else:
            return True

    def is_expired(self):
        if self.token_status == 1:
            return True
        else:
            return False

    def has_refresh_token(self):
        if self.token.refresh_token is None:
            return False
        else:
            return True

    def __init__(self, id=-1, path="", scope=GOOGLE_OAUTH_SCOPES):
        # Spanned Drive ID, 0 for primary account
        if id == -1:
            global NEXT_GOOGLE_ACCOUNT_ID
            self.id = NEXT_GOOGLE_ACCOUNT_ID
            NEXT_GOOGLE_ACCOUNT_ID = NEXT_GOOGLE_ACCOUNT_ID + 1
        else:
            self.id = id

        self.name = ""  # User Defined Drive Name
        self.email = ""  # Drive Email Address

        self.scope = scope

        if path == "":
            self.token_path = f"drives\\{self.id}.json"
        else:
            self.token_path = path
        self.token = None  # Token Object

        self.token_status = -1
        # -1: No Token, 0: Valid Token, 1: Expired Token, 2: Invalid Token

        self.service = None  # Google Drive Service Object
        self.last_result = dict

    def __str__(self):
        return f"Google Drive: {self.name} ({self.email})"

    def update_status(self):
        if self.token is None:
            self.token_status = -1  # No token
        else:
            if self.token.valid and not self.token.expired:
                self.token_status = 0  # Valid token

            elif self.token.expired and self.token.refresh_token:
                self.token_status = 1  # Expired token

            else:
                self.token_status = 2  # Invalid token

        return self.token_status

    def init_from_token_file(self, path):
        self.token_path = path
        self.token = Credentials.from_authorized_user_file(path, self.scope)
        return self.update_status()

    def signup(self):
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", self.scope
            )
            self.token = flow.run_local_server(port=0)
            GoogleDrive.number_of_accounts = GoogleDrive.number_of_accounts + 1
        except:
            self.token = None  # Invalid token
        return self.update_status()

    def save_token(self, path=""):
        if path is None or path == "":
            path = self.token_path
        if path is None or path == "":
            raise "Path cannot be empty"

        if self.token is not None:
            with open(path, 'w') as token:
                token.write(self.token.to_json())

    def service(self):
        self.service = build("drive", "v3", credentials=self.token)
        return self.service

    def refresh(self):
        try:
            self.token.refresh(Request())
        except:
            pass
        return self.update_status()

    def sync_appdata(self):
        # Get list of files in local appdata folder and subfolders
        local_appdata_folder = list
        for path, subdirs, files in os.walk("appdata"):
            for name in files:
                local_appdata_folder.append(os.path.join(path, name))

        # Get list of files in remote appdata folder and subfolders
        remote_appdata_folder = list
        response = (
            self.service.files()
            .list(
                spaces="appDataFolder",
                fields="nextPageToken, files(id, " "name)",
                pageSize=10,
            )
            .execute()
        )

        for file in response.get("files", []):
            print(f'Found file: {file.get("name")}, {file.get("id")}')
