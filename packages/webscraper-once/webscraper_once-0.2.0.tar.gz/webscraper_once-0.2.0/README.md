# WebScraper Once

Biblioteca Python simples para extrair dados de produtos de qualquer site.

## Instalação

```bash
pip install webscraper-once
```

## Uso

É super simples! Apenas importe e use:

```python
from webscraper import get_data

# URL do produto que você quer extrair
url = "https://exemplo.com.br/produto/123"

try:
    # Extrai todos os dados
    dados = get_data(url)
    
    # Acessa os dados
    print(f"Título: {dados['titulo']}")
    print(f"Preço: {dados['preco']}")
    print(f"Descrição: {dados['descricao']}")
    print(f"Imagens: {dados['imagens']}")
    
    # Todos os metadados extras
    print(f"Dados adicionais: {dados['dados_gerais']}")
    
except Exception as e:
    print(f"Erro: {str(e)}")
```

## Dados Retornados

O dicionário retornado contém:

```python
{
    'url': str,          # URL do produto
    'titulo': str,       # Título/nome do produto
    'descricao': str,    # Descrição do produto
    'preco': float,      # Preço (quando disponível)
    'imagens': list,     # Lista de URLs das imagens
    'dados_gerais': dict # Todos os metadados encontrados
    'html': str         # HTML da página para processamento adicional
}
```

## Salvando em JSON

```python
from webscraper import get_data
import json

url = "https://exemplo.com.br/produto/123"

try:
    dados = get_data(url)
    
    # Salva em arquivo JSON
    with open('produto.json', 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)
        
    print("Dados salvos em 'produto.json'")
    
except Exception as e:
    print(f"Erro: {str(e)}")
```

## Requisitos

- Python 3.7 ou superior
- Conexão com internet

## Licença

MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.