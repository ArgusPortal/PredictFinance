"""
Gerenciador de Database PostgreSQL/Supabase para Persistência em Produção

Este módulo fornece persistência real para previsões de monitoramento
usando Supabase (PostgreSQL gratuito na nuvem).

Configuração:
1. Crie uma conta em https://supabase.com (gratuito)
2. Crie um projeto novo
3. Vá em Project Settings > Database > Connection string > URI
4. Adicione a variável de ambiente SUPABASE_DB_URL com a URI
"""

import os
import logging
from datetime import datetime
from typing import List, Optional

logger = logging.getLogger(__name__)

# Verificar se psycopg2 está disponível
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_DISPONIVEL = True
except ImportError:
    PSYCOPG2_DISPONIVEL = False
    logger.warning("⚠️ psycopg2 não instalado. Instale com: pip install psycopg2-binary")


# URL do banco de dados Supabase (variável de ambiente)
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL", "")


class SupabaseManager:
    """Gerenciador de conexão com Supabase PostgreSQL"""
    
    def __init__(self, db_url: str = None):
        """
        Inicializa conexão com Supabase.
        
        Args:
            db_url: URL de conexão PostgreSQL (opcional, usa variável de ambiente)
        """
        self.db_url = db_url or SUPABASE_DB_URL
        self.connected = False
        
        if not PSYCOPG2_DISPONIVEL:
            logger.error("❌ psycopg2 não disponível")
            return
        
        if not self.db_url:
            logger.warning("⚠️ SUPABASE_DB_URL não configurado")
            return
        
        self._ensure_tables()
    
    def _get_connection(self):
        """Cria conexão com o banco"""
        if not PSYCOPG2_DISPONIVEL or not self.db_url:
            return None
        
        try:
            conn = psycopg2.connect(self.db_url)
            return conn
        except Exception as e:
            logger.error(f"❌ Erro ao conectar ao Supabase: {e}")
            return None
    
    def _ensure_tables(self):
        """Cria tabelas necessárias se não existirem"""
        conn = self._get_connection()
        if not conn:
            return
        
        try:
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
                    CREATE INDEX IF NOT EXISTS idx_predictions_ticker 
                    ON predictions(ticker)
                """)
                
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_predictions_validated 
                    ON predictions(validated)
                """)
                
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_predictions_timestamp 
                    ON predictions(timestamp DESC)
                """)
                
                conn.commit()
                self.connected = True
                logger.info("✅ Tabelas Supabase verificadas/criadas")
        except Exception as e:
            logger.error(f"❌ Erro ao criar tabelas: {e}")
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
        conn = self._get_connection()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO predictions 
                    (request_id, ticker, timestamp, predicted_value, validated)
                    VALUES (%s, %s, %s, %s, FALSE)
                    ON CONFLICT (request_id) DO UPDATE 
                    SET predicted_value = EXCLUDED.predicted_value
                """, (request_id, ticker, timestamp, predicted_value))
                
                conn.commit()
                logger.info(f"✅ Previsão {request_id[:8]} salva no Supabase")
                return True
        except Exception as e:
            logger.error(f"❌ Erro ao salvar previsão: {e}")
            return False
        finally:
            conn.close()
    
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
        conn = self._get_connection()
        if not conn:
            return False
        
        try:
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
                    logger.info(f"✅ Previsão {request_id[:8]} validada no Supabase")
                    return True
                return False
        except Exception as e:
            logger.error(f"❌ Erro ao validar previsão: {e}")
            return False
        finally:
            conn.close()
    
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
        conn = self._get_connection()
        if not conn:
            return []
        
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
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
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
            logger.error(f"❌ Erro ao buscar previsões: {e}")
            return []
        finally:
            conn.close()
    
    def get_prediction_stats(self, ticker: str = None) -> dict:
        """
        Retorna estatísticas das previsões
        
        Args:
            ticker: Filtrar por ticker (opcional)
        
        Returns:
            Dict com estatísticas
        """
        conn = self._get_connection()
        if not conn:
            return {"total": 0, "validated": 0, "pending": 0}
        
        ticker_filter = "AND ticker = %s" if ticker else ""
        params = [ticker] if ticker else []
        
        try:
            with conn.cursor() as cur:
                # Total e contagens
                cur.execute(f"""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN validated = TRUE THEN 1 ELSE 0 END) as validated_count,
                        SUM(CASE WHEN validated = FALSE THEN 1 ELSE 0 END) as pending_count
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
                        AVG(actual_value) as avg_actual,
                        SQRT(AVG(error * error)) as rmse
                    FROM predictions
                    WHERE validated = TRUE {ticker_filter}
                """, params)
                
                metrics_row = cur.fetchone()
                
                if metrics_row and metrics_row[0] is not None:
                    stats.update({
                        "mae": float(metrics_row[0]),
                        "mape": float(metrics_row[1]) if metrics_row[1] else None,
                        "min_error_pct": float(metrics_row[2]) if metrics_row[2] else None,
                        "max_error_pct": float(metrics_row[3]) if metrics_row[3] else None,
                        "avg_predicted": float(metrics_row[4]) if metrics_row[4] else None,
                        "avg_actual": float(metrics_row[5]) if metrics_row[5] else None,
                        "rmse": float(metrics_row[6]) if metrics_row[6] else None
                    })
                
                return stats
        except Exception as e:
            logger.error(f"❌ Erro ao calcular estatísticas: {e}")
            return {"total": 0, "validated": 0, "pending": 0}
        finally:
            conn.close()
    
    def is_connected(self) -> bool:
        """Verifica se está conectado ao Supabase"""
        return self.connected and bool(self.db_url)


# Instância global (será None se não configurado)
_supabase_instance = None


def get_supabase_db() -> Optional[SupabaseManager]:
    """
    Retorna instância do gerenciador Supabase.
    Retorna None se não configurado.
    """
    global _supabase_instance
    
    if _supabase_instance is None:
        _supabase_instance = SupabaseManager()
        
        if not _supabase_instance.is_connected():
            logger.warning("⚠️ Supabase não configurado. Usando SQLite local como fallback.")
            return None
    
    return _supabase_instance if _supabase_instance.is_connected() else None
