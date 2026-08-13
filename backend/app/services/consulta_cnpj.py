"""Consulta cadastral de empresas por CNPJ.

O provedor externo fica encapsulado no backend para que o frontend nunca
dependa diretamente do formato de resposta (ou da troca futura) do provedor.
"""

from typing import Any

import httpx
from fastapi import HTTPException, status

from app.core.config import get_settings


def _texto(valor: Any) -> str | None:
    if not isinstance(valor, str):
        return None
    limpo = valor.strip()
    return limpo or None


def normalizar_resposta_cnpj(cnpj: str, dados: dict[str, Any]) -> dict[str, str | None]:
    razao_social = _texto(dados.get("razao_social"))
    if not razao_social:
        raise ValueError("A consulta não retornou a razão social da empresa")

    nome_fantasia = _texto(dados.get("nome_fantasia")) or razao_social
    return {
        "cnpj": cnpj,
        "nome_fantasia": nome_fantasia,
        "razao_social": razao_social,
        "segmento": _texto(dados.get("cnae_fiscal_descricao")),
        "situacao_cadastral": _texto(dados.get("descricao_situacao_cadastral")),
        "cep": _texto(dados.get("cep")),
        "municipio": _texto(dados.get("municipio")),
        "uf": _texto(dados.get("uf")),
    }


async def consultar_cnpj(cnpj: str, client: httpx.AsyncClient | None = None) -> dict[str, str | None]:
    settings = get_settings()
    url = f"{settings.CNPJ_CONSULTA_BASE_URL.rstrip('/')}/{cnpj}"
    cliente_proprio = client is None
    cliente = client or httpx.AsyncClient(
        timeout=settings.CNPJ_CONSULTA_TIMEOUT_SECONDS,
        follow_redirects=False,
        headers={"Accept": "application/json", "User-Agent": "FreteWay/1.0"},
    )
    try:
        resposta = await cliente.get(url)
        if resposta.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(status_code=404, detail="CNPJ não encontrado na base de consulta")
        if resposta.status_code == status.HTTP_400_BAD_REQUEST:
            raise HTTPException(status_code=422, detail="CNPJ inválido para consulta")
        if resposta.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            raise HTTPException(status_code=503, detail="Serviço de consulta de CNPJ temporariamente ocupado")
        resposta.raise_for_status()
        try:
            dados = resposta.json()
            if not isinstance(dados, dict):
                raise ValueError
            return normalizar_resposta_cnpj(cnpj, dados)
        except (ValueError, TypeError) as exc:
            raise HTTPException(status_code=502, detail="Resposta inválida do serviço de consulta de CNPJ") from exc
    except HTTPException:
        raise
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=503,
            detail="Serviço de consulta de CNPJ indisponível. Preencha os dados manualmente.",
        ) from exc
    finally:
        if cliente_proprio:
            await cliente.aclose()
