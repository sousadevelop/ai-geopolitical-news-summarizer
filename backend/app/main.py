from __future__ import annotations

from fastapi import Depends, FastAPI, Query
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.errors import ApiError, api_error_handler, unhandled_error_handler, validation_error_handler
from app.logging_config import configure_logging
from app.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    CacheStatus,
    CreateSourceRequest,
    HealthResponse,
    LatestNewsResponse,
    NewsAnalysis,
    Source,
    SourceListResponse,
)
from app.services.analysis_service import AnalysisService
from app.services.news_cache import NewsCache


configure_logging()

cache = NewsCache(path=settings.cache_path, max_items=settings.cache_max_items)
analysis_service = AnalysisService(cache=cache)


def get_cache() -> NewsCache:
    return cache


def get_analysis_service() -> AnalysisService:
    return analysis_service


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="API para coleta RSS, sumarizacao, analise de vies, NER e consulta de noticias geopoliticas analisadas.",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )
    application.add_exception_handler(ApiError, api_error_handler)
    application.add_exception_handler(RequestValidationError, validation_error_handler)
    application.add_exception_handler(Exception, unhandled_error_handler)
    register_routes(application)
    return application


def register_routes(application: FastAPI) -> None:
    @application.get("/health", response_model=HealthResponse, tags=["Health"])
    async def get_health(cache_store: NewsCache = Depends(get_cache)) -> HealthResponse:
        return HealthResponse(
            status="ok",
            version=settings.version,
            environment=settings.environment,
            cache=CacheStatus(backend=cache_store.backend, items=cache_store.count_news()),
        )

    @application.get("/sources", response_model=SourceListResponse, tags=["Sources"])
    async def list_sources(
        enabled: bool | None = None,
        region: str | None = None,
        cache_store: NewsCache = Depends(get_cache),
    ) -> SourceListResponse:
        return SourceListResponse(items=cache_store.list_sources(enabled=enabled, region=region))

    @application.post("/sources", response_model=Source, status_code=201, tags=["Sources"])
    async def create_source(
        request: CreateSourceRequest,
        cache_store: NewsCache = Depends(get_cache),
    ) -> Source:
        return cache_store.add_source(
            name=request.name,
            url=request.url,
            region=request.region,
            language=request.language,
            enabled=request.enabled,
        )

    @application.post("/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
    async def analyze_content(
        request: AnalyzeRequest,
        service: AnalysisService = Depends(get_analysis_service),
    ) -> AnalyzeResponse:
        return await service.analyze(request)

    @application.get("/news/latest", response_model=LatestNewsResponse, tags=["News"])
    async def list_latest_news(
        limit: int = Query(default=20, ge=1, le=100),
        region: str | None = None,
        source_id: str | None = None,
        entity: str | None = None,
        cache_store: NewsCache = Depends(get_cache),
    ) -> LatestNewsResponse:
        items = cache_store.latest(limit=limit, region=region, source_id=source_id, entity=entity)
        return LatestNewsResponse(items=items, total=len(items))

    @application.get("/news/{id}", response_model=NewsAnalysis, tags=["News"])
    async def get_news_by_id(id: str, cache_store: NewsCache = Depends(get_cache)) -> NewsAnalysis:
        item = cache_store.get_news(id)
        if not item:
            raise ApiError(code="not_found", message="Noticia nao encontrada.", status_code=404)
        return item


app = create_app()
