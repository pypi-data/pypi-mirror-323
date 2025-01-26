class ScraperException(Exception):
    """Exceção base para erros de scraping"""
    pass

class InvalidURLException(ScraperException):
    """Exceção para URLs inválidas ou mal formatadas"""
    def __init__(self, url: str | None, message: str | None = None):
        self.url = url
        self.message = message or f"URL inválida: {url}"
        super().__init__(self.message)

class ProviderNotFoundException(ScraperException):
    """Exceção para quando não há scraper para o fornecedor"""
    def __init__(self, domain: str):
        self.domain = domain
        self.message = f"Não há scraper disponível para o domínio: {domain}"
        super().__init__(self.message)

class ExtractionError(ScraperException):
    """Exceção para erros durante a extração dos dados"""
    def __init__(self, url: str, reason: str):
        self.url = url
        self.reason = reason
        self.message = f"Erro ao extrair dados da URL {url}: {reason}"
        super().__init__(self.message)

class NetworkError(ScraperException):
    """Exceção para erros de rede durante o scraping"""
    def __init__(self, url: str, status_code: int | None = None):
        self.url = url
        self.status_code = status_code
        self.message = f"Erro de rede ao acessar {url}"
        if status_code:
            self.message += f" (Status: {status_code})"
        super().__init__(self.message) 