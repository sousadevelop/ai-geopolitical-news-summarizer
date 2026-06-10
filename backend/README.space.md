---
title: Geopolitical News API
emoji: 🌍
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8000
pinned: false
license: mit
---

# Geopolitical News API

API FastAPI para coletar feeds RSS e analisar notícias geopolíticas com sumarização, identificação de entidades e análise de viés.

## Endpoints principais

- `GET /health`: verifica a disponibilidade da API e o estado do cache.
- `GET /sources`: lista as fontes cadastradas.
- `POST /sources`: cadastra uma fonte RSS.
- `POST /analyze`: analisa um conteúdo ou artigo.
- `GET /news/latest`: retorna as notícias analisadas mais recentes.
- `GET /news/{id}`: retorna uma notícia pelo identificador.

A documentação interativa está disponível em [/docs](/docs).

## Variáveis de ambiente

- `APP_ENV`: ambiente de execução, como `development` ou `production`.
- `PORT`: porta HTTP; o Space usa `8000`.
- `CORS_ORIGINS`: origens permitidas, separadas por vírgula.
- `CACHE_PATH`: caminho do arquivo de cache.
- `CACHE_MAX_ITEMS`: quantidade máxima de notícias armazenadas no cache.
- `REQUEST_TIMEOUT_SECONDS`: tempo limite das requisições externas.
- `SUMMARY_PROVIDER`: provedor de sumarização.
- `SUMMARY_MODEL`: modelo opcional de sumarização.
- `LLM_API_KEY`: chave do provedor de LLM, quando necessária.

Ao usar `CACHE_PATH=/data/cache.json`, a permanência do cache depende do armazenamento configurado e do runtime do Space. Sem armazenamento persistente, o arquivo pode ser perdido quando o Space reiniciar ou for recriado.
