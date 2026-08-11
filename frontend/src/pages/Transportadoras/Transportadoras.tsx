import { Badge, Card } from "../../components/ui";
import { useTransportadoras } from "../../hooks/useTransportadoras";

export function Transportadoras() {
  const { data, isLoading, isError } = useTransportadoras();

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-medium">Transportadoras</h1>

      {isLoading && <p className="text-sm text-text-secondary">Carregando transportadoras...</p>}
      {isError && <p className="text-sm text-state-error">Não foi possível carregar as transportadoras.</p>}
      {data && data.length === 0 && <p className="text-sm text-text-secondary">Nenhuma transportadora cadastrada.</p>}

      {data && data.length > 0 && (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {data.map((t) => (
            <Card key={t.id}>
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-sm">{t.nome}</span>
                <Badge tone={t.ativa ? "success" : "warning"}>{t.ativa ? "Ativa" : "Inativa"}</Badge>
              </div>
              <div className="text-xs space-y-1 text-text-secondary">
                <p>Integração: {t.tipo_integracao}</p>
                <p>Sucesso: {t.taxa_sucesso}%</p>
                <p>Tempo médio: {t.tempo_medio_ms} ms</p>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
