import os
from email.message import EmailMessage

from config import Config
from send_mail import send
from getpass import getpass


SUBJECT = "Testnachricht"
BODY    = "Hallo,\ndies ist eine mit Python verschickte E-Mail."

cfg = Config()
cfg.load("config.json")

pw = os.getenv("somep")

cfg.password = pw or getpass("SMTP-Passwort: ")

# --- MAIL OBJEKT ---
mail = EmailMessage()
mail["From"] = cfg.user
mail["To"] = cfg.to
mail["Subject"] = SUBJECT
mail.set_content(BODY)

print('sending')

send(mail, cfg)