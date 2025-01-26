# WebScraper Once

Extrai dados de produtos de qualquer site.

## Instalação
```bash
pip install webscraper-once
```

## Como Usar
```python
from webscraper import get_data
import json

# URL do produto
url = "https://www.magazineluiza.com.br/produto/123"  # Coloque a URL que quiser

# Pega os dados
dados = get_data(url)

# Mostra os dados principais
print(f"Título: {dados['titulo']}")
print(f"Preço: {dados['preco']}")

# Salva tudo em JSON
with open('produto.json', 'w', encoding='utf-8') as f:
    json.dump(dados, f, ensure_ascii=False, indent=4)
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

## Requisitos

- Python 3.7 ou superior
- Conexão com internet

## Licença

MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.