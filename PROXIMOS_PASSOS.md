# Próximos Passos - Módulo de Tabela de Frete Universal

## 📋 Status Atual

✅ **Implementado (13 de 13 tarefas)**
- Modelos SQLAlchemy
- Schemas Pydantic
- Interfaces abstratas de extração
- TabelaFreteAdapter
- Motor de cálculo determinístico
- Endpoints REST
- Migration Alembic
- Testes unitários backend
- Frontend para upload e endpoint de armazenamento seguro
- Frontend de análise, revisão, aprovação e ativação
- Integração das tabelas ativas com o motor de cotações
- Teste E2E reproduzível do fluxo completo

⏳ **Pendente (0 de 13 tarefas)**

---

## 🚀 Fase 10: Frontend para Upload (Prioridade 🔴 Alta)

### Objetivo
Permitir usuários fazer upload de documentos e ver a análise estruturada.

### Arquivos a Criar

#### 1. **Novo Hook: `frontend/src/hooks/useTabelaFrete.ts`**

```typescript
import { useMutation, useQuery } from '@tanstack/react-query';
import { tabelaFreteService } from '../services/tabelaFreteService';

export const useTabelaFrete = () => {
  const criar = useMutation({
    mutationFn: (data) => tabelaFreteService.criar(data),
    onSuccess: () => console.log('Tabela criada'),
  });

  const listar = useQuery({
    queryKey: ['tabelas-frete'],
    queryFn: () => tabelaFreteService.listar(),
  });

  const obterDetalhes = (id: string) =>
    useQuery({
      queryKey: ['tabelas-frete', id],
      queryFn: () => tabelaFreteService.obter(id),
    });

  const upload = useMutation({
    mutationFn: ({ id, arquivo }: { id: string; arquivo: File }) =>
      tabelaFreteService.uploadDocumento(id, arquivo),
  });

  const analisar = useMutation({
    mutationFn: ({ id, documento_id }: { id: string; documento_id: string }) =>
      tabelaFreteService.analisar(id, documento_id),
  });

  const aprovar = useMutation({
    mutationFn: ({ id, motivo }: { id: string; motivo: string }) =>
      tabelaFreteService.aprovar(id, motivo),
  });

  const ativar = useMutation({
    mutationFn: (id: string) => tabelaFreteService.ativar(id),
  });

  return { criar, listar, obterDetalhes, upload, analisar, aprovar, ativar };
};
```

#### 2. **Serviço API: `frontend/src/services/tabelaFreteService.ts`**

```typescript
import { API_BASE_URL } from '../config';

class TabelaFreteService {
  private baseUrl = `${API_BASE_URL}/api/v1/tabelas-frete`;

  async criar(data: any) {
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Erro ao criar tabela');
    return response.json();
  }

  async listar(transportadora_id?: string) {
    let url = this.baseUrl;
    if (transportadora_id) url += `?transportadora_id=${transportadora_id}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error('Erro ao listar tabelas');
    return response.json();
  }

  async obter(id: string) {
    const response = await fetch(`${this.baseUrl}/${id}`);
    if (!response.ok) throw new Error('Erro ao obter tabela');
    return response.json();
  }

  async uploadDocumento(id: string, arquivo: File) {
    const formData = new FormData();
    formData.append('arquivo', arquivo);
    const response = await fetch(`${this.baseUrl}/${id}/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) throw new Error('Erro no upload');
    return response.json();
  }

  async analisar(id: string, documento_id: string) {
    const response = await fetch(`${this.baseUrl}/${id}/analisar?documento_id=${documento_id}`, {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Erro na análise');
    return response.json();
  }

  async aprovar(id: string, motivo: string) {
    const response = await fetch(`${this.baseUrl}/${id}/aprovar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ motivo }),
    });
    if (!response.ok) throw new Error('Erro ao aprovar');
    return response.json();
  }

  async ativar(id: string) {
    const response = await fetch(`${this.baseUrl}/${id}/ativar`, {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Erro ao ativar');
    return response.json();
  }
}

export const tabelaFreteService = new TabelaFreteService();
```

#### 3. **Componente: `frontend/src/pages/Transportadoras/TabelasFreteManager.tsx`**

```typescript
import React, { useState } from 'react';
import { useTabelaFrete } from '../../hooks/useTabelaFrete';

export const TabelasFreteManager: React.FC<{ transportadora_id: string }> = ({
  transportadora_id,
}) => {
  const [showForm, setShowForm] = useState(false);
  const { listar, criar } = useTabelaFrete();
  const { data: tabelas = [] } = listar;

  const handleCriar = async (dados: any) => {
    try {
      await criar.mutateAsync({ ...dados, transportadora_id });
      setShowForm(false);
    } catch (error) {
      console.error('Erro:', error);
    }
  };

  return (
    <div>
      <h2>Tabelas de Frete</h2>
      <button onClick={() => setShowForm(!showForm)}>
        + Nova Tabela
      </button>

      {showForm && (
        <TabelaFreteForm
          transportadora_id={transportadora_id}
          onSave={handleCriar}
          onCancel={() => setShowForm(false)}
        />
      )}

      <div className="grid gap-4 mt-4">
        {tabelas.map((tabela: any) => (
          <TabelaFreteCard key={tabela.id} tabela={tabela} />
        ))}
      </div>
    </div>
  );
};
```

#### 4. **Formulário: `frontend/src/pages/Transportadoras/TabelaFreteForm.tsx`**

```typescript
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';

interface TabelaFreteFormProps {
  transportadora_id: string;
  onSave: (data: any) => Promise<void>;
  onCancel: () => void;
}

export const TabelaFreteForm: React.FC<TabelaFreteFormProps> = ({
  transportadora_id,
  onSave,
  onCancel,
}) => {
  const { register, handleSubmit } = useForm({
    defaultValues: {
      transportadora_id,
      nome: '',
      codigo: '',
      versao: '2026.1',
      moeda: 'BRL',
      fator_cubagem: 300,
      data_inicio: new Date().toISOString().split('T')[0],
      data_fim: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000)
        .toISOString()
        .split('T')[0],
    },
  });

  const onSubmit = async (data: any) => {
    await onSave(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 border p-4 rounded">
      <input
        {...register('nome')}
        placeholder="Nome da tabela"
        className="w-full border px-2 py-1"
      />
      <input
        {...register('codigo')}
        placeholder="Código (ex: TABELA-2026-Q4)"
        className="w-full border px-2 py-1"
      />
      <input
        {...register('versao')}
        placeholder="Versão (ex: 2026.1)"
        className="w-full border px-2 py-1"
      />
      <input
        {...register('fator_cubagem', { valueAsNumber: true })}
        type="number"
        placeholder="Fator de cubagem (kg/m³)"
        className="w-full border px-2 py-1"
      />
      <input
        {...register('data_inicio')}
        type="date"
        className="w-full border px-2 py-1"
      />
      <input
        {...register('data_fim')}
        type="date"
        className="w-full border px-2 py-1"
      />

      <div className="flex gap-2">
        <button
          type="submit"
          className="px-4 py-2 bg-blue-500 text-white rounded"
        >
          Criar
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 bg-gray-300 rounded"
        >
          Cancelar
        </button>
      </div>
    </form>
  );
};

interface TabelaFreteCardProps {
  tabela: any;
}

export const TabelaFreteCard: React.FC<TabelaFreteCardProps> = ({ tabela }) => {
  const [showUpload, setShowUpload] = useState(false);
  const { upload } = useTabelaFrete();

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      await upload.mutateAsync({ id: tabela.id, arquivo: file });
      setShowUpload(false);
    } catch (error) {
      console.error('Erro no upload:', error);
    }
  };

  return (
    <div className="border p-4 rounded bg-white">
      <h3 className="font-bold">{tabela.nome}</h3>
      <p className="text-sm text-gray-600">
        {tabela.versao} • {tabela.status}
      </p>
      <div className="mt-2 flex gap-2">
        <button
          onClick={() => setShowUpload(!showUpload)}
          className="px-3 py-1 text-sm bg-green-500 text-white rounded"
        >
          Upload
        </button>
        <button className="px-3 py-1 text-sm bg-blue-500 text-white rounded">
          Revisar
        </button>
      </div>

      {showUpload && (
        <div className="mt-2 border-t pt-2">
          <input
            type="file"
            onChange={handleUpload}
            accept=".pdf,.xlsx,.xls,.docx,.jpg,.png,.csv"
          />
        </div>
      )}
    </div>
  );
};
```

### Checklist Fase 10
- [ ] Criar hook `useTabelaFrete.ts`
- [ ] Criar serviço `tabelaFreteService.ts`
- [ ] Criar componente `TabelasFreteManager.tsx`
- [ ] Criar formulário `TabelaFreteForm.tsx`
- [ ] Criar card `TabelaFreteCard.tsx`
- [ ] Adicionar rota no `frontend/src/routes/index.tsx`
- [ ] Testar upload e listagem

---

## 🎯 Fase 11: Frontend de Revisão

### Arquivos a Criar

1. **`frontend/src/pages/Transportadoras/TabelaFreteRevisao.tsx`**
   - Mostrar documento original (iframe para PDF)
   - Mostrar dados extraídos (tabela)
   - Mostrar confiança da extração
   - Campos com dúvida marcados
   - Permitir edição dos dados
   - Botão de aprovar

2. **`frontend/src/components/DocumentoViewer.tsx`**
   - Visualizar PDF
   - Visualizar imagem
   - Visualizar Excel

### Exemplo de Dados Retornados pelo Backend

```json
{
  "tabela_frete_id": "abc123",
  "documento_original": {
    "id": "doc001",
    "nome_arquivo": "tabela_transportadora_2026.pdf",
    "tipo_arquivo": "pdf"
  },
  "dados_extraidos": {
    "transportadora": "Transportadora X",
    "validade_inicio": "2026-08-01",
    "validade_fim": "2027-07-31",
    "abrangencias": [
      {
        "tipo": "UF",
        "uf": "SP"
      }
    ],
    "tarifas": [
      {
        "tipo_tarifa": "POR_KG",
        "valor": 12.50
      }
    ]
  },
  "confianca_extracao": 0.92,
  "campos_com_duvida": ["fator_cubagem", "valor_gris"],
  "avisos": ["Não encontrado taxa de pedágio"]
}
```

---

## 🔗 Fase 12: Integração com Cotações

### Modificação em `backend/app/services/cotacao_service.py`

```python
async def executar_cotacao(cotacao: CotacaoCreate) -> list[ResultadoTransportadora]:
    """Adiciona suporte para tabelas de frete."""
    ids = cotacao.transportadoras_ids or list(TRANSPORTADORAS_DISPONIVEIS.keys())
    payload = {
        "peso": cotacao.peso,
        "valor_nf": cotacao.valor_nf,
        "origem_uf": cotacao.origem_uf,
        "destino_uf": cotacao.destino_uf,
        "origem_cep": cotacao.origem_cep,
        "destino_cep": cotacao.destino_cep,
        "comprimento_cm": cotacao.volumes[0].comprimento_cm if cotacao.volumes else None,
        "largura_cm": cotacao.volumes[0].largura_cm if cotacao.volumes else None,
        "altura_cm": cotacao.volumes[0].altura_cm if cotacao.volumes else None,
    }

    tarefas = []
    for tid in ids:
        if tid in TRANSPORTADORAS_DISPONIVEIS:
            # Adapter de API
            tarefas.append(_cotar_uma(tid, TRANSPORTADORAS_DISPONIVEIS[tid], payload))
        else:
            # Verificar se é ID de tabela de frete
            tabela = await _carregar_tabela_frete(tid)
            if tabela:
                adapter = TabelaFreteAdapter(db_session, tid)
                tarefas.append(_cotar_tabela(tid, adapter, payload))

    return await asyncio.gather(*tarefas)
```

---

## 🧪 Fase 13: Testes E2E

### Usando Playwright/Cypress

```typescript
describe('Tabela de Frete - Fluxo Completo', () => {
  it('Deve criar, fazer upload, revisar e aprovar uma tabela', async ({ page }) => {
    // 1. Login
    await page.goto('http://localhost:5173/login');
    await page.fill('input[name="email"]', 'admin@fretesystem.com');
    await page.fill('input[name="password"]', 'admin123');
    await page.click('button:has-text("Login")');

    // 2. Ir para tabelas de frete
    await page.goto('http://localhost:5173/transportadoras/t1/tabelas');

    // 3. Criar nova tabela
    await page.click('button:has-text("+ Nova Tabela")');
    await page.fill('input[placeholder="Nome da tabela"]', 'Tabela Test 2026');
    await page.fill('input[placeholder="Código"]', 'TEST-2026');
    await page.click('button:has-text("Criar")');

    // 4. Fazer upload
    await page.click('button:has-text("Upload")');
    await page.setInputFiles('input[type="file"]', 'test-tabela.pdf');
    await page.click('button:has-text("Analisar")');

    // 5. Aguardar análise
    await page.waitForTimeout(3000);

    // 6. Revisar
    await page.click('button:has-text("Revisar")');
    // ... verificar dados extraídos
    await page.click('button:has-text("Aprovar")');

    // 7. Ativar
    await page.click('button:has-text("Ativar")');

    // 8. Usar em cotação
    await page.goto('http://localhost:5173/nova-cotacao');
    // ... verificar que tabela aparece como opção
  });
});
```

---

## 📦 Dependências Necessárias

### Backend (adicionar em `requirements.txt`)
```
python-multipart==0.0.6      # Upload de arquivos
python-magic==0.4.27          # Validação MIME type
pypdf==4.0.1                  # Extração de PDF
openpyxl==3.10.10            # Leitura Excel
python-docx==0.8.11          # Leitura Word
paddleocr==2.7.0.3           # OCR (opcional, pesado)
# ou
pytesseract==0.3.10           # Wrapper Tesseract (mais leve)
```

### Frontend (já deve ter)
```json
{
  "@tanstack/react-query": "^5.56.2",
  "react-hook-form": "^7.53.0"
}
```

---

## 🛠️ Como Rodar Agora

### 1. Executar Migration
```bash
cd backend
python -m alembic upgrade head
```

### 2. Rodar Testes Backend
```bash
pytest tests/test_tabela_frete_calculo.py -v
```

### 3. Testar Endpoints (Postman/cURL)
```bash
# Criar tabela
curl -X POST http://localhost:8000/api/v1/tabelas-frete \
  -H "Content-Type: application/json" \
  -d '{
    "transportadora_id": "t1",
    "nome": "Tabela Test",
    "codigo": "TEST",
    "versao": "2026.1",
    "data_inicio": "2026-08-01T00:00:00",
    "data_fim": "2026-12-31T23:59:59"
  }'

# Listar
curl http://localhost:8000/api/v1/tabelas-frete
```

---

## 📝 Checklist Final

- [x] Fase 10: Frontend upload concluído
- [x] Fase 11: Frontend revisão concluído
- [x] Fase 12: Integração com cotações concluído
- [x] Fase 13: Testes E2E concluído
- [x] Documentação atualizada
- [ ] Repositório atualizado
- [ ] Release em produção

---

## 🎓 Recursos Úteis

- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Query Docs](https://tanstack.com/query/latest)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
