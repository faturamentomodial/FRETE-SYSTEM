from app.services.tabela_frete.analise import adicionar_diagnostico_confianca


def test_diagnostico_explica_por_que_tabela_uf_zona_foi_bloqueada():
    resultado = adicionar_diagnostico_confianca({
        "confianca_extracao": 0.92,
        "dados_extraidos": {"formato": "uf_zona_peso_v1", "tarifas_por_zona": [{"uf": "PR"}]},
        "campos_com_duvida": ["mapeamento_zonas", "prazos_entrega", "icms"],
        "erros_validacao": [],
        "resumo": {"tarifas_zona": 18, "faixas_peso": 6},
    })

    diagnostico = resultado["diagnostico_confianca"]
    assert diagnostico["nivel"] == "bloqueado"
    assert diagnostico["arquivo_recebido"] is True
    assert diagnostico["arquivo_lido"] is True
    assert diagnostico["aceito_para_cadastro"] is False
    assert diagnostico["dados_detectados"]["tarifas_zona"] == 18
    assert any("CEPs/cidades" in item["titulo"] for item in diagnostico["motivos"])
    assert any("dias úteis" in item["impacto"] for item in diagnostico["motivos"])


def test_diagnostico_generico_informa_ausencia_de_ceps():
    resultado = adicionar_diagnostico_confianca({
        "confianca_extracao": 0.65,
        "dados_extraidos": {
            "formato": "documento_generico_v1",
            "ceps_detectados": [],
        },
        "campos_com_duvida": ["mapeamento_tarifario"],
        "erros_validacao": [],
    })

    motivos = resultado["diagnostico_confianca"]["motivos"]
    assert motivos[0]["campo"] == "ceps"
    assert "Nenhum CEP" in motivos[0]["titulo"]
