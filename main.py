#!/usr/bin/env python3
"""Daily frontend jobs digest.

Fetches jobs from TheirStack, appends them to a Google Sheet, and emails an
HTML summary. Built to run as a GitHub Actions cron job.

Required environment variables (set these as GitHub Actions secrets):
  THEIRSTACK_TOKEN     TheirStack API bearer token
  SPREADSHEET_ID       Target Google Sheet ID (from the sheet URL)
  GOOGLE_CREDENTIALS   Full service account JSON, pasted as one secret
  EMAIL_ADDRESS        Gmail address used to send the digest
  EMAIL_APP_PASSWORD   Gmail app password (not your normal password)
  EMAIL_TO             Recipient (optional, defaults to EMAIL_ADDRESS)
"""

import os
import json
import smtplib
import datetime as dt
from email.mime.text import MIMEText

import requests
import gspread
from google.oauth2.service_account import Credentials

SHEET_NAME = "Jobs"

JOB_TITLES = [
    "frontend", "front-end", "front end",
    "react developer", "react engineer",
    "vue developer", "vue engineer",
    "ui engineer", "ui developer",
    "web engineer", "product engineer",
]
JOB_TITLES_NOT = [
    "backend", "back-end", "fullstack", "full-stack", "full stack",
    "python", "ruby", "java", "devops", "embedded",
    "data engineer", "machine learning", "android", "ios", "mobile",
]
COUNTRIES = [
    "GB", "DE", "NL", "IE", "SE", "DK", "NO", "FI",
    "PL", "PT", "ES", "FR", "BE", "AT", "CH", "AE",
]


def is_sponsor(job):
    desc = (job.get("long_description") or "").lower()
    return any(k in desc for k in ("sponsor", "visa", "relocation"))


def company_of(job):
    obj = job.get("company_object")
    if obj and obj.get("name"):
        return obj["name"]
    return job.get("company") or "Unknown"


def fetch_jobs(token):
    resp = requests.post(
        "https://api.theirstack.com/v1/jobs/search",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={
            "page": 0,
            "limit": 25,
            "posted_at_max_age_days": 1,
            "job_title_or": JOB_TITLES,
            "job_title_not": JOB_TITLES_NOT,
            "job_country_code_or": COUNTRIES,
            "order_by": [{"desc": True, "field": "date_posted"}],
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json().get("data", [])


def append_rows(spreadsheet_id, creds_json, jobs, today):
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=scopes)
    sheet = gspread.authorize(creds).open_by_key(spreadsheet_id).worksheet(SHEET_NAME)

    rows = [
        [
            today,
            j.get("job_title", ""),
            company_of(j),
            j.get("location", ""),
            j.get("job_country_code", ""),
            j.get("date_posted", ""),
            "Yes" if is_sponsor(j) else "No",
            j.get("url", ""),
            "New",
        ]
        for j in jobs
    ]
    if rows:
        sheet.append_rows(rows, value_input_option="USER_ENTERED")
    return len(rows)


def build_html(jobs, today, spreadsheet_id, sheet_status):
    sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
    sponsor_count = sum(1 for j in jobs if is_sponsor(j))

    rows_html = []
    for j in jobs:
        badge = (
            '<span style="background:#22c55e;color:#fff;padding:2px 6px;'
            'border-radius:3px;font-size:11px;font-weight:bold;">SPONSORS</span> '
            if is_sponsor(j) else ""
        )
        location = j.get("location") or j.get("job_country_code", "")
        rows_html.append(
            "<tr>"
            f'<td style="padding:8px;border-bottom:1px solid #eee;">{badge}{j.get("job_title", "")}</td>'
            f'<td style="padding:8px;border-bottom:1px solid #eee;">{company_of(j)}</td>'
            f'<td style="padding:8px;border-bottom:1px solid #eee;">{location}</td>'
            f'<td style="padding:8px;border-bottom:1px solid #eee;"><a href="{j.get("url", "#")}">Apply</a></td>'
            "</tr>"
        )

    return (
        '<div style="font-family:Arial,sans-serif;max-width:700px;margin:0 auto;">'
        f'<h2 style="color:#1e293b;">Frontend Jobs - {today}</h2>'
        f'<p style="color:#475569;">Found <strong>{len(jobs)}</strong> jobs posted today. '
        f'<strong style="color:#22c55e;">{sponsor_count}</strong> mention sponsorship.</p>'
        '<table style="width:100%;border-collapse:collapse;">'
        '<thead><tr style="background:#f1f5f9;">'
        '<th style="padding:10px;text-align:left;">Title</th>'
        '<th style="padding:10px;text-align:left;">Company</th>'
        '<th style="padding:10px;text-align:left;">Location</th>'
        '<th style="padding:10px;text-align:left;">Link</th>'
        "</tr></thead><tbody>" + "".join(rows_html) + "</tbody></table>"
        f'<p style="margin-top:16px;"><a href="{sheet_url}" '
        'style="background:#6366f1;color:#fff;padding:10px 20px;text-decoration:none;'
        'border-radius:5px;display:inline-block;">Open Full Tracker Sheet</a></p>'
        f'<p style="color:#94a3b8;font-size:12px;">Sheet status: {sheet_status}</p>'
        "</div>"
    )


def send_email(html, subject, sender, password, recipient):
    msg = MIMEText(html, "html")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, [recipient], msg.as_string())


def main():
    token = os.environ["THEIRSTACK_TOKEN"]
    spreadsheet_id = os.environ["SPREADSHEET_ID"]
    sender = os.environ["EMAIL_ADDRESS"]
    password = os.environ["EMAIL_APP_PASSWORD"]
    recipient = os.environ.get("EMAIL_TO") or sender

    raw = os.environ["GOOGLE_CREDENTIALS"]
    creds_json = open(raw).read() if os.path.isfile(raw) else raw

    today = dt.date.today().isoformat()
    jobs = fetch_jobs(token)

    try:
        added = append_rows(spreadsheet_id, creds_json, jobs, today)
        sheet_status = f"{added} rows added"
    except Exception as exc:
        sheet_status = f"sheet error: {exc}"
        print(sheet_status)

    sponsor_count = sum(1 for j in jobs if is_sponsor(j))
    html = build_html(jobs, today, spreadsheet_id, sheet_status)
    subject = f"Frontend Jobs {today}: {len(jobs)} found, {sponsor_count} sponsor"
    send_email(html, subject, sender, password, recipient)

    print(f"{len(jobs)} jobs found, {sheet_status}, {sponsor_count} sponsors, email sent")


if __name__ == "__main__":
    main()