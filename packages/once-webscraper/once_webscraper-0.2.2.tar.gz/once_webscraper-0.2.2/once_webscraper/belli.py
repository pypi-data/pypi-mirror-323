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
    parsed = urlparse(url)
    return parsed.netloc == "www.bellikids.com.br"

def _extrair_info_basica(soup: BeautifulSoup) -> Dict[str, Any]:
    """Extrai informações básicas do produto"""
    nome = soup.select_one("h1.nome-produto").get_text(strip=True)
    sku = soup.select_one("meta[name='twitter:data1']").get("content", "")
    
    marca = ""
    marca_link = soup.select_one("div.produto-informacoes a[href*='/marca/']")
    if marca_link:
        marca = marca_link.get_text(strip=True)
    
    preco_tag = soup.find(text=re.compile(r"var produto_preco\s*=\s*(\d+\.?\d*)"))
    preco = 0.0
    if preco_tag:
        preco_match = re.search(r"var produto_preco\s*=\s*(\d+\.?\d*)", preco_tag)
        if preco_match:
            preco = float(preco_match.group(1))
            
    return {
        "nome": nome,
        "sku": sku,
        "marca": marca,
        "preco": preco
    }

def _extrair_descricao(soup: BeautifulSoup) -> str:
    """Extrai a descrição do produto"""
    descricao = ""
    descricao_div = soup.select_one("div#descricao")
    if descricao_div:
        for script in descricao_div.find_all(["script", "style"]):
            script.decompose()
        descricao = descricao_div.get_text(separator="\n", strip=True)
    return descricao

def _extrair_imagens(soup: BeautifulSoup) -> Dict[str, str]:
    """Extrai as URLs das imagens do produto, evitando duplicatas usando hash"""
    imagens = {}
    imagens_hash = set()
    idx = 1
    
    # Pega apenas as imagens grandes do produto
    for img_tag in soup.select("[data-imagem-grande]"):
        img_url = img_tag.get("data-imagem-grande")
        if img_url:
            # Usa hash para evitar duplicatas
            img_hash = hashlib.md5(img_url.encode()).hexdigest()
            if img_hash not in imagens_hash:
                imagens_hash.add(img_hash)
                imagens[f"Image_{idx}"] = img_url
                idx += 1
    
    return imagens

def _extrair_estoque(soup: BeautifulSoup, sku: str) -> Dict[str, Any]:
    """Extrai informações de estoque do produto"""
    variacoes = []
    estoque_total = 0
    
    for item in soup.select("a.atributo-item"):
        id_variacao = item.get("data-variacao-id")
        if id_variacao:
            tamanho = item.get("data-variacao-nome", "").strip()
            if tamanho and tamanho.isdigit():
                div_acoes = soup.select_one(f"div.acoes-produto[data-variacao-id='{id_variacao}']")
                estoque = 0
                if div_acoes:
                    estoque_tag = div_acoes.select_one("span.estoque b.qtde_estoque")
                    if estoque_tag:
                        estoque = int(estoque_tag.text)
                
                variacoes.append({
                    "sku": f"{sku}_{tamanho}",
                    "tamanho": tamanho,
                    "quantidade": estoque
                })
                estoque_total += estoque
    
    variacoes.sort(key=lambda x: int(x["tamanho"]))
    return {
        "total": estoque_total,
        "variacoes": variacoes
    }

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
        
    Returns:
        Dict com os dados do produto no formato padronizado
        
    Raises:
        URLInvalidaError: Se a URL não for do domínio bellikids.com.br
        ValueError: Se o tipo de extração for inválido
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
        
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    
    resultado = {"produto": {}}
    
    # Extrai apenas os dados solicitados
    if "all" in tipos or "basic_info" in tipos:
        resultado["produto"]["informacoes_basicas"] = _extrair_info_basica(soup)
        
    if "all" in tipos or "description" in tipos:
        resultado["produto"]["descricao"] = {"texto": _extrair_descricao(soup)}
        
    if "all" in tipos or "images" in tipos:
        resultado["produto"]["midia"] = {"imagens": _extrair_imagens(soup)}
        
    if "all" in tipos or "stock" in tipos:
        # Precisa do SKU para o estoque, então extrai info básica se necessário
        if "informacoes_basicas" not in resultado["produto"]:
            info_basica = _extrair_info_basica(soup)
            sku = info_basica["sku"]
        else:
            sku = resultado["produto"]["informacoes_basicas"]["sku"]
        resultado["produto"]["estoque"] = _extrair_estoque(soup, sku)
    
    # Adiciona metadados
    resultado["produto"]["metadata"] = {
        "fonte": "Belli Kids",
        "url_origem": url,
        "data_extracao": datetime.now().isoformat()
    }
    
    return resultado 