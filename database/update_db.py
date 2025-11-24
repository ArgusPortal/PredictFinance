"""
Script de Atualização Diária do Banco de Dados

Este script busca dados novos do Yahoo Finance desde a última data
armazenada no banco e atualiza o cache SQLite.

Uso:
    python database/update_db.py
    python database/update_db.py --ticker PETR4.SA

Projetado para ser executado em cron job ou GitHub Actions diariamente.
"""

import sys
import os
import argparse
import time
from datetime import datetime, timedelta
from pathlib import Path

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    import codecs
    if not hasattr(sys.stdout, 'buffer'):
        # Já está configurado, não fazer nada
        pass
    else:
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Adiciona diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

try:
    import yfinance as yf
    import pandas as pd
    from database import get_db
    from src.yahoo_finance_v8 import coletar_dados_yahoo_v8_custom_range
except ImportError as e:
    print(f"❌ Erro ao importar dependências: {e}")
    print("Execute: pip install yfinance pandas")
    sys.exit(1)


def buscar_dados_yahoo(ticker: str, start_date: str, end_date: str, max_tentativas: int = 3) -> pd.DataFrame:
    """
    Busca dados do Yahoo Finance usando API v8 como método primário.
    Fallback para yfinance se API v8 falhar.
    
    Args:
        ticker: Símbolo da ação (ex: B3SA3.SA)
        start_date: Data inicial (YYYY-MM-DD)
        end_date: Data final (YYYY-MM-DD)
        max_tentativas: Número máximo de tentativas
        
    Returns:
        DataFrame com dados OHLCV ou DataFrame vazio se falhar
    """
    # Método 1: API v8 (mais rápido e confiável)
    print(f"🚀 Tentando API v8 direta...")
    try:
        df = coletar_dados_yahoo_v8_custom_range(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            interval='1d'
        )
        
        if not df.empty:
            print(f"✅ API v8: {len(df)} registros obtidos")
            # Garantir colunas consistentes
            return df[['Open', 'High', 'Low', 'Close', 'Volume']]
    except Exception as e:
        print(f"⚠️  API v8 falhou: {str(e)}")
        print(f"🔄 Usando yfinance como fallback...")
    
    # Método 2: yfinance (fallback)
    for tentativa in range(1, max_tentativas + 1):
        try:
            print(f"🔄 Tentativa {tentativa}/{max_tentativas} - Buscando dados de {start_date} a {end_date}...")
            
            stock = yf.Ticker(ticker)
            df = stock.history(
                start=start_date,
                end=end_date,
                interval='1d',
                timeout=30
            )
            
            if not df.empty:
                print(f"✅ yfinance: {len(df)} registros obtidos")
                return df[['Open', 'High', 'Low', 'Close', 'Volume']]
            else:
                print(f"⚠️  Nenhum dado retornado para {ticker} (tentativa {tentativa})")
                
        except Exception as e:
            print(f"❌ Erro na tentativa {tentativa}: {str(e)}")
            
            if tentativa < max_tentativas:
                tempo_espera = 2 ** tentativa  # Backoff exponencial
                print(f"⏳ Aguardando {tempo_espera}s antes da próxima tentativa...")
                time.sleep(tempo_espera)
    
    print(f"❌ Falha após {max_tentativas} tentativas (ambos os métodos)")
    return pd.DataFrame()


def validar_dados(df: pd.DataFrame) -> bool:
    """
    Valida dados retornados pelo Yahoo Finance.
    
    Args:
        df: DataFrame com dados OHLCV
        
    Returns:
        True se dados são válidos, False caso contrário
    """
    if df.empty:
        print("❌ DataFrame vazio")
        return False
    
    # Verifica valores nulos
    if df.isnull().any().any():
        print("⚠️  Dados contêm valores nulos")
        return False
    
    # Verifica valores negativos
    if (df < 0).any().any():
        print("❌ Dados contêm valores negativos inválidos")
        return False
    
    # Verifica se High >= Low
    if not (df['High'] >= df['Low']).all():
        print("❌ Dados inválidos: High < Low em alguns registros")
        return False
    
    print("✅ Validação dos dados OK")
    return True


def atualizar_ticker(ticker: str) -> bool:
    """
    Atualiza dados de um ticker no banco de dados.
    
    Args:
        ticker: Símbolo da ação
        
    Returns:
        True se atualização foi bem sucedida, False caso contrário
    """
    print(f"\n{'='*60}")
    print(f"Atualizando {ticker}")
    print(f"{'='*60}")
    
    db = get_db()
    
    # Obtém última data no banco
    ultima_data = db.get_latest_date(ticker)
    
    if ultima_data:
        print(f"📅 Última data no banco: {ultima_data}")
        
        # Calcula data inicial (dia seguinte à última data)
        # ultima_data já é datetime, não precisa converter
        start_date = (ultima_data + timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        print(f"⚠️  Nenhum dado existente para {ticker}")
        # Se não há dados, busca últimos 5 anos
        start_date = (datetime.now() - timedelta(days=5*365)).strftime('%Y-%m-%d')
    
    # Data final é hoje
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    # Verifica se há dados novos para buscar
    if start_date >= end_date:
        print(f"✅ Banco já está atualizado (última data: {ultima_data})")
        return True
    
    print(f"📥 Buscando dados de {start_date} até {end_date}...")
    
    # Busca dados novos
    df = buscar_dados_yahoo(ticker, start_date, end_date)
    
    if df.empty:
        print(f"⚠️  Nenhum dado novo obtido do Yahoo Finance")
        return False
    
    # Valida dados
    if not validar_dados(df):
        print(f"❌ Dados inválidos - não salvos no banco")
        return False
    
    # Insere no banco
    try:
        registros_novos = db.insert_data(ticker, df)
        print(f"✅ {registros_novos} novos registros inseridos no banco")
        
        # Mostra estatísticas atualizadas
        stats = db.get_stats(ticker)
        print(f"\n📊 Estatísticas atualizadas:")
        print(f"   Total de registros: {stats['total_records']}")
        print(f"   Data mais antiga: {stats['oldest_date']}")
        print(f"   Data mais recente: {stats['newest_date']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inserir dados no banco: {str(e)}")
        return False


def main():
    """Função principal do script."""
    parser = argparse.ArgumentParser(
        description='Atualiza banco de dados SQLite com dados mais recentes do Yahoo Finance'
    )
    parser.add_argument(
        '--ticker',
        type=str,
        default='B3SA3.SA',
        help='Ticker da ação para atualizar (padrão: B3SA3.SA)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Atualiza todos os tickers no banco'
    )
    
    args = parser.parse_args()
    
    print(f"\n🚀 Script de Atualização do Banco de Dados")
    print(f"{'='*60}")
    print(f"Horário: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    db = get_db()
    sucesso_total = True
    
    if args.all:
        # Atualiza todos os tickers
        # Nota: Implementar método get_all_tickers() no db_manager.py se necessário
        print("⚠️  Modo --all ainda não implementado")
        print("Execute manualmente para cada ticker: python database/update_db.py --ticker TICKER")
        return
    else:
        # Atualiza ticker específico
        sucesso = atualizar_ticker(args.ticker)
        if not sucesso:
            sucesso_total = False
    
    print(f"\n{'='*60}")
    if sucesso_total:
        print("✅ Atualização concluída com sucesso!")
    else:
        print("⚠️  Atualização concluída com alguns erros")
    print(f"{'='*60}\n")
    
    # Exit code para GitHub Actions
    sys.exit(0 if sucesso_total else 1)


if __name__ == "__main__":
    main()
