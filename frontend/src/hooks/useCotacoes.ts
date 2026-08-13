import { keepPreviousData, useQuery } from "@tanstack/react-query";

import { cotacaoService } from "../services/cotacaoService";
import type { CotacaoFiltros } from "../types/cotacao";

export function useCotacoes(filtros: CotacaoFiltros) {
  return useQuery({
    queryKey: ["cotacoes", filtros],
    queryFn: () => cotacaoService.listar(filtros),
    placeholderData: keepPreviousData,
    refetchInterval: (query) =>
      query.state.data?.items.some((item) => item.status === "processing") ? 3_000 : false,
  });
}
