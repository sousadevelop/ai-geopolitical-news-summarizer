from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _get_int(name: str, default: int, minimum: int | None = None) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    if minimum is not None:
        return max(minimum, value)
    return value


def _get_float(name: str, default: float, minimum: float | None = None) -> float:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    if minimum is not None:
        return max(minimum, value)
    return value


def _get_cors_origins(environment: str) -> list[str]:
    raw = os.getenv("CORS_ORIGINS")
    if raw is None or raw.strip() == "":
        if environment.lower() == "development":
            return [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:5173",
                "http://127.0.0.1:5173",
            ]
        return []
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    return origins


@dataclass(frozen=True)
class Settings:
    app_name: str = "Sumarizador de Noticias Geopoliticas API"
    version: str = "0.1.0"
    environment: str = os.getenv("ENVIRONMENT") or os.getenv("APP_ENV", "development")
    port: int = _get_int("PORT", 8000, minimum=1)
    cors_origins: list[str] = None  # type: ignore[assignment]
    cache_path: Path | None = None
    cache_max_items: int = _get_int("CACHE_MAX_ITEMS", 500, minimum=1)
    request_timeout_seconds: float = _get_float("REQUEST_TIMEOUT_SECONDS", 10.0, minimum=0.1)
    request_max_bytes: int = _get_int("REQUEST_MAX_BYTES", 2_000_000, minimum=1024)
    request_max_redirects: int = _get_int("REQUEST_MAX_REDIRECTS", 5, minimum=0)
    rss_entry_max_chars: int = _get_int("RSS_ENTRY_MAX_CHARS", 20_000, minimum=1000)
    summary_provider: str = os.getenv("SUMMARY_PROVIDER", "local_extractive")

    def __post_init__(self) -> None:
        object.__setattr__(self, "cors_origins", _get_cors_origins(self.environment))
        cache_path = os.getenv("CACHE_PATH")
        if cache_path:
            object.__setattr__(self, "cache_path", Path(cache_path))


settings = Settings()
