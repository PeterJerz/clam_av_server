import json
from pathlib import Path

class Config:
    def __init__(self):
        self.host = ''
        self.port = ''
        self.user = ''
        self.password = ''
        self.to = ''

    def load(self, path: str = "config.json"):
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Config-Datei nicht gefunden: {p.resolve()}")

        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise ValueError(f"Ungültiges JSON in {p}: {e}") from e

        self.host = data.get("SMTP_HOST", "smtps.udag.de")
        self.port = int(data.get("SMTP_PORT", 587))
        self.user = data.get("SMTP_USER", "")
        self.password = data.get("SMTP_PASS") or ""
        self.to =   data.get("SMTP_TO", "")

