from __future__ import print_function

import os.path
import json
from re import I
import re
from textwrap import indent

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from utility import isEmpty

# If modifying these scopes, delete the file tokens.json.
SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.metadata",
    "https://www.googleapis.com/auth/drive",
]


def main():
    creds = []

    """
    The file tokens.json stores the locations of multiple users' access and refresh tokens, and is
    created automatically when the authorization flow completes for the first time.
    """

    tokens = []

    """
    tokens.json is a list of locations of cred files.
    """

    if not os.path.isdir("tokens"):
        os.mkdir("tokens")

    if os.path.exists("tokens\\tokens.json"):
        with open("tokens\\tokens.json", "r") as f:
            tokens = json.load(f)

        for token in tokens:
            creds.append(Credentials.from_authorized_user_file(token, SCOPES))


    if isEmpty(creds):
        # Let the user log in using primiary account (First Entry in tokens list)
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds.append(flow.run_local_server(port=0))

        # Update entry in tokens.json and save
        tokens.append("tokens\\" + str(len(tokens)) + ".json")
        with open("tokens\\tokens.json", "w") as f:
            json.dump(tokens, f, indent=4)

        # Save the credentials for next run
        with open(tokens[0], "w") as f:
            f.write(creds[0].to_json())

    if not creds[0].valid:
        if creds[0].expired and creds[0].refresh_token:
            creds[0].refresh(Request())

            # Save the credentials for next run
            with open(tokens[0], "w") as f:
                f.write(creds[0].to_json())
	

    toRefresh = []
    invalid = []
    valid = []


    # Check for validity of secondary accounts
    for cred in creds[1:]:
        if not cred.valid or cred.expired:
            if cred.expired and cred.refresh_token:
                toRefresh.append(cred)
            else:
                invalid.append(cred)
        else:
            valid.append(cred)

    #
    services = []
    try:
        for cred in valid:
            service = build("drive", "v3", credentials=cred)
            services.append(service)
            results = (
                service.files()
                .list(pageSize=10, fields="nextPageToken, files(id, name)")
                .execute()
            )

            items = results.get("files", [])

            if not items:
                print("No files found.")
                return
            print("Files:")
            for item in items:
                print("{0} ({1})".format(item["name"], item["id"]))

    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()