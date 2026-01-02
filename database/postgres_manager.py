"""
Gerenciador de Database PostgreSQL para Persistência de Previsões

Usa PostgreSQL no Render para persistir dados de monitoramento em produção.
"""

import os
import logging
from datetime import datetime
from typing import Optional, List
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

logger = logging.getLogger(__name__)

# URL de conexão do PostgreSQL (Render)
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://predictfinance_gb6k_user:NVqykY12EDGSl5fOee0MYUc7YaW64wIS@dpg-d5c2tcruibrs73cs32pg-a.ohio-postgres.render.com/predictfinance_gb6k'
)

# Tentar importar psycopg2
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_DISPONIVEL = True
except ImportError:
    POSTGRES_DISPONIVEL = False
    logger.warning("⚠️ psycopg2 não instalado. Use: pip install psycopg2-binary")


class PostgresManager:
    """Gerenciador de banco de dados PostgreSQL para previsões"""
    
    def __init__(self, database_url: str = None):
        """
        Inicializa conexão com PostgreSQL.
        
        Args:
            database_url: URL de conexão (usa env var se não fornecida)
        """
        self.database_url = database_url or DATABASE_URL
        self._ensure_tables()
    
    def _get_connection(self):
        """Cria uma nova conexão com o banco"""
        if not POSTGRES_DISPONIVEL:
            raise RuntimeError("psycopg2 não está instalado")
        
        return psycopg2.connect(self.database_url)
    
    def _ensure_tables(self):
        """Cria tabelas se não existirem"""
        if not POSTGRES_DISPONIVEL:
            logger.warning("⚠️ PostgreSQL não disponível - tabelas não criadas")
            return
        
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Tabela de previsões
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS predictions (
                            id SERIAL PRIMARY KEY,
                            request_id VARCHAR(100) UNIQUE NOT NULL,
                            ticker VARCHAR(20) NOT NULL,
                            timestamp TIMESTAMP NOT NULL,
                            predicted_value DECIMAL(10, 4) NOT NULL,
                            actual_value DECIMAL(10, 4),
                            error DECIMAL(10, 4),
                            error_pct DECIMAL(10, 4),
                            validated BOOLEAN DEFAULT FALSE,
                            validation_date TIMESTAMP,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Índices para performance
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_pred_ticker 
                        ON predictions(ticker)
                    """)
                    
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_pred_validated 
                        ON predictions(validated)
                    """)
                    
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_pred_timestamp 
                        ON predictions(timestamp DESC)
                    """)
                    
                    # Tabela de métricas diárias
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS daily_metrics (
                            id SERIAL PRIMARY KEY,
                            ticker VARCHAR(20) NOT NULL,
                            date DATE NOT NULL,
                            mae DECIMAL(10, 4),
                            mape DECIMAL(10, 4),
                            rmse DECIMAL(10, 4),
                            predictions_count INTEGER DEFAULT 0,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(ticker, date)
                        )
                    """)
                    
                    conn.commit()
                    logger.info("✅ Tabelas PostgreSQL verificadas/criadas")
                    
        except Exception as e:
            logger.error(f"❌ Erro ao criar tabelas PostgreSQL: {e}")
    
    def insert_prediction(
        self,
        request_id: str,
        ticker: str,
        timestamp: str,
        predicted_value: float
    ) -> bool:
        """
        Insere uma nova previsão no banco.
        
        Args:
            request_id: ID único da requisição
            ticker: Símbolo da ação
            timestamp: Data/hora da previsão (ISO format)
            predicted_value: Valor previsto
        
        Returns:
            True se inserido com sucesso
        """
        if not POSTGRES_DISPONIVEL:
            return False
        
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO predictions 
                        (request_id, ticker, timestamp, predicted_value, validated)
                        VALUES (%s, %s, %s, %s, FALSE)
                        ON CONFLICT (request_id) DO NOTHING
                    """, (request_id, ticker, timestamp, predicted_value))
                    
                    conn.commit()
                    logger.info(f"✅ Previsão {request_id[:8]} salva no PostgreSQL")
                    return True
                    
        except Exception as e:
            logger.error(f"❌ Erro ao salvar previsão no PostgreSQL: {e}")
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
        Atualiza uma previsão com dados de validação.
        
        Args:
            request_id: ID da previsão
            actual_value: Valor real observado
            error: Erro absoluto
            error_pct: Erro percentual
            validation_date: Data da validação (ISO format)
        
        Returns:
            True se atualizado com sucesso
        """
        if not POSTGRES_DISPONIVEL:
            return False
        
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE predictions 
                        SET actual_value = %s, 
                            error = %s, 
                            error_pct = %s,
                            validated = TRUE,
                            validation_date = %s
                        WHERE request_id = %s
                    """, (actual_value, error, error_pct, validation_date, request_id))
                    
                    conn.commit()
                    
                    if cur.rowcount > 0:
                        logger.info(f"✅ Previsão {request_id[:8]} validada no PostgreSQL")
                        return True
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erro ao validar previsão no PostgreSQL: {e}")
            return False
    
    def get_predictions(
        self,
        ticker: str = None,
        validated: bool = None,
        limit: int = 100
    ) -> List[dict]:
        """
        Busca previsões do banco.
        
        Args:
            ticker: Filtrar por ticker (opcional)
            validated: Filtrar por status de validação (opcional)
            limit: Número máximo de resultados
        
        Returns:
            Lista de dicionários com previsões
        """
        if not POSTGRES_DISPONIVEL:
            return []
        
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    query = "SELECT * FROM predictions WHERE 1=1"
                    params = []
                    
                    if ticker:
                        query += " AND ticker = %s"
                        params.append(ticker)
                    
                    if validated is not None:
                        query += " AND validated = %s"
                        params.append(validated)
                    
                    query += " ORDER BY timestamp DESC LIMIT %s"
                    params.append(limit)
                    
                    cur.execute(query, params)
                    rows = cur.fetchall()
                    
                    predictions = []
                    for row in rows:
                        predictions.append({
                            "request_id": row["request_id"],
                            "ticker": row["ticker"],
                            "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None,
                            "predicted_value": float(row["predicted_value"]) if row["predicted_value"] else None,
                            "actual_value": float(row["actual_value"]) if row["actual_value"] else None,
                            "error": float(row["error"]) if row["error"] else None,
                            "error_pct": float(row["error_pct"]) if row["error_pct"] else None,
                            "validated": row["validated"],
                            "validation_date": row["validation_date"].isoformat() if row["validation_date"] else None
                        })
                    
                    return predictions
                    
        except Exception as e:
            logger.error(f"❌ Erro ao buscar previsões do PostgreSQL: {e}")
            return []
    
    def get_prediction_stats(self, ticker: str = None) -> dict:
        """
        Retorna estatísticas das previsões.
        
        Args:
            ticker: Filtrar por ticker (opcional)
        
        Returns:
            Dict com estatísticas
        """
        if not POSTGRES_DISPONIVEL:
            return {"total": 0, "validated": 0, "pending": 0}
        
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    ticker_filter = "AND ticker = %s" if ticker else ""
                    params = [ticker] if ticker else []
                    
                    # Total e contagens
                    cur.execute(f"""
                        SELECT 
                            COUNT(*) as total,
                            SUM(CASE WHEN validated = TRUE THEN 1 ELSE 0 END) as validated,
                            SUM(CASE WHEN validated = FALSE THEN 1 ELSE 0 END) as pending
                        FROM predictions
                        WHERE 1=1 {ticker_filter}
                    """, params)
                    
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
                    """, params)
                    
                    metrics_row = cur.fetchone()
                    
                    if metrics_row and metrics_row[0] is not None:
                        # Calcular RMSE
                        cur.execute(f"""
                            SELECT error FROM predictions 
                            WHERE validated = TRUE AND error IS NOT NULL {ticker_filter}
                        """, params)
                        errors = [r[0] for r in cur.fetchall()]
                        rmse = (sum(float(e)**2 for e in errors) / len(errors)) ** 0.5 if errors else None
                        
                        stats.update({
                            "mae": float(metrics_row[0]) if metrics_row[0] else None,
                            "mape": float(metrics_row[1]) if metrics_row[1] else None,
                            "rmse": rmse,
                            "min_error_pct": float(metrics_row[2]) if metrics_row[2] else None,
                            "max_error_pct": float(metrics_row[3]) if metrics_row[3] else None,
                            "avg_predicted": float(metrics_row[4]) if metrics_row[4] else None,
                            "avg_actual": float(metrics_row[5]) if metrics_row[5] else None
                        })
                    
                    return stats
                    
        except Exception as e:
            logger.error(f"❌ Erro ao calcular estatísticas do PostgreSQL: {e}")
            return {"total": 0, "validated": 0, "pending": 0}
    
    def test_connection(self) -> bool:
        """
        Testa a conexão com o banco.
        
        Returns:
            True se conexão bem sucedida
        """
        if not POSTGRES_DISPONIVEL:
            return False
        
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    logger.info("✅ Conexão PostgreSQL OK")
                    return True
        except Exception as e:
            logger.error(f"❌ Erro de conexão PostgreSQL: {e}")
            return False


# Instância global
_pg_manager = None


def get_postgres_db() -> Optional[PostgresManager]:
    """
    Retorna instância global do PostgresManager.
    Cria a instância na primeira chamada.
    
    Returns:
        PostgresManager ou None se não disponível
    """
    global _pg_manager
    
    if not POSTGRES_DISPONIVEL:
        return None
    
    if _pg_manager is None:
        try:
            _pg_manager = PostgresManager()
        except Exception as e:
            logger.error(f"❌ Erro ao criar PostgresManager: {e}")
            return None
    
    return _pg_manager
