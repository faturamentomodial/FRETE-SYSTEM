from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.services.tabela_frete.analise import AnaliseDocumentoError, analisar_csv


def tabela_mock():
    tabela = MagicMock()
    tabela.transportadora_id = "transportadora-1"
    tabela.data_inicio = datetime(2026, 8, 1)
    tabela.data_fim = datetime(2027, 8, 31)
    tabela.observacoes = None
    return tabela


def test_analisar_csv_extrai_tarifas_e_prazos(tmp_path: Path):
    arquivo = tmp_path / "tabela.csv"
    arquivo.write_text('uf;tipo_tarifa;valor;prazo_dias\nPR;POR_KG;"2,50";3\nSC;VALOR_FIXO;80;4', encoding="utf-8")

    resultado = analisar_csv(arquivo, tabela_mock())

    assert resultado["confianca_extracao"] == 1
    assert resultado["dados_extraidos"]["tarifas"][0]["valor"] == 2.5
    assert resultado["dados_extraidos"]["prazos"][1]["dias"] == 4


def test_analisar_csv_marca_prazo_ausente(tmp_path: Path):
    arquivo = tmp_path / "tabela.csv"
    arquivo.write_text("uf,tipo_tarifa,valor\nPR,POR_KG,2.5", encoding="utf-8")

    resultado = analisar_csv(arquivo, tabela_mock())

    assert resultado["confianca_extracao"] == 0.9
    assert resultado["campos_com_duvida"] == ["prazo_dias"]


def test_analisar_csv_rejeita_colunas_ausentes(tmp_path: Path):
    arquivo = tmp_path / "tabela.csv"
    arquivo.write_text("uf,valor\nPR,2.5", encoding="utf-8")

    with pytest.raises(AnaliseDocumentoError, match="tipo_tarifa"):
        analisar_csv(arquivo, tabela_mock())
