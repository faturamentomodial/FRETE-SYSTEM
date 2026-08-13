import httpx
import pytest
from fastapi import HTTPException

from app.services.consulta_cnpj import consultar_cnpj, normalizar_resposta_cnpj


def test_normaliza_dados_cadastrais_e_faz_fallback_do_nome_fantasia():
    resultado = normalizar_resposta_cnpj(
        "04252011000110",
        {
            "razao_social": " EMPRESA TESTE LTDA ",
            "nome_fantasia": None,
            "cnae_fiscal_descricao": "Transporte rodoviário de carga",
            "descricao_situacao_cadastral": "ATIVA",
            "municipio": "São Paulo",
            "uf": "SP",
        },
    )

    assert resultado["nome_fantasia"] == "EMPRESA TESTE LTDA"
    assert resultado["razao_social"] == "EMPRESA TESTE LTDA"
    assert resultado["segmento"] == "Transporte rodoviário de carga"
    assert resultado["situacao_cadastral"] == "ATIVA"


@pytest.mark.asyncio
async def test_consulta_cnpj_mapeia_resposta_do_provedor():
    def responder(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/04252011000110")
        return httpx.Response(200, json={
            "razao_social": "Empresa Teste Ltda",
            "nome_fantasia": "Empresa Teste",
            "cnae_fiscal_descricao": "Transporte",
        })

    async with httpx.AsyncClient(transport=httpx.MockTransport(responder)) as client:
        resultado = await consultar_cnpj("04252011000110", client)

    assert resultado["nome_fantasia"] == "Empresa Teste"
    assert resultado["segmento"] == "Transporte"


@pytest.mark.asyncio
async def test_consulta_cnpj_traduz_nao_encontrado():
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda _request: httpx.Response(404, json={"message": "not found"}))
    ) as client:
        with pytest.raises(HTTPException) as erro:
            await consultar_cnpj("04252011000110", client)

    assert erro.value.status_code == 404
    assert erro.value.detail == "CNPJ não encontrado na base de consulta"
