from __future__ import annotations

from datetime import datetime
from typing import Literal
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator


def validate_http_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("URL invalida ou protocolo nao permitido.")
    return value


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CacheStatus(ApiModel):
    backend: Literal["memory", "json_file"]
    items: int = Field(ge=0)


class HealthResponse(ApiModel):
    status: Literal["ok"]
    version: str
    environment: str
    cache: CacheStatus


class Source(ApiModel):
    id: str
    name: str
    url: str
    region: str | None = None
    language: str | None = None
    enabled: bool
    created_at: datetime

    _validate_url = field_validator("url")(validate_http_url)


class CreateSourceRequest(ApiModel):
    name: str = Field(min_length=1, max_length=120)
    url: str
    region: str | None = Field(default=None, max_length=80)
    language: str | None = Field(default=None, min_length=2, max_length=8)
    enabled: bool = True

    _validate_url = field_validator("url")(validate_http_url)


class SourceListResponse(ApiModel):
    items: list[Source]


class AnalyzeRequest(ApiModel):
    input_type: Literal["url", "feed"]
    url: str
    language: str = Field(default="auto", min_length=2, max_length=8)
    max_items: int = Field(default=10, ge=1, le=20)
    include_entities: bool = True
    force_refresh: bool = False

    _validate_url = field_validator("url")(validate_http_url)


class SourceRef(ApiModel):
    id: str
    name: str
    url: str
    region: str | None = None

    _validate_url = field_validator("url")(validate_http_url)


class GeopoliticalAnalysis(ApiModel):
    key_points: list[str]
    actors: list[str]
    regions: list[str]
    risk_level: Literal["low", "medium", "high", "unknown"]
    context: str | None = None


class BiasReport(ApiModel):
    label: Literal["low", "moderate", "high", "unknown"]
    score: float = Field(ge=0, le=1)
    signals: list[str]


class Entity(ApiModel):
    text: str
    label: str
    confidence: float | None = Field(default=None, ge=0, le=1)


class NewsAnalysis(ApiModel):
    id: str
    source: SourceRef | None = None
    title: str
    url: str
    published_at: datetime | None = None
    summary: str
    analysis: GeopoliticalAnalysis
    bias: BiasReport
    entities: list[Entity]
    processed_at: datetime

    _validate_url = field_validator("url")(validate_http_url)


class AnalyzeResponse(ApiModel):
    items: list[NewsAnalysis]
    processed_count: int = Field(ge=0)
    cached_count: int = Field(default=0, ge=0)


class LatestNewsResponse(ApiModel):
    items: list[NewsAnalysis]
    total: int = Field(ge=0)

