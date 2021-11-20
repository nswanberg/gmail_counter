"""Based on https://developers.google.com/gmail/api/quickstart/python"""

from __future__ import print_function
import csv
import datetime
import os
from pathlib import Path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

CSV_FILENAME = "gmail_unread_count_v01.csv"


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    base_path = Path(__file__).parent
    token_file_path = (base_path / "token.json").resolve()
    if os.path.exists(token_file_path):
        creds = Credentials.from_authorized_user_file(token_file_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        print(f"{token_file_path} not found. Authorizing...")
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing credentials...")
            creds.refresh(Request())
        else:
            cred_file_path = (base_path / "credentials.json").resolve()
            flow = InstalledAppFlow.from_client_secrets_file(cred_file_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_file_path, "w") as token:
            print(f"saving token to {token_file_path}")
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)

    # Ensure the csv file exists
    csv_path = (Path.home() / "Dropbox/Records/PersonalData").resolve()
    if not os.path.exists(csv_path):
        print(f"Csv path {csv_path} not found. Creating csv directory")
        os.makedirs(csv_path)

    # Call the Gmail API
    results = service.users().labels().list(userId="me").execute()

    labels = results.get("labels", [])

    if not labels:
        print("No labels found.")
        return
    full_csv_path = (csv_path / CSV_FILENAME).resolve()
    csv_exists = os.path.exists(full_csv_path)

    with open(full_csv_path, "a") as csvfile:
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        fields = [
            "insert_datetime",
            "label_id",
            "label_name",
            "threads_unread",
            "threads_total",
            "result_size_estimate",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        if not csv_exists:
            writer.writeheader()

        for label in labels:
            view = [
                "CHAT",
                "SENT",
                "INBOX",
                "IMPORTANT",
                "TRASH",
                "DRAFT",
                "SPAM",
                "CATEGORY_FORUMS",
                "CATEGORY_UPDATES",
                "CATEGORY_PERSONAL",
                "CATEGORY_PROMOTIONS",
                "CATEGORY_SOCIAL",
                "STARRED",
                "UNREAD",
            ]

            label_name = label["name"]
            label_id = label["id"]

            if label_name in view:
                details = (
                    service.users().labels().get(userId="me", id=label_id).execute()
                )
                messages = (
                    service.users()
                    .messages()
                    .list(userId="me", labelIds=["INBOX", label_id], maxResults=500)
                    .execute()
                )
                record = {
                    "insert_datetime": now,
                    "label_id": label_id,
                    "label_name": label_name,
                    "threads_unread": details["threadsUnread"],
                    "threads_total": details["threadsTotal"],
                    "result_size_estimate": messages["resultSizeEstimate"],
                }
                writer.writerow(record)


if __name__ == "__main__":
    main()
