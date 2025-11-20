"""
Gerenciador de Database SQLite para Cache de Dados Históricos

Armazena dados OHLCV de ações para uso offline/fallback quando Yahoo Finance falhar.
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple, List
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Path do banco de dados
DB_PATH = Path(__file__).parent / "market_data.db"


class MarketDataDB:
    """Gerenciador de banco de dados de mercado"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._ensure_database()
    
    def _ensure_database(self):
        """Cria database e tabelas se não existirem"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stock_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    date DATE NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(ticker, date)
                )
            """)
            
            # Índices para performance
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ticker_date 
                ON stock_data(ticker, date DESC)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ticker 
                ON stock_data(ticker)
            """)
            
            logger.info(f"✅ Database inicializado: {self.db_path}")
    
    def insert_data(self, ticker: str, df: pd.DataFrame) -> int:
        """
        Insere dados históricos no banco
        
        Args:
            ticker: Símbolo da ação (ex: B3SA3.SA)
            df: DataFrame com colunas [Date, Open, High, Low, Close, Volume]
        
        Returns:
            Número de linhas inseridas
        """
        with sqlite3.connect(self.db_path) as conn:
            inserted = 0
            
            for idx, row in df.iterrows():
                try:
                    # Extrair data do index (datetime)
                    if isinstance(idx, pd.Timestamp):
                        date_str = idx.strftime('%Y-%m-%d')
                    else:
                        date_str = str(idx)[:10]
                    
                    conn.execute("""
                        INSERT OR REPLACE INTO stock_data 
                        (ticker, date, open, high, low, close, volume)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        ticker,
                        date_str,
                        float(row['Open']),
                        float(row['High']),
                        float(row['Low']),
                        float(row['Close']),
                        int(row['Volume'])
                    ))
                    inserted += 1
                
                except Exception as e:
                    logger.warning(f"Erro ao inserir linha {idx}: {e}")
                    continue
            
            logger.info(f"✅ {inserted} registros inseridos para {ticker}")
            return inserted
    
    def get_data(
        self, 
        ticker: str, 
        dias: int = 60,
        end_date: Optional[datetime] = None
    ) -> Tuple[Optional[np.ndarray], Optional[pd.DataFrame]]:
        """
        Busca dados históricos do banco
        
        Args:
            ticker: Símbolo da ação
            dias: Número de dias necessários
            end_date: Data final (default: hoje)
        
        Returns:
            Tuple (numpy array, DataFrame) ou (None, None) se insuficiente
        """
        if end_date is None:
            end_date = datetime.now()
        
        end_str = end_date.strftime('%Y-%m-%d')
        
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT date, open, high, low, close, volume
                FROM stock_data
                WHERE ticker = ? AND date <= ?
                ORDER BY date DESC
                LIMIT ?
            """
            
            cursor = conn.execute(query, (ticker, end_str, dias))
            rows = cursor.fetchall()
            
            if len(rows) < dias:
                logger.warning(
                    f"⚠️ Dados insuficientes no DB: {len(rows)}/{dias} dias"
                )
                return None, None
            
            # Converter para DataFrame (reverter ordem: mais antigo → mais recente)
            df = pd.DataFrame(
                reversed(rows),
                columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            )
            
            # Converter Date para datetime
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            
            # Converter para numpy array (OHLCV)
            data_array = df[['Open', 'High', 'Low', 'Close', 'Volume']].values
            
            logger.info(f"✅ {len(df)} dias recuperados do DB para {ticker}")
            
            return data_array, df
    
    def get_data_by_period(
        self,
        ticker: str,
        start_date,  # Union[str, datetime]
        end_date     # Union[str, datetime]
    ) -> Optional[pd.DataFrame]:
        """
        Busca dados por período específico
        
        Args:
            ticker: Símbolo da ação
            start_date: Data inicial (str YYYY-MM-DD ou datetime)
            end_date: Data final (str YYYY-MM-DD ou datetime)
        
        Returns:
            DataFrame ou None
        """
        # Normalizar datas para string
        if hasattr(start_date, 'strftime'):
            start_str = start_date.strftime('%Y-%m-%d')
        else:
            start_str = str(start_date)
            
        if hasattr(end_date, 'strftime'):
            end_str = end_date.strftime('%Y-%m-%d')
        else:
            end_str = str(end_date)
        
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT date, open, high, low, close, volume
                FROM stock_data
                WHERE ticker = ? 
                  AND date BETWEEN ? AND ?
                ORDER BY date ASC
            """
            
            df = pd.read_sql_query(
                query, 
                conn, 
                params=(ticker, start_str, end_str),
                parse_dates=['date'],
                index_col='date'
            )
            
            if df.empty:
                return None
            
            # Renomear colunas para capitalizado
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            
            logger.info(
                f"✅ Período {start_str} a {end_str}: "
                f"{len(df)} dias"
            )
            
            return df
    
    def get_latest_date(self, ticker: str) -> Optional[datetime]:
        """
        Retorna data mais recente disponível para um ticker
        
        Args:
            ticker: Símbolo da ação
        
        Returns:
            datetime ou None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT MAX(date) FROM stock_data WHERE ticker = ?
            """, (ticker,))
            
            result = cursor.fetchone()[0]
            
            if result:
                return datetime.strptime(result, '%Y-%m-%d')
            
            return None
    
    def get_stats(self, ticker: str) -> dict:
        """
        Retorna estatísticas do banco para um ticker
        
        Args:
            ticker: Símbolo da ação
        
        Returns:
            Dict com estatísticas
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    MIN(date) as oldest_date,
                    MAX(date) as newest_date
                FROM stock_data
                WHERE ticker = ?
            """, (ticker,))
            
            row = cursor.fetchone()
            
            if row and row[0] > 0:
                return {
                    'total_records': row[0],
                    'oldest_date': row[1],
                    'newest_date': row[2],
                    'has_data': True
                }
            
            return {'has_data': False}
    
    def delete_ticker(self, ticker: str) -> int:
        """
        Remove todos os dados de um ticker
        
        Args:
            ticker: Símbolo da ação
        
        Returns:
            Número de linhas deletadas
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM stock_data WHERE ticker = ?
            """, (ticker,))
            
            deleted = cursor.rowcount
            logger.info(f"🗑️ {deleted} registros deletados para {ticker}")
            
            return deleted


# Instância global
db = MarketDataDB()


def get_db() -> MarketDataDB:
    """Retorna instância global do database"""
    return db
