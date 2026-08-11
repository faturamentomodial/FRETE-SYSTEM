from app.schemas.cotacao import VolumeIn
from app.services.cubagem import calcular_cubagem_m3


def test_cubagem_um_volume():
    volumes = [VolumeIn(quantidade=2, comprimento_cm=50, largura_cm=40, altura_cm=30, peso_kg=20)]
    assert calcular_cubagem_m3(volumes) == 0.12


def test_cubagem_varios_volumes():
    volumes = [
        VolumeIn(quantidade=1, comprimento_cm=100, largura_cm=100, altura_cm=100, peso_kg=50),
        VolumeIn(quantidade=2, comprimento_cm=50, largura_cm=50, altura_cm=50, peso_kg=10),
    ]
    assert calcular_cubagem_m3(volumes) == 1.25
