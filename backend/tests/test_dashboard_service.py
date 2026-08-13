from unittest.mock import MagicMock

from app.services.dashboard_service import agregar_resultados


def resultado(cotacao_id: str, status: str, valor: float | None):
    item = MagicMock()
    item.cotacao_id = cotacao_id
    item.status = status
    item.valor_frete = valor
    return item


def test_agregar_resultados_calcula_taxa_valor_e_economia():
    resultados = [
        resultado("c1", "success", 100),
        resultado("c1", "success", 140),
        resultado("c2", "success", 80),
        resultado("c2", "error", None),
    ]

    taxa, valor, economia = agregar_resultados(resultados)

    assert taxa == 75
    assert valor == 180
    assert economia == 40


def test_agregar_resultados_vazio_retorna_zeros():
    assert agregar_resultados([]) == (0, 0, 0)
