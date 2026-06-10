from __future__ import annotations

import json
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

from app.config import settings
from app.errors import ApiError
from app.models.schemas import NewsAnalysis, Source


class NewsCache:
    def __init__(self, path: Path | None = None, max_items: int | None = None) -> None:
        self.path = path
        self.max_items = max_items or settings.cache_max_items
        self._news: dict[str, NewsAnalysis] = {}
        self._sources: dict[str, Source] = {}
        self._load()

    @property
    def backend(self) -> str:
        return "json_file" if self.path else "memory"

    def count_news(self) -> int:
        return len(self._news)

    def cache_key_for_url(self, url: str) -> str:
        return sha256(url.strip().lower().encode("utf-8")).hexdigest()[:24]

    def get_by_url(self, url: str) -> NewsAnalysis | None:
        return self._news.get(self.cache_key_for_url(url))

    def get_news(self, news_id: str) -> NewsAnalysis | None:
        return self._news.get(news_id)

    def upsert_news(self, item: NewsAnalysis) -> NewsAnalysis:
        self._news[item.id] = item
        self._trim_news()
        self._save()
        return item

    def latest(
        self,
        limit: int,
        region: str | None = None,
        source_id: str | None = None,
        entity: str | None = None,
    ) -> list[NewsAnalysis]:
        items = list(self._news.values())
        if region:
            items = [item for item in items if item.source and item.source.region == region]
        if source_id:
            items = [item for item in items if item.source and item.source.id == source_id]
        if entity:
            needle = entity.lower()
            items = [
                item
                for item in items
                if any(needle in candidate.text.lower() for candidate in item.entities)
            ]
        return sorted(items, key=lambda item: item.processed_at, reverse=True)[:limit]

    def list_sources(self, enabled: bool | None = None, region: str | None = None) -> list[Source]:
        items = list(self._sources.values())
        if enabled is not None:
            items = [item for item in items if item.enabled is enabled]
        if region:
            items = [item for item in items if item.region == region]
        return sorted(items, key=lambda item: item.created_at)

    def add_source(self, name: str, url: str, region: str | None, language: str | None, enabled: bool) -> Source:
        normalized_url = url.strip()
        if any(source.url.strip().lower() == normalized_url.lower() for source in self._sources.values()):
            raise ApiError(
                code="source_conflict",
                message="Fonte ja cadastrada.",
                status_code=409,
                details={"field": "url"},
            )
        source = Source(
            id=f"src_{self.cache_key_for_url(normalized_url)[:12]}",
            name=name,
            url=normalized_url,
            region=region,
            language=language,
            enabled=enabled,
            created_at=datetime.now(UTC),
        )
        self._sources[source.id] = source
        self._save()
        return source

    def source_ref_for_url(self, url: str):
        from app.models.schemas import SourceRef

        normalized = url.strip().lower()
        for source in self._sources.values():
            if source.url.strip().lower() == normalized:
                return SourceRef(id=source.id, name=source.name, url=source.url, region=source.region)
        return None

    def _trim_news(self) -> None:
        if len(self._news) <= self.max_items:
            return
        items = sorted(self._news.values(), key=lambda item: item.processed_at, reverse=True)
        self._news = {item.id: item for item in items[: self.max_items]}

    def _load(self) -> None:
        if not self.path or not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self._news = {
                raw["id"]: NewsAnalysis.model_validate(raw)
                for raw in data.get("news", [])
                if isinstance(raw, dict) and raw.get("id")
            }
            self._sources = {
                raw["id"]: Source.model_validate(raw)
                for raw in data.get("sources", [])
                if isinstance(raw, dict) and raw.get("id")
            }
        except (OSError, json.JSONDecodeError, ValueError):
            self._news = {}
            self._sources = {}

    def _save(self) -> None:
        if not self.path:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "news": [item.model_dump(mode="json") for item in self._news.values()],
            "sources": [item.model_dump(mode="json") for item in self._sources.values()],
        }
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

