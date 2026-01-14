import base64
from bs4 import BeautifulSoup
from typing import Dict, Tuple

def _decode_b64url(data: str) -> str:
    return base64.urlsafe_b64decode(data.encode("UTF-8")).decode("UTF-8", errors="ignore")

def extract_headers(message: Dict) -> Tuple[str, str, str, str]:
    """
    Returns (from_email, subject, date_str, message_id)
    """
    headers = message.get("payload", {}).get("headers", [])
    hmap = {h["name"].lower(): h["value"] for h in headers}
    from_email = hmap.get("from", "")
    subject = hmap.get("subject", "")
    date_str = hmap.get("date", "")
    message_id = message.get("id", "")
    return from_email, subject, date_str, message_id

def extract_body_plain_text(message: Dict) -> str:
    """
    Extracts plain text from message payload. Handles text/plain and text/html.
    """
    payload = message.get("payload", {})
    parts = payload.get("parts", [])
    data = payload.get("body", {}).get("data")

    def html_to_text(html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator="\n").strip()

    # If single-part message
    if data:
        text = _decode_b64url(data)
        # Heuristic: if looks like HTML, convert
        if "<html" in text.lower():
            return html_to_text(text)
        return text.strip()

    # Multipart: search for text/plain first
    for p in parts or []:
        mime = p.get("mimeType", "")
        pdata = p.get("body", {}).get("data")
        if not pdata:
            continue
        decoded = _decode_b64url(pdata)
        if mime == "text/plain":
            return decoded.strip()
    # Fallback: use first text/html
    for p in parts or []:
        mime = p.get("mimeType", "")
        pdata = p.get("body", {}).get("data")
        if not pdata:
            continue
        decoded = _decode_b64url(pdata)
        if mime == "text/html":
            return html_to_text(decoded)
    return ""