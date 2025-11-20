"""
Módulo para busca automática de dados do Yahoo Finance

Fornece funções para buscar dados históricos OHLCV via yfinance
para uso nos endpoints de previsão automática.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple

import numpy as np
import pandas as pd
import yfinance as yf
from fastapi import HTTPException, status


def buscar_dados_historicos(
    ticker: str,
    dias: int = 60,
    validar: bool = True
) -> Tuple[np.ndarray, pd.DataFrame]:
    """
    Busca dados históricos OHLCV do Yahoo Finance.
    
    Args:
        ticker: Símbolo do ticker (ex: 'B3SA3.SA')
        dias: Número de dias de histórico necessários (padrão: 60)
        validar: Se True, valida que há dados suficientes
        
    Returns:
        Tuple contendo:
        - numpy array shape (dias, 5) com [Open, High, Low, Close, Volume]
        - DataFrame original do yfinance para referência
        
    Raises:
        HTTPException: Se ticker inválido ou dados insuficientes
    """
    try:
        # Buscar com margem extra para compensar fins de semana/feriados
        # Pedir ~90 dias para garantir 60 dias úteis
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=dias * 2)
        
        # Download dos dados
        ticker_obj = yf.Ticker(ticker)
        df = ticker_obj.history(
            start=data_inicio,
            end=data_fim,
            interval='1d',
            auto_adjust=False  # Manter dados originais sem ajustes
        )
        
        # Validações
        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticker '{ticker}' não encontrado ou sem dados disponíveis"
            )
        
        if len(df) < dias:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dados insuficientes para '{ticker}'. "
                       f"Necessário: {dias} dias, Disponível: {len(df)} dias"
            )
        
        # Selecionar últimos N dias e features necessárias
        df_recente = df.tail(dias).copy()
        
        # Garantir que temos todas as colunas necessárias
        colunas_necessarias = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in df_recente.columns for col in colunas_necessarias):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Dados incompletos para '{ticker}'. "
                       f"Colunas esperadas: {colunas_necessarias}"
            )
        
        # Extrair array numpy no formato correto [Open, High, Low, Close, Volume]
        dados_array = df_recente[colunas_necessarias].values
        
        # Validar que não há valores nulos
        if np.isnan(dados_array).any():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Dados contêm valores nulos para '{ticker}'"
            )
        
        # Validar que valores são positivos (exceto volume que pode ser 0)
        if (dados_array[:, :4] <= 0).any():  # Primeiras 4 colunas (OHLC)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Dados contêm valores inválidos (≤0) para '{ticker}'"
            )
        
        return dados_array, df_recente
        
    except HTTPException:
        # Re-raise HTTPException
        raise
        
    except Exception as e:
        # Capturar outros erros (rede, timeout, etc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Erro ao buscar dados para '{ticker}': {str(e)}"
        )


def formatar_dados_para_modelo(
    dados: np.ndarray,
    window_size: int = 60
) -> np.ndarray:
    """
    Formata dados brutos para o formato esperado pelo modelo.
    
    Args:
        dados: Array shape (dias, 5) com dados OHLCV
        window_size: Tamanho da janela temporal (padrão: 60)
        
    Returns:
        Array shape (1, window_size, 5) pronto para predição
        
    Raises:
        ValueError: Se dimensões incorretas
    """
    if dados.shape[0] != window_size:
        raise ValueError(
            f"Esperado {window_size} dias, recebido {dados.shape[0]}"
        )
    
    if dados.shape[1] != 5:
        raise ValueError(
            f"Esperado 5 features (OHLCV), recebido {dados.shape[1]}"
        )
    
    # Adicionar dimensão batch: (60, 5) -> (1, 60, 5)
    return dados.reshape(1, window_size, 5)


def validar_ticker_format(ticker: str) -> str:
    """
    Valida e normaliza formato do ticker.
    
    Args:
        ticker: Símbolo do ticker
        
    Returns:
        Ticker normalizado em uppercase
        
    Raises:
        HTTPException: Se formato inválido
    """
    ticker = ticker.strip().upper()
    
    if not ticker:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticker não pode ser vazio"
        )
    
    # Validação básica de formato
    if len(ticker) < 2 or len(ticker) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ticker '{ticker}' com formato inválido (2-10 caracteres)"
        )
    
    # Para ações brasileiras, sugerir adicionar .SA se não tiver
    if not '.' in ticker and len(ticker) <= 6:
        ticker = f"{ticker}.SA"
    
    return ticker


def obter_info_ticker(ticker: str) -> Optional[dict]:
    """
    Obtém informações básicas sobre o ticker.
    
    Args:
        ticker: Símbolo do ticker
        
    Returns:
        Dicionário com informações ou None se erro
    """
    try:
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.info
        
        return {
            "nome": info.get('longName', 'N/A'),
            "setor": info.get('sector', 'N/A'),
            "moeda": info.get('currency', 'BRL'),
            "preco_atual": info.get('currentPrice', 0.0)
        }
    except Exception:
        return None
