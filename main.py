from sources.config import load_config
from sources.email.send import send
from getpass import getpass

cfg = load_config("config.json")

# Passwort ggf. sicher nachfragen
if not cfg["SMTP_PASS"]:
    cfg["SMTP_PASS"] = getpass("SMTP-Passwort: ")

print('huhu')

print(f"SMTP -> {cfg['SMTP_USER']}@{cfg['SMTP_HOST']}:{cfg['SMTP_PORT']}  TO={cfg['SMTP_TO']}")

send()