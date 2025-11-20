"""
Módulo para busca automática de dados do Yahoo Finance

Fornece funções para buscar dados históricos OHLCV via yfinance
para uso nos endpoints de previsão automática.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
import time
import logging

import numpy as np
import pandas as pd
import yfinance as yf
from fastapi import HTTPException, status

# Importar dados de fallback
try:
    from api.fallback_data import get_dados_exemplo, usar_fallback_disponivel
    FALLBACK_DISPONIVEL = True
except ImportError:
    FALLBACK_DISPONIVEL = False

# Configurar logging
logger = logging.getLogger(__name__)


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
        logger.info(f"📥 Iniciando busca: ticker={ticker}, dias={dias}")
        
        # Buscar com margem extra para compensar fins de semana/feriados
        # Pedir ~90 dias para garantir 60 dias úteis
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=dias * 2)
        
        logger.info(f"📅 Período: {data_inicio.date()} até {data_fim.date()}")
        
        # Download dos dados com retry limitado
        max_tentativas = 3
        ultimo_erro = None
        df = pd.DataFrame()
        
        for tentativa in range(max_tentativas):
            logger.info(f"🔄 Tentativa {tentativa + 1}/{max_tentativas}")
            try:
                # Criar ticker com timeout maior
                ticker_obj = yf.Ticker(ticker)
                
                # Tentar buscar dados
                df = ticker_obj.history(
                    start=data_inicio,
                    end=data_fim,
                    interval='1d',
                    auto_adjust=False,
                    timeout=30
                )
                
                # Se conseguiu dados, sair do loop
                if not df.empty:
                    logger.info(f"✅ Dados obtidos: {len(df)} registros")
                    break
                
                # Se vazio mas sem erro, tentar novamente
                logger.warning(f"⚠️ DataFrame vazio na tentativa {tentativa + 1}")
                ultimo_erro = f"DataFrame vazio na tentativa {tentativa + 1}"
                
            except Exception as e:
                logger.error(f"❌ Erro na tentativa {tentativa + 1}: {str(e)[:100]}")
                ultimo_erro = str(e)
                # Só aguardar se não for a última tentativa
                if tentativa < max_tentativas - 1:
                    time.sleep(2 ** (tentativa + 1))  # 2, 4, 8 segundos
        
        # Validações
        if df.empty:
            # Tentar usar dados de fallback antes de falhar
            if FALLBACK_DISPONIVEL and ticker.upper() == "B3SA3.SA" and dias == 60:
                logger.warning(f"Yahoo Finance falhou, usando dados de fallback para {ticker}")
                try:
                    dados_fallback = get_dados_exemplo(ticker, dias)
                    # Criar DataFrame mock para retorno
                    df_fallback = pd.DataFrame(
                        dados_fallback,
                        columns=['Open', 'High', 'Low', 'Close', 'Volume']
                    )
                    logger.info(f"✅ Fallback: {len(df_fallback)} dias de dados")
                    return dados_fallback, df_fallback
                except Exception as e:
                    logger.error(f"Erro ao usar fallback: {e}")
            
            # Se fallback também falhar ou não disponível
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Yahoo Finance temporariamente indisponível para '{ticker}'. "
                       f"Tentativas: {max_tentativas}. Último erro: {ultimo_erro}. "
                       f"Tente novamente em alguns minutos."
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
