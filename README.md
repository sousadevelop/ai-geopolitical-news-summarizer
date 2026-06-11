# GeoPolaris

Aplicação para coletar e analisar notícias geopolíticas por RSS ou URL. O backend FastAPI gera resumos e sinais locais de análise; o frontend React/Vite apresenta os resultados.

O contrato da API está em [openapi.yaml](openapi.yaml). Os exemplos de consumo ficam em [docs/api-docs.md](docs/api-docs.md).

## Demonstração

![Demonstração do GeoPolaris](docs/assets/gifs/projeto-geopolaris.gif)

## Estado atual

- Backend FastAPI implementado em `backend/`.
- Frontend React/Vite implementado em `frontend/`.
- Cache local em memória ou JSON, sem banco obrigatório.
- Proteções básicas contra SSRF em downloads externos.
- CORS restrito por padrão fora de desenvolvimento.
- Deploy documentado para backend Docker/Hugging Face Spaces e frontend Netlify.
- Backend publicado no [Hugging Face Space](https://huggingface.co/spaces/ySolis/geopolitical-news-api), com API em `https://ysolis-geopolitical-news-api.hf.space`.
- Frontend publicado em [geopolaris.netlify.app](https://geopolaris.netlify.app).

![Dashboard do GeoPolaris](docs/assets/screenshots/dashboard-cache.png)

## Uso da análise

- Prefira um feed RSS. Alguns sites bloqueiam a coleta automática de URLs diretas.
- Exemplo BBC: `https://feeds.bbci.co.uk/news/world/rss.xml`.
- `language` indica o idioma preferencial da análise, mas não traduz o conteúdo na v1.
- A v1 usa processamento local e não oferece tradução nem integração com LLM.
- Para feed direto sem fonte cadastrada, a origem usa o título do feed ou, se ele não existir, o domínio da URL.

![Análise de feed RSS no GeoPolaris](docs/assets/screenshots/analyze-rss-result.png)

## Requisitos

- Python 3.11 ou superior.
- Node.js 20 LTS ou superior.
- npm.
- Docker apenas para build/execução em container.

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

Validações registradas em 2026-06-10:

- `python -m pytest`: 8/8 passaram, com 1 warning de depreciação em `fastapi.testclient`/Starlette.
- `npm run test`: 4 arquivos e 8/8 testes passaram.
- `npm run build`: passou.
- `npm audit --audit-level=moderate`: 0 vulnerabilities.
- Build e execução local do Docker: validados.
- API pública: `/health` e `/docs` responderam HTTP 200.

## Variáveis de ambiente

Backend:

| Variável | Uso |
| --- | --- |
| `APP_ENV` ou `ENVIRONMENT` | Ambiente exibido no healthcheck e usado nos padrões de CORS. |
| `PORT` | Mantida como configuração; a imagem do Space inicia em porta fixa 8000. |
| `CORS_ORIGINS` | Lista de origens permitidas, separadas por vírgula. |
| `CACHE_PATH` | Caminho opcional do cache JSON. |
| `CACHE_MAX_ITEMS` | Limite de notícias mantidas no cache. |
| `REQUEST_TIMEOUT_SECONDS` | Timeout de downloads externos. |
| `REQUEST_MAX_BYTES` | Limite de bytes por download externo. |
| `REQUEST_MAX_REDIRECTS` | Limite de redirecionamentos manuais. |
| `RSS_ENTRY_MAX_CHARS` | Limite de caracteres usados por item RSS. |
| `SUMMARY_PROVIDER` | Provider de resumo. Default atual: `local_extractive`. |

Frontend:

| Variável | Uso |
| --- | --- |
| `VITE_API_BASE_URL` | URL base da API FastAPI. |

No Netlify, defina `VITE_API_BASE_URL=https://ysolis-geopolitical-news-api.hf.space`. Não grave a URL da API diretamente no código do frontend.

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
  assets/
    gifs/
    screenshots/

.memory/
  known-issues.md
  roadmap.md
```

## Documentação

- [Desenvolvimento](docs/development.md)
- [API](docs/api-docs.md)
- [Deploy](docs/deployment.md)
- [Segurança](docs/security.md)
- [Known issues](.memory/known-issues.md)
- [Roadmap](.memory/roadmap.md)

## Limitações da v1

- Sem autenticação.
- Sem rate limit.
- Sem banco durável para histórico.
- Cache JSON não é adequado para múltiplas réplicas.
- Sumarização, NER e análise de viés são locais e simples.
- URLs diretas podem retornar falha de coleta quando o site bloqueia leitura automática; use RSS quando disponível.
- `language` não traduz o texto recebido.
- `CACHE_PATH=/data/cache.json` só persiste conforme o runtime e o storage disponíveis no Space.
