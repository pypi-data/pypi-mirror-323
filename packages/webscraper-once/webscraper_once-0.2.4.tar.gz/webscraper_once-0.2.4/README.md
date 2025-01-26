# WebScraper Once

Extrai dados de produtos de qualquer site.

## Instalação
```bash
pip install webscraper-once
```

## Como Usar
```python
# IMPORTANTE: o import correto é webscraper_once (com underline)
from webscraper_once import get_data
import json
from pprint import pprint

# URL do produto
url = "https://www.bellikids.com.br/conjunto-junino-banana-club-sofia-xadrez-preto"

try:
    # Extrai os dados
    dados = get_data(url)
    
    # Mostra os dados principais
    print(f"Título: {dados['titulo']}")
    print(f"Preço: {dados['preco']}")
    
    # Mostra todos os dados
    pprint(dados)
    
    # Salva em JSON
    with open('produto.json', 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)
        
except Exception as e:
    print(f"Erro: {str(e)}")
```

## O que retorna
```python
{
    'titulo': str,      # Nome/título do produto
    'preco': float,     # Preço do produto
    'descricao': str,   # Descrição
    'imagens': list,    # Lista de URLs das imagens
    'dados_gerais': {}, # Outros dados encontrados
    'url': str,         # URL do produto
    'html': str         # HTML da página
}
```