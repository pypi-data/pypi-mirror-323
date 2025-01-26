import re
import hashlib
from typing import Dict, Any, List
from bs4 import BeautifulSoup
import requests
from ...core.base_scraper import BaseScraper
from ...core.exceptions import InvalidURLException
from ...utils.url_matcher import URLMatcher
from datetime import datetime

class DataExtractor:
    _ultima_extracao = None

    @classmethod
    def salvar_ultima_extracao(cls, dados: Dict[str, Any]) -> None:
        """Salva os dados da última extração na memória"""
        cls._ultima_extracao = dados
    
    @classmethod
    def obter_ultima_extracao(cls) -> Dict[str, Any]:
        """Retorna os dados da última extração realizada
        
        Returns:
            Dict[str, Any]: Dados do último produto extraído ou dicionário vazio se não houver dados
        """
        if cls._ultima_extracao is None:
            return cls.get_empty_data()
        return cls._ultima_extracao

    def __init__(self, soup: BeautifulSoup):
        self.soup = soup

    def extrair_nome(self) -> str:
        nome_element = self.soup.select_one("h1.nome-produto")
        return nome_element.get_text(strip=True) if nome_element else ""

    def extrair_sku(self) -> str:
        sku_meta = self.soup.select_one("meta[name='twitter:data1']")
        return sku_meta.get("content", "") if sku_meta else ""

    def extrair_marca(self) -> str:
        # Primeiro tenta encontrar no dataLayer
        script_tag = self.soup.find("script", text=re.compile(r"dataLayer\s*="))
        if script_tag:
            match = re.search(r"'productBrandName':\s*'([^']*)'", script_tag.string)
            if match and match.group(1):
                return match.group(1)
        
        # Se não encontrar no dataLayer, tenta encontrar pelo elemento HTML
        marca_element = self.soup.select_one("span.marca-produto a")
        if marca_element and marca_element.get_text(strip=True):
            return marca_element.get_text(strip=True)
        
        # Tenta um terceiro método usando o link da marca
        marca_link = self.soup.select_one("a[href*='/marca/']")
        if marca_link:
            return marca_link.get_text(strip=True)
        
        return ""

    def extrair_preco(self) -> float:
        preco_tag = self.soup.find(text=re.compile(r"var produto_preco\s*=\s*(\d+\.?\d*)"))
        if preco_tag:
            preco_match = re.search(r"var produto_preco\s*=\s*(\d+\.?\d*)", preco_tag)
            if preco_match:
                return float(preco_match.group(1))
        return 0.0

    def extrair_descricao(self) -> str:
        """Extrai e formata a descrição do produto"""
        descricao_div = self.soup.select_one("div.produto-descricao")
        if descricao_div:
            # Remove tags HTML mantendo apenas o texto
            texto = descricao_div.get_text(separator=' ', strip=True)
            
            # Remove palavras em maiúsculas coladas
            texto = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', texto)
            
            # Adiciona espaço entre palavras em maiúsculas
            texto = re.sub(r'([a-z])([A-Z])', r'\1 \2', texto)
            
            # Remove múltiplos espaços
            texto = re.sub(r'\s+', ' ', texto)
            
            # Organiza a estrutura do texto
            partes = texto.split('*')
            descricao_principal = partes[0].strip()
            observacoes = [obs.strip() for obs in partes[1:] if obs.strip()]
            
            # Monta o texto final formatado
            texto_final = descricao_principal
            if observacoes:
                texto_final += "\n\nObservações:\n" + "\n".join(f"• {obs}" for obs in observacoes)
            
            return texto_final
        
        # Se não encontrar a descrição na div, tenta nas meta tags
        for meta_name in ['twitter:description', 'description']:
            descricao_meta = self.soup.select_one(f"meta[name='{meta_name}']")
            if descricao_meta:
                return descricao_meta.get("content", "")
        
        return ""

    def extrair_imagens(self) -> Dict[str, str]:
        """Extrai as imagens do produto e retorna um dicionário com índices"""
        imagens = {}
        imagens_hash = set()
        contador = 1
        
        for img_tag in self.soup.select("[data-imagem-grande]"):
            img_url = img_tag.get("data-imagem-grande")
            if img_url:
                img_hash = hashlib.md5(img_url.encode()).hexdigest()
                if img_hash not in imagens_hash:
                    imagens_hash.add(img_hash)
                    imagens[f"Image_{contador}"] = img_url
                    contador += 1
        
        return imagens

    def extrair_variacoes(self) -> List[Dict[str, Any]]:
        """Extrai apenas as informações essenciais das variações"""
        variacoes = {}
        
        # Coleta os estoques primeiro
        acoes_produto_divs = self.soup.select("div.acoes-produto")
        for div in acoes_produto_divs:
            id_variacao = div.get("data-variacao-id")
            if id_variacao:
                id_variacao_unico = id_variacao.split('-')[-1]
                estoque_tag = div.select_one("span.estoque b.qtde_estoque")
                estoque = int(estoque_tag.text) if estoque_tag else 0
                variacoes[id_variacao_unico] = {"estoque": estoque}
        
        # Associa os tamanhos aos estoques
        atributo_items = self.soup.select("a.atributo-item")
        for item in atributo_items:
            id_variacao = item.get("data-variacao-id")
            if id_variacao:
                id_variacao_unico = id_variacao.split('-')[-1]
                tamanho = item.get("data-variacao-nome", "").strip()
                if id_variacao_unico in variacoes and tamanho.isdigit():
                    variacoes[id_variacao_unico].update({
                        "sku": f"{self.extrair_sku()}_{tamanho}",
                        "tamanho": tamanho
                    })
        
        # Converte para lista e remove variações incompletas
        variacoes_lista = [
            {
                "sku": v["sku"],
                "tamanho": v["tamanho"],
                "estoque": v["estoque"]
            }
            for v in variacoes.values()
            if "tamanho" in v and "sku" in v
        ]
        
        return sorted(variacoes_lista, key=lambda x: int(x["tamanho"]))

    def obter_dados_produto(self) -> Dict[str, Any]:
        """Retorna os dados do produto em formato otimizado para APIs"""
        variacoes = self.extrair_variacoes()
        
        dados = {
            "produto": {
                "informacoes_basicas": {
                    "nome": self.extrair_nome(),
                    "sku": self.extrair_sku(),
                    "marca": self.extrair_marca(),
                    "preco": self.extrair_preco()
                },
                "descricao": {
                    "texto": self.extrair_descricao()
                },
                "midia": {
                    "imagens": self.extrair_imagens()
                },
                "estoque": {
                    "total": sum(v["estoque"] for v in variacoes),
                    "variacoes": [
                        {
                            "sku": v["sku"],
                            "tamanho": v["tamanho"],
                            "quantidade": v["estoque"]
                        }
                        for v in sorted(variacoes, key=lambda x: int(x["tamanho"]))
                    ]
                },
                "metadata": {
                    "fonte": "Belli Kids",
                    "url_origem": self.soup.select_one("link[rel='canonical']").get("href", "") if self.soup.select_one("link[rel='canonical']") else "",
                    "data_extracao": datetime.now().isoformat()
                }
            }
        }
        
        self.salvar_ultima_extracao(dados)
        return dados

    @staticmethod
    def get_empty_data() -> Dict[str, Any]:
        """Retorna um dicionário vazio com a estrutura padrão otimizada"""
        return {
            "produto": {
                "informacoes_basicas": {
                    "nome": "",
                    "sku": "",
                    "marca": "",
                    "preco": 0.0
                },
                "descricao": {
                    "texto": ""
                },
                "midia": {
                    "imagens": {}
                },
                "estoque": {
                    "total": 0,
                    "variacoes": []
                },
                "metadata": {
                    "fonte": "",
                    "url_origem": "",
                    "data_extracao": ""
                }
            }
        }

class BelliKidsScraper(BaseScraper):
    DOMAIN = "bellikids.com.br"
    
    def __init__(self):
        self.session = requests.Session()
    
    def validate_url(self, url: str) -> bool:
        return self.DOMAIN in url.lower()
    
    def extract_product_data(self, url: str) -> Dict[str, Any]:
        if not self.validate_url(url):
            raise InvalidURLException(f"URL não pertence ao domínio {self.DOMAIN}")
            
        response = self.session.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        extractor = DataExtractor(soup)
        return extractor.obter_dados_produto()

# Registra o scraper para o domínio da Belli Kids
URLMatcher.register_provider(BelliKidsScraper.DOMAIN, BelliKidsScraper) 