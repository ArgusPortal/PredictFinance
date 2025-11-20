"""
Sistema de Logging e Monitoramento para API de Previsão B3SA3

Implementa logging estruturado de requisições para auditoria e análise.
Registra timestamp, request_id, estatísticas dos inputs e resultados.
"""

import logging
import uuid
import json
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
import numpy as np


# Configuração do diretório de logs
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Configuração de logging
LOG_FILE = LOGS_DIR / "predictions.log"
METRICS_FILE = LOGS_DIR / "metrics.log"


class PredictionLogger:
    """
    Logger especializado para registrar previsões do modelo em produção.
    
    Registra:
    - Timestamp da requisição
    - ID único da requisição
    - Estatísticas dos dados de entrada (média, std, min, max)
    - Resultado previsto
    - Tempo de processamento
    """
    
    def __init__(self):
        """Inicializa o logger de previsões."""
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """
        Configura o logger com formato estruturado.
        
        Returns:
            Logger configurado
        """
        logger = logging.getLogger("prediction_logger")
        logger.setLevel(logging.INFO)
        
        # Remove handlers existentes para evitar duplicação
        logger.handlers.clear()
        
        # Handler para arquivo
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Handler para stdout (capturado pelo Render)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        
        # Formato estruturado (facilita parsing posterior)
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        
        return logger
    
    def log_prediction(
        self,
        input_data: List[List[float]],
        prediction: float,
        processing_time_ms: float,
        request_id: str = None,
        data_source: str = None
    ) -> str:
        """
        Registra uma previsão do modelo.
        
        Args:
            input_data: Dados de entrada (shape: [60, 5])
            prediction: Valor previsto
            processing_time_ms: Tempo de processamento em ms
            request_id: ID da requisição (gerado se não fornecido)
            data_source: Fonte dos dados (ex: "Yahoo Finance API v8", "yfinance", "SQLite Cache")
        
        Returns:
            ID da requisição
        """
        # Gera ID único se não fornecido
        if request_id is None:
            request_id = str(uuid.uuid4())[:8]
        
        # Converte para numpy para facilitar cálculos
        data_array = np.array(input_data)
        
        # Calcula estatísticas dos dados de entrada
        stats = {
            "mean": float(np.mean(data_array)),
            "std": float(np.std(data_array)),
            "min": float(np.min(data_array)),
            "max": float(np.max(data_array)),
            "median": float(np.median(data_array)),
            "shape": list(data_array.shape)
        }
        
        # Monta mensagem de log estruturada
        log_entry = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "event": "prediction",
            "data_source": data_source or "unknown",
            "input_stats": stats,
            "prediction": float(prediction),
            "processing_time_ms": float(processing_time_ms),
            "status": "success"
        }
        
        # Registra como JSON em uma linha
        self.logger.info(json.dumps(log_entry, ensure_ascii=False))
        
        return request_id
    
    def log_error(
        self,
        error_message: str,
        input_data: Any = None,
        request_id: str = None
    ):
        """
        Registra um erro durante a previsão.
        
        Args:
            error_message: Mensagem de erro
            input_data: Dados de entrada (opcional)
            request_id: ID da requisição
        """
        if request_id is None:
            request_id = str(uuid.uuid4())[:8]
        
        log_entry = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "event": "prediction_error",
            "error": str(error_message),
            "has_input_data": input_data is not None,
            "status": "error"
        }
        
        self.logger.error(json.dumps(log_entry, ensure_ascii=False))


class MetricsLogger:
    """
    Logger para métricas de performance do sistema.
    
    Registra:
    - Número de requisições por período
    - Latência média
    - Taxa de erros
    - Estatísticas de uso
    """
    
    def __init__(self):
        """Inicializa o logger de métricas."""
        self.logger = self._setup_logger()
        self.request_count = 0
        self.error_count = 0
    
    def _setup_logger(self) -> logging.Logger:
        """
        Configura o logger de métricas.
        
        Returns:
            Logger configurado
        """
        logger = logging.getLogger("metrics_logger")
        logger.setLevel(logging.INFO)
        
        # Remove handlers existentes
        logger.handlers.clear()
        
        # Handler para arquivo de métricas
        file_handler = logging.FileHandler(METRICS_FILE, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def log_system_metrics(self, metrics: Dict[str, Any]):
        """
        Registra métricas do sistema.
        
        Args:
            metrics: Dicionário com métricas do sistema
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "system_metrics",
            **metrics
        }
        
        self.logger.info(json.dumps(log_entry, ensure_ascii=False))
    
    def increment_request(self):
        """Incrementa contador de requisições."""
        self.request_count += 1
    
    def increment_error(self):
        """Incrementa contador de erros."""
        self.error_count += 1
    
    def get_counters(self) -> Dict[str, int]:
        """
        Obtém contadores atuais.
        
        Returns:
            Dicionário com contadores
        """
        return {
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "success_rate": (
                (self.request_count - self.error_count) / self.request_count 
                if self.request_count > 0 else 0.0
            )
        }


# Instâncias globais (singleton)
prediction_logger = PredictionLogger()
metrics_logger = MetricsLogger()


def get_prediction_logger() -> PredictionLogger:
    """
    Obtém instância do logger de previsões.
    
    Returns:
        PredictionLogger instance
    """
    return prediction_logger


def get_metrics_logger() -> MetricsLogger:
    """
    Obtém instância do logger de métricas.
    
    Returns:
        MetricsLogger instance
    """
    return metrics_logger
