import { apiClient } from "../api/client";
import type { Transportadora } from "../types/transportadora";

export const transportadoraService = {
  async listar(): Promise<Transportadora[]> {
    const { data } = await apiClient.get<Transportadora[]>("/transportadoras");
    return data;
  },
};
