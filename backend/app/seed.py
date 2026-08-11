import asyncio

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal, Base, engine
from app.models.models import Transportadora, User

TRANSPORTADORAS_SEED = [
    ("Jamef", "api"),
    ("Jadlog", "api"),
    ("Braspress", "webservice"),
    ("Generoso", "n8n"),
    ("Mira", "playwright"),
    ("Minuano", "edi"),
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        db.add(User(email="admin@fretesystem.com", password_hash=hash_password("admin123"), nome="Administrador"))
        for nome, tipo in TRANSPORTADORAS_SEED:
            db.add(Transportadora(nome=nome, tipo_integracao=tipo, ativa=True, taxa_sucesso=0.0, tempo_medio_ms=0))
        await db.commit()

    print("Seed concluído: usuário admin@fretesystem.com / admin123 e transportadoras criadas.")


if __name__ == "__main__":
    asyncio.run(seed())
