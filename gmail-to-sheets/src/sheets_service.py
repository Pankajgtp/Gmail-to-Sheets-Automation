from typing import List, Dict
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os
import time

from config import SPREADSHEET_ID, SHEET_NAME, MAX_RETRIES, RETRY_BACKOFF_SECONDS

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def _retry(func, *args, **kwargs):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return func(*args, **kwargs)
        except Exception:
            if attempt == MAX_RETRIES:
                raise
            time.sleep(RETRY_BACKOFF_SECONDS * attempt)

def get_sheets_service():
    creds = None
    token_path = "token_sheets.json"
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(None)
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials/credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    return build("sheets", "v4", credentials=creds)

def ensure_header_row(service):
    """
    Ensures the sheet has the header row: From, Subject, Date, Content, MessageId
    """
    sheet_range = f"{SHEET_NAME}!A1:E1"
    values = [["From", "Subject", "Date", "Content", "MessageId"]]
    body = {"values": values}
    _retry(service.spreadsheets().values().update,
           spreadsheetId=SPREADSHEET_ID,
           range=sheet_range,
           valueInputOption="RAW",
           body=body).execute()

def get_existing_message_ids(service) -> set:
    """
    Reads the MessageId column to prevent duplicates.
    Assumes header row present.
    """
    sheet_range = f"{SHEET_NAME}!E2:E"  # MessageId column
    resp = _retry(service.spreadsheets().values().get,
                  spreadsheetId=SPREADSHEET_ID,
                  range=sheet_range).execute()
    values = resp.get("values", [])
    return set(v[0] for v in values if v)

def append_rows(service, rows: List[List[str]]):
    """
    Appends rows to the sheet.
    """
    if not rows:
        return
    sheet_range = f"{SHEET_NAME}!A2:E"
    body = {"values": rows}
    _retry(service.spreadsheets().values().append,
           spreadsheetId=SPREADSHEET_ID,
           range=sheet_range,
           valueInputOption="RAW",
           insertDataOption="INSERT_ROWS",
           body=body).execute()