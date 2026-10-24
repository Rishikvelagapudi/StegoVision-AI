"""Runtime configuration, read from environment variables (see .env.example).

Settings are read on every call so tests can override them with monkeypatch.
"""
import os
from dataclasses import dataclass


def _int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    max_upload_bytes: int
    max_dimension: int
    min_dimension: int
    max_pixels: int
    max_payload_bytes: int
    ttl_seconds: int
    allowed_origins: tuple
    model_path: str


def get_settings() -> Settings:
    origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    return Settings(
        max_upload_bytes=_int("MAX_UPLOAD_MB", 15) * 1024 * 1024,
        max_dimension=_int("MAX_DIMENSION", 8000),
        min_dimension=_int("MIN_DIMENSION", 8),
        max_pixels=_int("MAX_PIXELS", 40_000_000),
        max_payload_bytes=_int("MAX_PAYLOAD_MB", 10) * 1024 * 1024,
        ttl_seconds=_int("RESULT_TTL_SECONDS", 3600),
        allowed_origins=tuple(o.strip() for o in origins.split(",") if o.strip()),
        model_path=os.environ.get("STEGO_MODEL_PATH", "").strip(),
    )
