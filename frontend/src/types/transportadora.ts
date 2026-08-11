export interface Transportadora {
  id: string;
  nome: string;
  tipo_integracao: "api" | "webservice" | "soap" | "edi" | "n8n" | "playwright";
  ativa: boolean;
  taxa_sucesso: number;
  tempo_medio_ms: number;
}
