import { useRef, useState } from "react";
import { Upload } from "lucide-react";

import { Badge, Card } from "../../components/ui";
import { useAnalisarTabelaFrete, useAtivarTabelaFrete, useUploadTabelaFrete } from "../../hooks/useTabelaFrete";
import type { TabelaFreteListItem, TabelaFreteStatus } from "../../types/tabelaFrete";

const statusInfo: Record<TabelaFreteStatus, { texto: string; tone: "default" | "success" | "warning" | "error" | "info" }> = {
  draft: { texto: "Rascunho", tone: "default" },
  processing: { texto: "Processando", tone: "info" },
  review: { texto: "Em revisão", tone: "warning" },
  approved: { texto: "Aprovada", tone: "success" },
  active: { texto: "Ativa", tone: "success" },
  expired: { texto: "Expirada", tone: "warning" },
  cancelled: { texto: "Cancelada", tone: "error" },
};

export function TabelaFreteCard({ tabela, onReview }: { tabela: TabelaFreteListItem; onReview: () => void }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const upload = useUploadTabelaFrete();
  const analisar = useAnalisarTabelaFrete(tabela.transportadora_id);
  const ativar = useAtivarTabelaFrete(tabela.transportadora_id);
  const [documentoId, setDocumentoId] = useState<string | null>(null);
  const [mensagem, setMensagem] = useState("");
  const info = statusInfo[tabela.status];

  async function enviar(arquivo?: File) {
    if (!arquivo) return;
    setMensagem("");
    try {
      const resultado = await upload.mutateAsync({ tabelaId: tabela.id, arquivo });
      setDocumentoId(resultado.documento_id);
      setMensagem("Documento recebido. Inicie a análise.");
    } catch (error) {
      setMensagem(error instanceof Error ? error.message : "Não foi possível enviar o documento.");
    } finally {
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <Card>
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium">{tabela.nome}</p>
          <p className="mt-1 text-xs text-text-secondary">Versão {tabela.versao}</p>
        </div>
        <Badge tone={info.tone}>{info.texto}</Badge>
      </div>
      <p className="mt-3 text-xs text-text-secondary">
        Vigência: {new Date(tabela.data_inicio).toLocaleDateString("pt-BR")} a {new Date(tabela.data_fim).toLocaleDateString("pt-BR")}
      </p>
      {tabela.status === "draft" && (
        <div className="mt-3">
          <input ref={inputRef} className="hidden" type="file" accept=".pdf,.xlsx,.xls,.docx,.csv,image/*" onChange={(e) => enviar(e.target.files?.[0])} />
          <button type="button" disabled={upload.isPending} onClick={() => inputRef.current?.click()} className="inline-flex h-8 items-center gap-2 rounded border border-border px-3 text-xs disabled:opacity-50">
            <Upload size={14} /> {upload.isPending ? "Enviando..." : "Enviar documento"}
          </button>
          {documentoId && (
            <button type="button" disabled={analisar.isPending} onClick={async () => { await analisar.mutateAsync({ tabelaId: tabela.id, documentoId }); onReview(); }} className="ml-2 h-8 rounded bg-state-info px-3 text-xs text-white disabled:opacity-50">
              {analisar.isPending ? "Analisando..." : "Analisar documento"}
            </button>
          )}
        </div>
      )}
      {tabela.status === "review" && <button onClick={onReview} className="mt-3 h-8 rounded border border-border px-3 text-xs">Revisar dados</button>}
      {tabela.status === "approved" && <button disabled={ativar.isPending} onClick={() => ativar.mutate(tabela.id)} className="mt-3 h-8 rounded bg-state-success px-3 text-xs text-white">Ativar tabela</button>}
      {mensagem && <p className={`mt-2 text-xs ${upload.isError ? "text-state-error" : "text-state-success"}`}>{mensagem}</p>}
    </Card>
  );
}
