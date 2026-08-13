import pytest

from app.services.tabela_frete.calculo_rodonaves import CalculoRodonavesError, calcular_rodonaves


@pytest.fixture
def dados():
    return {
        "fator_cubagem": 300,
        "peso_limite_kg": 7000,
        "matriz_tarifas": [{
            "descricao": "001 a 100 Km", "km_min": 1, "km_max": 100,
            "ate_10": 20, "ate_20": 30, "ate_40": 40, "ate_60": 50,
            "ate_100": 60, "por_kg_acima_100": 1.1,
        }],
        "coberturas": [{
            "cidade": "TESTE", "uf": "SP", "cep_inicio": 1000000, "cep_fim": 1000999,
            "km": 50, "prazo_pj": 3, "taxa_final": 5,
        }],
        "zonas": {"restricao_rj": [], "risco_sp": [], "centro_expandido_sp": []},
        "regras": {
            "frete_valor_percentual": .0025, "frete_valor_minimo": 6.49,
            "gris_sul_sudeste_percentual_ate_10k": .001, "gris_sul_sudeste_percentual_acima_10k": .0023,
            "gris_sul_sudeste_minimo": 3, "gris_demais_percentual": .003, "gris_demais_minimo": 2.47,
            "pedagio_por_100kg": 11.18, "centro_sp_faixas": [],
        },
    }


def test_calculo_usa_maior_peso_e_prazo_pj(dados):
    resultado = calcular_rodonaves(dados, {
        "destino_cep": "01000-100", "peso": 20, "volume_total_m3": .2, "valor_nf": 1000,
    })
    assert resultado["peso_considerado_kg"] == 60
    assert resultado["prazo_dias"] == 3
    assert resultado["valor_total"] == 75.67


def test_calculo_acima_100_usa_valor_por_kg(dados):
    resultado = calcular_rodonaves(dados, {
        "destino_cep": "01000-100", "peso": 120, "volume_total_m3": 0, "valor_nf": 1000,
    })
    assert resultado["taxas_detalhadas"][0]["valor"] == 132


def test_calculo_rejeita_cep_sem_cobertura(dados):
    with pytest.raises(CalculoRodonavesError, match="não atendido"):
        calcular_rodonaves(dados, {"destino_cep": "99999-999", "peso": 10, "valor_nf": 100})


def test_cotacao_goiania_confere_com_portal_rodonaves(dados):
    dados["matriz_tarifas"] = [{
        "descricao": "801 a 1000 Km", "km_min": 801, "km_max": 1000,
        "ate_10": 60.297903264, "ate_20": 75.533140512,
        "ate_40": 88.826874312, "ate_60": 105.657359616,
        "ate_100": 123.959430336, "por_kg_acima_100": 2.2308740256,
    }]
    dados["coberturas"] = [{
        "cidade": "GOIANIA", "uf": "GO", "cep_inicio": 74000001, "cep_fim": 74899999,
        "km": 946, "prazo_pj": 3, "taxa_final": 37.26912,
    }]
    dados["regras"].update({
        "taxa_administrativa": {"valor": 12.75, "ufs": ["GO"]},
        "taxas_entrega_por_peso": [{
            "cidades": ["GOIANIA"], "peso_limite": 100,
            "ate_limite": 15.79, "acima_limite": 37.27,
        }],
        "icms": {
            "aliquota_reduzida": .07, "aliquota_padrao": .12,
            "origens_reduzida": ["SP"], "destinos_reduzida": ["GO"],
        },
    })

    resultado = calcular_rodonaves(dados, {
        "origem_uf": "SP", "destino_cep": "74075-110", "peso": 46,
        "volume_total_m3": .056, "valor_nf": 390,
    })

    assert resultado["valor_total"] == 166.52
    assert resultado["prazo_dias"] == 3
    assert resultado["peso_considerado_kg"] == 46
    assert resultado["taxas_detalhadas"][4] == {"nome": "Taxas do destino", "valor": 15.79}
    assert resultado["taxas_detalhadas"][5] == {"nome": "TAS", "valor": 12.75}
    assert resultado["detalhe_calculo"]["aliquota_icms"] == .07
