import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    nome: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Transportadora(Base):
    __tablename__ = "transportadoras"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    nome: Mapped[str] = mapped_column(String(120), unique=True)
    tipo_integracao: Mapped[str] = mapped_column(String(50))  # api | webservice | soap | edi | n8n | playwright
    ativa: Mapped[bool] = mapped_column(default=True)
    taxa_sucesso: Mapped[float] = mapped_column(Float, default=0.0)
    tempo_medio_ms: Mapped[int] = mapped_column(Integer, default=0)
    ultima_consulta: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Cotacao(Base):
    __tablename__ = "cotacoes"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    status: Mapped[str] = mapped_column(String(30), default="processing")
    origem_cep: Mapped[str] = mapped_column(String(20))
    origem_cidade: Mapped[str] = mapped_column(String(120))
    origem_uf: Mapped[str] = mapped_column(String(2))
    destino_cep: Mapped[str] = mapped_column(String(20))
    destino_cidade: Mapped[str] = mapped_column(String(120))
    destino_uf: Mapped[str] = mapped_column(String(2))
    valor_nf: Mapped[float] = mapped_column(Float)
    peso: Mapped[float] = mapped_column(Float)
    cubagem_m3: Mapped[float] = mapped_column(Float, default=0.0)
    melhor_opcao_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    volumes: Mapped[list["CotacaoVolume"]] = relationship(back_populates="cotacao", cascade="all, delete-orphan")
    resultados: Mapped[list["CotacaoResultado"]] = relationship(back_populates="cotacao", cascade="all, delete-orphan")


class CotacaoVolume(Base):
    __tablename__ = "cotacao_volumes"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    cotacao_id: Mapped[str] = mapped_column(ForeignKey("cotacoes.id"))
    quantidade: Mapped[int] = mapped_column(Integer)
    comprimento_cm: Mapped[float] = mapped_column(Float)
    largura_cm: Mapped[float] = mapped_column(Float)
    altura_cm: Mapped[float] = mapped_column(Float)
    peso_kg: Mapped[float] = mapped_column(Float)

    cotacao: Mapped[Cotacao] = relationship(back_populates="volumes")


class CotacaoResultado(Base):
    __tablename__ = "cotacao_resultados"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    cotacao_id: Mapped[str] = mapped_column(ForeignKey("cotacoes.id"))
    transportadora_id: Mapped[str] = mapped_column(ForeignKey("transportadoras.id"))
    status: Mapped[str] = mapped_column(String(20))  # success | error | timeout
    valor_frete: Mapped[float | None] = mapped_column(Float, nullable=True)
    prazo_dias: Mapped[int | None] = mapped_column(Integer, nullable=True)
    erro_codigo: Mapped[str | None] = mapped_column(String(60), nullable=True)
    erro_mensagem: Mapped[str | None] = mapped_column(Text, nullable=True)
    request_id: Mapped[str] = mapped_column(String(50), default=gen_uuid)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    cotacao: Mapped[Cotacao] = relationship(back_populates="resultados")


class LogIntegracao(Base):
    __tablename__ = "logs_integracao"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    request_id: Mapped[str] = mapped_column(String(50), index=True)
    transportadora_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    etapa: Mapped[str] = mapped_column(String(60))  # ex: fastapi, n8n, playwright
    mensagem: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
