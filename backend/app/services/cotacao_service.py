import asyncio
import uuid

from app.core.config import get_settings
from app.integrations.transportadoras.mock.client import MockTransportadoraAdapter
from app.schemas.cotacao import CotacaoCreate, ErroResultado, ResultadoTransportadora

settings = get_settings()

# Sprint 1/2/3: todas as transportadoras usam o adapter mock. Cada uma será
# substituída pelo adapter real na sua respectiva sprint (4, 5, 6...) sem
# alterar este serviço nem o contrato consumido pelo frontend.
TRANSPORTADORAS_DISPONIVEIS = {
    "t1": "Jamef",
    "t2": "Jadlog",
    "t3": "Braspress",
    "t4": "Generoso",
    "t5": "Mira",
    "t6": "Minuano",
}


async def _cotar_uma(transportadora_id: str, nome: str, payload: dict) -> ResultadoTransportadora:
    adapter = MockTransportadoraAdapter(nome)
    request_id = str(uuid.uuid4())
    timeout = settings.TIMEOUT_API_INTEGRACAO

    try:
        resultado = await asyncio.wait_for(adapter.cotar(payload), timeout=timeout)
    except asyncio.TimeoutError:
        return ResultadoTransportadora(
            transportadora_id=transportadora_id,
            transportadora=nome,
            status="timeout",
            erro=ErroResultado(codigo="TRANSPORTADORA_TIMEOUT", mensagem="Tempo limite excedido."),
            request_id=request_id,
        )

    if resultado.status == "success":
        return ResultadoTransportadora(
            transportadora_id=transportadora_id,
            transportadora=nome,
            status="success",
            valor_frete=resultado.valor_frete,
            prazo_dias=resultado.prazo_dias,
            moeda=resultado.moeda,
            request_id=request_id,
        )

    return ResultadoTransportadora(
        transportadora_id=transportadora_id,
        transportadora=nome,
        status="error",
        erro=ErroResultado(codigo=resultado.erro_codigo or "ERRO_DESCONHECIDO", mensagem=resultado.erro_mensagem or ""),
        request_id=request_id,
    )


async def executar_cotacao(cotacao: CotacaoCreate) -> list[ResultadoTransportadora]:
    """Dispara as consultas a todas as transportadoras selecionadas de forma
    concorrente. Uma falha isolada nunca derruba as demais (Sprint 3)."""
    ids = cotacao.transportadoras_ids or list(TRANSPORTADORAS_DISPONIVEIS.keys())
    payload = {"peso": cotacao.peso, "valor_nf": cotacao.valor_nf}

    tarefas = [
        _cotar_uma(tid, TRANSPORTADORAS_DISPONIVEIS[tid], payload)
        for tid in ids
        if tid in TRANSPORTADORAS_DISPONIVEIS
    ]
    return await asyncio.gather(*tarefas)


def determinar_melhor_opcao(resultados: list[ResultadoTransportadora]) -> str | None:
    sucessos = [r for r in resultados if r.status == "success"]
    if not sucessos:
        return None
    melhor = min(sucessos, key=lambda r: r.valor_frete)
    return melhor.transportadora_id


def determinar_status_geral(resultados: list[ResultadoTransportadora]) -> str:
    if all(r.status == "success" for r in resultados):
        return "completed"
    if any(r.status == "success" for r in resultados):
        return "completed_with_errors"
    return "failed"
