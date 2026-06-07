import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from config import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASS, TO_EMAIL, DEBUG


def send_email(subject: str, html: str) -> bool:
    if not SMTP_USER or not SMTP_PASS or not TO_EMAIL:
        print("[email] ERROR: SMTP not configured (SMTP_USER, SMTP_PASS, TO_EMAIL)")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = SMTP_USER
    msg["To"] = TO_EMAIL
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30) as s:
            s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(SMTP_USER, [TO_EMAIL], msg.as_string())
        print("[email] Sent successfully")
        return True
    except Exception as e:
        print(f"[email] Failed: {e}")
        return False
