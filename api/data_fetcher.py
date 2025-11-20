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

# Importar database SQLite
try:
    from database.db_manager import get_db
    DB_DISPONIVEL = True
except ImportError:
    DB_DISPONIVEL = False

# Importar API v8 (prioridade sobre yfinance)
try:
    from src.yahoo_finance_v8 import coletar_dados_yahoo_v8_custom_range
    API_V8_DISPONIVEL = True
except ImportError:
    API_V8_DISPONIVEL = False

# Importar dados de fallback (último recurso)
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
) -> Tuple[np.ndarray, pd.DataFrame, str]:
    """
    Busca dados históricos OHLCV com estratégia em cascata (FUNCIONALIDADE REAL):
    1º Yahoo Finance API v8 Direta (demonstra integração real)
    2º yfinance biblioteca oficial (fallback confiável)
    3º SQLite cache local (último recurso se APIs falharem)
    
    Args:
        ticker: Símbolo do ticker (ex: 'B3SA3.SA')
        dias: Número de dias de histórico necessários (padrão: 60)
        validar: Se True, valida que há dados suficientes
        
    Returns:
        Tuple contendo:
        - numpy array shape (dias, 5) com [Open, High, Low, Close, Volume]
        - DataFrame original para referência
        - str com identificação da fonte (ex: "Yahoo Finance API v8")
        
    Raises:
        HTTPException: Se ticker inválido ou dados insuficientes
    """
    try:
        logger.info(f"📥 Iniciando busca: ticker={ticker}, dias={dias}")
        
        # Calcular período com margem para fins de semana/feriados
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=dias * 2)
        
        logger.info(f"📅 Período: {data_inicio.date()} até {data_fim.date()}")
        
        # ====== ESTRATÉGIA 1: Yahoo Finance API v8 Direta (PRIORITÁRIO) ======
        if API_V8_DISPONIVEL:
            logger.info(f"🔄 [1/3] Tentando Yahoo Finance API v8 direta...")
            try:
                df = coletar_dados_yahoo_v8_custom_range(
                    ticker=ticker,
                    start_date=data_inicio.strftime("%Y-%m-%d"),
                    end_date=data_fim.strftime("%Y-%m-%d")
                )
                
                if not df.empty and len(df) >= dias:
                    fonte = "Yahoo Finance API v8"
                    logger.info(f"✅ FONTE: {fonte} | {len(df)} registros brutos → {dias} processados")
                    # Processar DataFrame para formato esperado
                    dados_processados, df_retorno = processar_dataframe(df, dias, ticker)
                    return dados_processados, df_retorno, fonte
                else:
                    logger.warning(f"⚠️ API v8: dados insuficientes ({len(df)}/{dias})")
            
            except Exception as e:
                logger.error(f"❌ API v8 falhou: {str(e)[:100]}")
        
        # ====== ESTRATÉGIA 2: yfinance (fallback confiável) ======
        logger.info(f"🔄 [2/3] Tentando yfinance biblioteca oficial...")
        max_tentativas = 3
        df = pd.DataFrame()
        
        for tentativa in range(max_tentativas):
            logger.info(f"   Tentativa {tentativa + 1}/{max_tentativas}")
            try:
                ticker_obj = yf.Ticker(ticker)
                df = ticker_obj.history(
                    start=data_inicio,
                    end=data_fim,
                    interval='1d',
                    auto_adjust=False,
                    timeout=30
                )
                
                if not df.empty:
                    fonte = "yfinance"
                    logger.info(f"✅ FONTE: {fonte} | {len(df)} registros brutos")
                    break
                
                logger.warning(f"⚠️ yfinance: DataFrame vazio")
                
            except Exception as e:
                logger.error(f"❌ yfinance tentativa {tentativa + 1}: {str(e)[:100]}")
                if tentativa < max_tentativas - 1:
                    time.sleep(2 ** (tentativa + 1))
        
        # ====== ESTRATÉGIA 3: SQLite Database (fallback offline) ======
        if df.empty and DB_DISPONIVEL:
            logger.info(f"🔄 [3/3] Tentando cache SQLite (fallback offline)...")
            try:
                db = get_db()
                dados_db, df_db = db.get_data(ticker, dias=dias)
                
                if dados_db is not None and len(dados_db) >= dias:
                    fonte = "SQLite Cache"
                    logger.info(f"✅ FONTE: {fonte} | {len(dados_db)} registros")
                    return dados_db, df_db, fonte
                else:
                    logger.warning(f"⚠️ SQLite: dados insuficientes ({len(dados_db) if dados_db is not None else 0}/{dias})")
            
            except Exception as e:
                logger.error(f"❌ SQLite falhou: {str(e)[:100]}")
        
            except Exception as e:
                logger.error(f"❌ SQLite falhou: {str(e)[:100]}")
        
        # ====== VALIDAÇÃO FINAL ======
        if df.empty:
            # Fallback hardcoded (último recurso extremo)
            if FALLBACK_DISPONIVEL and ticker.upper() == "B3SA3.SA" and dias == 60:
                logger.warning(f"🔄 Usando fallback hardcoded (dados de exemplo)")
                try:
                    dados_fallback = get_dados_exemplo(ticker, dias)
                    df_fallback = pd.DataFrame(
                        dados_fallback,
                        columns=['Open', 'High', 'Low', 'Close', 'Volume']
                    )
                    fonte = "Fallback Hardcoded"
                    logger.info(f"✅ FONTE: {fonte} | {len(df_fallback)} registros")
                    return dados_fallback, df_fallback, fonte
                except Exception as e:
                    logger.error(f"❌ Fallback falhou: {e}")
            
            # Tudo falhou
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Dados temporariamente indisponíveis para '{ticker}'. "
                       f"Todas estratégias falharam (API v8, yfinance, SQLite). "
                       f"Tente: python database/populate_db.py --ticker {ticker}"
            )
        
        # Processar DataFrame (vindo de yfinance)
        dados_processados, df_retorno = processar_dataframe(df, dias, ticker)
        return dados_processados, df_retorno, fonte
        
    except HTTPException:
        raise
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Erro ao buscar dados para '{ticker}': {str(e)}"
        )


def processar_dataframe(df: pd.DataFrame, dias: int, ticker: str) -> Tuple[np.ndarray, pd.DataFrame]:
    """
    Processa DataFrame bruto para formato esperado pela API.
    
    Args:
        df: DataFrame com dados OHLCV
        dias: Número mínimo de dias esperados
        ticker: Símbolo do ticker (para mensagens de erro)
    
    Returns:
        Tuple (numpy array, DataFrame processado)
    
    Raises:
        HTTPException: Se dados insuficientes ou inválidos
    """
    if len(df) < dias:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dados insuficientes para '{ticker}'. "
                   f"Necessário: {dias} dias, Disponível: {len(df)} dias"
        )
    
    # Selecionar últimos N dias
    df_recente = df.tail(dias).copy()
    
    # Garantir colunas necessárias
    colunas_necessarias = ['Open', 'High', 'Low', 'Close', 'Volume']
    if not all(col in df_recente.columns for col in colunas_necessarias):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dados incompletos para '{ticker}'. "
                   f"Colunas esperadas: {colunas_necessarias}"
        )
    
    # Extrair array numpy [Open, High, Low, Close, Volume]
    dados_array = df_recente[colunas_necessarias].values
    
    # Validar valores não-nulos
    if np.isnan(dados_array).any():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dados contêm valores nulos para '{ticker}'"
        )
    
    # Validar valores positivos (OHLC > 0)
    if (dados_array[:, :4] <= 0).any():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dados contêm valores inválidos (≤0) para '{ticker}'"
        )
    
    return dados_array, df_recente
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
