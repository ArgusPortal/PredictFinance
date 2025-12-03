"""
Gerenciador de Database SQLite para Cache de Dados Históricos

Armazena dados OHLCV de ações para uso offline/fallback quando Yahoo Finance falhar.
"""

import os
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple, List
import numpy as np
import pandas as pd

# Suporte opcional a PostgreSQL (Render DB)
DATABASE_URL = os.getenv("DATABASE_URL")
PG_AVAILABLE = False
try:
    import psycopg2
    import psycopg2.extras
    PG_AVAILABLE = bool(DATABASE_URL)
except Exception:
    psycopg2 = None
    psycopg2_extras = None
    PG_AVAILABLE = False

logger = logging.getLogger(__name__)

# Path do banco de dados
DB_PATH = Path(__file__).parent / "market_data.db"


class MarketDataDB:
    """Gerenciador de banco de dados de mercado"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._ensure_database()

        # Inicializar conexão PostgreSQL se variável de ambiente estiver presente
        self.pg_enabled = False
        if PG_AVAILABLE:
            try:
                # Testar conexão e garantir tabela de previsões em Postgres
                self._ensure_predictions_table_pg()
                self.pg_enabled = True
                logger.info("✅ PostgreSQL disponível para persistência de previsões")
            except Exception as e:
                logger.warning(f"⚠️ PostgreSQL detectado mas não inicializado: {e}")
    
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
    
    # ============================================================
    # MÉTODOS PARA PERSISTÊNCIA DE PREVISÕES DE MONITORAMENTO
    # ============================================================
    
    def _ensure_predictions_table(self):
        """Cria tabela de previsões se não existir"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT UNIQUE NOT NULL,
                    ticker TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    predicted_value REAL NOT NULL,
                    actual_value REAL,
                    error REAL,
                    error_pct REAL,
                    validated INTEGER DEFAULT 0,
                    validation_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Índices para performance
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_predictions_ticker 
                ON predictions(ticker)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_predictions_validated 
                ON predictions(validated)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_predictions_timestamp 
                ON predictions(timestamp DESC)
            """)
            
            logger.info("✅ Tabela predictions verificada/criada")

    def _ensure_predictions_table_pg(self):
        """Cria tabela de previsões no PostgreSQL se não existir"""
        if not DATABASE_URL:
            raise RuntimeError("DATABASE_URL não definida")

        conn = psycopg2.connect(DATABASE_URL)
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS predictions (
                            id SERIAL PRIMARY KEY,
                            request_id TEXT UNIQUE NOT NULL,
                            ticker TEXT NOT NULL,
                            timestamp TIMESTAMP NOT NULL,
                            predicted_value DOUBLE PRECISION NOT NULL,
                            actual_value DOUBLE PRECISION,
                            error DOUBLE PRECISION,
                            error_pct DOUBLE PRECISION,
                            validated BOOLEAN DEFAULT FALSE,
                            validation_date TIMESTAMP,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                        """
                    )
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_predictions_ticker ON predictions(ticker)")
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_predictions_validated ON predictions(validated)")
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON predictions(timestamp DESC)")
        finally:
            conn.close()
    
    def insert_prediction(
        self,
        request_id: str,
        ticker: str,
        timestamp: str,
        predicted_value: float
    ) -> bool:
        """
        Insere uma nova previsão no banco
        
        Args:
            request_id: ID único da requisição
            ticker: Símbolo da ação
            timestamp: Data/hora da previsão (ISO format)
            predicted_value: Valor previsto
        
        Returns:
            True se inserido com sucesso
        """
        # Se Postgres estiver habilitado, usar ele para persistência
        if getattr(self, 'pg_enabled', False):
            try:
                conn = psycopg2.connect(DATABASE_URL)
                with conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            INSERT INTO predictions (request_id, ticker, timestamp, predicted_value, validated)
                            VALUES (%s, %s, %s, %s, FALSE)
                            ON CONFLICT (request_id) DO UPDATE SET
                                predicted_value = EXCLUDED.predicted_value,
                                timestamp = EXCLUDED.timestamp
                            """,
                            (request_id, ticker, timestamp, predicted_value)
                        )
                logger.info(f"✅ Previsão {request_id[:8]} salva no Postgres")
                return True
            except Exception as e:
                logger.error(f"❌ Erro ao salvar previsão no Postgres: {e}")
                # cair no fallback para SQLite

        # Fallback: SQLite local
        self._ensure_predictions_table()
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO predictions 
                    (request_id, ticker, timestamp, predicted_value, validated)
                    VALUES (?, ?, ?, ?, 0)
                """, (request_id, ticker, timestamp, predicted_value))
                logger.info(f"✅ Previsão {request_id[:8]} salva no DB (SQLite)")
                return True
        except Exception as e:
            logger.error(f"❌ Erro ao salvar previsão: {e}")
            return False
    
    def update_prediction_validation(
        self,
        request_id: str,
        actual_value: float,
        error: float,
        error_pct: float,
        validation_date: str
    ) -> bool:
        """
        Atualiza uma previsão com dados de validação
        
        Args:
            request_id: ID da previsão
            actual_value: Valor real observado
            error: Erro absoluto
            error_pct: Erro percentual
            validation_date: Data da validação (ISO format)
        
        Returns:
            True se atualizado com sucesso
        """
        # Primeiro, tentar atualizar no Postgres se habilitado
        if getattr(self, 'pg_enabled', False):
            try:
                conn = psycopg2.connect(DATABASE_URL)
                with conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            UPDATE predictions
                            SET actual_value = %s,
                                error = %s,
                                error_pct = %s,
                                validated = TRUE,
                                validation_date = %s
                            WHERE request_id = %s
                            """,
                            (actual_value, error, error_pct, validation_date, request_id)
                        )
                        if cur.rowcount > 0:
                            logger.info(f"✅ Previsão {request_id[:8]} validada no Postgres")
                            return True
            except Exception as e:
                logger.error(f"❌ Erro ao validar previsão no Postgres: {e}")

        # Fallback: SQLite
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    UPDATE predictions 
                    SET actual_value = ?, 
                        error = ?, 
                        error_pct = ?,
                        validated = 1,
                        validation_date = ?
                    WHERE request_id = ?
                """, (actual_value, error, error_pct, validation_date, request_id))

                if cursor.rowcount > 0:
                    logger.info(f"✅ Previsão {request_id[:8]} validada no DB (SQLite)")
                    return True
                return False
        except Exception as e:
            logger.error(f"❌ Erro ao validar previsão: {e}")
            return False
    
    def get_predictions(
        self,
        ticker: str = None,
        validated: bool = None,
        limit: int = 100
    ) -> List[dict]:
        """
        Busca previsões do banco
        
        Args:
            ticker: Filtrar por ticker (opcional)
            validated: Filtrar por status de validação (opcional)
            limit: Número máximo de resultados
        
        Returns:
            Lista de dicionários com previsões
        """
        # Tentar obter previsões do Postgres se habilitado
        if getattr(self, 'pg_enabled', False):
            try:
                conn = psycopg2.connect(DATABASE_URL)
                with conn:
                    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                        sql = "SELECT request_id, ticker, timestamp, predicted_value, actual_value, error, error_pct, validated, validation_date FROM predictions WHERE 1=1"
                        params = []
                        if ticker:
                            sql += " AND ticker = %s"
                            params.append(ticker)
                        if validated is not None:
                            sql += " AND validated = %s"
                            params.append(validated)
                        sql += " ORDER BY timestamp DESC LIMIT %s"
                        params.append(limit)
                        cur.execute(sql, tuple(params))
                        rows = cur.fetchall()
                        preds = []
                        for r in rows:
                            preds.append({
                                "request_id": r["request_id"],
                                "ticker": r["ticker"],
                                "timestamp": r["timestamp"].isoformat() if r["timestamp"] else None,
                                "predicted_value": r["predicted_value"],
                                "actual_value": r["actual_value"],
                                "error": r["error"],
                                "error_pct": r["error_pct"],
                                "validated": bool(r["validated"]),
                                "validation_date": r["validation_date"].isoformat() if r["validation_date"] else None
                            })
                        return preds
            except Exception as e:
                logger.error(f"❌ Erro ao buscar previsões no Postgres: {e}")

        # Fallback: SQLite
        self._ensure_predictions_table()
        query = "SELECT * FROM predictions WHERE 1=1"
        params = []
        if ticker:
            query += " AND ticker = ?"
            params.append(ticker)
        if validated is not None:
            query += " AND validated = ?"
            params.append(1 if validated else 0)
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                predictions = []
                for row in rows:
                    predictions.append({
                        "request_id": row["request_id"],
                        "ticker": row["ticker"],
                        "timestamp": row["timestamp"],
                        "predicted_value": row["predicted_value"],
                        "actual_value": row["actual_value"],
                        "error": row["error"],
                        "error_pct": row["error_pct"],
                        "validated": bool(row["validated"]),
                        "validation_date": row["validation_date"]
                    })
                return predictions
        except Exception as e:
            logger.error(f"❌ Erro ao buscar previsões: {e}")
            return []
    
    def get_prediction_stats(self, ticker: str = None) -> dict:
        """
        Retorna estatísticas das previsões
        
        Args:
            ticker: Filtrar por ticker (opcional)
        
        Returns:
            Dict com estatísticas
        """
        # Tentar Postgres primeiro
        if getattr(self, 'pg_enabled', False):
            try:
                conn = psycopg2.connect(DATABASE_URL)
                with conn:
                    with conn.cursor() as cur:
                        params = []
                        ticker_filter = "AND ticker = %s" if ticker else ""
                        if ticker:
                            params.append(ticker)

                        cur.execute(f"""
                            SELECT 
                                COUNT(*) as total,
                                SUM(CASE WHEN validated THEN 1 ELSE 0 END) as validated,
                                SUM(CASE WHEN NOT validated THEN 1 ELSE 0 END) as pending
                            FROM predictions
                            WHERE 1=1 {ticker_filter}
                        """, tuple(params))
                        row = cur.fetchone()
                        stats = {
                            "total": row[0] or 0,
                            "validated": row[1] or 0,
                            "pending": row[2] or 0
                        }

                        # Métricas de validados
                        cur.execute(f"""
                            SELECT 
                                AVG(error) as mae,
                                AVG(error_pct) as mape,
                                MIN(error_pct) as min_error_pct,
                                MAX(error_pct) as max_error_pct,
                                AVG(predicted_value) as avg_predicted,
                                AVG(actual_value) as avg_actual
                            FROM predictions
                            WHERE validated = TRUE {ticker_filter}
                        """, tuple(params))
                        metrics_row = cur.fetchone()
                        if metrics_row and metrics_row[0] is not None:
                            cur.execute(f"SELECT error FROM predictions WHERE validated = TRUE AND error IS NOT NULL {ticker_filter}", tuple(params))
                            errors = [r[0] for r in cur.fetchall()]
                            rmse = (sum(e**2 for e in errors) / len(errors)) ** 0.5 if errors else None
                            stats.update({
                                "mae": metrics_row[0],
                                "mape": metrics_row[1],
                                "rmse": rmse,
                                "min_error_pct": metrics_row[2],
                                "max_error_pct": metrics_row[3],
                                "avg_predicted": metrics_row[4],
                                "avg_actual": metrics_row[5]
                            })
                        return stats
            except Exception as e:
                logger.error(f"❌ Erro ao calcular estatísticas no Postgres: {e}")

        # Fallback: SQLite
        self._ensure_predictions_table()
        ticker_filter = "AND ticker = ?" if ticker else ""
        params = [ticker] if ticker else []
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Total e contagens
                cursor = conn.execute(f"""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN validated = 1 THEN 1 ELSE 0 END) as validated,
                        SUM(CASE WHEN validated = 0 THEN 1 ELSE 0 END) as pending
                    FROM predictions
                    WHERE 1=1 {ticker_filter}
                """, params)
                row = cursor.fetchone()
                stats = {
                    "total": row[0] or 0,
                    "validated": row[1] or 0,
                    "pending": row[2] or 0
                }
                cursor = conn.execute(f"""
                    SELECT 
                        AVG(error) as mae,
                        AVG(error_pct) as mape,
                        MIN(error_pct) as min_error_pct,
                        MAX(error_pct) as max_error_pct,
                        AVG(predicted_value) as avg_predicted,
                        AVG(actual_value) as avg_actual
                    FROM predictions
                    WHERE validated = 1 {ticker_filter}
                """, params)
                metrics_row = cursor.fetchone()
                if metrics_row and metrics_row[0] is not None:
                    cursor2 = conn.execute(f"""
                        SELECT error FROM predictions 
                        WHERE validated = 1 AND error IS NOT NULL {ticker_filter}
                    """, params)
                    errors = [r[0] for r in cursor2.fetchall()]
                    rmse = (sum(e**2 for e in errors) / len(errors)) ** 0.5 if errors else None
                    stats.update({
                        "mae": metrics_row[0],
                        "mape": metrics_row[1],
                        "rmse": rmse,
                        "min_error_pct": metrics_row[2],
                        "max_error_pct": metrics_row[3],
                        "avg_predicted": metrics_row[4],
                        "avg_actual": metrics_row[5]
                    })
                return stats
        except Exception as e:
            logger.error(f"❌ Erro ao calcular estatísticas: {e}")
            return {"total": 0, "validated": 0, "pending": 0}


# Instância global
db = MarketDataDB()


def get_db() -> MarketDataDB:
    """Retorna instância global do database"""
    return db
