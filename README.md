# frete-system

Plataforma de cotação de fretes: React + TypeScript + Vite (frontend) e
FastAPI + PostgreSQL (backend), conectados pelo contrato de API descrito
em `backend/README.md`.

## Rodando tudo junto

```bash
cp backend/.env.example backend/.env      # defina um JWT_SECRET forte
cp frontend/.env.example frontend/.env

docker compose up --build
```

Popule o banco (transportadoras + usuário de teste):

```bash
docker compose exec backend python -m app.seed
```

- Frontend: http://localhost:5173 (login: `admin@fretesystem.com` / `admin123`)
- Backend: http://localhost:8000 (`/docs` para o Swagger gerado pelo FastAPI)

## O que já funciona (Sprint 1 + parte da Sprint 2/3)

```
Login (JWT real)
  ↓
Dashboard (lista transportadoras via API)
  ↓
Nova cotação
  ↓
POST /api/v1/cotacoes → cubagem recalculada no backend
  ↓
Polling em GET /api/v1/cotacoes/{id} (TanStack Query)
  ↓
Consultas em paralelo aos adapters mock de cada transportadora
  ↓
Resultado normalizado + melhor opção destacada
  ↓
POST /api/v1/cotacoes/{id}/selecionar
```

Nenhuma transportadora derruba as demais em caso de erro/timeout — cada
consulta roda de forma independente no backend (`app/services/cotacao_service.py`).

## O que ainda falta

- `GET /api/v1/cotacoes` com paginação e filtros (histórico completo — Passos 55/56)
- `GET /api/v1/dashboard` com métricas agregadas reais (Sprint 3)
- Adapters reais das transportadoras, substituindo o `MockTransportadoraAdapter`
  (Sprints 4-6: Jamef, Jadlog, Braspress)
- n8n + Playwright para transportadoras sem API oficial (Sprints 7-8)
- Integração Sankhya (Sprint 9)
- Autorização por permissão de usuário, logs estruturados, observabilidade (Sprint 10)

## Estrutura

```
frete-system/
├── backend/     FastAPI + PostgreSQL + Alembic (ver backend/README.md)
├── frontend/    React + TypeScript + Vite + Tailwind + TanStack Query
└── docker-compose.yml
```
