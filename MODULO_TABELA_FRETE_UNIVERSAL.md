# Módulo de Tabela de Frete Universal - Documentação

## 📋 Resumo Executivo

O **Módulo de Tabela de Frete Universal** foi implementado no FRETE SYSTEM para permitir a cotação de fretes através de **tabelas comerciais estruturadas**, não apenas via APIs de transportadoras.

### Objetivos
✅ Centralizar diferentes fontes de cotação (API, PDF, Excel, Imagem, etc.)  
✅ Separar extração de dados, normalização, validação e cálculo  
✅ Implementar motor determinístico de cálculo  
✅ Preparar infraestrutura para IA sem acoplamento  
✅ Manter auditoria completa de todos os processos

---

## 🏗️ Arquitetura Implementada

### Níveis de Dados

```
DOCUMENTO ORIGINAL (PDF, Excel, Imagem)
    ↓ (DocumentExtractor)
CONTEÚDO EXTRAÍDO (texto, tabelas, metadados)
    ↓ (AIExtractionProvider)
JSON NORMALIZADO (dados estruturados)
    ↓ (ValidationProvider)
TABELA APROVADA (regras e tarifas)
    ↓ (TabelaFreteCalculoService)
RESULTADO DA COTAÇÃO (valor, prazo, breakdown)
```

### Arquitetura de Adapters

```
TransportadoraAdapter (interface abstrata)
    ├── MockTransportadoraAdapter (APIs mock)
    ├── JamefAdapter (futura integração)
    ├── BraspressAdapter (futura integração)
    └── TabelaFreteAdapter ← NOVO: tabelas estruturadas
```

O sistema **não diferencia** entre uma cotação via API e uma cotação via tabela. Ambas retornam `ResultadoCotacao` padronizado.

---

## 📦 Componentes Implementados

### 1. **Modelos SQLAlchemy** (`backend/app/models/models.py`)

#### TabelaFrete
Tabela comercial com versioning e ciclo de vida:
- Status: `DRAFT` → `PROCESSING` → `REVIEW` → `APPROVED` → `ACTIVE` → `EXPIRED`/`CANCELLED`
- Suporta múltiplas versões (ex: 2026.1, 2026.2)
- Auditoria: quem criou, quem aprovou, quando

```python
TabelaFrete(
    transportadora_id: str,      # FK para Transportadora
    nome: str,                   # "Tabela Q4 2026"
    codigo: str,                 # "TAB-TRANS-2026"
    versao: str,                 # "2026.1"
    status: str,                 # draft, active, etc.
    data_inicio: datetime,       # Vigência
    data_fim: datetime,          # Vigência
    fator_cubagem: float,        # kg/m³ - padrão 300
    # ... relacionamentos com regras
)
```

#### DocumentoFrete
Armazena documentos originais para auditoria (nunca são apagados):
- Nome, tipo, hash SHA-256 (deduplicação)
- Caminho de storage
- Metadados (número de páginas, origem, etc.)
- Permite rastrear: "qual tabela veio deste PDF?"

#### Componentes de Regras
Cada um é uma entidade separada para máxima flexibilidade:

| Entidade | Propósito | Exemplo |
|----------|-----------|---------|
| **AbrangenciaFrete** | Cobertura geográfica | SP, capital, 01000-05999 CEP |
| **RegraRota** | Rotas específicas | SP→MG, São Paulo→Rio |
| **RegraCubagem** | Fator de volume | 300 kg/m³ |
| **RegraPeso** | Faixas de peso | 0-10kg: R$50, 10-20kg: R$65 |
| **TarifaFrete** | Tarifas base | Fixo, por kg, percentual |
| **TaxaFrete** | Taxas adicionais | GRIS, Ad Valorem, Pedágio |
| **RegraFreteMinimo** | Frete mínimo | R$ 50 |
| **RegraExcedente** | Peso extra | Acima 100kg: +R$2,50/kg |
| **RegraPrazo** | Entrega | 4 dias úteis SP→MG |
| **RegraPesoConsiderado** | Qual peso usar | MAX(real, cubado) |
| **AuditoriaTabela** | Histórico | Criação, edição, aprovação |

### 2. **Schemas Pydantic** (`backend/app/schemas/tabela_frete.py`)

Validação de dados em todos os fluxos:
- **Entrada**: `TabelaFreteCreate`, `RegraPesoCreate`, etc.
- **Saída**: `TabelaFreteResponse`, `TabelaFreteDetalhada`
- **Processamento**: `ExtratedTableData`, `TabelaFreteAnaliseResultado`
- **Cálculo**: `DadosCotacaoTabelaFrete`, `ResultadoCalculoTabelaFrete`

Exemplo de resposta de cálculo:
```python
{
    "status": "success",
    "frete_base": 350.00,
    "taxas_detalhadas": [
        {"tipo": "GRIS", "nome": "GRIS", "valor": 10.50},
        {"tipo": "PEDAGIO", "nome": "Pedágio", "valor": 5.00}
    ],
    "total_taxas": 15.50,
    "frete_com_minimo": 360.00,  # aplicado
    "valor_total": 375.50,
    "prazo_dias": 4,
    "peso_considerado_kg": 25.5
}
```

### 3. **Interfaces Abstratas** (`backend/app/integrations/extracoes/__init__.py`)

Permite múltiplos provedores de IA/OCR **sem acoplamento**:

```python
class DocumentExtractor(ABC):
    """Extrai de PDF, Excel, Word, Imagem, CSV"""
    async def extrair(caminho: str) -> list[ExtratedContent]
    async def extrair_tabelas(caminho: str) -> list[TabelaFreteExtraidaRaw]

class AIExtractionProvider(ABC):
    """Interpreta com LLM/IA"""
    async def normalizar_tabela(tabela_raw, contexto) -> dict
    async def detectar_campos_suspeitos(tabela_raw) -> list[dict]
    async def extrair_metadados(tabela_raw) -> dict

class ValidationProvider(ABC):
    """Valida dados estruturados"""
    def validar_tabela(dados) -> (bool, [erros], [avisos])
    def detectar_sobreposicoes(dados) -> [conflitos]
    def verificar_completude(dados) -> (percentual, campos_faltando)

class OCRProvider(ABC):
    """Reconhecimento óptico"""
    async def processar_imagem(caminho) -> str
    async def processar_pdf_escaneado(caminho) -> [textos_por_página]
```

No futuro, múltiplas implementações sem alterar domínio:
- OpenAI GPT, Claude (LLM)
- PaddleOCR, Tesseract (OCR local)
- Custom (seus próprios extractores)

### 4. **TabelaFreteAdapter** (`backend/app/integrations/transportadoras/tabela_frete.py`)

Implementa `TransportadoraAdapter` para integração perfeita:

```python
class TabelaFreteAdapter(TransportadoraAdapter):
    async def cotar(cotacao_payload: dict) -> ResultadoCotacao:
        # Valida tabela
        # Valida vigência
        # Chama TabelaFreteCalculoService
        # Retorna ResultadoCotacao (padrão)
```

**Benefício**: Tabelas são tratadas como qualquer outro adapter. Cotações não sabem se vieram de API ou tabela.

### 5. **Motor de Cálculo Determinístico** (`backend/app/services/tabela_frete/calculo.py`)

`TabelaFreteCalculoService` implementa o fluxo completo e determinístico:

```python
async def calcular(tabela_frete_id, dados_cotacao) -> dict:
    # 1. Valida entrada
    # 2. Calcula peso cubado (se dimensões fornecidas)
    # 3. Determina peso considerado (real vs cubado)
    # 4. Localiza abrangência (UF, CEP, região, etc.)
    # 5. Localiza tarifa (por peso, tipo, prioridade)
    # 6. Calcula frete base
    # 7. Aplica excedente de peso (se houver)
    # 8. Aplica frete mínimo
    # 9. Calcula taxas (GRIS, Ad Valorem, etc.)
    # 10. Calcula impostos
    # 11. Determina prazo
    # 12. Retorna breakdown completo
```

**Não executa código arbitrário**. Apenas interpreta regras estruturadas.

### 6. **Endpoints REST** (`backend/app/api/v1/endpoints/tabelas_frete.py`)

#### CRUD Básico
```
POST   /api/v1/tabelas-frete              # Criar (status: draft)
GET    /api/v1/tabelas-frete              # Listar com filtros
GET    /api/v1/tabelas-frete/{id}         # Obter detalhes
PUT    /api/v1/tabelas-frete/{id}         # Atualizar (apenas draft)
DELETE /api/v1/tabelas-frete/{id}         # Deletar (apenas draft)
```

#### Upload e Processamento
```
POST   /api/v1/tabelas-frete/{id}/upload  # Upload documento
POST   /api/v1/tabelas-frete/{id}/analisar # Análise com IA/OCR
GET    /api/v1/tabelas-frete/{id}/revisao  # Dados para revisão
```

#### Fluxo de Aprovação
```
POST   /api/v1/tabelas-frete/{id}/aprovar  # Aprovar (review → approved)
POST   /api/v1/tabelas-frete/{id}/ativar   # Ativar (approved → active)
POST   /api/v1/tabelas-frete/{id}/cancelar # Cancelar
POST   /api/v1/tabelas-frete/{id}/status   # Mudar status manualmente
```

#### Histórico
```
GET    /api/v1/tabelas-frete/{id}/historico   # Auditoria
GET    /api/v1/tabelas-frete/{id}/documentos  # Documentos originais
```

### 7. **Migration Alembic** (`backend/alembic/versions/001_initial_tabela_frete.py`)

Cria todas as 13 tabelas com:
- Foreign keys apropriadas
- Índices em colunas de busca (transportadora_id, status, data_inicio, etc.)
- Constraints de integridade

---

## 🔄 Ciclo de Vida de uma Tabela

```
1. CRIAÇÃO (DRAFT)
   └─ POST /api/v1/tabelas-frete
   └─ Status: DRAFT (editável)

2. IMPORTAÇÃO (DRAFT → PROCESSING)
   └─ POST /api/v1/tabelas-frete/{id}/upload (documento)
   └─ POST /api/v1/tabelas-frete/{id}/analisar (IA/OCR)
   └─ Status: PROCESSING (análise em andamento)

3. REVISÃO (PROCESSING → REVIEW)
   └─ GET /api/v1/tabelas-frete/{id}/revisao
   └─ Mostra: documento, dados extraídos, confiança, erros
   └─ Usuário edita se necessário

4. APROVAÇÃO (REVIEW → APPROVED)
   └─ POST /api/v1/tabelas-frete/{id}/aprovar
   └─ Registra quem aprovou e quando

5. ATIVAÇÃO (APPROVED → ACTIVE)
   └─ POST /api/v1/tabelas-frete/{id}/ativar
   └─ Tabela passa a ser usada em cotações

6. VIGÊNCIA
   └─ Cotação verifica: data_inicio <= agora <= data_fim
   └─ Se fora do período: erro "TABELA_FORA_VIGENCIA"

7. EXPIRAÇÃO/CANCELAMENTO (ACTIVE → EXPIRED/CANCELLED)
   └─ Automático (data_fim) ou manual (POST .../cancelar)
   └─ Tabela não é deletada (auditoria)
```

---

## 💻 Integrando com Cotações Existentes

### Fluxo Atual (sem mudanças)
```
POST /api/v1/cotacoes
├─ MockTransportadoraAdapter (Jamef, Jadlog, etc.)
└─ Resultado: valor_frete, prazo_dias
```

### Fluxo com Tabelas (novo)
```
POST /api/v1/cotacoes
├─ MockTransportadoraAdapter (Jamef, Jadlog, etc.)
├─ TabelaFreteAdapter (Transportadora X com tabela)
└─ Resultado: valor_frete, prazo_dias (ambos)
```

**Modificação necessária**: `backend/app/services/cotacao_service.py`
- Ao selecionar transportadora, verificar se tem tabela ativa
- Se sim: criar instância de `TabelaFreteAdapter`
- Motor de cotações não vê diferença

---

## 🧪 Exemplos de Uso

### 1. Criar Tabela (Draft)
```bash
POST /api/v1/tabelas-frete
{
    "transportadora_id": "t1",
    "nome": "Tabela Braspress Q4 2026",
    "codigo": "BRASPRESS-Q4",
    "versao": "2026.2",
    "moeda": "BRL",
    "fator_cubagem": 300.0,
    "data_inicio": "2026-10-01T00:00:00",
    "data_fim": "2026-12-31T23:59:59",
    "observacoes": "Conforme contrato 12345"
}
```

### 2. Adicionar Regras (via CRUD de componentes - futura implementação)
```bash
POST /api/v1/tabelas-frete/{id}/abrangencias
{ "tipo": "UF", "uf": "SP", "prioridade": 0 }

POST /api/v1/tabelas-frete/{id}/tarifas
{
    "tipo_tarifa": "POR_KG",
    "valor": 12.50,
    "abrangencia_id": "abc123",
    "prioridade": 0
}

POST /api/v1/tabelas-frete/{id}/taxas
{
    "tipo": "GRIS",
    "nome": "GRIS",
    "tipo_calculo": "PERCENTUAL",
    "percentual": 0.30,
    "base_calculo": "VALOR_NF",
    "valor_minimo": 10.0
}
```

### 3. Aprovar e Ativar
```bash
POST /api/v1/tabelas-frete/{id}/aprovar
{ "motivo": "Conforme contrato Q4 2026" }

POST /api/v1/tabelas-frete/{id}/ativar
# Status: ACTIVE - pronto para usar em cotações
```

### 4. Usar em Cotação
```bash
POST /api/v1/cotacoes
{
    "origem_cep": "01310100",
    "destino_uf": "RJ",
    "peso": 25.5,
    "comprimento_cm": 100,
    "largura_cm": 50,
    "altura_cm": 30,
    "valor_nf": 5000.0,
    "transportadoras_ids": ["t1", "t2", "t3", "tabela-braspress-2026"]
}
```

---

## 📊 Validações Implementadas

### Validação de Entrada (antes do cálculo)
- ✅ Peso obrigatório e > 0
- ✅ Destino UF obrigatório
- ✅ Origem UF obrigatório
- ✅ Dimensões (se fornecidas) devem ser > 0

### Validação de Tabela
- ✅ Tabela existe?
- ✅ Status é ACTIVE?
- ✅ Está dentro da vigência?
- ✅ Transportadora existe?

### Validação de Cobertura
- ✅ Há abrangência para o destino?
- ✅ Há tarifa para o peso?
- ✅ Faixa de CEP cobre?
- ✅ Região está coberta?

### Validação de Dados (pré-aprovação)
- Detectar sobreposição de faixas de peso
- Verificar lacunas (gaps) em cobertura
- Validar percentuais (0-100)
- Validar datas (início < fim)
- Verificar completude de mapeamento

---

## 🔒 Segurança

✅ **Sem execução de código arbitrário**
- Apenas regras estruturadas e determinísticas

✅ **Auditoria completa**
- DocumentoFrete: nunca apaga documento original
- AuditoriaTabela: registra cada ação
- Quem: user_id
- O quê: ação (criada, editada, aprovada)
- Quando: timestamp
- Como mudou: alteracoes (JSON)

✅ **Validação de upload**
- MIME type
- Tamanho máximo
- Hash SHA-256 (deduplicação)
- Separar storage

✅ **Sem dados sensíveis em logs**
- Não registra tokens, passwords, API keys
- Apenas informações de negócio

---

## 🚀 Próximas Fases

### Fase 8: Testes Backend
- Testes de validação
- Testes de cálculo (faixa, per kg, percentual)
- Testes de taxas
- Testes de vigência

### Fase 9: Extractores
- PDFExtractor (pypdf)
- SpreadsheetExtractor (openpyxl)
- ImageOCRExtractor (paddleocr/tesseract)
- CSVExtractor

### Fase 10: Frontend
- TabelasFreteManager.tsx (lista, CRUD)
- TabelaFreteForm.tsx (criar/editar)
- TabelaFreteRevisao.tsx (revisão humana)
- useTabelaFrete.ts (hook customizado)

### Fase 11: Integração com Cotações
- Modificar cotacao_service.py
- UI para selecionar tipo de transportadora
- Suportar tabelas em paralelo com APIs

---

## 📚 Referências de Código

| Componente | Arquivo | Linhas |
|-----------|---------|--------|
| Modelos | `backend/app/models/models.py` | 98-350+ |
| Schemas | `backend/app/schemas/tabela_frete.py` | 1-400+ |
| Interfaces | `backend/app/integrations/extracoes/__init__.py` | 1-150+ |
| Adapter | `backend/app/integrations/transportadoras/tabela_frete.py` | 1-150+ |
| Serviço Cálculo | `backend/app/services/tabela_frete/calculo.py` | 1-400+ |
| Endpoints | `backend/app/api/v1/endpoints/tabelas_frete.py` | 1-400+ |
| Migration | `backend/alembic/versions/001_initial_tabela_frete.py` | 1-300+ |

---

## 📝 Notas Importantes

1. **Banco de dados**: Execute a migration antes de usar
   ```bash
   cd backend
   alembic upgrade head
   ```

2. **Ordem de uso**: Sempre DRAFT → PROCESSING → REVIEW → APPROVED → ACTIVE

3. **Não pode voltar**: ACTIVE → APPROVED não é permitido (apenas cancelar)

4. **Auditoria**: Tabelas aprovadas não podem ser deletadas, apenas canceladas

5. **IA desacoplada**: Implementar `AIExtractionProvider` conforme necessário (LLM, OCR, etc.)

6. **Cálculo determinístico**: Sem randomness, sem IA no cálculo final. IA apenas interpreta documentos.

---

## 🎯 Fluxo de Extração de Documento (Futuro)

```
ARQUIVO
  ├─ DocumentExtractor.extrair() → ExtratedContent
  │  └─ PDFExtractor, SpreadsheetExtractor, ImageOCRExtractor, etc.
  │
  ├─ DocumentExtractor.extrair_tabelas() → TabelaFreteExtraidaRaw
  │
  ├─ AIExtractionProvider.normalizar_tabela() → dict (JSON)
  │  └─ Interpreta campos, estrutura, relacionamentos
  │
  ├─ AIExtractionProvider.detectar_campos_suspeitos() → [campos]
  │  └─ Score de confiança por campo
  │
  ├─ ValidationProvider.validar_tabela() → (bool, [erros], [avisos])
  │
  └─ Resultado: TabelaFreteAnaliseResultado
     ├─ status: success | error | partial
     ├─ dados_extraidos: ExtratedTableData
     ├─ confianca_extracao: 0.95
     ├─ erros: []
     ├─ avisos: ["Campo 'taxa_minima' não encontrado"]
     └─ campos_com_duvida: ["valor_gris", "fator_cubagem"]
```

Usuário revisa → Aprova → Ativa → Pronta para uso em cotações

