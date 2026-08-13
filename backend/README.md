# FreteWay — backend

FastAPI + PostgreSQL + Docker, seguindo o contrato de API consumido pelo
protótipo de frontend (`frete-system-prototype.jsx`).

## O que este Sprint 1 entrega

- `GET /health` — health check usado pelo indicador "Backend conectado" do frontend
- `POST /api/v1/auth/login` — autenticação JWT
- `GET /api/v1/transportadoras` — lista vinda do banco (nunca hardcoded no frontend)
- `POST /api/v1/cotacoes` — cria a cotação, recalcula a cubagem no backend e dispara
  as consultas em paralelo em background (`processing` → `completed`/`completed_with_errors`/`failed`)
- `GET /api/v1/cotacoes/{id}` — consulta de status (usado pelo polling do frontend)
- `POST /api/v1/cotacoes/{id}/selecionar` — seleção da transportadora vencedora
- Todas as transportadoras usam, por enquanto, o `MockTransportadoraAdapter`
  (`app/integrations/transportadoras/mock/client.py`) — cada uma será trocada
  pelo adapter real nas Sprints 4, 5, 6... sem mudar o contrato nem o frontend.

## Como rodar

```bash
cp backend/.env.example backend/.env
# edite backend/.env e defina um JWT_SECRET forte

docker compose up --build
```

Depois, popule o banco (transportadoras + usuário de teste):

```bash
docker compose exec backend python -m app.seed
```

Login de teste criado pelo seed:

```
email: admin@fretesystem.com
senha: admin123
```

A API fica em `http://localhost:8000`, com documentação automática em
`http://localhost:8000/docs`.

## Gerando a primeira migration

O modelo já está definido em `app/models/models.py`. Para gerar a migration
inicial via Alembic (dentro do container, com o Postgres no ar):

```bash
docker compose exec backend alembic revision --autogenerate -m "schema inicial"
docker compose exec backend alembic upgrade head
```

(O `seed.py` já cria as tabelas diretamente para acelerar o Sprint 1 — a
migration formal deve ser gerada antes de ir para produção.)

## Testes

```bash
docker compose exec backend pytest
```

## Próximos passos (fora do escopo deste Sprint 1)

- Conectar o `frete-system-prototype.jsx` a este backend real
  (trocar o mock local do frontend por chamadas via `axios`/TanStack Query)
- Sprint 3: métricas reais de sucesso/tempo médio por transportadora
- Sprint 4-6: adapters reais (Jamef, Jadlog, Braspress) com credenciais oficiais
- Sprint 7-8: n8n + Playwright para transportadoras sem API
- Sprint 9: integração Sankhya
