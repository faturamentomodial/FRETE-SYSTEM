import { FileUp } from "lucide-react";
import { useRef, useState } from "react";
import { useForm } from "react-hook-form";

import { Field, Input } from "../../components/ui";
import type { TabelaFreteCreate } from "../../types/tabelaFrete";

interface Props {
  transportadoraId: string;
  salvando: boolean;
  onSave: (dados: TabelaFreteCreate, arquivo: File) => Promise<void>;
  onCancel: () => void;
}

function dataFutura(dias: number) {
  const data = new Date();
  data.setDate(data.getDate() + dias);
  return data.toISOString().slice(0, 10);
}

export function TabelaFreteForm({ transportadoraId, salvando, onSave, onCancel }: Props) {
  const arquivoRef = useRef<HTMLInputElement>(null);
  const [arquivo, setArquivo] = useState<File | null>(null);
  const { register, handleSubmit, formState: { errors } } = useForm<TabelaFreteCreate>({
    defaultValues: {
      transportadora_id: transportadoraId,
      nome: "",
      codigo: "",
      versao: "",
      moeda: "BRL",
      fator_cubagem: undefined as unknown as number,
      data_inicio: "",
      data_fim: "",
    },
  });

  return (
    <form onSubmit={handleSubmit((dados) => {
      if (!arquivo) return;
      const base = arquivo.name.replace(/\.[^.]+$/, "");
      onSave({
        ...dados,
        nome: dados.nome.trim() || base,
        codigo: dados.codigo.trim() || `IMP-${Date.now()}`,
        versao: dados.versao.trim() || "1",
        fator_cubagem: Number.isFinite(dados.fator_cubagem) ? dados.fator_cubagem : 300,
        data_inicio: dados.data_inicio || new Date().toISOString().slice(0, 10),
        data_fim: dados.data_fim || dataFutura(90),
      }, arquivo);
    })} className="grid gap-3 sm:grid-cols-2 rounded-lg border border-border bg-surface2 p-4">
      <Field label="Nome">
        <Input {...register("nome")} placeholder="Preenchido pelo arquivo se vazio" />
      </Field>
      <Field label="Código">
        <Input {...register("codigo")} placeholder="Gerado automaticamente se vazio" />
      </Field>
      <Field label="Versão">
        <Input {...register("versao")} placeholder="1" />
      </Field>
      <Field label="Fator de cubagem (kg/m³)">
        <Input type="number" min="1" step="0.01" {...register("fator_cubagem", { valueAsNumber: true })} placeholder="300" />
      </Field>
      <Field label="Início da vigência">
        <Input type="date" {...register("data_inicio")} />
      </Field>
      <Field label="Fim da vigência">
        <Input type="date" {...register("data_fim")} />
      </Field>
      <div className="sm:col-span-2">
        <span className="text-xs font-medium text-text-secondary">Documento da tabela *</span>
        <input ref={arquivoRef} className="hidden" type="file" accept=".pdf,.xlsx,.xls,.xlsm,.doc,.docx,.csv,.png,.jpg,.jpeg" onChange={(e) => setArquivo(e.target.files?.[0] ?? null)} />
        <button type="button" onClick={() => arquivoRef.current?.click()} onDragOver={(e) => { e.preventDefault(); e.currentTarget.classList.add("border-state-info"); }} onDragLeave={(e) => e.currentTarget.classList.remove("border-state-info")} onDrop={(e) => { e.preventDefault(); e.currentTarget.classList.remove("border-state-info"); setArquivo(e.dataTransfer.files?.[0] ?? null); }} className="mt-1.5 flex min-h-20 w-full items-center justify-center gap-2 rounded border border-dashed border-border bg-surface px-3 text-sm text-text-secondary hover:border-state-info">
          <FileUp size={18} /> {arquivo ? arquivo.name : "Selecionar PDF, Excel, Word, CSV ou imagem"}
        </button>
        <p className="mt-1 text-center text-xs text-text-secondary">Clique para selecionar ou arraste o arquivo para esta área.</p>
        <p className="mt-1 text-xs text-text-secondary">Após confirmar, o arquivo será enviado e analisado. Nenhuma tabela entra em cotação sem sua revisão e aprovação.</p>
      </div>
      {Object.keys(errors).length > 0 && <p className="sm:col-span-2 text-xs text-state-error">Revise os campos informados.</p>}
      <div className="sm:col-span-2 flex justify-end gap-2">
        <button type="button" onClick={onCancel} className="h-9 rounded border border-border px-3 text-sm">Cancelar</button>
        <button disabled={salvando || !arquivo} className="h-9 rounded bg-state-info px-3 text-sm text-white disabled:opacity-50">
          {salvando ? "Enviando e analisando..." : "Criar e analisar"}
        </button>
      </div>
    </form>
  );
}
