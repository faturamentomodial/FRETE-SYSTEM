import asyncio

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal, Base, engine
from app.models.models import Role, Transportadora, User

TRANSPORTADORAS_SEED = [
    ("Jamef", "Jamef Transportes Ltda.", "10000000108", "fracionado", "api"),
    ("Jadlog", "Jadlog Logística S.A.", "10000000280", "expresso", "api"),
    ("Braspress", "Braspress Transportes Urgentes Ltda.", "10000000361", "rodoviario", "webservice"),
    ("Generoso", "Transportes Generoso Ltda.", "10000000442", "rodoviario", "n8n"),
    ("Mira", "Mira Transportes Ltda.", "10000000523", "fracionado", "playwright"),
    ("Minuano", "Transportes Minuano Ltda.", "10000000604", "dedicado", "edi"),
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).options(selectinload(User.roles)).filter_by(email="admin@fretesystem.com"))
        admin = result.scalars().first()
        if not admin:
            admin = User(email="admin@fretesystem.com", password_hash=hash_password("admin123"), nome="Administrador")
            db.add(admin)
        role_admin = await db.scalar(select(Role).where(Role.nome == "admin"))
        if role_admin and role_admin not in admin.roles:
            admin.roles.append(role_admin)

        for nome, razao_social, cnpj_cpf, segmento, tipo in TRANSPORTADORAS_SEED:
            result = await db.execute(select(Transportadora).filter_by(nome=nome))
            if not result.scalars().first():
                db.add(Transportadora(nome=nome, razao_social=razao_social, cnpj_cpf=cnpj_cpf, segmento=segmento, tipo_integracao=tipo, ativa=True, taxa_sucesso=0.0, tempo_medio_ms=0))

        await db.commit()

    print("Seed concluído: usuário admin@fretesystem.com / admin123 e transportadoras criadas (ou já existentes).")


if __name__ == "__main__":
    asyncio.run(seed())
