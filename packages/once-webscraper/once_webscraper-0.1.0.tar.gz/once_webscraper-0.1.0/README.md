# Once WebScraper

Uma biblioteca simples para web scraping de fornecedores.

## Instalação

```bash
pip install once-webscraper
```

## Uso Básico

```python
# Importando a biblioteca
from once_webscraper import get_belli

# Exemplo de uso com tratamento de erros
try:
    # URL de exemplo de um produto da Belli Kids
    url = "https://www.bellikids.com.br/conjunto-junino-banana-club-sofia-xadrez-preto"
    
    # Extrair dados do produto
    produto = get_belli(url)
    
    # Acessando os dados
    nome = produto["produto"]["informacoes_basicas"]["nome"]
    preco = produto["produto"]["informacoes_basicas"]["preco"]
    marca = produto["produto"]["informacoes_basicas"]["marca"]
    
    # Acessando estoque
    estoque_total = produto["produto"]["estoque"]["total"]
    variacoes = produto["produto"]["estoque"]["variacoes"]
    
    # Acessando imagens
    imagens = produto["produto"]["midia"]["imagens"]
    
    # Exemplo de impressão dos dados
    print(f"Nome: {nome}")
    print(f"Preço: R$ {preco:.2f}")
    print(f"Marca: {marca}")
    print(f"Estoque Total: {estoque_total}")
    
    # Imprimindo variações disponíveis
    print("\nVariações disponíveis:")
    for var in variacoes:
        print(f"Tamanho {var['tamanho']}: {var['quantidade']} unidades")

except URLInvalidaError as e:
    print(f"Erro: {e}")
except Exception as e:
    print(f"Erro ao extrair dados: {e}")
```

## Formato do Retorno

O retorno é um dicionário com a seguinte estrutura:

```python
{
    "produto": {
        "informacoes_basicas": {
            "nome": str,
            "sku": str,
            "marca": str,
            "preco": float
        },
        "descricao": {
            "texto": str
        },
        "midia": {
            "imagens": {
                "Image_1": str,  # URL da imagem
                "Image_2": str,
                # ...
            }
        },
        "estoque": {
            "total": int,
            "variacoes": [
                {
                    "sku": str,
                    "tamanho": str,
                    "quantidade": int
                },
                # ...
            ]
        },
        "metadata": {
            "fonte": str,
            "url_origem": str,
            "data_extracao": str  # ISO format
        }
    }
}
```

## Funcionalidades

- Extração de dados de produtos da Belli Kids
- Validação automática de URLs
- Retorno em formato JSON padronizado
- Tratamento de erros para URLs inválidas
- Extração automática de:
  - Informações básicas (nome, SKU, marca, preço)
  - Descrição do produto
  - Imagens em alta resolução
  - Estoque por tamanho
  - Metadados da extração 