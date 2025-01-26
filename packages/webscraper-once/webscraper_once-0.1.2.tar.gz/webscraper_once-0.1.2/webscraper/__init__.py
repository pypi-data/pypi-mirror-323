from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
import logging
from .utils.url_matcher import URLMatcher
from .core.exceptions import (
    InvalidURLException,
    ProviderNotFoundException,
    ExtractionError,
    NetworkError
)

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScraper:
    """
    Interface principal para o scraper de produtos.
    
    Exemplo de uso:
        >>> scraper = WebScraper()
        >>> produto = scraper.get_product("https://bellikids.com.br/produto/123")
        >>> print(produto["nome"])
    """
    
    def __init__(self, debug: bool = False):
        self._last_result = None
        if debug:
            logger.setLevel(logging.DEBUG)
    
    def get_product(self, url: str, retry_count: int = 1) -> Dict[str, Any]:
        """
        Extrai dados de um produto a partir da URL.
        
        Args:
            url: URL do produto para extrair dados
            retry_count: Número de tentativas em caso de erro de rede
            
        Returns:
            Dict com os dados do produto contendo no mínimo:
                - nome: Nome do produto
                - preco: Preço atual
                - disponivel: Boolean indicando disponibilidade
                
        Raises:
            InvalidURLException: Se a URL for inválida
            ProviderNotFoundException: Se não houver scraper para o domínio
            ExtractionError: Se houver erro na extração dos dados
            NetworkError: Se houver erro de conexão
        """
        try:
            # Validação básica da URL
            if not url or not isinstance(url, str):
                raise InvalidURLException(url, "URL não pode ser vazia")
                
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                raise InvalidURLException(url, "URL mal formatada")
            
            logger.debug(f"Iniciando extração da URL: {url}")
            
            # Obtém o scraper apropriado
            try:
                scraper = URLMatcher.get_scraper_for_url(url)
            except Exception as e:
                raise ProviderNotFoundException(parsed.netloc)
            
            # Tenta extrair os dados com retry
            last_error = None
            for attempt in range(retry_count):
                try:
                    self._last_result = scraper.extract_product_data(url)
                    logger.debug(f"Dados extraídos com sucesso: {self._last_result}")
                    return self._last_result
                except Exception as e:
                    last_error = e
                    logger.warning(f"Tentativa {attempt + 1} falhou: {str(e)}")
                    
            # Se chegou aqui, todas as tentativas falharam
            raise ExtractionError(url, str(last_error))
            
        except InvalidURLException:
            raise
        except ProviderNotFoundException:
            raise
        except Exception as e:
            logger.error(f"Erro inesperado: {str(e)}")
            raise ExtractionError(url, str(e))
    
    def get_last_result(self) -> Optional[Dict[str, Any]]:
        """Retorna o resultado da última extração bem-sucedida"""
        return self._last_result
    
    @staticmethod
    def get_supported_domains() -> List[str]:
        """Retorna lista de domínios suportados atualmente"""
        return URLMatcher.get_supported_domains()
    
    def validate_url(self, url: str) -> bool:
        """
        Verifica se uma URL é válida e tem scraper disponível
        
        Args:
            url: URL para validar
            
        Returns:
            True se a URL for válida e tiver scraper disponível
        """
        try:
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                return False
            return URLMatcher.has_scraper_for_url(url)
        except:
            return False

# Cria uma instância global para uso direto
scraper = WebScraper()

# Funções de conveniência para uso mais simples
def get_product(url: str, retry_count: int = 1) -> Dict[str, Any]:
    """Extrai dados de um produto (forma mais simples de uso)"""
    return scraper.get_product(url, retry_count)

def get_last_result() -> Optional[Dict[str, Any]]:
    """Retorna o último resultado extraído"""
    return scraper.get_last_result()

def get_supported_domains() -> List[str]:
    """Lista domínios suportados"""
    return WebScraper.get_supported_domains()

def validate_url(url: str) -> bool:
    """Valida se uma URL é suportada"""
    return scraper.validate_url(url) 