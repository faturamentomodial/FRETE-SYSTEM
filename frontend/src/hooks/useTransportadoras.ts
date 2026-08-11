import { useQuery } from "@tanstack/react-query";

import { transportadoraService } from "../services/transportadoraService";

export function useTransportadoras() {
  return useQuery({
    queryKey: ["transportadoras"],
    queryFn: transportadoraService.listar,
  });
}
