import re
from datetime import datetime
from typing import Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

class URLInvalidaError(Exception):
    pass

def validar_url_belli(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.netloc == "www.bellikids.com.br"

def get_belli(url: str) -> Dict[str, Any]:
    """
    Extrai dados de um produto da Belli Kids.
    
    Args:
        url: URL do produto na Belli Kids
        
    Returns:
        Dict com os dados do produto no formato padronizado
        
    Raises:
        URLInvalidaError: Se a URL não for do domínio bellikids.com.br
    """
    if not validar_url_belli(url):
        raise URLInvalidaError("A URL fornecida não é do domínio bellikids.com.br")
        
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    
    # Extrair informações básicas
    nome = soup.select_one("h1.nome-produto").get_text(strip=True)
    sku = soup.select_one("meta[name='twitter:data1']").get("content", "")
    
    # Extrair marca (novo método)
    marca = ""
    marca_link = soup.select_one("div.produto-informacoes a[href*='/marca/']")
    if marca_link:
        marca = marca_link.get_text(strip=True)
    
    # Extrair preço
    preco_tag = soup.find(text=re.compile(r"var produto_preco\s*=\s*(\d+\.?\d*)"))
    preco = 0.0
    if preco_tag:
        preco_match = re.search(r"var produto_preco\s*=\s*(\d+\.?\d*)", preco_tag)
        if preco_match:
            preco = float(preco_match.group(1))
    
    # Extrair descrição (novo método)
    descricao = ""
    descricao_div = soup.select_one("div#descricao")
    if descricao_div:
        # Remove tags script e style
        for script in descricao_div.find_all(["script", "style"]):
            script.decompose()
        descricao = descricao_div.get_text(separator="\n", strip=True)
    
    # Extrair imagens
    imagens = {}
    for idx, img_tag in enumerate(soup.select("[data-imagem-grande]"), 1):
        img_url = img_tag.get("data-imagem-grande")
        if img_url:
            imagens[f"Image_{idx}"] = img_url
            
    # Extrair variações e estoque
    variacoes = []
    estoque_total = 0
    
    for item in soup.select("a.atributo-item"):
        id_variacao = item.get("data-variacao-id")
        if id_variacao:
            tamanho = item.get("data-variacao-nome", "").strip()
            if tamanho and tamanho.isdigit():
                # Buscar estoque para esta variação
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
    
    # Ordenar variações por tamanho
    variacoes.sort(key=lambda x: int(x["tamanho"]))
    
    # Montar resposta no formato padronizado
    return {
        "produto": {
            "informacoes_basicas": {
                "nome": nome,
                "sku": sku,
                "marca": marca,
                "preco": preco
            },
            "descricao": {
                "texto": descricao
            },
            "midia": {
                "imagens": imagens
            },
            "estoque": {
                "total": estoque_total,
                "variacoes": variacoes
            },
            "metadata": {
                "fonte": "Belli Kids",
                "url_origem": url,
                "data_extracao": datetime.now().isoformat()
            }
        }
    } 