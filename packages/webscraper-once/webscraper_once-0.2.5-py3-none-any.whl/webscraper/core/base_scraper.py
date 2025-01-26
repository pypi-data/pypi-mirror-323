from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from urllib.parse import urlparse
import requests
from .exceptions import InvalidURLException, NetworkError, ExtractionError

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """
    Classe base para todos os scrapers de fornecedores.
    Implementa funcionalidades comuns e define a interface que deve ser seguida.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    @abstractmethod
    def extract_product_data(self, url: str) -> Dict[str, Any]:
        """
        Método principal para extrair dados do produto.
        Deve ser implementado por cada fornecedor.
        
        Args:
            url: URL do produto
            
        Returns:
            Dict contendo os dados do produto com no mínimo:
                - nome: str
                - preco: float
                - disponivel: bool
                - url: str
                
        Raises:
            InvalidURLException: Se a URL for inválida
            NetworkError: Se houver erro de conexão
            ExtractionError: Se houver erro na extração
        """
        pass
    
    @abstractmethod
    def validate_url(self, url: str) -> bool:
        """
        Valida se a URL pertence a este fornecedor
        
        Args:
            url: URL para validar
            
        Returns:
            True se a URL for válida para este fornecedor
        """
        pass
    
    def get_page_content(self, url: str) -> str:
        """
        Obtém o conteúdo HTML da página com tratamento de erros
        
        Args:
            url: URL para obter conteúdo
            
        Returns:
            Conteúdo HTML da página
            
        Raises:
            NetworkError: Se houver erro de conexão
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            status_code = getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            raise NetworkError(url, status_code)
    
    def clean_text(self, text: Optional[str]) -> str:
        """
        Limpa um texto removendo espaços extras e caracteres indesejados
        
        Args:
            text: Texto para limpar
            
        Returns:
            Texto limpo
        """
        if not text:
            return ""
        return " ".join(text.split())
    
    def extract_float_price(self, price_str: Optional[str]) -> Optional[float]:
        """
        Converte uma string de preço em float
        
        Args:
            price_str: String contendo o preço (ex: "R$ 99,90")
            
        Returns:
            Valor float do preço ou None se inválido
        """
        if not price_str:
            return None
            
        try:
            # Remove símbolos de moeda e converte vírgula para ponto
            clean_price = price_str.replace("R$", "").replace(".", "").replace(",", ".").strip()
            return float(clean_price)
        except (ValueError, TypeError):
            return None 