import os
import time
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta, timezone

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import STATE_FILE, GMAIL_QUERY, MAX_RETRIES, RETRY_BACKOFF_SECONDS, PROCESS_LAST_HOURS

# Gmail scopes: read-only + modify (to mark as read)
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def _retry(func, *args, **kwargs):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return func(*args, **kwargs)
        except HttpError as e:
            if attempt == MAX_RETRIES:
                raise
            time.sleep(RETRY_BACKOFF_SECONDS * attempt)

def get_gmail_service():
    creds = None
    token_path = "token.json"
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            _retry(creds.refresh, None)
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials/credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)

def _load_last_history_id() -> Optional[str]:
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE, "r") as f:
        data = json.load(f)
        return data.get("lastHistoryId")

def _save_last_history_id(history_id: str):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump({"lastHistoryId": history_id}, f)

def _within_last_hours(internal_date_ms: int) -> bool:
    if PROCESS_LAST_HOURS <= 0:
        return True
    msg_dt = datetime.fromtimestamp(internal_date_ms / 1000, tz=timezone.utc)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=PROCESS_LAST_HOURS)
    return msg_dt >= cutoff

def fetch_unread_messages(service) -> List[Dict]:
    """
    Returns a list of full message objects for unread emails in inbox,
    filtered by optional PROCESS_LAST_HOURS.
    """
    user_id = "me"
    query = GMAIL_QUERY
    messages = []

    def list_messages():
        return service.users().messages().list(userId=user_id, q=query).execute()

    response = _retry(list_messages)
    ids = response.get("messages", [])
    next_page_token = response.get("nextPageToken")

    while next_page_token:
        response = _retry(service.users().messages().list, userId=user_id, q=query, pageToken=next_page_token).execute()
        ids.extend(response.get("messages", []))
        next_page_token = response.get("nextPageToken")

    for m in ids:
        def get_msg():
            return service.users().messages().get(userId=user_id, id=m["id"], format="full").execute()
        msg = _retry(get_msg)
        internal_date_ms = int(msg.get("internalDate", "0"))
        if _within_last_hours(internal_date_ms):
            messages.append(msg)

    return messages

def mark_messages_read(service, message_ids: List[str]):
    if not message_ids:
        return
    user_id = "me"
    body = {
        "ids": message_ids,
        "removeLabelIds": ["UNREAD"]
    }
    _retry(service.users().messages().batchModify, userId=user_id, body=body).execute()

def get_latest_history_id(service) -> Optional[str]:
    """
    Fetch the current historyId from the latest message to persist state.
    """
    user_id = "me"
    resp = _retry(service.users().messages().list, userId=user_id, maxResults=1, q="").execute()
    msgs = resp.get("messages", [])
    if not msgs:
        return None
    latest = _retry(service.users().messages().get, userId=user_id, id=msgs[0]["id"]).execute()
    return latest.get("historyId")

def persist_run_state(service):
    latest_history_id = get_latest_history_id(service)
    if latest_history_id:
        _save_last_history_id(latest_history_id)