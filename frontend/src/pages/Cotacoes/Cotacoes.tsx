import { Card } from "../../components/ui";

export function Cotacoes() {
  return (
    <div className="space-y-4">
      <h1 className="text-lg font-medium">Cotações</h1>
      <Card>
        <p className="text-sm text-text-secondary">
          Esta tela depende de <code className="text-text-primary">GET /api/v1/cotacoes</code> com paginação
          (Passo 55/56 do plano), que ainda não foi implementado no backend. Assim que existir, esta página
          lista o histórico com os mesmos filtros do backend, sem baixar registros extras para filtrar no
          navegador.
        </p>
      </Card>
    </div>
  );
}
