from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from time import struct_time
from urllib.parse import urljoin

import feedparser
from bs4 import BeautifulSoup

from app.config import settings
from app.errors import ApiError
from app.services.article_fetcher import ArticleFetcher, validate_external_url


@dataclass(frozen=True)
class RssItem:
    title: str
    url: str
    content: str
    published_at: datetime | None
    language: str | None


class RssService:
    def __init__(self, fetcher: ArticleFetcher | None = None) -> None:
        self.fetcher = fetcher or ArticleFetcher()

    async def fetch(self, feed_url: str, max_items: int = 10, max_chars: int | None = None) -> list[RssItem]:
        validate_external_url(feed_url)
        body, final_url, _ = await self.fetcher.fetch_bytes(feed_url)
        parsed = feedparser.parse(body)
        if parsed.bozo and not parsed.entries:
            raise ApiError(
                code="invalid_feed",
                message="Feed RSS invalido ou sem entradas legiveis.",
                status_code=502,
                details={"url": feed_url},
            )
        limit = min(max_items, 20)
        char_limit = max_chars or settings.rss_entry_max_chars
        feed_language = self._normalize_language(parsed.feed.get("language"))
        items: list[RssItem] = []
        for entry in parsed.entries[:limit]:
            link = entry.get("link") or entry.get("id") or final_url
            item_url = urljoin(final_url, link)
            try:
                validate_external_url(item_url)
            except ApiError:
                continue
            content = self._entry_content(entry)
            title = self._clean(entry.get("title") or item_url)
            items.append(
                RssItem(
                    title=title,
                    url=item_url,
                    content=content[:char_limit],
                    published_at=self._entry_datetime(entry),
                    language=self._normalize_language(entry.get("language")) or feed_language,
                )
            )
        return items

    def _entry_content(self, entry: feedparser.FeedParserDict) -> str:
        if entry.get("content"):
            raw = " ".join(part.get("value", "") for part in entry.content)
        else:
            raw = entry.get("summary") or entry.get("description") or ""
        return self._strip_html(raw)

    def _entry_datetime(self, entry: feedparser.FeedParserDict) -> datetime | None:
        for key in ("published_parsed", "updated_parsed", "created_parsed"):
            value = entry.get(key)
            if isinstance(value, struct_time):
                return datetime(*value[:6], tzinfo=UTC)
        for key in ("published", "updated", "created"):
            raw = entry.get(key)
            if not raw:
                continue
            try:
                return parsedate_to_datetime(raw)
            except (TypeError, ValueError):
                continue
        return None

    def _strip_html(self, value: str) -> str:
        soup = BeautifulSoup(value, "html.parser")
        return self._clean(soup.get_text(" ", strip=True))

    def _clean(self, value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()

    def _normalize_language(self, value: str | None) -> str | None:
        if not value:
            return None
        value = value.strip().lower()
        if not value:
            return None
        return value.split("-")[0]

