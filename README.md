# Sumarizador de Noticias Geopoliticas

Aplicacao para coletar noticias geopoliticas por RSS ou URL, gerar resumo, extrair pontos de analise, identificar entidades nomeadas e expor os resultados em uma API FastAPI consumida por um frontend React/Vite.

O contrato da API esta em [openapi.yaml](openapi.yaml). Os exemplos de consumo ficam em [docs/api-docs.md](docs/api-docs.md).

## Estado atual

- Backend FastAPI implementado em `backend/`.
- Frontend React/Vite implementado em `frontend/`.
- Cache local em memoria ou JSON, sem banco obrigatorio.
- Protecoes basicas contra SSRF em downloads externos.
- CORS restrito por default fora de desenvolvimento.
- Deploy documentado para backend Docker/Hugging Face Spaces e frontend Netlify.
- Backend publicado no [Hugging Face Space](https://huggingface.co/spaces/ySolis/geopolitical-news-api), com API em `https://ysolis-geopolitical-news-api.hf.space`.

## Requisitos

- Python 3.11 ou superior.
- Node.js 20 LTS ou superior.
- npm.
- Docker apenas para build/execucao em container.

## Backend local

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Healthcheck:

```powershell
Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing
```

## Frontend local

```powershell
cd frontend
npm install
npm run dev
```

Configure `frontend/.env.local`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Testes e build

Backend:

```powershell
cd backend
python -m pytest
```

Frontend:

```powershell
cd frontend
npm run test
npm run build
npm audit --audit-level=moderate
```

Validacoes registradas em 2026-06-10:

- `python -m pytest`: 8/8 passaram, com 1 warning de deprecacao em `fastapi.testclient`/Starlette.
- `npm run test`: 4 arquivos e 8/8 testes passaram.
- `npm run build`: passou.
- `npm audit --audit-level=moderate`: 0 vulnerabilities.
- Build e execucao local do Docker: validados.
- API publica: `/health` e `/docs` responderam HTTP 200.

## Variaveis de ambiente

Backend:

| Variavel | Uso |
| --- | --- |
| `APP_ENV` ou `ENVIRONMENT` | Ambiente exibido no healthcheck e usado em defaults de CORS. |
| `PORT` | Mantida como configuracao; a imagem do Space inicia em porta fixa 8000. |
| `CORS_ORIGINS` | Lista de origens permitidas, separadas por virgula. |
| `CACHE_PATH` | Caminho opcional do cache JSON. |
| `CACHE_MAX_ITEMS` | Limite de noticias mantidas no cache. |
| `REQUEST_TIMEOUT_SECONDS` | Timeout de downloads externos. |
| `REQUEST_MAX_BYTES` | Limite de bytes por download externo. |
| `REQUEST_MAX_REDIRECTS` | Limite de redirecionamentos manuais. |
| `RSS_ENTRY_MAX_CHARS` | Limite de caracteres usados por item RSS. |
| `SUMMARY_PROVIDER` | Provider de resumo. Default atual: `local_extractive`. |
| `LLM_API_KEY` | Reservado para provider remoto futuro. |

Frontend:

| Variavel | Uso |
| --- | --- |
| `VITE_API_BASE_URL` | URL base da API FastAPI. |

No Netlify, defina `VITE_API_BASE_URL=https://ysolis-geopolitical-news-api.hf.space`. Nao grave a URL da API diretamente no codigo do frontend.

## Estrutura

```text
backend/
  app/
  tests/
  Dockerfile
  requirements.txt
  requirements-dev.txt

frontend/
  src/
  package.json
  netlify.toml

docs/
  api-docs.md
  development.md
  deployment.md
  security.md

.memory/
  known-issues.md
  roadmap.md
```

## Documentacao

- [Desenvolvimento](docs/development.md)
- [API](docs/api-docs.md)
- [Deploy](docs/deployment.md)
- [Seguranca](docs/security.md)
- [Known issues](.memory/known-issues.md)
- [Roadmap](.memory/roadmap.md)

## Limitacoes da v1

- Sem autenticacao.
- Sem rate limit.
- Sem banco duravel para historico.
- Cache JSON nao e adequado para multiplas replicas.
- Sumarizacao, NER e analise de vies sao locais e simples.
- O frontend ainda precisa ser publicado no Netlify.
- Depois da publicacao, `CORS_ORIGINS` no Space deve receber o dominio definitivo do Netlify. Nunca use `*`.
- `CACHE_PATH=/data/cache.json` so persiste conforme o runtime e o storage disponiveis no Space.
