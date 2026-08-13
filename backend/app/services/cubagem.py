from app.schemas.cotacao import VolumeIn


def calcular_cubagem(comprimento: float, largura: float, altura: float, unidade: str = "cm") -> float:
    """Calcula o volume em m³ para dimensões na mesma unidade."""
    divisores = {"cm": 1_000_000, "m": 1, "mm": 1_000_000_000}
    if unidade not in divisores:
        raise ValueError(f"Unidade de dimensão não suportada: {unidade}")
    if comprimento < 0 or largura < 0 or altura < 0:
        raise ValueError("As dimensões não podem ser negativas")
    return (comprimento * largura * altura) / divisores[unidade]


def calcular_cubagem_m3(volumes: list[VolumeIn]) -> float:
    """Recalcula a cubagem no backend. O valor exibido no frontend é apenas
    para feedback do usuário — este é o valor oficial usado pelo sistema."""
    total = 0.0
    for v in volumes:
        total += (v.comprimento_cm * v.largura_cm * v.altura_cm * v.quantidade) / 1_000_000
    return round(total, 3)
