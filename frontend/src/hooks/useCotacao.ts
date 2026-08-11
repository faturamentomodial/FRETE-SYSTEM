import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { cotacaoService } from "../services/cotacaoService";
import type { CotacaoCreate } from "../types/cotacao";

const POLLING_INTERVAL_MS = 1500;

export function useCotacao() {
  const [cotacaoId, setCotacaoId] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const criarMutation = useMutation({
    mutationFn: (payload: CotacaoCreate) => cotacaoService.criar(payload),
    onSuccess: (data) => setCotacaoId(data.id),
  });

  // Polling: enquanto status === "processing", consulta de novo.
  // Estrutura pronta para trocar por WebSocket/SSE (Passo 41) sem alterar
  // as telas que consomem este hook.
  const statusQuery = useQuery({
    queryKey: ["cotacao", cotacaoId],
    queryFn: () => cotacaoService.obter(cotacaoId as string),
    enabled: Boolean(cotacaoId),
    refetchInterval: (query) => (query.state.data?.status === "processing" ? POLLING_INTERVAL_MS : false),
  });

  const selecionarMutation = useMutation({
    mutationFn: (transportadoraId: string) => cotacaoService.selecionar(cotacaoId as string, transportadoraId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["cotacao", cotacaoId] }),
  });

  return {
    criar: criarMutation.mutateAsync,
    isCriando: criarMutation.isPending,
    cotacao: statusQuery.data,
    isCarregando: statusQuery.isLoading,
    selecionar: selecionarMutation.mutateAsync,
    reset: () => setCotacaoId(null),
  };
}
