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

def _extrair_estoque_metodo_1(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Extrai estoque usando o método original (span.estoque)"""
    variacoes = []
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
                
                variacoes.append({
                    "tamanho": tamanho,
                    "quantidade": estoque
                })
    
    return sorted(variacoes, key=lambda x: int(x["tamanho"]))

def _extrair_estoque_metodo_2(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Extrai estoque usando o método alternativo (div.acoes-produto)"""
    variacoes = {}
    
    # Primeiro coleta os estoques
    acoes_produto_divs = soup.select("div.acoes-produto")
    for div in acoes_produto_divs:
        id_variacao = div.get("data-variacao-id")
        if id_variacao:
            id_variacao_unico = id_variacao.split('-')[-1]
            estoque_tag = div.select_one("span.estoque b.qtde_estoque")
            estoque = int(estoque_tag.text) if estoque_tag else 0
            variacoes[id_variacao_unico] = {"estoque": estoque}
    
    # Depois associa os tamanhos
    atributo_items = soup.select("a.atributo-item")
    for item in atributo_items:
        id_variacao = item.get("data-variacao-id")
        if id_variacao:
            id_variacao_unico = id_variacao.split('-')[-1]
            tamanho = item.get("data-variacao-nome", "").strip()
            if id_variacao_unico in variacoes and (tamanho.isdigit() or tamanho.lower() == "unico"):
                variacoes[id_variacao_unico]["tamanho"] = tamanho
    
    # Converte para lista e filtra apenas os que têm tamanho
    variacoes_lista = [
        {
            "tamanho": v["tamanho"],
            "quantidade": v["estoque"]
        }
        for v in variacoes.values()
        if "tamanho" in v and v["tamanho"].strip()
    ]
    
    # Ordena por tamanho, colocando "Unico" no final
    def chave_ordenacao(x):
        tamanho = x["tamanho"]
        return float('inf') if tamanho.lower() == "unico" else int(tamanho)
    
    return sorted(variacoes_lista, key=chave_ordenacao)

def _extrair_estoque_sem_variacao(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Extrai estoque para produtos sem variações de tamanho"""
    variacoes = []
    
    # Procura o estoque diretamente na div de ações do produto
    div_acoes = soup.select_one("div.acoes-produto")
    if div_acoes:
        estoque_tag = div_acoes.select_one("span.estoque b.qtde_estoque")
        if estoque_tag:
            estoque = int(estoque_tag.text)
            
            # Verifica se tem tamanho único
            tamanho_unico = soup.select_one("a.atributo-item[data-variacao-nome='Unico']")
            tamanho = "Unico" if tamanho_unico else "Único"
            
            variacoes.append({
                "tamanho": tamanho,
                "quantidade": estoque
            })
    
    return variacoes

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
    
    # Verifica se é um produto com variações
    atributo_items = soup.select("a.atributo-item")
    tem_variacoes_numericas = False
    tem_variacao_unica = False
    
    for item in atributo_items:
        tamanho = item.get("data-variacao-nome", "").strip()
        if tamanho:
            if tamanho.isdigit():
                tem_variacoes_numericas = True
                break
            elif tamanho.lower() == "unico":
                tem_variacao_unica = True
                break
    
    if tem_variacoes_numericas:
        # Extrai estoque usando ambos os métodos para produtos com variações numéricas
        variacoes_metodo1 = _extrair_estoque_metodo_1(soup)
        variacoes_metodo2 = _extrair_estoque_metodo_2(soup)
        
        # Combina os resultados dos dois métodos, priorizando o que tem estoque
        variacoes_combinadas = {}
        
        # Primeiro adiciona as variações do método 1
        for var in variacoes_metodo1:
            variacoes_combinadas[var["tamanho"]] = var["quantidade"]
        
        # Depois adiciona as variações do método 2, se tiverem mais estoque
        for var in variacoes_metodo2:
            tamanho = var["tamanho"]
            if tamanho not in variacoes_combinadas or var["quantidade"] > variacoes_combinadas[tamanho]:
                variacoes_combinadas[tamanho] = var["quantidade"]
        
        # Converte para o formato final
        dados["estoque"]["variacoes"] = [
            {
                "sku": f"{dados['sku']}_{tamanho}",
                "tamanho": tamanho,
                "quantidade": quantidade
            }
            for tamanho, quantidade in variacoes_combinadas.items()
        ]
    else:
        # Para produtos sem variações ou com tamanho único
        variacoes_sem_variacao = _extrair_estoque_sem_variacao(soup)
        dados["estoque"]["variacoes"] = [
            {
                "sku": dados["sku"],
                "tamanho": var["tamanho"],
                "quantidade": var["quantidade"]
            }
            for var in variacoes_sem_variacao
        ]
    
    # Ordena por tamanho (se for numérico) e calcula o total
    def chave_ordenacao(x):
        tamanho = x["tamanho"]
        if tamanho.lower() == "unico" or tamanho == "Único":
            return float('inf')
        return int(tamanho) if tamanho.isdigit() else float('inf')
    
    dados["estoque"]["variacoes"].sort(key=chave_ordenacao)
    dados["estoque"]["total"] = sum(var["quantidade"] for var in dados["estoque"]["variacoes"])
    
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