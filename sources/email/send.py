# send_plain_smtp.py  —  einfache Mail ohne Exchange
import os, smtplib, ssl
from email.message import EmailMessage

# --- KONFIG (trag hier deinen Provider ein) ---
SMTP_HOST = os.getenv("SMTP_HOST", "smtps.udag.de")   # z.B. mail.gmx.net, smtp.strato.de, smtp.mailbox.org, smtp.gmail.com
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))       # 587 = STARTTLS, 465 = SSL
SMTP_USER = os.getenv("SMTP_USER", "test@jerz.eu")
SMTP_PASS = os.getenv("SMTP_PASS")
TO_ADDR    = os.getenv("SMTP_TO",  "jerz@teilnehmer.btz-rr.de")

SUBJECT = "Testnachricht an Christian(ohne Exchange)"
BODY    = "Hallo,\ndies ist eine mit Python verschickte E-Mail."

# --- MAIL OBJEKT ---
msg = EmailMessage()
msg["From"] = SMTP_USER
msg["To"] = TO_ADDR
msg["Subject"] = SUBJECT
msg.set_content(BODY)

ctx = ssl.create_default_context()

def send_via_starttls():
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as s:
        s.ehlo()
        if SMTP_PORT == 587:
            s.starttls(context=ctx)
            s.ehlo()
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)

def send_via_ssl():
    with smtplib.SMTP_SSL(SMTP_HOST, 465, context=ctx, timeout=30) as s:
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)


def send():
    try:
        if SMTP_PORT == 465:
            send_via_ssl()
        else:
            try:
                send_via_starttls()
            except smtplib.SMTPNotSupportedError:
                # Fallback: mancher Provider will Port 465/SSL
                send_via_ssl()
        print("OK: E-Mail wurde gesendet.")
    except smtplib.SMTPAuthenticationError as e:
        detail = e.smtp_error.decode() if isinstance(e.smtp_error, bytes) else str(e.smtp_error)
        print(f"Auth-Fehler ({e.smtp_code}): {detail}")
    except Exception as e:
        print("Fehler:", e)
