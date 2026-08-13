import pytest
from pydantic import ValidationError

from app.schemas.transportadora import TransportadoraCreate, documento_valido


@pytest.mark.parametrize("documento", ["529.982.247-25", "04.252.011/0001-10"])
def test_documento_valido_aceita_cpf_e_cnpj(documento):
    assert documento_valido(documento)


@pytest.mark.parametrize("documento", ["111.111.111-11", "04.252.011/0001-11", "123"])
def test_documento_valido_rejeita_documentos_invalidos(documento):
    assert not documento_valido(documento)


def test_create_normaliza_documento_e_tipo():
    dados = TransportadoraCreate(
        nome=" Transportadora Teste ",
        razao_social=" Transportadora Teste Ltda. ",
        cnpj_cpf="04.252.011/0001-10",
        segmento=" Expresso ",
        tipo_integracao="API",
    )
    assert dados.cnpj_cpf == "04252011000110"
    assert dados.tipo_integracao == "api"
    assert dados.nome == "Transportadora Teste"


def test_create_rejeita_tipo_desconhecido():
    with pytest.raises(ValidationError):
        TransportadoraCreate(
            nome="Teste", razao_social="Teste Ltda.", cnpj_cpf="52998224725",
            segmento="Expresso", tipo_integracao="ftp",
        )


def test_create_aceita_api_sem_credencial():
    dados = TransportadoraCreate(
        nome="API Futura", razao_social="API Futura Ltda.", cnpj_cpf="52998224725",
        segmento="Expresso", tipo_integracao="api", metodo_calculo="api",
        api_base_url="https://api.exemplo.com", api_ambiente="homologacao",
    )
    assert dados.api_key is None
    assert dados.metodo_calculo == "api"
