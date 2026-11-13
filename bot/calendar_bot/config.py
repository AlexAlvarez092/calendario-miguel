from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

BOT_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    telegram_token: str
    allowed_user_id: int
    gemini_api_key: str
    repo_dir: Path
    gemini_model: str = "gemini-3.5-flash-lite"
    healthcheck_url: Optional[str] = None

    @property
    def events_path(self) -> Path:
        return self.repo_dir / "data" / "events.json"


def load_env_file(path: Path) -> None:
    """Load KEY=VALUE lines into the environment without overriding existing values."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def load_settings(env_file: Optional[Path] = None) -> Settings:
    load_env_file(env_file or BOT_DIR / ".env")
    return Settings(
        telegram_token=os.environ["TELEGRAM_BOT_TOKEN"],
        allowed_user_id=int(os.environ["TELEGRAM_ALLOWED_ID"]),
        gemini_api_key=os.environ["GEMINI_API_KEY"],
        repo_dir=Path(os.environ["REPO_DIR"]).expanduser(),
        gemini_model=os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite"),
        healthcheck_url=os.environ.get("HEALTHCHECK_URL") or None,
    )
