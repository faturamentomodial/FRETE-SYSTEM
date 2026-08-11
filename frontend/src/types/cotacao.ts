export interface Endereco {
  cep: string;
  cidade: string;
  uf: string;
}

export interface VolumeIn {
  quantidade: number;
  comprimento_cm: number;
  largura_cm: number;
  altura_cm: number;
  peso_kg: number;
}

export interface CotacaoCreate {
  origem: Endereco;
  destino: Endereco;
  valor_nf: number;
  peso: number;
  volumes: VolumeIn[];
  transportadoras_ids?: string[] | null;
}

export interface ErroResultado {
  codigo: string;
  mensagem: string;
}

export type StatusResultado = "processing" | "success" | "error" | "timeout";
export type StatusCotacao = "processing" | "completed" | "completed_with_errors" | "failed";

export interface ResultadoTransportadora {
  transportadora_id: string;
  transportadora: string;
  status: StatusResultado;
  valor_frete: number | null;
  prazo_dias: number | null;
  moeda: string;
  erro: ErroResultado | null;
  request_id: string;
}

export interface CotacaoOut {
  id: string;
  status: StatusCotacao;
  cubagem_m3: number;
  melhor_opcao_id: string | null;
  resultados: ResultadoTransportadora[];
}
