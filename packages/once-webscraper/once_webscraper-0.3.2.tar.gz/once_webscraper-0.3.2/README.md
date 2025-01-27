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

# URL de exemplo de um produto da Belli Kids
url = "https://www.bellikids.com.br/conjunto-junino-banana-club-sofia-xadrez-preto"

# Extrair todos os dados (comportamento padrão)
produto_completo = get_belli(url)

# Extrair apenas imagens
produto_imagens = get_belli(url, tipo="images")

# Extrair apenas informações básicas
produto_basico = get_belli(url, tipo="basic_info")

# Extrair múltiplos tipos de dados
produto_parcial = get_belli(url, tipo=["basic_info", "stock"])

# Exemplo de uso com tratamento de erros
try:
    # Acessando os dados
    nome = produto_completo["produto"]["informacoes_basicas"]["nome"]
    preco = produto_completo["produto"]["informacoes_basicas"]["preco"]
    marca = produto_completo["produto"]["informacoes_basicas"]["marca"]
    
    # Acessando estoque
    estoque_total = produto_completo["produto"]["estoque"]["total"]
    variacoes = produto_completo["produto"]["estoque"]["variacoes"]
    
    # Acessando imagens
    imagens = produto_completo["produto"]["midia"]["imagens"]
    
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

## Tipos de Extração Disponíveis

- `"all"`: Extrai todos os dados (padrão)
- `"basic_info"`: Apenas informações básicas (nome, SKU, marca, preço)
- `"description"`: Apenas descrição
- `"images"`: Apenas imagens
- `"stock"`: Apenas estoque

## Formato do Retorno

O retorno é um dicionário que contém apenas as seções solicitadas. Por exemplo:

### Extração Completa (`tipo="all"`):
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

### Extração Parcial (exemplo com `tipo="images"`):
```python
{
    "produto": {
        "midia": {
            "imagens": {
                "Image_1": str,  # URL da imagem
                "Image_2": str,
                # ...
            }
        },
        "metadata": {
            "fonte": str,
            "url_origem": str,
            "data_extracao": str
        }
    }
}
```

## Funcionalidades

- Extração seletiva de dados (escolha quais dados extrair)
- Validação automática de URLs
- Retorno em formato JSON padronizado
- Tratamento de erros para URLs inválidas
- Extração automática de:
  - Informações básicas (nome, SKU, marca, preço)
  - Descrição do produto
  - Imagens em alta resolução
  - Estoque por tamanho
  - Metadados da extração 