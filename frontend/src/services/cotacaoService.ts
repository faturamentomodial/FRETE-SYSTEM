import { apiClient } from "../api/client";
import type { CotacaoCreate, CotacaoOut } from "../types/cotacao";

export const cotacaoService = {
  async criar(payload: CotacaoCreate): Promise<CotacaoOut> {
    const { data } = await apiClient.post<CotacaoOut>("/cotacoes", payload);
    return data;
  },

  async obter(id: string): Promise<CotacaoOut> {
    const { data } = await apiClient.get<CotacaoOut>(`/cotacoes/${id}`);
    return data;
  },

  async selecionar(id: string, transportadoraId: string): Promise<void> {
    await apiClient.post(`/cotacoes/${id}/selecionar`, { transportadora_id: transportadoraId });
  },
};
