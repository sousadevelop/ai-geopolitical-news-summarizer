# Desenvolvimento

Use `backend/requirements-dev.txt` no desenvolvimento. O Dockerfile e qualquer runtime de producao devem usar `backend/requirements.txt`.

## Requisitos locais

- Python 3.11 ou superior.
- Node.js 20 LTS ou superior.
- npm.
- Docker Desktop com Linux engine ativo, apenas se for validar container.

## Backend

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

Testes:

```powershell
cd backend
python -m pytest
```

Validacao registrada em 2026-06-10: 8/8 passaram, com 1 warning de deprecacao em `fastapi.testclient`/Starlette.

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

Arquivo local:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Testes e build:

```powershell
cd frontend
npm run test
npm run build
npm audit --audit-level=moderate
```

Validacoes registradas em 2026-06-10:

- `npm run test`: 4 arquivos e 8/8 testes passaram.
- `npm run build`: passou.
- `npm audit --audit-level=moderate`: 0 vulnerabilities.
- Build e execucao local do Docker: validados.

## Variaveis de ambiente

### Backend

| Variavel | Default | Observacao |
| --- | --- | --- |
| `APP_ENV` | `development` | Tambem usado para preencher `ENVIRONMENT` no container. |
| `ENVIRONMENT` | valor de `APP_ENV` | Tem precedencia no codigo quando definido. |
| `PORT` | `8000` | Mantido como configuracao de ambiente; o `CMD` JSON do Space usa porta fixa 8000. |
| `CORS_ORIGINS` | localhost em dev, vazio fora de dev | Lista separada por virgula. |
| `CACHE_PATH` | vazio | Quando definido, ativa cache JSON. |
| `CACHE_MAX_ITEMS` | `500` | Limite do cache local. |
| `REQUEST_TIMEOUT_SECONDS` | `10` | Timeout dos downloads externos. |
| `REQUEST_MAX_BYTES` | `2000000` | Limite de bytes por resposta externa. |
| `REQUEST_MAX_REDIRECTS` | `5` | Limite de redirecionamentos manuais. |
| `RSS_ENTRY_MAX_CHARS` | `20000` | Limite de texto usado por item RSS. |
| `SUMMARY_PROVIDER` | `local_extractive` | Provider atual de resumo. |
| `LLM_API_KEY` | vazio | Reservado para provider remoto futuro. |

### Frontend

| Variavel | Exemplo |
| --- | --- |
| `VITE_API_BASE_URL` | `http://localhost:8000` |

Variaveis `VITE_` sao embutidas no bundle. Nao coloque segredos no frontend.
No Netlify, use `VITE_API_BASE_URL=https://ysolis-geopolitical-news-api.hf.space`; nao grave a URL no codigo.

## Contrato da API

O contrato canonico esta em [`../openapi.yaml`](../openapi.yaml). Atualize o OpenAPI junto com qualquer mudanca de endpoint, schema ou codigo de erro.

## Fluxo sugerido

1. Inicie o backend e valide `/health`.
2. Inicie o frontend com `VITE_API_BASE_URL` apontando para o backend local.
3. Teste `POST /analyze` com uma URL ou feed controlado.
4. Rode os testes do backend e do frontend antes de fechar a mudanca.
5. Atualize docs quando comandos, variaveis ou contrato mudarem.

## Notas de manutencao

- `requirements.txt` deve conter apenas dependencias de runtime.
- `requirements-dev.txt` deve incluir `-r requirements.txt` e ferramentas de teste/desenvolvimento.
- Itens RSS com `blocked_url` ou `invalid_url` sao pulados durante analise de feed.
- O cache local facilita a v1, mas nao substitui banco para historico duravel ou multiplas replicas.
- No Space, `CACHE_PATH=/data/cache.json` depende do runtime e do storage configurados e pode nao oferecer persistencia duravel.
