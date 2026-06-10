from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app, get_analysis_service, get_cache
from app.services.analysis_service import AnalysisService
from app.services.article_fetcher import ArticleContent
from app.services.news_cache import NewsCache


FIXTURES_DIR = Path(__file__).parent / "fixtures"


class FixtureFetcher:
    async def fetch_bytes(self, url: str):
        body = (FIXTURES_DIR / "sample_feed.xml").read_bytes()
        return body, url, {}

    async def fetch_article(self, url: str) -> ArticleContent:
        if "border-talks" in url:
            return ArticleContent(
                title="Border talks resume in Geneva",
                url=url,
                text=(
                    "Diplomats from Brazil, France, and the United Nations discussed sanctions, "
                    "border security, and regional stability during a summit in Geneva."
                ),
            )
        return ArticleContent(
            title="Pacific alliance expands patrols",
            url=url,
            text=(
                "The Pacific alliance announced coordinated maritime patrols after missile tests "
                "near disputed waters and rising tension among regional powers."
            ),
        )


@pytest.fixture
def cache() -> NewsCache:
    return NewsCache(path=None, max_items=10)


@pytest.fixture
def client(cache: NewsCache) -> TestClient:
    app = create_app()
    service = AnalysisService(cache=cache, fetcher=FixtureFetcher())
    app.dependency_overrides[get_cache] = lambda: cache
    app.dependency_overrides[get_analysis_service] = lambda: service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
