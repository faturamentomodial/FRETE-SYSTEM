# Frete System - Documentação Completa do Projeto

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Arquitetura](#arquitetura)
3. [Stack Tecnológico](#stack-tecnológico)
4. [Estrutura de Pastas](#estrutura-de-pastas)
5. [Como Rodar](#como-rodar)
6. [Modelos de Dados](#modelos-de-dados)
7. [API Endpoints](#api-endpoints)
8. [Fluxo de Funcionamento](#fluxo-de-funcionamento)
9. [Frontend](#frontend)
10. [Backend](#backend)
11. [Próximos Passos](#próximos-passos)

---

## Visão Geral

**Frete System** é uma plataforma de cotação de fretes que conecta clientes a múltiplas transportadoras de forma automática e paralela.

### Objetivo
- Permitir que usuários solicitem cotações de frete
- Consultar múltiplas transportadoras em paralelo
- Selecionar a melhor opção (menor preço/prazo)
- Acompanhar o status das cotações em tempo real

### Status Atual (Sprint 1-3)
- ✅ Autenticação JWT
- ✅ Cotação com cálculo de cubagem no backend
- ✅ Consultas paralelas em background
- ✅ Mock de transportadoras funcionando
- ✅ Dashboard com histórico básico
- ⏳ Histórico completo com paginação (em progresso)

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (React)                      │
│              Vite + TypeScript + Tailwind               │
│   http://localhost:5173                                │
└─────────────────┬───────────────────────────────────────┘
                  │ HTTP/REST (Axios)
                  │
┌─────────────────┴───────────────────────────────────────┐
│                   API Gateway                           │
│              FastAPI + CORS                             │
│   http://localhost:8000                                │
└─────────────────┬───────────────────────────────────────┘
                  │
    ┌─────────────┴──────────────┐
    │                            │
    │ Autenticação & Dados       │ Background Jobs
    │                            │
┌───┴────────────────────┐  ┌───┴──────────────────────┐
│   PostgreSQL 16        │  │  Consultas em Paralelo  │
│   (Database)           │  │  (Transportadoras)      │
│   :5432                │  │                         │
└────────────────────────┘  └─────────────────────────┘
```

### Fluxo de Dados
```
Usuário faz login
    ↓
Frontend armazena JWT no localStorage
    ↓
Usuário cria nova cotação
    ↓
Frontend POST /api/v1/cotacoes
    ↓
Backend calcula cubagem + cria registro
    ↓
Backend dispara consultas paralelas (background)
    ↓
Frontend faz polling GET /api/v1/cotacoes/{id}
    ↓
Transportadoras respondem (success/error/timeout)
    ↓
Frontend mostra resultados + melhor opção
    ↓
Usuário seleciona transportadora
    ↓
Backend POST /api/v1/cotacoes/{id}/selecionar
```

---

## Stack Tecnológico

### Frontend
| Tecnologia | Versão | Propósito |
|-----------|--------|----------|
| React | 18.3.1 | UI Framework |
| TypeScript | 5.5.4 | Type Safety |
| Vite | 5.4.5 | Build Tool |
| React Router | 6.26.2 | Roteamento |
| TanStack Query | 5.56.2 | State Management + API Caching |
| Axios | 1.7.7 | HTTP Client |
| React Hook Form | 7.53.0 | Gerenciamento de Formulários |
| Zod | 3.23.8 | Validação de Schema |
| Zustand | 4.5.5 | State Management Leve |
| Tailwind CSS | 3.4.10 | Estilização |
| Lucide React | 0.445.0 | Ícones |
| Recharts | 2.12.7 | Gráficos |

### Backend
| Tecnologia | Versão | Propósito |
|-----------|--------|----------|
| FastAPI | 0.115.0 | Web Framework |
| Python | 3.x | Linguagem |
| SQLAlchemy | 2.0.35 | ORM |
| Alembic | 1.13.2 | Database Migrations |
| PostgreSQL | 16 (Alpine) | Database |
| asyncpg | 0.29.0 | Async PostgreSQL Driver |
| Pydantic | 2.9.2 | Data Validation |
| python-jose | 3.3.0 | JWT |
| passlib | 1.7.4 | Password Hashing |
| Pytest | 8.3.3 | Testing |
| httpx | 0.27.2 | HTTP Client |

### DevOps
| Ferramenta | Propósito |
|-----------|----------|
| Docker | Containerização |
| Docker Compose | Orquestração de containers |
| Alembic | Database versioning |

---

## Estrutura de Pastas

```
frete-system/
├── docker-compose.yml           # Orquestração dos containers
├── README.md                     # Guia rápido
├── PROJETO_COMPLETO.md          # Este arquivo
│
├── backend/                      # FastAPI + PostgreSQL
│   ├── Dockerfile               # Imagem Docker do backend
│   ├── README.md                # Documentação do backend
│   ├── requirements.txt          # Dependências Python
│   ├── alembic.ini              # Configuração do Alembic
│   │
│   ├── alembic/                 # Database migrations
│   │   ├── env.py               # Configuração do Alembic
│   │   ├── script.py.mako       # Template de migration
│   │   └── versions/            # Histórico de migrations
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # Ponto de entrada FastAPI
│   │   ├── seed.py              # Seed de dados (transportadoras + usuário)
│   │   │
│   │   ├── api/                 # Rotas HTTP
│   │   │   └── v1/
│   │   │       ├── router.py    # Agregador de rotas
│   │   │       └── endpoints/
│   │   │           ├── auth.py        # Autenticação (login)
│   │   │           ├── health.py      # Health check
│   │   │           ├── cotacoes.py    # Endpoints de cotações
│   │   │           └── transportadoras.py  # Endpoints de transportadoras
│   │   │
│   │   ├── core/                # Configuração global
│   │   │   ├── config.py        # Variáveis de ambiente
│   │   │   ├── deps.py          # Dependency injection
│   │   │   └── security.py      # JWT + Hashing
│   │   │
│   │   ├── db/                  # Database
│   │   │   └── session.py       # Conexão async com PostgreSQL
│   │   │
│   │   ├── models/              # SQLAlchemy ORM models
│   │   │   └── models.py        # User, Transportadora, Cotacao, etc.
│   │   │
│   │   ├── schemas/             # Pydantic schemas (request/response)
│   │   │   ├── auth.py          # LoginRequest, TokenResponse
│   │   │   └── cotacao.py       # CotacaoRequest, CotacaoResponse
│   │   │
│   │   ├── services/            # Lógica de negócio
│   │   │   ├── cotacao_service.py    # Criação, consulta de cotações
│   │   │   └── cubagem.py            # Cálculo de cubagem
│   │   │
│   │   └── integrations/        # Adaptadores de transportadoras
│   │       └── transportadoras/
│   │           ├── base.py      # Interface abstrata
│   │           └── mock/
│   │               └── client.py # Mock adapter (todas usam por enquanto)
│   │
│   └── tests/
│       └── test_cubagem.py      # Testes unitários
│
├── frontend/                     # React + TypeScript + Vite
│   ├── Dockerfile               # Imagem Docker do frontend
│   ├── package.json             # Dependências Node
│   ├── tsconfig.json            # Configuração TypeScript
│   ├── vite.config.ts           # Configuração Vite
│   ├── tailwind.config.ts       # Configuração Tailwind CSS
│   ├── postcss.config.js        # Configuração PostCSS
│   ├── index.html               # HTML entry point
│   │
│   └── src/
│       ├── App.tsx              # Root component
│       ├── main.tsx             # React entry point
│       ├── index.css            # Estilos globais + Tailwind
│       │
│       ├── api/
│       │   └── client.ts        # Axios client com baseURL
│       │
│       ├── components/          # Componentes reutilizáveis
│       │   └── ui/
│       │       └── index.tsx    # Componentes UI primitivos
│       │
│       ├── hooks/               # Custom React hooks
│       │   ├── useAuth.ts       # Autenticação
│       │   ├── useCotacao.ts    # Cotações (TanStack Query)
│       │   └── useTransportadoras.ts  # Transportadoras
│       │
│       ├── layouts/
│       │   └── AppLayout.tsx    # Layout compartilhado (sidebar, header)
│       │
│       ├── pages/               # Page components (uma por rota)
│       │   ├── Login/
│       │   │   └── Login.tsx
│       │   ├── Dashboard/
│       │   │   └── Dashboard.tsx
│       │   ├── NovaCotacao/
│       │   │   └── NovaCotacao.tsx
│       │   ├── Cotacoes/
│       │   │   └── Cotacoes.tsx
│       │   └── Transportadoras/
│       │       └── Transportadoras.tsx
│       │
│       ├── routes/
│       │   ├── index.tsx        # Definição de rotas
│       │   └── ProtectedRoute.tsx  # Proteção com JWT
│       │
│       ├── services/            # Chamadas HTTP
│       │   ├── authService.ts   # POST /auth/login
│       │   ├── cotacaoService.ts # CRUD de cotações
│       │   └── transportadoraService.ts # GET transportadoras
│       │
│       ├── stores/              # Zustand stores
│       │   └── authStore.ts     # Estado de autenticação
│       │
│       └── types/               # TypeScript interfaces
│           ├── auth.ts
│           ├── cotacao.ts
│           └── transportadora.ts
```

---

## Como Rodar

### Pré-requisitos
- Docker & Docker Compose
- (Opcional) Node.js 18+, Python 3.10+ (para desenvolvimento local)

### 1. Clonar e configurar

```bash
git clone <repositorio>
cd frete-system

# Copiar arquivos de configuração
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### 2. Definir JWT_SECRET no backend

Edite `backend/.env` e defina um JWT_SECRET forte:

```bash
JWT_SECRET="sua-chave-secreta-super-segura-aqui"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Iniciar os containers

```bash
docker compose up --build
```

Espere até que todos os serviços estejam rodando:
- PostgreSQL: porta 5432
- Backend: porta 8000
- Frontend: porta 5173

### 4. Popular o banco (seed)

```bash
docker compose exec backend python -m app.seed
```

Isso cria:
- Usuário: `admin@fretesystem.com` / `admin123`
- Transportadoras: Jamef, Jadlog, Braspress, Sedex (mocks)

### 5. Acessar

- **Frontend**: http://localhost:5173
- **Backend (API Docs)**: http://localhost:8000/docs
- **Backend (Health Check)**: http://localhost:8000/health

---

## Modelos de Dados

### User (Usuários)
```python
id: UUID
email: str (unique, indexed)
password_hash: str
nome: str
created_at: datetime
```

### Transportadora (Fornecedoras de Frete)
```python
id: UUID
nome: str (unique)
tipo_integracao: str  # 'api', 'webservice', 'soap', 'edi', 'n8n', 'playwright'
ativa: bool
taxa_sucesso: float  # Métrica de sucesso (0-1)
tempo_medio_ms: int  # Tempo médio de resposta
ultima_consulta: datetime (nullable)
```

### Cotacao (Solicitação de Frete)
```python
id: UUID
status: str  # 'processing', 'completed', 'completed_with_errors', 'failed'
origem_cep: str
origem_cidade: str
origem_uf: str
destino_cep: str
destino_cidade: str
destino_uf: str
valor_nf: float  # Valor da nota fiscal
peso: float  # Peso total em kg
cubagem_m3: float  # Cubagem calculada
melhor_opcao_id: str (nullable)  # ID do resultado selecionado
created_at: datetime
volumes: list[CotacaoVolume]  # Relacionamento 1-N
resultados: list[CotacaoResultado]  # Relacionamento 1-N
```

### CotacaoVolume (Itens de Uma Cotação)
```python
id: UUID
cotacao_id: UUID (FK)
quantidade: int
comprimento_cm: float
largura_cm: float
altura_cm: float
peso_kg: float
```

### CotacaoResultado (Resposta de Cada Transportadora)
```python
id: UUID
cotacao_id: UUID (FK)
transportadora_id: UUID (FK)
status: str  # 'success', 'error', 'timeout'
valor_frete: float (nullable)
prazo_dias: int (nullable)
```

---

## API Endpoints

### Autenticação

#### Login
```
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "admin@fretesystem.com",
  "senha": "admin123"
}

Response 200:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### Transportadoras

#### Listar todas
```
GET /api/v1/transportadoras
Authorization: Bearer <token>

Response 200:
[
  {
    "id": "uuid",
    "nome": "Jamef",
    "tipo_integracao": "api",
    "ativa": true,
    "taxa_sucesso": 0.98,
    "tempo_medio_ms": 245
  },
  ...
]
```

### Cotações

#### Criar cotação
```
POST /api/v1/cotacoes
Authorization: Bearer <token>
Content-Type: application/json

{
  "origem_cep": "01310100",
  "origem_cidade": "São Paulo",
  "origem_uf": "SP",
  "destino_cep": "30140071",
  "destino_cidade": "Belo Horizonte",
  "destino_uf": "MG",
  "valor_nf": 1500.00,
  "peso": 50.0,
  "volumes": [
    {
      "quantidade": 1,
      "comprimento_cm": 100,
      "largura_cm": 50,
      "altura_cm": 30,
      "peso_kg": 50
    }
  ]
}

Response 201:
{
  "id": "uuid",
  "status": "processing",
  "cubagem_m3": 0.15,
  "created_at": "2024-01-15T10:30:00"
}
```

#### Obter cotação
```
GET /api/v1/cotacoes/{id}
Authorization: Bearer <token>

Response 200:
{
  "id": "uuid",
  "status": "completed",
  "cubagem_m3": 0.15,
  "melhor_opcao_id": "resultado_uuid",
  "resultados": [
    {
      "id": "resultado_uuid",
      "transportadora_id": "transportadora_uuid",
      "status": "success",
      "valor_frete": 450.00,
      "prazo_dias": 3
    },
    ...
  ]
}
```

#### Selecionar transportadora
```
POST /api/v1/cotacoes/{id}/selecionar
Authorization: Bearer <token>
Content-Type: application/json

{
  "resultado_id": "resultado_uuid"
}

Response 200:
{
  "id": "uuid",
  "melhor_opcao_id": "resultado_uuid",
  "status": "completed"
}
```

### Health Check

```
GET /health

Response 200:
{
  "status": "ok"
}
```

---

## Fluxo de Funcionamento

### 1. Autenticação

```
Usuário abre http://localhost:5173
  ↓
Frontend verifica JWT no localStorage
  ↓
Se não existir, redireciona para /login
  ↓
Usuário insere email + senha
  ↓
Frontend POST /api/v1/auth/login
  ↓
Backend valida credenciais
  ↓
Backend gera JWT (30 minutos de validade)
  ↓
Frontend armazena JWT no Zustand + localStorage
  ↓
Frontend redireciona para /dashboard
```

### 2. Listar Transportadoras

```
Frontend carrega no App.tsx ou Dashboard
  ↓
Hook useTransportadoras (TanStack Query)
  ↓
Frontend GET /api/v1/transportadoras
  ↓
Backend retorna todas ativas
  ↓
Frontend exibe em tabela/cards
```

### 3. Nova Cotação

```
Usuário clica em "Nova Cotação"
  ↓
Frontend vai para /nova-cotacao
  ↓
Usuário preenche formulário (origem, destino, volumes)
  ↓
Usuário clica em "Consultar Fretes"
  ↓
Frontend POST /api/v1/cotacoes
  ↓
Backend:
  1. Calcula cubagem via cubagem_service.py
  2. Cria registro com status='processing'
  3. Cria CotacaoVolume para cada item
  4. Dispara cotacao_service.consultar_transportadoras() em background
  5. Retorna cotacao com ID
  ↓
Frontend redireciona para /cotacoes/{id}
  ↓
Frontend começa polling GET /api/v1/cotacoes/{id} a cada 2s
```

### 4. Processamento em Background

```
Backend (async):
  1. Percorre todas as transportadoras ativas
  2. Para cada uma, chama adapter.consultar() em paralelo
  3. Cada transportadora:
     - Tenta conectar
     - Envia dados
     - Aguarda resposta (timeout de 30s)
     - Retorna valor_frete + prazo ou erro
  4. Cria CotacaoResultado para cada resposta
  5. Identifica melhor opção (menor valor_frete)
  6. Atualiza status da cotação para 'completed'/'completed_with_errors'/'failed'
```

### 5. Exibição de Resultados

```
Frontend polling:
  ↓
GET /api/v1/cotacoes/{id}
  ↓
Status = 'processing'?
  ↓
  └─ Sim: mostra "Consultando transportadoras..." + loading
  └─ Não: exibe tabela com resultados
  ↓
Cada resultado mostra:
  - Nome da transportadora
  - Valor do frete
  - Prazo (dias)
  - Status (success/error/timeout)
  - Badge "Melhor opção" se for a escolhida
  ↓
Usuário clica em "Selecionar"
  ↓
Frontend POST /api/v1/cotacoes/{id}/selecionar
  ↓
Backend atualiza melhor_opcao_id
  ↓
Frontend exibe confirmação
```

---

## Frontend

### Estrutura de Componentes

```
<App>
  │
  ├── <QueryClientProvider>
  │   │
  │   └── <BrowserRouter>
  │       │
  │       └── <AppRoutes>
  │           │
  │           ├── <ProtectedRoute>
  │           │   ├── <AppLayout>
  │           │   │   ├── <Sidebar>
  │           │   │   ├── <Header>
  │           │   │   └── <Outlet /> (página atual)
  │           │   │
  │           │   ├── /dashboard → <Dashboard>
  │           │   ├── /cotacoes → <Cotacoes>
  │           │   ├── /nova-cotacao → <NovaCotacao>
  │           │   └── /transportadoras → <Transportadoras>
  │           │
  │           └── /login → <Login>
```

### Rotas

| Rota | Componente | Autenticação | Descrição |
|------|-----------|--------------|-----------|
| `/login` | Login | ❌ Pública | Tela de autenticação |
| `/dashboard` | Dashboard | ✅ Privada | Inicio com resumo |
| `/cotacoes` | Cotacoes | ✅ Privada | Histórico de cotações |
| `/nova-cotacao` | NovaCotacao | ✅ Privada | Criar nova cotação |
| `/transportadoras` | Transportadoras | ✅ Privada | Listar transportadoras |

### Custom Hooks

#### useAuth
```typescript
const { usuario, token, login, logout, isAuthenticated } = useAuth();
```
- Gerencia estado de autenticação (Zustand)
- Persiste token no localStorage
- Fornece método de logout

#### useCotacao
```typescript
const { data: cotacao, isLoading, error } = useCotacao(cotacaoId);
```
- Usa TanStack Query
- Polling automático enquanto status = 'processing'
- Cache inteligente
- Refetch manual disponível

#### useTransportadoras
```typescript
const { data: transportadoras, isLoading } = useTransportadoras();
```
- Lista todas as transportadoras ativas
- Cache com stale time de 5 minutos

### Estado Global (Zustand)

```typescript
// authStore.ts
interface AuthState {
  usuario: Usuario | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email, senha) => Promise<void>;
  logout: () => void;
  setToken: (token) => void;
}
```

### Formulários (React Hook Form + Zod)

#### Login
```typescript
interface LoginFormData {
  email: string;
  senha: string;
}
```

#### Nova Cotação
```typescript
interface NovaCotacaoFormData {
  origem_cep: string;
  origem_cidade: string;
  origem_uf: string;
  destino_cep: string;
  destino_cidade: string;
  destino_uf: string;
  valor_nf: number;
  peso: number;
  volumes: Array<{
    quantidade: number;
    comprimento_cm: number;
    largura_cm: number;
    altura_cm: number;
    peso_kg: number;
  }>;
}
```

### Estilos (Tailwind CSS)

- Tema: Light (default)
- Cores: Azul/Cinza
- Componentes: Botões, inputs, cards via className
- Icons: Lucide React (search, check, x, arrow, etc)

---

## Backend

### Estrutura FastAPI

```python
app = FastAPI(title="Frete System")
  │
  ├── CORS Middleware
  │   └── Permite http://localhost:5173
  │
  └── Routes (v1)
      ├── /health
      ├── /api/v1/auth/
      ├── /api/v1/cotacoes/
      └── /api/v1/transportadoras/
```

### Autenticação (JWT)

```python
# Token gerado com:
# - sub (subject): email do usuário
# - exp (expiration): 30 minutos
# - iat (issued at): agora
# - algoritmo: HS256

# Header: Authorization: Bearer <token>
```

### Camadas

#### 1. **Endpoints** (`api/v1/endpoints/`)
- Recebem requisições HTTP
- Validam schemas Pydantic
- Chamam services
- Retornam respostas

#### 2. **Schemas** (`schemas/`)
- Pydantic models para request/response
- Validação automática de tipos
- Documentação automática no Swagger

#### 3. **Services** (`services/`)
- Lógica de negócio
- Consultas complexas
- Chamadas a adapters

#### 4. **Models** (`models/`)
- SQLAlchemy ORM
- Definição de tabelas
- Relacionamentos

#### 5. **Integrations** (`integrations/`)
- Adapters de transportadoras
- Implementação real vs mock

#### 6. **Core** (`core/`)
- Configuração global
- Segurança (JWT, hashing)
- Dependency injection

#### 7. **DB** (`db/`)
- Sessão async
- Connection pooling

### Fluxo de Cotação (Backend)

```python
@router.post("/cotacoes")
async def criar_cotacao(cotacao_req: CotacaoRequest, db: Session):
    # 1. Validar dados (automático via Pydantic)
    
    # 2. Calcular cubagem
    cubagem = calcular_cubagem(volumes)
    
    # 3. Criar registro no BD
    cotacao = Cotacao(
        status="processing",
        cubagem_m3=cubagem,
        ...
    )
    db.add(cotacao)
    db.commit()
    
    # 4. Disparar background job
    asyncio.create_task(
        consultar_transportadoras(cotacao.id, db)
    )
    
    # 5. Retornar resposta (sem esperar)
    return CotacaoResponse.from_orm(cotacao)


async def consultar_transportadoras(cotacao_id: str, db: Session):
    # 1. Buscar cotação
    cotacao = db.query(Cotacao).filter(...).first()
    
    # 2. Buscar transportadoras ativas
    transportadoras = db.query(Transportadora).filter(...).all()
    
    # 3. Criar tasks paralelas
    tasks = [
        adapter.consultar(cotacao, transportadora)
        for transportadora in transportadoras
    ]
    
    # 4. Executar em paralelo (timeout 30s)
    resultados = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 5. Salvar resultados
    for resultado, transportadora in zip(resultados, transportadoras):
        cotacao_resultado = CotacaoResultado(
            cotacao_id=cotacao.id,
            transportadora_id=transportadora.id,
            status=resultado['status'],
            valor_frete=resultado.get('valor'),
            prazo_dias=resultado.get('prazo')
        )
        db.add(cotacao_resultado)
    
    # 6. Identificar melhor opção
    melhores = db.query(CotacaoResultado).filter(
        CotacaoResultado.status == 'success',
        CotacaoResultado.cotacao_id == cotacao.id
    ).order_by(CotacaoResultado.valor_frete).first()
    
    cotacao.melhor_opcao_id = melhores.id if melhores else None
    
    # 7. Atualizar status
    cotacao.status = "completed" if melhores else "completed_with_errors"
    
    db.commit()
```

### Cálculo de Cubagem

```python
def calcular_cubagem(volumes: list[CotacaoVolume]) -> float:
    """
    Cubagem = (comprimento × largura × altura) / 5000
    
    Fator 5000 é padrão da indústria brasileira
    """
    total_m3 = 0.0
    
    for vol in volumes:
        # Converter cm para metros
        comp_m = vol.comprimento_cm / 100
        larg_m = vol.largura_cm / 100
        alt_m = vol.altura_cm / 100
        
        # Volume de um item
        vol_item = comp_m * larg_m * alt_m
        
        # Multiplicar pela quantidade
        vol_total_item = vol_item * vol.quantidade
        
        total_m3 += vol_total_item
    
    return round(total_m3, 4)
```

### Mock Adapter

```python
class MockTransportadoraAdapter:
    async def consultar(self, cotacao: Cotacao, transportadora: Transportadora):
        """Simula resposta de uma transportadora"""
        
        # Simular latência (200-2000ms)
        await asyncio.sleep(random.uniform(0.2, 2.0))
        
        # 80% chance de sucesso
        if random.random() < 0.8:
            # Simular cálculo de frete
            valor_base = 100  # R$ 100 de base
            valor_por_kg = cotacao.peso * 2.50
            valor_por_m3 = cotacao.cubagem_m3 * 500
            valor_frete = valor_base + valor_por_kg + valor_por_m3
            
            prazo = random.randint(1, 7)  # 1-7 dias
            
            return {
                'status': 'success',
                'valor': round(valor_frete, 2),
                'prazo': prazo
            }
        else:
            # 20% chance de erro/timeout
            return {
                'status': 'error',
                'valor': None,
                'prazo': None
            }
```

### Database

#### Async SQLAlchemy
```python
# session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

DATABASE_URL = "postgresql+asyncpg://user:pass@host/db"

engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with SessionLocal() as session:
        yield session
```

#### Migrations (Alembic)
```bash
# Primeira migration (manual ou automática)
alembic revision --autogenerate -m "schema inicial"

# Aplicar
alembic upgrade head

# Ver histórico
alembic current
alembic history
```

### Testing

```bash
pytest tests/test_cubagem.py -v
```

Exemplo:
```python
def test_calculo_cubagem():
    volume = CotacaoVolume(
        quantidade=1,
        comprimento_cm=100,
        largura_cm=50,
        altura_cm=30,
        peso_kg=50
    )
    
    cubagem = calcular_cubagem([volume])
    
    # (1m * 0.5m * 0.3m) = 0.15 m³
    assert cubagem == 0.15
```

---

## Próximos Passos

### Sprint 2-3 (Em Progresso)
- [ ] Implementar `GET /api/v1/cotacoes` com paginação
- [ ] Adicionar filtros (status, data, transportadora)
- [ ] Criar primeira migration formal (Alembic)
- [ ] Testes de integração

### Sprint 4-6 (Adapters Reais)
- [ ] Adapter real Jamef (API)
- [ ] Adapter real Jadlog (API)
- [ ] Adapter real Braspress (API)
- [ ] Credenciais via variáveis de ambiente
- [ ] Error handling robusto

### Sprint 7-8 (n8n + Playwright)
- [ ] Transportadoras sem API
- [ ] Automação via n8n workflows
- [ ] Scraping com Playwright (último recurso)

### Sprint 9 (Integração ERP)
- [ ] Integração Sankhya
- [ ] Sincronização de vendas
- [ ] Dados de frete no ERP

### Funcionalidades Futuras
- [ ] Rastreamento em tempo real (webhook de transportadoras)
- [ ] Histórico de preços por rota
- [ ] Recomendações inteligentes
- [ ] Dashboard com métricas
- [ ] API pública para clientes
- [ ] Mobile app
- [ ] Notificações por email/SMS
- [ ] Integração com pick & pack

---

## Como Contribuir

### Setup Local para Desenvolvimento

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Rodando em Desenvolvimento Local (sem Docker)

```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: PostgreSQL
docker run -e POSTGRES_PASSWORD=frete -e POSTGRES_USER=frete -e POSTGRES_DB=frete -p 5432:5432 postgres:16-alpine
```

### Git Workflow

1. Create branch: `git checkout -b feature/sua-feature`
2. Commit: `git commit -m "feat: descrição clara"`
3. Push: `git push origin feature/sua-feature`
4. Pull Request

### Padrão de Commits

- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `refactor:` Refatoração
- `docs:` Documentação
- `test:` Testes
- `chore:` Manutenção

---

## Troubleshooting

### Backend não conecta ao PostgreSQL
```bash
# Verificar status dos containers
docker ps

# Ver logs
docker logs frete-system-postgres-1
docker logs frete-system-backend-1

# Recrear containers
docker compose down
docker compose up --build
```

### Frontend não conecta à API
```bash
# Verificar variável VITE_API_URL
echo $VITE_API_URL  # Deve ser http://localhost:8000/api/v1

# Verificar CORS no backend
# backend/core/config.py deve ter: CORS_ORIGINS = ["http://localhost:5173"]

# Limpar cache/localStorage
# F12 → Application → Clear Storage
```

### JWT Inválido
```bash
# Logout e login novamente
# localStorage é apagado automaticamente

# Ou manualmente:
# F12 → Console → localStorage.removeItem('token')
```

### Testes falhando
```bash
# Rodar com mais verbosidade
docker compose exec backend pytest -v -s

# Rodar teste específico
docker compose exec backend pytest tests/test_cubagem.py::test_calculo_cubagem -v
```

---

## Referências Úteis

### Documentação Oficial
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Alembic](https://alembic.sqlalchemy.org/)
- [React 18](https://react.dev/)
- [TypeScript](https://www.typescriptlang.org/)
- [TanStack Query](https://tanstack.com/query/latest)
- [Tailwind CSS](https://tailwindcss.com/)

### Ferramentas
- **Swagger/OpenAPI**: http://localhost:8000/docs
- **PostgreSQL CLI**: `docker compose exec postgres psql -U frete -d frete`
- **VS Code Extensions**: REST Client, SQLTools, Pylance, Thunder Client

### Contato
Para dúvidas sobre a arquitetura ou documentação, consulte o `README.md` raiz.

---

**Última atualização**: 2024-01-15  
**Versão do Projeto**: Sprint 1-3 (MVP)
