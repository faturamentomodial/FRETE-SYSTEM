"""Cliente OAuth2 e serviços genéricos do API Gateway Sankhya."""

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.url_security import UnsafeUrlError, validate_external_url

logger = logging.getLogger(__name__)


class SankhyaError(Exception):
    def __init__(self, codigo: str, mensagem: str, status_code: int = 502):
        super().__init__(mensagem)
        self.codigo = codigo
        self.mensagem = mensagem
        self.status_code = status_code


@dataclass
class SankhyaCredentials:
    client_id: str
    client_secret: str
    x_token: str


class SankhyaClient:
    _tokens: dict[str, tuple[str, float]] = {}

    def __init__(
        self, client_key: str, base_url: str, credentials: SankhyaCredentials,
        timeout: float = 30, retry_attempts: int = 3,
    ):
        self.client_key = client_key
        try:
            self.base_url = validate_external_url(base_url).rstrip("/")
        except UnsafeUrlError as exc:
            raise SankhyaError("SANKHYA_URL_INSEGURA", str(exc), 422) from exc
        self.credentials = credentials
        self.timeout = timeout
        self.retry_attempts = max(1, retry_attempts)

    async def authenticate(self, force: bool = False) -> str:
        cached = self._tokens.get(self.client_key)
        if not force and cached and cached[1] > time.monotonic() + 30:
            return cached[0]
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/authenticate",
                    headers={"X-Token": self.credentials.x_token},
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.credentials.client_id,
                        "client_secret": self.credentials.client_secret,
                    },
                )
        except httpx.TransportError as exc:
            raise SankhyaError("SANKHYA_AUTH_NETWORK", "Falha de rede ao autenticar no Sankhya") from exc
        if response.status_code in {400, 401, 403}:
            raise SankhyaError("SANKHYA_CREDENCIAL_INVALIDA", "Credenciais do Gateway Sankhya inválidas", 502)
        try:
            response.raise_for_status()
            body = response.json()
            token = body.get("access_token") or body.get("bearerToken")
            expires_in = int(body.get("expires_in", 1800))
        except (httpx.HTTPError, ValueError, TypeError) as exc:
            raise SankhyaError("SANKHYA_AUTH_RESPOSTA_INVALIDA", "Resposta de autenticação inválida") from exc
        if not token:
            raise SankhyaError("SANKHYA_AUTH_SEM_TOKEN", "Gateway não retornou access_token")
        self._tokens[self.client_key] = (token, time.monotonic() + expires_in)
        return token

    async def service(self, module: str, service_name: str, request_body: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}/gateway/v1/{module}/service.sbr"
        payload = {"serviceName": service_name, "requestBody": request_body}
        refreshed = False
        for attempt in range(self.retry_attempts):
            token = await self.authenticate(force=refreshed)
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        url, params={"serviceName": service_name, "outputType": "json"},
                        headers={"Authorization": f"Bearer {token}"}, json=payload,
                    )
            except httpx.TransportError as exc:
                if attempt + 1 == self.retry_attempts:
                    raise SankhyaError("SANKHYA_NETWORK", "Falha de rede ao acessar o Gateway") from exc
                await asyncio.sleep(2 ** attempt)
                continue
            if response.status_code == 401 and not refreshed:
                refreshed = True
                self._tokens.pop(self.client_key, None)
                continue
            if response.status_code == 429 or response.status_code >= 500:
                if attempt + 1 < self.retry_attempts:
                    await asyncio.sleep(2 ** attempt)
                    continue
            try:
                response.raise_for_status()
                body = response.json()
            except (httpx.HTTPError, ValueError) as exc:
                raise SankhyaError("SANKHYA_HTTP_ERROR", f"Gateway respondeu HTTP {response.status_code}") from exc
            if str(body.get("status")) != "1":
                mensagem = body.get("statusMessage") or body.get("responseBody", {}).get("error") or "Serviço Sankhya recusou a operação"
                raise SankhyaError("SANKHYA_SERVICE_ERROR", str(mensagem))
            return body
        raise SankhyaError("SANKHYA_RETRY_EXHAUSTED", "Tentativas de acesso ao Gateway esgotadas")

    async def pedido_existe(self, entity_name: str, pedido_field: str, numero_pedido: str) -> bool:
        body = await self.service("mge", "CRUDServiceProvider.loadRecords", {
            "dataSet": {
                "rootEntity": entity_name, "includePresentationFields": "N", "offsetPage": "0",
                "criteria": {"expression": {"$": f"{pedido_field} = ?"}, "parameter": [{"$": numero_pedido, "type": "I"}]},
                "entity": {"fieldset": {"list": pedido_field}},
            }
        })
        total = body.get("responseBody", {}).get("entities", {}).get("total", "0")
        return int(total or 0) > 0

    async def gravar_registros(self, entity_name: str, registros: list[dict[str, Any]]) -> int:
        if not registros:
            return 0
        fields = list(registros[0])
        records = [{"values": {str(i): registro.get(field) for i, field in enumerate(fields)}} for registro in registros]
        body = await self.service("mge", "DatasetSP.save", {
            "entityName": entity_name, "standAlone": False, "fields": fields, "records": records,
        })
        return int(body.get("responseBody", {}).get("total", len(registros)))
