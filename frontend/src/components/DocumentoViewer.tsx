import { useEffect, useState } from "react";

import { apiClient } from "../api/client";
import type { DocumentoFrete } from "../types/tabelaFrete";

export function DocumentoViewer({ documento }: { documento: DocumentoFrete }) {
  const [url, setUrl] = useState<string | null>(null);
  useEffect(() => {
    let ativo = true;
    let objectUrl: string | null = null;
    apiClient.get(`/tabelas-frete/documentos/${documento.id}/conteudo`, { responseType: "blob" })
      .then(({ data }) => {
        objectUrl = URL.createObjectURL(data);
        if (ativo) setUrl(objectUrl);
      });
    return () => {
      ativo = false;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [documento.id]);
  return (
    <div className="rounded border border-border bg-surface2 p-3">
      <p className="text-sm font-medium">{documento.nome_arquivo}</p>
      <p className="mt-1 text-xs text-text-secondary">{(documento.tamanho_bytes / 1024).toFixed(1)} KB</p>
      {url ? <a href={url} target="_blank" rel="noreferrer" className="mt-3 inline-block text-xs text-state-info underline">Abrir documento original</a> : <p className="mt-3 text-xs text-text-secondary">Carregando documento...</p>}
    </div>
  );
}
