"""
WebScraper Once - Extrai dados de produtos de qualquer site
"""

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
import requests
from bs4 import BeautifulSoup

__version__ = "0.2.3"

# Configuração básica do logger
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

class ScraperError(Exception):
    """Erro base para problemas no scraping"""
    pass

def get_data(url: str) -> dict:
    """Extrai dados de um produto a partir da URL"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'lxml')
    
    return {
        'url': url,
        'titulo': _get_text(soup.find(['h1', 'title'])),
        'descricao': _get_text(soup.find(['meta[name="description"]', 'meta[property="og:description"]'], attrs={'content': True}, content=True)),
        'preco': _extract_price(soup),
        'imagens': _get_images(soup),
        'dados_gerais': _get_metadata(soup),
        'html': response.text
    }

def _get_text(element):
    """Extrai texto de um elemento"""
    if not element:
        return None
    if element.get('content'):
        return element['content'].strip()
    return element.get_text().strip()

def _extract_price(soup):
    """Tenta extrair o preço da página"""
    price_selectors = [
        '.price', '.product-price', '.valor', 
        'meta[property="product:price:amount"]',
        'meta[property="og:price:amount"]'
    ]
    
    for selector in price_selectors:
        element = soup.select_one(selector)
        if element:
            try:
                text = element.get('content') or element.get_text()
                clean = text.replace('R$', '').replace('.', '').replace(',', '.').strip()
                return float(clean)
            except:
                continue
    return None

def _get_images(soup):
    """Extrai URLs das imagens"""
    images = []
    
    og_image = soup.find('meta', property='og:image')
    if og_image and og_image.get('content'):
        images.append(og_image['content'])
    
    for img in soup.select('img[src]'):
        if src := img.get('src'):
            if src.startswith('//'):
                src = 'https:' + src
            images.append(src)
            
    return list(set(images))

def _get_metadata(soup):
    """Extrai metadados gerais da página"""
    metadata = {}
    
    for meta in soup.find_all('meta'):
        name = meta.get('name') or meta.get('property')
        content = meta.get('content')
        if name and content:
            metadata[name] = content
            
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            import json
            data = json.loads(script.string)
            if isinstance(data, dict):
                metadata.update(data)
        except:
            continue
            
    return metadata

# Exporta apenas o necessário
__all__ = ['get_data', 'ScraperError'] 