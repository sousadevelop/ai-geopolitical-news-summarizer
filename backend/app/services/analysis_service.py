from __future__ import annotations

from datetime import UTC, datetime
from urllib.parse import urlparse

from app.errors import ApiError
from app.models.schemas import AnalyzeRequest, AnalyzeResponse, GeopoliticalAnalysis, NewsAnalysis, SourceRef
from app.services.article_fetcher import ArticleContent, ArticleFetcher
from app.services.bias_analyzer import BiasAnalyzer
from app.services.ner_service import LightNerService
from app.services.news_cache import NewsCache
from app.services.rss_service import RssItem, RssService
from app.services.summarizer import LocalSummarizer


class AnalysisService:
    def __init__(
        self,
        cache: NewsCache,
        fetcher: ArticleFetcher | None = None,
        rss_service: RssService | None = None,
        summarizer: LocalSummarizer | None = None,
        bias_analyzer: BiasAnalyzer | None = None,
        ner_service: LightNerService | None = None,
    ) -> None:
        self.cache = cache
        self.fetcher = fetcher or ArticleFetcher()
        self.rss_service = rss_service or RssService(self.fetcher)
        self.summarizer = summarizer or LocalSummarizer()
        self.bias_analyzer = bias_analyzer or BiasAnalyzer()
        self.ner_service = ner_service or LightNerService()

    async def analyze(self, request: AnalyzeRequest) -> AnalyzeResponse:
        if request.input_type == "feed":
            return await self._analyze_feed(request)
        return await self._analyze_url(request)

    async def _analyze_url(self, request: AnalyzeRequest) -> AnalyzeResponse:
        cached = None if request.force_refresh else self.cache.get_by_url(request.url)
        if cached:
            return AnalyzeResponse(items=[cached], processed_count=0, cached_count=1)
        article = await self.fetcher.fetch_article(request.url)
        item = self._build_news(article, request.language, request.include_entities)
        self.cache.upsert_news(item)
        return AnalyzeResponse(items=[item], processed_count=1, cached_count=0)

    async def _analyze_feed(self, request: AnalyzeRequest) -> AnalyzeResponse:
        rss_items = await self.rss_service.fetch(request.url, max_items=request.max_items)
        source = self.cache.source_ref_for_url(request.url)
        if source is None and rss_items:
            source_name = rss_items[0].source_name or urlparse(request.url).hostname
            if source_name:
                source = SourceRef(
                    id=f"src_{self.cache.cache_key_for_url(request.url)[:12]}",
                    name=source_name,
                    url=request.url,
                )
        output: list[NewsAnalysis] = []
        cached_count = 0
        processed_count = 0
        for rss_item in rss_items:
            cached = None if request.force_refresh else self.cache.get_by_url(rss_item.url)
            if cached:
                if cached.source is None and source is not None:
                    cached = cached.model_copy(update={"source": source})
                    self.cache.upsert_news(cached)
                output.append(cached)
                cached_count += 1
                continue
            try:
                article = await self._article_from_rss_item(rss_item)
            except ApiError as exc:
                if exc.code in {"blocked_url", "invalid_url"}:
                    continue
                raise
            item = self._build_news(article, request.language, request.include_entities, source=source)
            self.cache.upsert_news(item)
            output.append(item)
            processed_count += 1
        return AnalyzeResponse(items=output, processed_count=processed_count, cached_count=cached_count)

    async def _article_from_rss_item(self, item: RssItem) -> ArticleContent:
        try:
            fetched = await self.fetcher.fetch_article(item.url)
            text = fetched.text or item.content
            return ArticleContent(
                title=fetched.title or item.title,
                url=fetched.url or item.url,
                text=text,
                published_at=fetched.published_at or item.published_at,
            )
        except ApiError as exc:
            if exc.code in {"blocked_url", "invalid_url"}:
                raise
            return ArticleContent(
                title=item.title,
                url=item.url,
                text=item.content,
                published_at=item.published_at,
            )
        except Exception:
            return ArticleContent(
                title=item.title,
                url=item.url,
                text=item.content,
                published_at=item.published_at,
            )

    def _build_news(
        self,
        article: ArticleContent,
        language: str,
        include_entities: bool,
        source=None,
    ) -> NewsAnalysis:
        text = article.text.strip()
        entities = self.ner_service.extract(text) if include_entities else []
        summary = self.summarizer.summarize(text, language=language, length="medium")
        key_points = self.summarizer.key_points(text, limit=4)
        actors = [entity.text for entity in entities if entity.label in {"ORG", "PERSON"}][:10]
        regions = [entity.text for entity in entities if entity.label in {"GPE", "LOC"}][:10]
        analysis = GeopoliticalAnalysis(
            key_points=key_points,
            actors=actors,
            regions=regions,
            risk_level=self._risk_level(text),
            context=self._context(text),
        )
        return NewsAnalysis(
            id=self.cache.cache_key_for_url(article.url),
            source=source,
            title=article.title,
            url=article.url,
            published_at=article.published_at,
            summary=summary,
            analysis=analysis,
            bias=self.bias_analyzer.analyze(text),
            entities=entities,
            processed_at=datetime.now(UTC),
        )

    def _risk_level(self, text: str) -> str:
        lowered = text.lower()
        high_terms = ("war", "guerra", "invasion", "invasao", "invasão", "nuclear", "missile", "míssil", "attack", "ataque")
        medium_terms = ("sanction", "sancao", "sanção", "troops", "tropas", "border", "fronteira", "ceasefire", "cessar-fogo")
        if any(term in lowered for term in high_terms):
            return "high"
        if any(term in lowered for term in medium_terms):
            return "medium"
        return "low" if text.strip() else "unknown"

    def _context(self, text: str) -> str | None:
        sentences = self.summarizer.key_points(text, limit=1)
        return sentences[0] if sentences else None
