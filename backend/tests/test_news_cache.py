from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.models.schemas import BiasReport, Entity, GeopoliticalAnalysis, NewsAnalysis, SourceRef
from app.services.news_cache import NewsCache


def make_news(
    url: str,
    title: str,
    processed_at: datetime,
    source: SourceRef | None = None,
    entities: list[Entity] | None = None,
) -> NewsAnalysis:
    return NewsAnalysis(
        id=NewsCache(path=None).cache_key_for_url(url),
        source=source,
        title=title,
        url=url,
        published_at=None,
        summary=f"Summary for {title}",
        analysis=GeopoliticalAnalysis(
            key_points=[title],
            actors=[],
            regions=[],
            risk_level="low",
            context=None,
        ),
        bias=BiasReport(label="low", score=0.1, signals=[]),
        entities=entities or [],
        processed_at=processed_at,
    )


def test_cache_adds_lists_fetches_by_url_and_respects_limit() -> None:
    cache = NewsCache(path=None, max_items=2)
    now = datetime.now(UTC)
    first = make_news("https://news.example.com/1", "First", now - timedelta(minutes=3))
    second = make_news("https://news.example.com/2", "Second", now - timedelta(minutes=2))
    third = make_news("https://news.example.com/3", "Third", now - timedelta(minutes=1))

    cache.upsert_news(first)
    cache.upsert_news(second)
    cache.upsert_news(third)

    assert cache.count_news() == 2
    assert cache.get_by_url(first.url) is None
    assert cache.get_by_url(third.url) == third
    assert [item.title for item in cache.latest(limit=10)] == ["Third", "Second"]


def test_cache_filters_latest_news_by_source_region_and_entity() -> None:
    cache = NewsCache(path=None, max_items=5)
    source = SourceRef(
        id="src_global",
        name="Global Feed",
        url="https://feeds.example.com/global.xml",
        region="global",
    )
    now = datetime.now(UTC)
    cache.upsert_news(
        make_news(
            "https://news.example.com/un",
            "UN diplomacy",
            now,
            source=source,
            entities=[Entity(text="United Nations", label="ORG", confidence=0.9)],
        )
    )
    cache.upsert_news(make_news("https://news.example.com/local", "Local economy", now - timedelta(minutes=1)))

    assert [item.title for item in cache.latest(limit=10, region="global")] == ["UN diplomacy"]
    assert [item.title for item in cache.latest(limit=10, source_id="src_global")] == ["UN diplomacy"]
    assert [item.title for item in cache.latest(limit=10, entity="nations")] == ["UN diplomacy"]
