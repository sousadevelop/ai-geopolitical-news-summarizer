from __future__ import annotations

import re
import socket
from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime
from ipaddress import ip_address
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from app.config import settings
from app.errors import ApiError

_ALLOWED_SCHEMES = {"http", "https"}
_BLOCKED_HOSTNAMES = {"localhost", "localhost.localdomain"}
_REDIRECT_STATUS_CODES = {301, 302, 303, 307, 308}


@dataclass(frozen=True)
class ArticleContent:
    title: str
    url: str
    text: str
    published_at: datetime | None = None


def validate_external_url(url: str) -> str:
    normalized = url.strip()
    parsed = urlparse(normalized)
    host = parsed.hostname
    if parsed.scheme.lower() not in _ALLOWED_SCHEMES or not parsed.netloc or not host:
        raise ApiError(
            code="invalid_url",
            message="URL invalida ou protocolo nao permitido.",
            status_code=400,
            details={"field": "url"},
        )
    if parsed.username or parsed.password or _is_blocked_host(host):
        raise ApiError(
            code="blocked_url",
            message="URL aponta para host nao permitido.",
            status_code=400,
            details={"field": "url"},
        )
    return normalized


def _validate_fetch_target(url: str) -> str:
    normalized = validate_external_url(url)
    host = urlparse(normalized).hostname
    if host and _host_resolves_to_blocked_ip(host):
        raise ApiError(
            code="blocked_url",
            message="URL aponta para host nao permitido.",
            status_code=400,
            details={"field": "url"},
        )
    return normalized


def _is_blocked_host(host: str) -> bool:
    hostname = host.rstrip(".").lower()
    if hostname in _BLOCKED_HOSTNAMES or hostname.endswith(".localhost"):
        return True
    try:
        return _is_blocked_ip(ip_address(hostname))
    except ValueError:
        return False


def _host_resolves_to_blocked_ip(host: str) -> bool:
    hostname = host.rstrip(".").lower()
    if _is_blocked_host(hostname):
        return True
    try:
        addresses = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except socket.gaierror:
        return False
    for address in addresses:
        candidate = address[4][0]
        try:
            if _is_blocked_ip(ip_address(candidate)):
                return True
        except ValueError:
            continue
    return False


def _is_blocked_ip(candidate) -> bool:
    return (
        candidate.is_private
        or candidate.is_loopback
        or candidate.is_link_local
        or candidate.is_multicast
        or candidate.is_reserved
        or candidate.is_unspecified
    )


def _safe_url_details(url: str) -> dict[str, str]:
    parsed = urlparse(url)
    if parsed.scheme and parsed.hostname:
        return {"url": f"{parsed.scheme}://{parsed.hostname}"}
    return {"field": "url"}


class ArticleFetcher:
    def __init__(
        self,
        timeout_seconds: float | None = None,
        max_bytes: int | None = None,
        max_redirects: int | None = None,
    ) -> None:
        self.timeout_seconds = timeout_seconds or settings.request_timeout_seconds
        self.max_bytes = max_bytes or settings.request_max_bytes
        self.max_redirects = settings.request_max_redirects if max_redirects is None else max_redirects

    async def fetch_bytes(self, url: str) -> tuple[bytes, str, httpx.Headers]:
        current_url = _validate_fetch_target(url)
        headers = {
            "User-Agent": "geopolitical-news-summarizer/0.1",
            "Accept": "text/html,application/rss+xml,application/xml,text/xml;q=0.9,*/*;q=0.8",
        }
        try:
            async with httpx.AsyncClient(
                follow_redirects=False,
                timeout=httpx.Timeout(self.timeout_seconds),
                headers=headers,
            ) as client:
                for redirect_count in range(self.max_redirects + 1):
                    async with client.stream("GET", current_url) as response:
                        if response.status_code in _REDIRECT_STATUS_CODES:
                            location = response.headers.get("location")
                            if not location:
                                raise ApiError(
                                    code="fetch_failed",
                                    message="Redirecionamento externo sem destino.",
                                    status_code=502,
                                    details=_safe_url_details(current_url),
                                )
                            if redirect_count >= self.max_redirects:
                                raise ApiError(
                                    code="too_many_redirects",
                                    message="Conteudo externo excede o limite de redirecionamentos.",
                                    status_code=502,
                                    details={"max_redirects": self.max_redirects},
                                )
                            current_url = _validate_fetch_target(urljoin(str(response.url), location))
                            continue
                        response.raise_for_status()
                        content_length = response.headers.get("content-length")
                        if content_length and content_length.isdigit() and int(content_length) > self.max_bytes:
                            raise ApiError(
                                code="content_too_large",
                                message="Conteudo externo excede o limite permitido.",
                                status_code=502,
                                details={"max_bytes": self.max_bytes},
                            )
                        chunks: list[bytes] = []
                        total = 0
                        async for chunk in response.aiter_bytes():
                            total += len(chunk)
                            if total > self.max_bytes:
                                raise ApiError(
                                    code="content_too_large",
                                    message="Conteudo externo excede o limite permitido.",
                                    status_code=502,
                                    details={"max_bytes": self.max_bytes},
                                )
                            chunks.append(chunk)
                        final_url = _validate_fetch_target(str(response.url))
                        return b"".join(chunks), final_url, response.headers
                raise ApiError(
                    code="too_many_redirects",
                    message="Conteudo externo excede o limite de redirecionamentos.",
                    status_code=502,
                    details={"max_redirects": self.max_redirects},
                )
        except ApiError:
            raise
        except httpx.TimeoutException as exc:
            raise ApiError(
                code="fetch_timeout",
                message="Tempo limite excedido ao coletar conteudo externo.",
                status_code=502,
                details=_safe_url_details(url),
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise ApiError(
                code="fetch_failed",
                message="Falha ao coletar conteudo externo.",
                status_code=502,
                details={**_safe_url_details(url), "status_code": exc.response.status_code},
            ) from exc
        except httpx.HTTPError as exc:
            raise ApiError(
                code="fetch_failed",
                message="Falha ao coletar conteudo externo.",
                status_code=502,
                details=_safe_url_details(url),
            ) from exc

    async def fetch_article(self, url: str) -> ArticleContent:
        body, final_url, headers = await self.fetch_bytes(url)
        text = self._decode(body, headers.get("content-type"))
        soup = BeautifulSoup(text, "html.parser")
        title = self._extract_title(soup, final_url)
        published_at = self._extract_published_at(soup)
        article_text = self._extract_text(soup)
        if not article_text:
            raise ApiError(
                code="empty_content",
                message="Nao foi possivel extrair texto da URL informada.",
                status_code=502,
                details={"url": url},
            )
        return ArticleContent(
            title=title,
            url=final_url,
            text=article_text[:100_000],
            published_at=published_at,
        )

    def _decode(self, body: bytes, content_type: str | None) -> str:
        encoding = "utf-8"
        if content_type:
            match = re.search(r"charset=([^;]+)", content_type, re.IGNORECASE)
            if match:
                encoding = match.group(1).strip()
        return body.decode(encoding, errors="replace")

    def _extract_title(self, soup: BeautifulSoup, url: str) -> str:
        selectors = [
            ("meta", {"property": "og:title"}),
            ("meta", {"name": "twitter:title"}),
        ]
        for name, attrs in selectors:
            tag = soup.find(name, attrs=attrs)
            content = tag.get("content") if tag else None
            if content:
                return self._clean(content)
        for name in ("h1", "title"):
            tag = soup.find(name)
            if tag and tag.get_text(strip=True):
                return self._clean(tag.get_text(" ", strip=True))
        return url

    def _extract_published_at(self, soup: BeautifulSoup) -> datetime | None:
        candidates = [
            ("meta", {"property": "article:published_time"}),
            ("meta", {"name": "pubdate"}),
            ("meta", {"name": "date"}),
            ("time", {}),
        ]
        for name, attrs in candidates:
            tag = soup.find(name, attrs=attrs)
            if not tag:
                continue
            raw = tag.get("content") or tag.get("datetime") or tag.get_text(strip=True)
            parsed = self._parse_datetime(raw)
            if parsed:
                return parsed
        return None

    def _parse_datetime(self, raw: str | None) -> datetime | None:
        if not raw:
            return None
        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            try:
                return parsedate_to_datetime(raw)
            except (TypeError, ValueError):
                return None

    def _extract_text(self, soup: BeautifulSoup) -> str:
        for tag in soup(["script", "style", "noscript", "svg", "nav", "footer", "header", "form"]):
            tag.decompose()
        container = soup.find("article") or soup.find("main") or soup.body or soup
        paragraphs = [self._clean(node.get_text(" ", strip=True)) for node in container.find_all(["p", "li"])]
        long_paragraphs = [text for text in paragraphs if len(text) >= 40]
        if not long_paragraphs:
            fallback = self._clean(container.get_text(" ", strip=True))
            return fallback
        return "\n\n".join(long_paragraphs)

    def _clean(self, value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()
