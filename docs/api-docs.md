# Documentacao da API

Contrato canonico: [`../openapi.yaml`](../openapi.yaml). Este arquivo traz exemplos curtos e notas de consumo.

Base local: `http://localhost:8000`

## Autenticacao

A v1 nao exige autenticacao. Se a API for exposta publicamente, proteja os endpoints que disparam downloads externos com autenticacao, rate limit ou uma camada de proxy.

## Erros

Erros conhecidos retornam:

```json
{
  "code": "invalid_url",
  "message": "URL invalida ou protocolo nao permitido.",
  "details": {
    "field": "url"
  }
}
```

Excecoes inesperadas retornam `internal_error` sem stack trace.

## GET /health

Verifica se a API esta disponivel.

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

- `400 invalid_url`: URL invalida ou protocolo nao permitido.
- `409 source_conflict`: fonte ja cadastrada.
- `422 validation_error`: payload fora do schema.

## POST /analyze

Analisa uma URL de noticia ou um feed RSS. Para `input_type: "url"`, retorna uma analise. Para `input_type: "feed"`, processa ate `max_items`.

Request para noticia:

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
          "Negociacoes buscam reduzir escalada militar.",
          "Atores regionais tentam preservar influencia diplomatica."
        ],
        "actors": ["Country A", "Country B", "UN"],
        "regions": ["Middle East"],
        "risk_level": "medium",
        "context": "O encontro ocorre apos semanas de tensao na fronteira."
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

- `400 invalid_url`: URL invalida ou protocolo nao permitido.
- `400 blocked_url`: host bloqueado por protecao SSRF.
- `422 validation_error`: payload fora do schema.
- `502 fetch_failed`: falha ao baixar ou processar conteudo externo.
- `502 fetch_timeout`: timeout no download externo.
- `502 too_many_redirects`: limite de redirecionamentos atingido.
- `502 content_too_large`: resposta maior que `REQUEST_MAX_BYTES`.
- `502 empty_content`: pagina sem conteudo util para analise.

Para feeds RSS, itens com URL bloqueada ou invalida sao pulados. Isso evita que um item ruim derrube o processamento do feed inteiro.

## GET /news/latest

Retorna ultimas noticias analisadas presentes no cache.

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

Retorna uma noticia analisada especifica.

Erro `404`:

```json
{
  "code": "not_found",
  "message": "Noticia nao encontrada."
}
```

## Notas para o frontend

- Configure `VITE_API_BASE_URL`; nao fixe a URL da API no bundle.
- Use `GET /health` para exibir status de indisponibilidade.
- Use `POST /analyze` para analise manual de URL/feed.
- Use `GET /news/latest` para o dashboard inicial.
- Trate `{code, message, details}` de forma centralizada no cliente HTTP.
- Renderize conteudo externo como texto, nao como HTML confiavel.
