# Documentação da API

Contrato canônico: [`../openapi.yaml`](../openapi.yaml). Este arquivo traz exemplos curtos e notas de consumo.

Base local: `http://localhost:8000`

![Swagger UI da API GeoPolaris](assets/screenshots/swagger-api.png)

## Autenticação

A v1 não exige autenticação. Se a API for exposta publicamente, proteja os endpoints que disparam downloads externos com autenticação, rate limit ou uma camada de proxy.

## Erros

Erros conhecidos retornam:

```json
{
  "code": "invalid_url",
  "message": "URL inválida ou protocolo não permitido.",
  "details": {
    "field": "url"
  }
}
```

Exceções inesperadas retornam `internal_error` sem stack trace.

## GET /health

Verifica se a API está disponível.

Resposta `200`:

```json
{
  "status": "ok",
  "version": "0.1.0",
  "environment": "development",
  "cache": {
    "backend": "json_file",
    "items": 12
  }
}
```

## GET /sources

Lista fontes RSS configuradas.

Query params:

- `enabled`: boolean opcional.
- `region`: string opcional.

Resposta `200`:

```json
{
  "items": [
    {
      "id": "src_abc123",
      "name": "Example Feed",
      "url": "https://example.com/rss.xml",
      "region": "global",
      "language": "en",
      "enabled": true,
      "created_at": "2026-06-09T20:00:00Z"
    }
  ]
}
```

## POST /sources

Adiciona uma fonte RSS ao cache local.

![Cadastro de fonte RSS](assets/screenshots/sources-rss.png)

Request:

```json
{
  "name": "Example Feed",
  "url": "https://example.com/rss.xml",
  "region": "global",
  "language": "en",
  "enabled": true
}
```

Resposta `201`: objeto `Source`.

Erros comuns:

- `400 invalid_url`: URL inválida ou protocolo não permitido.
- `409 source_conflict`: fonte já cadastrada.
- `422 validation_error`: payload fora do schema.

## POST /analyze

Analisa uma URL de notícia ou um feed RSS. Para `input_type: "url"`, retorna uma análise. Para `input_type: "feed"`, processa até `max_items`.

`language` indica o idioma preferencial da análise. Ele não traduz o conteúdo na v1. A v1 usa processamento local, sem integração com LLM.

URLs diretas podem ser bloqueadas pelo site durante a coleta. Prefira RSS quando disponível, por exemplo `https://feeds.bbci.co.uk/news/world/rss.xml`.

![Resultado de análise por feed RSS](assets/screenshots/analyze-rss-result.png)

Request para notícia:

```json
{
  "input_type": "url",
  "url": "https://example.com/article",
  "language": "pt",
  "include_entities": true,
  "force_refresh": false
}
```

Request para feed:

```json
{
  "input_type": "feed",
  "url": "https://example.com/rss.xml",
  "language": "en",
  "max_items": 5,
  "include_entities": true
}
```

Resposta `200`:

```json
{
  "items": [
    {
      "id": "b4e8d6a2f9c1",
      "source": {
        "id": "src_abc123",
        "name": "Example Feed",
        "url": "https://example.com/rss.xml",
        "region": "global"
      },
      "title": "Regional powers meet for ceasefire talks",
      "url": "https://example.com/article",
      "published_at": "2026-06-09T18:30:00Z",
      "summary": "Representantes regionais se reuniram para discutir uma proposta de cessar-fogo.",
      "analysis": {
        "key_points": [
          "Negociações buscam reduzir escalada militar.",
          "Atores regionais tentam preservar influência diplomática."
        ],
        "actors": ["Country A", "Country B", "UN"],
        "regions": ["Middle East"],
        "risk_level": "medium",
        "context": "O encontro ocorre após semanas de tensão na fronteira."
      },
      "bias": {
        "label": "moderate",
        "score": 0.42,
        "signals": ["Uso frequente de termos avaliativos"]
      },
      "entities": [
        {
          "text": "UN",
          "label": "ORG",
          "confidence": 0.91
        }
      ],
      "processed_at": "2026-06-09T20:05:00Z"
    }
  ],
  "processed_count": 1,
  "cached_count": 0
}
```

Erros comuns:

- `400 invalid_url`: URL inválida ou protocolo não permitido.
- `400 blocked_url`: host bloqueado por proteção SSRF.
- `422 validation_error`: payload fora do schema.
- `502 fetch_failed`: falha ao baixar ou processar conteúdo externo.
- `502 fetch_timeout`: timeout no download externo.
- `502 too_many_redirects`: limite de redirecionamentos atingido.
- `502 content_too_large`: resposta maior que `REQUEST_MAX_BYTES`.
- `502 empty_content`: página sem conteúdo útil para análise.

Para feeds RSS, itens com URL bloqueada ou inválida são pulados. Isso evita que um item ruim derrube o processamento do feed inteiro.

Quando um feed direto não corresponde a uma fonte cadastrada, `source.name` usa o título do feed. Se o feed não informar título, usa o domínio da URL.

## GET /news/latest

Retorna últimas notícias analisadas presentes no cache.

Query params:

- `limit`: inteiro de 1 a 100, default 20.
- `region`: string opcional.
- `source_id`: string opcional.
- `entity`: string opcional.

Resposta `200`:

```json
{
  "items": [],
  "total": 0
}
```

## GET /news/{id}

Retorna uma notícia analisada específica.

Erro `404`:

```json
{
  "code": "not_found",
  "message": "Notícia não encontrada."
}
```

## Notas para o frontend

- Configure `VITE_API_BASE_URL`; não fixe a URL da API no bundle.
- Use `GET /health` para exibir status de indisponibilidade.
- Use `POST /analyze` para análise manual de URL/feed.
- Use `GET /news/latest` para o dashboard inicial.
- Trate `{code, message, details}` de forma centralizada no cliente HTTP.
- Para `blocked_url`, mostre `URL bloqueada por segurança.`
- Para `invalid_url`, mostre `URL inválida.`
- Para `fetch_failed`, `fetch_timeout` ou `empty_content`, mostre `Não foi possível coletar essa página. Alguns sites bloqueiam leitura automática. Tente um RSS.`
- Renderize conteúdo externo como texto, não como HTML confiável.
