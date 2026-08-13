import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { transportadoraService } from "../services/transportadoraService";
import type { TransportadoraInput } from "../types/transportadora";
import type { ConfiguracaoApiInput } from "../types/transportadora";

export function useTransportadoras() {
  return useQuery({
    queryKey: ["transportadoras"],
    queryFn: transportadoraService.listar,
  });
}

export function useCriarTransportadora() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: transportadoraService.criar,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["transportadoras"] }),
  });
}

export function useAtualizarTransportadora() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, dados }: { id: string; dados: TransportadoraInput }) => transportadoraService.atualizar(id, dados),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["transportadoras"] }),
  });
}

export function useAlterarStatusTransportadora() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ativa }: { id: string; ativa: boolean }) => transportadoraService.alterarStatus(id, ativa),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["transportadoras"] }),
  });
}

export function useExcluirTransportadora() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: transportadoraService.excluir,
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["transportadoras"] }),
        queryClient.invalidateQueries({ queryKey: ["dashboard"] }),
      ]);
    },
  });
}

export function useConsultaCnpj() {
  return useMutation({ mutationFn: transportadoraService.consultarCnpj });
}

export function useConfiguracaoApi(transportadoraId: string | null) {
  return useQuery({
    queryKey: ["transportadoras", transportadoraId, "configuracao-api"],
    queryFn: () => transportadoraService.obterConfiguracaoApi(transportadoraId as string),
    enabled: Boolean(transportadoraId),
  });
}

export function useSalvarConfiguracaoApi(transportadoraId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (dados: ConfiguracaoApiInput) => transportadoraService.salvarConfiguracaoApi(transportadoraId, dados),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["transportadoras", transportadoraId, "configuracao-api"] }),
  });
}
