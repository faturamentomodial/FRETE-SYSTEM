from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TransportadoraOut(BaseModel):
    id: str
    nome: str
    tipo_integracao: str
    ativa: bool
    taxa_sucesso: float
    tempo_medio_ms: int
