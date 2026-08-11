from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import AsyncSessionLocal, get_db
from app.models.models import Cotacao, CotacaoResultado, CotacaoVolume
from app.schemas.cotacao import (
    CotacaoCreate,
    CotacaoOut,
    ResultadoTransportadora,
    SelecionarTransportadora,
)
from app.services.cotacao_service import (
    determinar_melhor_opcao,
    determinar_status_geral,
    executar_cotacao,
)
from app.services.cubagem import calcular_cubagem_m3

router = APIRouter()


async def _processar_cotacao_em_background(cotacao_id: str, payload: CotacaoCreate):
    """Executa as consultas às transportadoras e grava os resultados.
    Roda fora do ciclo de request/response — é por isso que o endpoint de
    criação responde imediatamente com status 'processing'."""
    resultados = await executar_cotacao(payload)

    async with AsyncSessionLocal() as db:
        for r in resultados:
            db.add(
                CotacaoResultado(
                    cotacao_id=cotacao_id,
                    transportadora_id=r.transportadora_id,
                    status=r.status,
                    valor_frete=r.valor_frete,
                    prazo_dias=r.prazo_dias,
                    erro_codigo=r.erro.codigo if r.erro else None,
                    erro_mensagem=r.erro.mensagem if r.erro else None,
                    request_id=r.request_id,
                )
            )

        cotacao = await db.get(Cotacao, cotacao_id)
        cotacao.status = determinar_status_geral(resultados)
        cotacao.melhor_opcao_id = determinar_melhor_opcao(resultados)
        await db.commit()


@router.post("/cotacoes", response_model=CotacaoOut, status_code=status.HTTP_201_CREATED)
async def criar_cotacao(
    payload: CotacaoCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    cubagem = calcular_cubagem_m3(payload.volumes)  # backend é a fonte oficial, nunca confia no frontend

    cotacao = Cotacao(
        status="processing",
        origem_cep=payload.origem.cep,
        origem_cidade=payload.origem.cidade,
        origem_uf=payload.origem.uf,
        destino_cep=payload.destino.cep,
        destino_cidade=payload.destino.cidade,
        destino_uf=payload.destino.uf,
        valor_nf=payload.valor_nf,
        peso=payload.peso,
        cubagem_m3=cubagem,
    )
    db.add(cotacao)
    await db.flush()

    for v in payload.volumes:
        db.add(
            CotacaoVolume(
                cotacao_id=cotacao.id,
                quantidade=v.quantidade,
                comprimento_cm=v.comprimento_cm,
                largura_cm=v.largura_cm,
                altura_cm=v.altura_cm,
                peso_kg=v.peso_kg,
            )
        )
    await db.commit()

    background_tasks.add_task(_processar_cotacao_em_background, cotacao.id, payload)

    return CotacaoOut(id=cotacao.id, status="processing", cubagem_m3=cubagem, resultados=[])


@router.get("/cotacoes/{cotacao_id}", response_model=CotacaoOut)
async def obter_cotacao(
    cotacao_id: str,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    cotacao = await db.get(Cotacao, cotacao_id)
    if not cotacao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cotação não encontrada.")

    result = await db.execute(select(CotacaoResultado).where(CotacaoResultado.cotacao_id == cotacao_id))
    resultados_db = result.scalars().all()

    from app.services.cotacao_service import TRANSPORTADORAS_DISPONIVEIS
    from app.schemas.cotacao import ErroResultado

    resultados = [
        ResultadoTransportadora(
            transportadora_id=r.transportadora_id,
            transportadora=TRANSPORTADORAS_DISPONIVEIS.get(r.transportadora_id, r.transportadora_id),
            status=r.status,
            valor_frete=r.valor_frete,
            prazo_dias=r.prazo_dias,
            erro=ErroResultado(codigo=r.erro_codigo, mensagem=r.erro_mensagem) if r.erro_codigo else None,
            request_id=r.request_id,
        )
        for r in resultados_db
    ]

    return CotacaoOut(
        id=cotacao.id,
        status=cotacao.status,
        cubagem_m3=cotacao.cubagem_m3,
        melhor_opcao_id=cotacao.melhor_opcao_id,
        resultados=resultados,
    )


@router.post("/cotacoes/{cotacao_id}/selecionar")
async def selecionar_transportadora(
    cotacao_id: str,
    payload: SelecionarTransportadora,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    cotacao = await db.get(Cotacao, cotacao_id)
    if not cotacao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cotação não encontrada.")

    result = await db.execute(
        select(CotacaoResultado).where(
            CotacaoResultado.cotacao_id == cotacao_id,
            CotacaoResultado.transportadora_id == payload.transportadora_id,
        )
    )
    resultado = result.scalar_one_or_none()
    if not resultado or resultado.status != "success":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Resultado indisponível para seleção.")

    cotacao.melhor_opcao_id = payload.transportadora_id
    await db.commit()
    return {"ok": True, "transportadora_id": payload.transportadora_id}
