from app.schemas.cotacao import VolumeIn


def calcular_cubagem_m3(volumes: list[VolumeIn]) -> float:
    """Recalcula a cubagem no backend. O valor exibido no frontend é apenas
    para feedback do usuário — este é o valor oficial usado pelo sistema."""
    total = 0.0
    for v in volumes:
        total += (v.comprimento_cm * v.largura_cm * v.altura_cm * v.quantidade) / 1_000_000
    return round(total, 3)
