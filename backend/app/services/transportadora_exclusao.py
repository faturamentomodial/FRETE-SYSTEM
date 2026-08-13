"""Exclusão física de uma transportadora e de todos os dados vinculados."""

from pathlib import Path

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.models import (
    AbrangenciaFrete,
    AuditoriaTabela,
    Cotacao,
    CotacaoResultado,
    DocumentoFrete,
    LogIntegracao,
    RegraCubagem,
    RegraExcedente,
    RegraFreteMinimo,
    RegraPeso,
    RegraPesoConsiderado,
    RegraPrazo,
    RegraRota,
    TabelaFrete,
    TabelaFreteDadosImportados,
    TarifaFrete,
    TaxaFrete,
    Transportadora,
    TransportadoraConfiguracaoApi,
)


async def excluir_transportadora_definitivamente(
    db: AsyncSession, transportadora_id: str
) -> list[str]:
    """Remove dados relacionais em ordem segura, sem confirmar a transação."""
    tabelas_ids = select(TabelaFrete.id).where(TabelaFrete.transportadora_id == transportadora_id)
    caminhos = list((await db.scalars(
        select(DocumentoFrete.caminho_storage).where(DocumentoFrete.tabela_frete_id.in_(tabelas_ids))
    )).all())

    # Estes filhos também apontam para abrangências/rotas e devem sair primeiro.
    for modelo in (
        TabelaFreteDadosImportados,
        DocumentoFrete,
        RegraPeso,
        TarifaFrete,
        RegraPrazo,
        RegraCubagem,
        TaxaFrete,
        RegraFreteMinimo,
        RegraExcedente,
        RegraPesoConsiderado,
        AuditoriaTabela,
    ):
        await db.execute(delete(modelo).where(modelo.tabela_frete_id.in_(tabelas_ids)))

    await db.execute(delete(AbrangenciaFrete).where(AbrangenciaFrete.tabela_frete_id.in_(tabelas_ids)))
    await db.execute(delete(RegraRota).where(RegraRota.tabela_frete_id.in_(tabelas_ids)))
    await db.execute(delete(TabelaFrete).where(TabelaFrete.transportadora_id == transportadora_id))
    await db.execute(delete(TransportadoraConfiguracaoApi).where(
        TransportadoraConfiguracaoApi.transportadora_id == transportadora_id
    ))
    await db.execute(delete(CotacaoResultado).where(CotacaoResultado.transportadora_id == transportadora_id))
    await db.execute(update(Cotacao).where(Cotacao.melhor_opcao_id == transportadora_id).values(melhor_opcao_id=None))
    await db.execute(delete(LogIntegracao).where(LogIntegracao.transportadora_id == transportadora_id))
    await db.execute(delete(Transportadora).where(Transportadora.id == transportadora_id))
    return caminhos


def remover_arquivos_transportadora(caminhos_relativos: list[str]) -> None:
    """Apaga somente arquivos resolvidos dentro do storage configurado."""
    raiz = Path(get_settings().TABELA_FRETE_STORAGE_DIR).resolve()
    for caminho_relativo in caminhos_relativos:
        caminho = (raiz / caminho_relativo).resolve()
        if raiz in caminho.parents:
            try:
                caminho.unlink(missing_ok=True)
            except OSError:
                # O banco já foi confirmado; uma falha pontual do storage não
                # deve fazer o frontend acreditar que a exclusão não ocorreu.
                pass
