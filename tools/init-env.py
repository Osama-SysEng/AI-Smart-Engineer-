from __future__ import annotations

import secrets
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[1] / ".env.example"
TARGET = Path(__file__).resolve().parents[1] / ".env"

if TARGET.exists():
    raise SystemExit(".env already exists; refusing to overwrite it")

text = TEMPLATE.read_text(encoding="utf-8")
text = text.replace("replace-with-at-least-48-random-characters", secrets.token_urlsafe(48))
text = text.replace("replace-with-local-password", secrets.token_urlsafe(24))
text = text.replace("SAP_MOCK_MODE=true", "SAP_MOCK_MODE=true")
TARGET.write_text(text, encoding="utf-8")
TARGET.chmod(0o600)
print(f"created {TARGET} with development-only random values; keep it out of Git and ZIP")
