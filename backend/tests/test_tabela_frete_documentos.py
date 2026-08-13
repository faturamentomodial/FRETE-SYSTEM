from io import BytesIO
from pathlib import Path

import pytest
from fastapi import UploadFile

from app.services.tabela_frete.documentos import (
    DocumentoInvalidoError,
    armazenar_documento,
    validar_metadados,
)


def test_validar_metadados_remove_caminho_e_sanitiza_nome():
    nome, tipo = validar_metadados("../../Tabela Frete 2026.PDF", "application/pdf")
    assert nome == "Tabela_Frete_2026.pdf"
    assert tipo == "pdf"


def test_validar_metadados_rejeita_extensao_desconhecida():
    with pytest.raises(DocumentoInvalidoError, match="Tipo de arquivo não permitido"):
        validar_metadados("tabela.exe", "application/octet-stream")


def test_validar_metadados_rejeita_mime_incompativel():
    with pytest.raises(DocumentoInvalidoError, match="não corresponde"):
        validar_metadados("tabela.pdf", "image/png")


@pytest.mark.asyncio
async def test_armazenar_documento_calcula_hash_e_caminho_relativo(tmp_path: Path):
    upload = UploadFile(filename="tabela.csv", file=BytesIO(b"peso,valor\n10,25"))
    upload.headers = {"content-type": "text/csv"}

    salvo = await armazenar_documento(upload, "tabela-1", tmp_path, 1024)

    assert salvo.tamanho_bytes == 16
    assert salvo.hash_conteudo == "6dc52a869b29157f9e6a51c7d8faae777d94411136520fc8d147ca0d71063531"
    assert salvo.caminho_relativo.startswith("tabela-1/")
    assert salvo.caminho_absoluto.read_bytes() == b"peso,valor\n10,25"


@pytest.mark.asyncio
async def test_armazenar_documento_remove_parcial_quando_excede_limite(tmp_path: Path):
    upload = UploadFile(filename="tabela.csv", file=BytesIO(b"conteudo grande"))
    upload.headers = {"content-type": "text/csv"}

    with pytest.raises(DocumentoInvalidoError, match="excede o limite"):
        await armazenar_documento(upload, "tabela-1", tmp_path, 5)

    assert not list(tmp_path.rglob("*.csv"))
