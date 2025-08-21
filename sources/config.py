import json
from pathlib import Path

def load_config(path: str = "config.json") -> dict:
    """Liest SMTP-Config aus config.json und fragt das Passwort nach, wenn leer/fehlt."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config-Datei nicht gefunden: {p.resolve()}")

    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"Ungültiges JSON in {p}: {e}") from e

    cfg = {
        "SMTP_HOST": data.get("SMTP_HOST", "smtps.udag.de"),
        "SMTP_PORT": int(data.get("SMTP_PORT", 587)),
        "SMTP_USER": data.get("SMTP_USER", ""),
        "SMTP_PASS": data.get("SMTP_PASS") or "",
        "SMTP_TO":   data.get("SMTP_TO", ""),
    }

    # Pflichtfelder prüfen
    missing = [k for k in ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_TO") if not cfg.get(k)]
    if missing:
        raise ValueError(f"Fehlende Pflichtfelder in {path}: {', '.join(missing)}")


    return cfg

