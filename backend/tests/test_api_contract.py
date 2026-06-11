from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

import pytest

from app.errors import ApiError
from app.models.schemas import AnalyzeRequest
from app.models.schemas import BiasReport, GeopoliticalAnalysis, NewsAnalysis
from app.services.analysis_service import AnalysisService
from app.services.article_fetcher import ArticleContent
from app.services.news_cache import NewsCache
from app.services.rss_service import RssItem


def make_news(news_id: str, title: str, processed_at: datetime | None = None) -> NewsAnalysis:
    return NewsAnalysis(
        id=news_id,
        title=title,
        url=f"https://news.example.com/{news_id}",
        published_at=None,
        summary=f"Summary for {title}",
        analysis=GeopoliticalAnalysis(
            key_points=[f"Point for {title}"],
            actors=["United Nations"],
            regions=["Geneva"],
            risk_level="medium",
            context="Diplomatic context.",
        ),
        bias=BiasReport(label="low", score=0.2, signals=[]),
        entities=[],
        processed_at=processed_at or datetime.now(UTC),
    )


def test_health_returns_cache_status(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["version"]
    assert payload["environment"]
    assert payload["cache"] == {"backend": "memory", "items": 0}


def test_analyze_rejects_disallowed_url_protocol(client: TestClient) -> None:
    response = client.post(
        "/analyze",
        json={"input_type": "url", "url": "file:///etc/passwd", "language": "pt"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": "invalid_url",
        "message": "URL invalida ou protocolo nao permitido.",
        "details": {"field": "url"},
    }


def test_analyze_feed_uses_fixture_and_respects_max_items(client: TestClient) -> None:
    response = client.post(
        "/analyze",
        json={
            "input_type": "feed",
            "url": "https://feeds.example.com/geopolitics.xml",
            "language": "en",
            "max_items": 1,
            "include_entities": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["processed_count"] == 1
    assert payload["cached_count"] == 0
    assert len(payload["items"]) == 1
    assert payload["items"][0]["title"] == "Border talks resume in Geneva"


def test_analyze_feed_builds_source_ref_from_feed_title(client: TestClient, cache: NewsCache) -> None:
    feed_url = "https://feeds.example.com/geopolitics.xml"

    response = client.post(
        "/analyze",
        json={"input_type": "feed", "url": feed_url, "max_items": 1},
    )

    assert response.status_code == 200
    source = response.json()["items"][0]["source"]
    assert source == {
        "id": f"src_{cache.cache_key_for_url(feed_url)[:12]}",
        "name": "Fixture Geopolitical Feed",
        "url": feed_url,
        "region": None,
    }


def test_analyze_feed_backfills_source_on_cached_items(client: TestClient, cache: NewsCache) -> None:
    feed_url = "https://feeds.example.com/geopolitics.xml"

    first = client.post(
        "/analyze",
        json={"input_type": "feed", "url": feed_url, "max_items": 1},
    )
    cached = cache.get_by_url(first.json()["items"][0]["url"])
    assert cached is not None
    cache.upsert_news(cached.model_copy(update={"source": None}))

    second = client.post(
        "/analyze",
        json={"input_type": "feed", "url": feed_url, "max_items": 1},
    )

    assert second.status_code == 200
    payload = second.json()
    assert payload["processed_count"] == 0
    assert payload["cached_count"] == 1
    assert payload["items"][0]["source"]["name"] == "Fixture Geopolitical Feed"


@pytest.mark.asyncio
async def test_analyze_feed_skips_rss_items_blocked_by_url_policy(cache: NewsCache) -> None:
    class BlockedFetcher:
        async def fetch_article(self, url: str) -> ArticleContent:
            raise ApiError(
                code="blocked_url",
                message="URL aponta para host nao permitido.",
                status_code=400,
                details={"field": "url"},
            )

    class SingleItemRssService:
        async def fetch(self, feed_url: str, max_items: int = 10):
            return [
                RssItem(
                    title="Internal host should be skipped",
                    url="http://127.0.0.1/private",
                    content="Fallback content should not be persisted for blocked URLs.",
                    published_at=None,
                    language="en",
                )
            ]

    service = AnalysisService(
        cache=cache,
        fetcher=BlockedFetcher(),
        rss_service=SingleItemRssService(),
    )

    response = await service.analyze(
        AnalyzeRequest(
            input_type="feed",
            url="https://feeds.example.com/geopolitics.xml",
            max_items=1,
        )
    )

    assert response.processed_count == 0
    assert response.cached_count == 0
    assert response.items == []
    assert cache.count_news() == 0


def test_latest_news_returns_envelope_and_missing_news_is_structured_404(
    client: TestClient,
    cache: NewsCache,
) -> None:
    cache.upsert_news(make_news("older", "Older story", datetime.now(UTC) - timedelta(hours=1)))
    cache.upsert_news(make_news("newer", "Newer story", datetime.now(UTC)))

    latest_response = client.get("/news/latest", params={"limit": 1})
    assert latest_response.status_code == 200
    latest_payload = latest_response.json()
    assert latest_payload["total"] == 1
    assert [item["id"] for item in latest_payload["items"]] == ["newer"]

    missing_response = client.get("/news/does-not-exist")
    assert missing_response.status_code == 404
    assert missing_response.json() == {"code": "not_found", "message": "Noticia nao encontrada."}
