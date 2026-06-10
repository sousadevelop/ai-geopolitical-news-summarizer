# Seguranca

## Escopo

Este documento cobre a API backend que recebe URLs externas em `POST /analyze` e `POST /sources`, baixa artigos ou feeds RSS e armazena resultados em cache local ou JSON.

## Superficies de ataque

- `POST /analyze`: aceita URL de artigo ou feed e dispara downloads HTTP externos.
- `POST /sources`: cadastra fontes externas.
- `GET /news/latest` e `GET /news/{id}`: expoem dados persistidos no cache.
- Variaveis de ambiente: `CORS_ORIGINS`, `REQUEST_TIMEOUT_SECONDS`, `REQUEST_MAX_BYTES`, `REQUEST_MAX_REDIRECTS`, `CACHE_PATH` e chaves futuras.
- Cache JSON em disco quando `CACHE_PATH` e definido.

## Mitigacoes implementadas

- URLs externas aceitam apenas `http` e `https`.
- Hosts `localhost`, dominios `.localhost`, IPs privados, loopback, link-local, multicast, reservados e nao especificados sao bloqueados.
- Antes do fetch, o host e resolvido por DNS. Se qualquer IP resolvido for bloqueado, a URL e rejeitada.
- Redirecionamentos nao sao seguidos automaticamente. Cada `Location` e normalizado, validado e resolvido antes de continuar.
- Limite padrao de redirecionamentos: `REQUEST_MAX_REDIRECTS=5`.
- Timeout padrao de downloads externos: `REQUEST_TIMEOUT_SECONDS=10`.
- Limite padrao de resposta externa: `REQUEST_MAX_BYTES=2000000`, validado por `Content-Length` e pelo stream recebido.
- `max_items` de feed RSS e limitado pelo schema a 20.
- Itens RSS com `blocked_url` ou `invalid_url` sao pulados, em vez de derrubar o feed inteiro.
- Em desenvolvimento, CORS permite apenas localhost em portas comuns. Fora de desenvolvimento, o default e lista vazia.
- Erros conhecidos retornam `{code, message, details}`. Erros inesperados retornam `internal_error` sem stack trace.
- Erros de fetch usam URL reduzida sem query string.

## Riscos residuais

- A protecao SSRF reduz o risco basico, mas nao elimina DNS rebinding, mudanca de rota entre resolucao e conexao ou protecoes de rede incompletas do provedor.
- A v1 nao tem autenticacao nem rate limit.
- `CORS_ORIGINS=*` pode ser definido por configuracao operacional. Nao use esse valor em producao.
- Conteudo externo pode conter texto malicioso. O frontend deve renderizar campos como texto, nao como HTML confiavel.
- O cache JSON nao e criptografado.
- Sem banco ou trilha de auditoria, investigacao de abuso depende dos logs do ambiente de execucao.

## Recomendacoes para producao

- Coloque a API atras de um proxy com rate limit.
- Exija autenticacao para endpoints que buscam URLs externas.
- Defina `CORS_ORIGINS` com o dominio exato do frontend.
- Rode o container como usuario sem privilegios, como ja previsto no Dockerfile.
- Evite armazenar segredos em URLs ou conteudo processado.
- Use logs do provedor para monitorar volume de chamadas e falhas de fetch.
- Considere uma allowlist de dominios RSS se o uso publico crescer.
