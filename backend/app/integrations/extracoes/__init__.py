"""Interfaces abstratas para extração e processamento de documentos de tabelas de frete.

Permite implementações múltiplas (PDF, OCR, LLM, etc.) sem acoplamento com o domínio.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ExtratedContent:
    """Resultado bruto da extração de um documento."""

    tipo_conteudo: str  # text, table, image, mixed
    conteudo: str  # Texto extraído ou descrição
    confianca: float = 0.0  # 0.0-1.0, se aplicável
    metadados: dict = field(default_factory=dict)  # Info adicional sobre a extração


@dataclass
class TabelaFreteExtraidaRaw:
    """Estrutura bruta de uma tabela extraída, antes da normalização."""

    titulo: str
    linhas: list[dict]  # Cada linha é um dicionário com chaves detectadas
    confianca_geral: float = 0.0
    conteudo_original: list[ExtratedContent] = field(default_factory=list)
    metadados: dict = field(default_factory=dict)


class DocumentExtractor(ABC):
    """Contrato para extractors de documentos específicos (PDF, Excel, Word, Imagem, etc.)."""

    tipo_suportado: str  # pdf, xlsx, xls, docx, doc, jpg, png, csv, webp

    @abstractmethod
    async def extrair(self, caminho_arquivo: str) -> list[ExtratedContent]:
        """Extrai conteúdo bruto de um documento.

        Args:
            caminho_arquivo: Caminho local do arquivo

        Returns:
            Lista de conteúdos extraídos (pode ser múltiplas tabelas/seções)

        Raises:
            ValueError: Se arquivo inválido ou não suportado
            FileNotFoundError: Se arquivo não existe
        """
        ...

    @abstractmethod
    async def extrair_tabelas(self, caminho_arquivo: str) -> list[TabelaFreteExtraidaRaw]:
        """Extrai e estrutura tabelas de um documento.

        Returns:
            Lista de tabelas estruturadas encontradas no documento
        """
        ...


class AIExtractionProvider(ABC):
    """Contrato para provedores de IA (LLM, OCR inteligente, etc.)
    que enriquecem a extração com interpretação semântica."""

    nome: str

    @abstractmethod
    async def normalizar_tabela(self, tabela_raw: TabelaFreteExtraidaRaw, contexto: dict) -> dict:
        """Recebe uma tabela bruta e retorna dados estruturados e normalizados.

        Args:
            tabela_raw: Tabela extraída mecanicamente
            contexto: Contexto adicional (ex: nome da transportadora, tipo de tabela)

        Returns:
            Dicionário com estrutura normalizada conforme JSON schema da tabela

        Exemplo de retorno:
        {
            "transportadora": "Transportadora X",
            "validade_inicio": "2026-08-01",
            "validade_fim": "2027-07-31",
            "abrangencias": [...],
            "tarifas": [...]
        }
        """
        ...

    @abstractmethod
    async def detectar_campos_suspeitos(self, tabela_raw: TabelaFreteExtraidaRaw) -> list[dict]:
        """Identifica campos que podem conter erros de extração.

        Returns:
            Lista de campos suspeitos com score de confiança
        """
        ...

    @abstractmethod
    async def extrair_metadados(self, tabela_raw: TabelaFreteExtraidaRaw) -> dict:
        """Extrai metadados úteis da tabela (versão, data, tipo, etc.)."""
        ...


class ValidationProvider(ABC):
    """Contrato para validadores de dados extraídos."""

    @abstractmethod
    def validar_tabela(self, dados_normalizados: dict) -> tuple[bool, list[str], list[str]]:
        """Valida dados estruturados de uma tabela.

        Returns:
            (é_válido, erros: list, avisos: list)
        """
        ...

    @abstractmethod
    def detectar_sobreposicoes(self, dados_normalizados: dict) -> list[str]:
        """Detecta sobreposições ou conflitos de regras (ex: faixas de peso sobrepostas)."""
        ...

    @abstractmethod
    def verificar_completude(self, dados_normalizados: dict) -> tuple[float, list[str]]:
        """Verifica o quão completo é o mapeamento da tabela.

        Returns:
            (percentual_completude, campos_faltando)
        """
        ...


class OCRProvider(ABC):
    """Contrato para provedores de OCR (reconhecimento óptico de caracteres)."""

    @abstractmethod
    async def processar_imagem(self, caminho_imagem: str) -> str:
        """Extrai texto de uma imagem.

        Args:
            caminho_imagem: Caminho da imagem (jpg, png, webp, etc.)

        Returns:
            Texto extraído
        """
        ...

    @abstractmethod
    async def processar_pdf_escaneado(self, caminho_pdf: str) -> list[str]:
        """Extrai texto de páginas escaneadas de um PDF.

        Returns:
            Lista com texto por página
        """
        ...
