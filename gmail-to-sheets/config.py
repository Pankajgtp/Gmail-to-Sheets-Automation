import os

# Spreadsheet configuration
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID","example=9ngtvzuEJrfmpYsWRLVxGZyPl1gU")  # set via .env or environment
SHEET_NAME = os.getenv("SHEET_NAME", "Emails")

# Gmail query: unread inbox only
# You can add subject filters like: 'label:inbox is:unread subject:Invoice'
GMAIL_QUERY = os.getenv("GMAIL_QUERY", "label:inbox is:unread")

# State file path
STATE_FILE = os.getenv("STATE_FILE", "state/last_history_id.json")

# Duplicate prevention: use Gmail message ID as unique key
DEDUP_KEY_COLUMN = "MessageId"

# Optional: process only last N hours (bonus change-ready)
PROCESS_LAST_HOURS = int(os.getenv("PROCESS_LAST_HOURS", "0"))  # 0 = disabled

# Retry settings
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_BACKOFF_SECONDS = float(os.getenv("RETRY_BACKOFF_SECONDS", "1.5"))
