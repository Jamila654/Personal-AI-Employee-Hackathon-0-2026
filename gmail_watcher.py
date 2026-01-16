import os
import time
import imaplib
import email
from email.header import decode_header

# ── CONFIG ────────────────────────────────────────────────
EMAIL_ADDRESS    = "nurjamila1@gmail.com"          # ← change
APP_PASSWORD     = "xjkhqsdaksykoami"           # ← your 16-char app password (no spaces!)
CHECK_INTERVAL   = 60                              # seconds between checks
VAULT_BASE       = os.path.dirname(os.path.abspath(__file__))
NEEDS_ACTION     = os.path.join(VAULT_BASE, "Needs_Action")
# You can also use "Email_Inbox" folder:
# EMAIL_INBOX    = os.path.join(VAULT_BASE, "Email_Inbox")

os.makedirs(NEEDS_ACTION, exist_ok=True)

# Track the last seen UID to avoid re-processing old emails
last_uid = None

def decode_subject(subject):
    decoded = decode_header(subject)[0][0]
    if isinstance(decoded, bytes):
        return decoded.decode(errors="replace")
    return decoded

def get_clean_filename(subject):
    """Turn subject into safe filename (remove bad chars)"""
    bad_chars = '<>:"/\\|?*'
    for c in bad_chars:
        subject = subject.replace(c, "")
    subject = subject.strip().replace(" ", "_")[:80]  # limit length
    if not subject:
        subject = "email_no_subject"
    return f"{subject}.md"

def process_email(msg):
    # From
    from_ = msg.get("From", "Unknown")
    # Subject
    subject = decode_subject(msg["Subject"] or "(No Subject)")
    # Date
    date_str = msg.get("Date", time.strftime("%Y-%m-%d %H:%M"))
    # Body (simple text version)
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode(errors="replace")
                break
    else:
        body = msg.get_payload(decode=True).decode(errors="replace")

    # Short preview
    preview = body.strip()[:200].replace("\n", " ") + "..." if len(body) > 200 else body.strip()

    # Markdown content
    content = f"""---
from: {from_}
date: {date_str}
subject: {subject}
---

# {subject}

**From:** {from_}  
**Date:** {date_str}

{preview}

[Full email in Gmail]
"""

    # Save to Needs_Action
    filename = get_clean_filename(subject)
    path = os.path.join(NEEDS_ACTION, filename)

    # Avoid overwriting if same subject (you can improve with UID later)
    if os.path.exists(path):
        print(f"Skipping existing note: {filename}")
        return

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Created Obsidian note: {filename}")

def check_gmail():
    global last_uid

    print("Starting Gmail check...")

    try:
        print("Connecting to imap.gmail.com...")
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        print("Connection successful.")

        print("Attempting login...")
        mail.login(EMAIL_ADDRESS, APP_PASSWORD)
        print("Login successful!")

        print("Selecting inbox...")
        mail.select("inbox")
        print("Inbox selected.")

        status, data = mail.uid("search", None, "ALL")
        if status != "OK":
            print("Search failed:", status)
            return

        uids = data[0].split()
        print(f"Found {len(uids)} emails in inbox")

        if not uids:
            print("No emails found")
            return

        newest_uid = uids[-1]
        print(f"Newest UID: {newest_uid.decode()}")

        if last_uid is None:
            last_uid = newest_uid
            print("First run: remembering newest UID, no processing yet")
            return

        if newest_uid == last_uid:
            print("No new email since last check")
            return

        print(f"New email! Previous last: {last_uid.decode() if last_uid else 'None'}, now: {newest_uid.decode()}")

        status, msg_data = mail.uid("fetch", newest_uid, "(RFC822)")
        if status == "OK":
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            process_email(msg)
        else:
            print("Fetch failed:", status)

        last_uid = newest_uid

        mail.logout()
        print("Logged out cleanly")

    except Exception as e:
        print(f"ERROR during Gmail check: {type(e).__name__}: {str(e)}")
        if "AUTHENTICATIONFAILED" in str(e):
            print("→ This usually means the app password is wrong, expired, revoked, or 2FA settings changed.")
            print("→ Double-check: generate a NEW app password at https://myaccount.google.com/apppasswords")
        elif "getaddrinfo" in str(e) or "Connection" in str(e):
            print("→ Network issue – check your internet")
        elif "SSL" in str(e):
            print("→ SSL/TLS problem – rare, but try updating Python if very old")
# ── MAIN LOOP ─────────────────────────────────────────────
print(f"Monitoring Gmail inbox for {EMAIL_ADDRESS} every {CHECK_INTERVAL}s ...")

while True:
    check_gmail()
    time.sleep(CHECK_INTERVAL)