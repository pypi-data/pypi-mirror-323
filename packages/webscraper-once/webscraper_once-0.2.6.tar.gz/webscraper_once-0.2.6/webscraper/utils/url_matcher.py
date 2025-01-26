from typing import Dict, Type, Optional
from urllib.parse import urlparse
import re
from ..core.base_scraper import BaseScraper
from ..core.exceptions import ProviderNotFoundException

class URLMatcher:
    """
    Classe responsável por mapear URLs para seus respectivos scrapers
    """
    
    _scrapers: Dict[str, Type[BaseScraper]] = {}
    _domain_patterns: Dict[str, re.Pattern] = {}
    _providers = {}
    
    @classmethod
    def register_scraper(cls, domain_pattern: str, scraper_class: Type[BaseScraper]) -> None:
        """
        Registra um novo scraper para um padrão de domínio
        
        Args:
            domain_pattern: Regex pattern para matching do domínio
            scraper_class: Classe do scraper a ser registrada
        """
        cls._scrapers[domain_pattern] = scraper_class
        cls._domain_patterns[domain_pattern] = re.compile(domain_pattern, re.IGNORECASE)
    
    @classmethod
    def get_scraper_for_url(cls, url: str) -> BaseScraper:
        """
        Retorna uma instância do scraper apropriado para a URL
        
        Args:
            url: URL do produto
            
        Returns:
            Instância do scraper apropriado
            
        Raises:
            ProviderNotFoundException: Se não houver scraper para o domínio
        """
        domain = urlparse(url).netloc.lower()
        
        # Tenta encontrar um scraper que corresponda ao domínio
        for pattern, regex in cls._domain_patterns.items():
            if regex.match(domain):
                return cls._scrapers[pattern]()
                
        raise ProviderNotFoundException(domain)
    
    @classmethod
    def has_scraper_for_url(cls, url: str) -> bool:
        """
        Verifica se existe um scraper disponível para a URL
        
        Args:
            url: URL para verificar
            
        Returns:
            True se houver um scraper disponível
        """
        try:
            domain = urlparse(url).netloc.lower()
            return any(regex.match(domain) for regex in cls._domain_patterns.values())
        except:
            return False
    
    @classmethod
    def get_supported_domains(cls) -> list[str]:
        """
        Retorna lista de padrões de domínio suportados
        
        Returns:
            Lista de patterns de domínio suportados
        """
        return list(cls._scrapers.keys())
    
    @classmethod
    def clear_scrapers(cls) -> None:
        """Limpa todos os scrapers registrados (útil para testes)"""
        cls._scrapers.clear()
        cls._domain_patterns.clear()

    @classmethod
    def register_provider(cls, domain: str, provider_class) -> None:
        """Registra um provedor para um domínio específico"""
        cls._providers[domain] = provider_class

    @classmethod
    def get_provider(cls, domain: str):
        """Retorna o provedor registrado para o domínio"""
        return cls._providers.get(domain) 