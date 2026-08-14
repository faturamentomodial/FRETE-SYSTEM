"""Validation for administrator-configured outbound HTTP endpoints."""

import ipaddress
import socket
from urllib.parse import urlparse


class UnsafeUrlError(ValueError):
    pass


def validate_external_url(url: str, *, allow_local: bool = False) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise UnsafeUrlError("A URL externa deve ser HTTPS e não pode conter credenciais")
    host = parsed.hostname.lower().rstrip(".")
    if host == "localhost" or host.endswith(".localhost"):
        if allow_local:
            return url
        raise UnsafeUrlError("Endereços locais não são permitidos")
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(host, parsed.port or 443)}
    except socket.gaierror as exc:
        raise UnsafeUrlError("Não foi possível resolver o endereço da integração") from exc
    for address in addresses:
        ip = ipaddress.ip_address(address)
        if not ip.is_global:
            raise UnsafeUrlError("A integração não pode acessar redes privadas ou reservadas")
    return url
