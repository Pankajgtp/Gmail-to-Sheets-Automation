import sys
from typing import List

from config import DEDUP_KEY_COLUMN
from src.gmail_service import get_gmail_service, fetch_unread_messages, mark_messages_read, persist_run_state
from src.sheets_service import get_sheets_service, ensure_header_row, get_existing_message_ids, append_rows
from src.email_parser import extract_headers, extract_body_plain_text

def build_rows(messages) -> List[List[str]]:
    rows = []
    for msg in messages:
        from_email, subject, date_str, message_id = extract_headers(msg)
        body_text = extract_body_plain_text(msg)
        rows.append([from_email, subject, date_str, body_text, message_id])
    return rows

def main():
    try:
        gmail = get_gmail_service()
        sheets = get_sheets_service()

        ensure_header_row(sheets)

        # Fetch unread messages
        messages = fetch_unread_messages(gmail)
        if not messages:
            print("No unread messages matching query.")
            return

        # Dedup using MessageId column
        existing_ids = get_existing_message_ids(sheets)
        to_append = []
        to_mark_read = []

        for msg in messages:
            message_id = msg.get("id")
            if message_id in existing_ids:
                # Already logged—mark read to avoid reprocessing
                to_mark_read.append(message_id)
                continue
            to_append.append(msg)
            to_mark_read.append(message_id)

        # Build rows and append
        rows = build_rows(to_append)
        append_rows(sheets, rows)

        # Mark processed messages as read
        mark_messages_read(gmail, to_mark_read)

        # Persist state (latest historyId)
        persist_run_state(gmail)

        print(f"Appended {len(rows)} new rows. Marked {len(to_mark_read)} messages as read.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()