"""
===================================================================
PredictFinance - Módulo de Utilitários
Funções auxiliares reutilizáveis em todo o projeto
===================================================================

Autor: ArgusPortal
Data: 02/11/2025
Versão: 1.0.0
"""

import os
import json
import pickle
from datetime import datetime
from typing import Any, Dict, List
import numpy as np
import pandas as pd


def criar_diretorio(caminho: str) -> None:
    """
    Cria diretório se não existir.
    
    Parâmetros:
    -----------
    caminho : str
        Caminho do diretório a criar
    """
    os.makedirs(caminho, exist_ok=True)


def salvar_json(dados: Dict, caminho: str) -> None:
    """
    Salva dados em formato JSON.
    
    Parâmetros:
    -----------
    dados : dict
        Dados a salvar
    caminho : str
        Caminho do arquivo
    """
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


def carregar_json(caminho: str) -> Dict:
    """
    Carrega dados de arquivo JSON.
    
    Parâmetros:
    -----------
    caminho : str
        Caminho do arquivo
        
    Retorna:
    --------
    dict
        Dados carregados
    """
    with open(caminho, 'r', encoding='utf-8') as f:
        return json.load(f)


def salvar_pickle(obj: Any, caminho: str) -> None:
    """
    Salva objeto em formato pickle.
    
    Parâmetros:
    -----------
    obj : Any
        Objeto a salvar
    caminho : str
        Caminho do arquivo
    """
    with open(caminho, 'wb') as f:
        pickle.dump(obj, f)


def carregar_pickle(caminho: str) -> Any:
    """
    Carrega objeto de arquivo pickle.
    
    Parâmetros:
    -----------
    caminho : str
        Caminho do arquivo
        
    Retorna:
    --------
    Any
        Objeto carregado
    """
    with open(caminho, 'rb') as f:
        return pickle.load(f)


def formatar_timestamp() -> str:
    """
    Retorna timestamp formatado.
    
    Retorna:
    --------
    str
        Timestamp no formato ISO 8601
    """
    return datetime.now().isoformat()


def calcular_metricas_basicas(valores_reais: np.ndarray, 
                               valores_previstos: np.ndarray) -> Dict[str, float]:
    """
    Calcula métricas básicas de avaliação.
    
    Parâmetros:
    -----------
    valores_reais : np.ndarray
        Valores reais
    valores_previstos : np.ndarray
        Valores previstos
        
    Retorna:
    --------
    dict
        Dicionário com métricas
    """
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    
    rmse = np.sqrt(mean_squared_error(valores_reais, valores_previstos))
    mae = mean_absolute_error(valores_reais, valores_previstos)
    mape = np.mean(np.abs((valores_reais - valores_previstos) / valores_reais)) * 100
    r2 = r2_score(valores_reais, valores_previstos)
    
    return {
        'rmse': float(rmse),
        'mae': float(mae),
        'mape': float(mape),
        'r2_score': float(r2)
    }


def printar_separador(titulo: str = "", char: str = "=", largura: int = 70) -> None:
    """
    Imprime separador formatado.
    
    Parâmetros:
    -----------
    titulo : str
        Título a exibir
    char : str
        Caractere para o separador
    largura : int
        Largura do separador
    """
    if titulo:
        print(f"\n{char*largura}")
        print(f"{titulo.center(largura)}")
        print(f"{char*largura}\n")
    else:
        print(f"\n{char*largura}\n")


if __name__ == "__main__":
    print("Módulo de utilitários - PredictFinance")
    print("Importe as funções necessárias em seus scripts")
