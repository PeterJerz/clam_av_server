import os, smtplib, ssl
from email.message import EmailMessage
from config import Config

ctx = ssl.create_default_context()

def send_via_starttls(mail, cfg):
    print('sending via starttls')
    with smtplib.SMTP(cfg.host, cfg.port, timeout=30) as s:
        s.ehlo()
        if cfg.port == 587:
            s.starttls(context=ctx)
            s.ehlo()
        s.login(cfg.user, cfg.password)
        s.send_message(mail)

def send_via_ssl(mail, cfg):
    print('sending via ssl')
    with smtplib.SMTP_SSL(cfg.host, 465, context=ctx, timeout=30) as s:
        s.login(cfg.user, cfg.password)
        s.send_message(mail)


def send(mail, cfg):
    print('sending')
    try:
        if cfg.port == 465:
            send_via_ssl(mail, cfg)
        else:
            try:
                send_via_starttls(mail, cfg)
            except smtplib.SMTPNotSupportedError:
                # Fallback: mancher Provider will Port 465/SSL
                send_via_ssl(mail, cfg)
        print("OK: E-Mail wurde gesendet.")
    except smtplib.SMTPAuthenticationError as e:
        detail = e.smtp_error.decode() if isinstance(e.smtp_error, bytes) else str(e.smtp_error)
        print(f"Auth-Fehler ({e.smtp_code}): {detail}")
    except Exception as e:
        print("Fehler:", e)
