import re
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
import requests
import hashlib
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from enum import Enum, auto

class ScrapingType(Enum):
    ALL = "all"
    BASIC_INFO = "basic_info"
    DESCRIPTION = "description"
    IMAGES = "images"
    STOCK = "stock"

class URLInvalidaError(Exception):
    pass

def validar_url_belli(url: str) -> bool:
    return "www.bellikids.com.br" in url

def _extrair_dados_basicos(soup: BeautifulSoup) -> Dict[str, Any]:
    """Extrai todos os dados básicos de uma vez para evitar múltiplas consultas ao DOM"""
    dados = {
        "nome": "",
        "sku": "",
        "marca": "",
        "preco": 0.0,
        "descricao": "",
        "imagens": {},
        "estoque": {"total": 0, "variacoes": []}
    }
    
    # Extrai nome e SKU
    nome_element = soup.select_one("h1.nome-produto")
    if nome_element:
        dados["nome"] = nome_element.get_text(strip=True)
    
    sku_meta = soup.select_one("meta[name='twitter:data1']")
    if sku_meta:
        dados["sku"] = sku_meta.get("content", "")
    
    # Extrai marca
    marca_link = soup.select_one("div.produto-informacoes a[href*='/marca/']")
    if marca_link:
        dados["marca"] = marca_link.get_text(strip=True)
    
    # Extrai preço
    preco_tag = soup.find(text=re.compile(r"var produto_preco\s*=\s*(\d+\.?\d*)"))
    if preco_tag:
        preco_match = re.search(r"var produto_preco\s*=\s*(\d+\.?\d*)", preco_tag)
        if preco_match:
            dados["preco"] = float(preco_match.group(1))
    
    # Extrai descrição
    descricao_div = soup.select_one("div#descricao")
    if descricao_div:
        for script in descricao_div.find_all(["script", "style"]):
            script.decompose()
        dados["descricao"] = descricao_div.get_text(separator="\n", strip=True)
    
    # Extrai imagens (novo método usando URLs únicas)
    urls_unicas = set()
    idx = 1
    
    # Pega apenas as imagens do container principal de thumbs
    for img_tag in soup.select("div.produto-thumbs [data-imagem-grande]"):
        img_url = img_tag.get("data-imagem-grande")
        if img_url and img_url not in urls_unicas:
            urls_unicas.add(img_url)
            dados["imagens"][f"Image_{idx}"] = img_url
            idx += 1
    
    # Extrai estoque e variações
    variacoes = {}
    estoque_total = 0
    
    # Coleta todos os elementos necessários de uma vez
    atributo_items = soup.select("a.atributo-item")
    acoes_produto_divs = {
        div.get("data-variacao-id"): div 
        for div in soup.select("div.acoes-produto")
    }
    
    for item in atributo_items:
        id_variacao = item.get("data-variacao-id")
        if id_variacao:
            tamanho = item.get("data-variacao-nome", "").strip()
            if tamanho and tamanho.isdigit():
                div_acoes = acoes_produto_divs.get(id_variacao)
                estoque = 0
                if div_acoes:
                    estoque_tag = div_acoes.select_one("span.estoque b.qtde_estoque")
                    if estoque_tag:
                        estoque = int(estoque_tag.text)
                
                dados["estoque"]["variacoes"].append({
                    "sku": f"{dados['sku']}_{tamanho}",
                    "tamanho": tamanho,
                    "quantidade": estoque
                })
                estoque_total += estoque
    
    dados["estoque"]["total"] = estoque_total
    dados["estoque"]["variacoes"].sort(key=lambda x: int(x["tamanho"]))
    
    return dados

def get_belli(url: str, tipo: Union[str, List[str]] = "all") -> Dict[str, Any]:
    """
    Extrai dados de um produto da Belli Kids.
    
    Args:
        url: URL do produto na Belli Kids
        tipo: Tipo de dados a extrair. Pode ser uma string ou lista de strings com os valores:
            - "all": Extrai todos os dados (padrão)
            - "basic_info": Apenas informações básicas (nome, SKU, marca, preço)
            - "description": Apenas descrição
            - "images": Apenas imagens
            - "stock": Apenas estoque
    """
    if not validar_url_belli(url):
        raise URLInvalidaError("A URL fornecida não é do domínio bellikids.com.br")
    
    # Normaliza o tipo para lista
    if isinstance(tipo, str):
        tipos = [tipo.lower()]
    else:
        tipos = [t.lower() for t in tipo]
    
    # Valida os tipos
    tipos_validos = {t.value for t in ScrapingType}
    for t in tipos:
        if t not in tipos_validos:
            raise ValueError(f"Tipo de extração inválido: {t}. Tipos válidos: {tipos_validos}")
    
    # Se "all" estiver na lista, ignora os outros tipos
    if "all" in tipos:
        tipos = ["all"]
    
    # Faz apenas uma requisição e extrai todos os dados de uma vez
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    dados = _extrair_dados_basicos(soup)
    
    # Monta o resultado apenas com os dados solicitados
    resultado = {"produto": {}}
    
    if "all" in tipos or "basic_info" in tipos:
        resultado["produto"]["informacoes_basicas"] = {
            "nome": dados["nome"],
            "sku": dados["sku"],
            "marca": dados["marca"],
            "preco": dados["preco"]
        }
    
    if "all" in tipos or "description" in tipos:
        resultado["produto"]["descricao"] = {"texto": dados["descricao"]}
    
    if "all" in tipos or "images" in tipos:
        resultado["produto"]["midia"] = {"imagens": dados["imagens"]}
    
    if "all" in tipos or "stock" in tipos:
        resultado["produto"]["estoque"] = dados["estoque"]
    
    # Adiciona metadados
    resultado["produto"]["metadata"] = {
        "fonte": "Belli Kids",
        "url_origem": url,
        "data_extracao": datetime.now().isoformat()
    }
    
    return resultado 