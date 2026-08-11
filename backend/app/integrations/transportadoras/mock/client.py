import asyncio
import random

from app.integrations.transportadoras.base import ResultadoCotacao, TransportadoraAdapter

# Perfis de resposta simulados por transportadora, usados apenas até que os
# adapters reais (Sprints 4-6) sejam implementados com credenciais oficiais.
PERFIS = {
    "Jamef": {"delay": (0.4, 1.2), "falha": 0.03},
    "Jadlog": {"delay": (0.6, 1.6), "falha": 0.05},
    "Braspress": {"delay": (0.8, 2.0), "falha": 0.06},
    "Generoso": {"delay": (1.5, 4.0), "falha": 0.18},
    "Mira": {"delay": (2.0, 6.0), "falha": 0.35},
    "Minuano": {"delay": (0.9, 2.2), "falha": 0.08},
}


class MockTransportadoraAdapter(TransportadoraAdapter):
    def __init__(self, nome: str):
        self.nome = nome
        self.perfil = PERFIS.get(nome, {"delay": (1.0, 2.5), "falha": 0.1})

    async def cotar(self, cotacao_payload: dict) -> ResultadoCotacao:
        lo, hi = self.perfil["delay"]
        await asyncio.sleep(random.uniform(lo, hi))

        if random.random() < self.perfil["falha"]:
            erro = random.choice(
                [
                    ("TRANSPORTADORA_TIMEOUT", "A transportadora não respondeu dentro do tempo limite."),
                    ("AUTH_ERROR", "Falha na autenticação com a transportadora."),
                ]
            )
            return ResultadoCotacao(status="error", erro_codigo=erro[0], erro_mensagem=erro[1])

        peso = cotacao_payload.get("peso", 10)
        valor_base = 180 + peso * 3.4 + random.uniform(-30, 60)
        return ResultadoCotacao(
            status="success",
            valor_frete=round(valor_base, 2),
            prazo_dias=random.randint(2, 6),
        )
