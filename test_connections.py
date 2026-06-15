"""Smoke test for Google Sheets and Gmail connections.

Run with: python test_connections.py

Required env vars (must match main.py names, not the old .env names):
  GOOGLE_CREDENTIALS   service account JSON string
  SPREADSHEET_ID       sheet ID from the URL
  EMAIL_ADDRESS        your Gmail address
  EMAIL_APP_PASSWORD   Gmail app password (16-char code from Google Account)
  EMAIL_TO             recipient (optional, defaults to EMAIL_ADDRESS)
"""

import os
import datetime as dt
from dotenv import load_dotenv
from main import append_rows, send_email, build_html

load_dotenv()

DUMMY_JOB = {
    "job_title": "Test: AI Engineer",
    "company": "Smoke Test Co",
    "location": "Lagos, Nigeria",
    "job_country_code": "NG",
    "date_posted": dt.date.today().isoformat(),
    "long_description": "This is a test row. Safe to delete.",
    "url": "https://example.com/test-job",
}


def test_sheets():
    spreadsheet_id = os.environ["SPREADSHEET_ID"]
    raw = os.environ["GOOGLE_CREDENTIALS"]
    creds_json = open(raw).read() if os.path.isfile(raw) else raw
    today = dt.date.today().isoformat()

    print("Testing Google Sheets connection...")
    added = append_rows(spreadsheet_id, creds_json, [DUMMY_JOB], today)
    print(f"  ✓ Wrote {added} row to sheet. Open your sheet and confirm it's there.")


def test_email():
    sender = os.environ["EMAIL_ADDRESS"]
    password = os.environ["EMAIL_APP_PASSWORD"]
    recipient = os.environ.get("EMAIL_TO") or sender
    spreadsheet_id = os.environ["SPREADSHEET_ID"]
    today = dt.date.today().isoformat()

    print("Testing Gmail connection...")
    html = build_html([DUMMY_JOB], today, spreadsheet_id, "smoke test")
    send_email(html, f"[TEST] Jobber AI smoke test {today}", sender, password, recipient)
    print(f"  ✓ Email sent to {recipient}. Check your inbox.")


if __name__ == "__main__":
    try:
        test_sheets()
    except Exception as e:
        print(f"  ✗ Sheets failed: {e}")

    try:
        test_email()
    except Exception as e:
        print(f"  ✗ Email failed: {e}")
