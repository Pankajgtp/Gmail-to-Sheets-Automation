

# Gmail to Google Sheets Automation
**By Pankaj**

---

## 📌 Project Overview
This project automates the process of fetching unread Gmail messages and logging them into a Google Sheet.  
It uses **Python**, **Gmail API**, and **Google Sheets API** with OAuth 2.0 authentication.  

Key features:
- Fetches unread emails from Gmail inbox.
- Extracts headers and body content.
- Appends data into a Google Sheet (`From`, `Subject`, `Date`, `Content`, `MessageId`).
- Marks processed emails as **read**.
- Prevents duplicates using Gmail `MessageId`.
- Maintains state with `last_history_id.json`.

---

## 🏗️ Architecture Diagram
![Architecture Diagram](proof/images/archi_diagram.png)

## ⚙️ Setup Instructions

### 1. Clone Repository
```bash
git clone https://github.com/Pankajgtp/Gmail-to-Google-Sheets-Automation.git

cd gmail-to-sheets
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Linux/Mac
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Enable APIs
- Go to Google Cloud Console [(console.cloud.google.com )](https://www.bing.com/search?q="https%3A%2F%2Fconsole.cloud.google.com%2F").
- Create a new project.
- Enable **Gmail API** and **Google Sheets API**.
- Configure **OAuth Consent Screen** (External, add scopes, add test user).
- Create **OAuth Client ID** (Desktop app).
- Download `credentials.json` → place in `credentials/` folder.

### 5. Configure Project
Edit `config.py`:
```python
SPREADSHEET_ID = "your_spreadsheet_id_here"
SHEET_NAME = "Emails"
```

### 6. Create Google Sheet
- Create a new sheet.
- Rename tab to `Emails`.
- Add header row:
  ```
  From | Subject | Date | Content | MessageId
  ```

### 7. Run Script
```bash
python -m src.main
```
- First run → OAuth prompts (browser opens twice: Gmail + Sheets).
- Approve scopes → `token.json` and `token_sheets.json` created.
- Emails appended to sheet, marked as read.

---

## 📂 Proof
Screenshots and demo video are available in the `/proof/` folder:
- Gmail inbox before run (unread emails).
- Google Sheet after run (rows appended).
- Demo video (2–3 minutes, no voice).

---

## 🔒 Security
- `.gitignore` excludes:
  - `credentials/credentials.json`
  - `token.json`
  - `token_sheets.json`
  - `/state/*.json`

---

## 📝 Explanation
- **OAuth Flow:** Prompts twice (Gmail + Sheets), tokens saved locally.
- **Duplicate Prevention:** Uses Gmail `MessageId` as unique key.
- **State Persistence:** Tracks last history ID in `state/last_history_id.json`.
- **Error Handling:** Retries with backoff (`MAX_RETRIES`, `RETRY_BACKOFF_SECONDS`).

---

## ⚠️ Challenges Faced
- Parsing HTML vs plain text email bodies.
- Handling environment variables vs hardcoded config.
- Resolving Python import paths (`src/` package structure).

---

## 🚫 Limitations
- Attachments not processed.
- Only plain text body extracted.
- Works only for Gmail inbox (no custom labels yet).

---

## 👤 Author
**Pankaj Verma**  
Bachelor of Computer Applications (BCA), Adhunik Group of Institutions, Ghaziabad  
Focused on full‑stack development, automation, and real‑world project delivery.
