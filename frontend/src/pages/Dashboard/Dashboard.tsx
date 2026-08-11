import { useNavigate } from "react-router-dom";

import { Card } from "../../components/ui";
import { useTransportadoras } from "../../hooks/useTransportadoras";

export function Dashboard() {
  const navigate = useNavigate();
  const { data: transportadoras } = useTransportadoras();

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-medium">Dashboard</h1>
        <button onClick={() => navigate("/cotacoes/nova")} className="h-9 px-3.5 rounded text-sm font-medium bg-state-info text-white">
          Nova cotação
        </button>
      </div>

      <Card>
        <p className="text-sm text-text-secondary">
          {transportadoras?.length ?? 0} transportadoras cadastradas, vindas de{" "}
          <code className="text-text-primary">GET /api/v1/transportadoras</code>.
        </p>
        <p className="text-xs text-text-secondary mt-2">
          Métricas agregadas de cotações (hoje, taxa de sucesso, economia) entram na Sprint 3, quando
          <code className="text-text-primary"> GET /api/v1/dashboard</code> for implementado no backend.
        </p>
      </Card>
    </div>
  );
}
