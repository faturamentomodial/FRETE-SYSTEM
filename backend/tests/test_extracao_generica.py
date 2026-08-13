from pathlib import Path

from openpyxl import Workbook

from app.services.tabela_frete.extracao_generica import extrair_documento_generico
from app.services.tabela_frete.tabela_import import normalizar_preview


def test_extrai_indicadores_de_excel_generico(tmp_path: Path):
    caminho = tmp_path / "tabela.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.append(["CEP", "Valor", "Prazo"])
    ws.append(["01000-000", "R$ 25,50", "3 dias úteis"])
    wb.save(caminho)

    dados = extrair_documento_generico(caminho, "xlsx")

    assert dados["formato"] == "documento_generico_v1"
    assert "01000-000" in dados["ceps_detectados"]
    assert "R$ 25,50" in dados["valores_detectados"]
    assert any("3 dias" in prazo for prazo in dados["prazos_detectados"])
    preview = normalizar_preview(dados)
    assert preview["requer_mapeamento_tarifario"] is True
    assert preview["fonte"]["ceps_detectados"] == ["01000-000"]
