"""
Sistema de Monitoramento de Performance do Modelo em Produção

Compara previsões realizadas com valores reais obtidos posteriormente.
Calcula métricas de erro (MAE, MAPE) e detecta degradação do modelo.

IMPORTANTE: Hierarquia de persistência:
1. PostgreSQL Render (produção na nuvem - persistente)
2. SQLite local (fallback se PostgreSQL não disponível)
3. JSON local (backup adicional)
"""

import json
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import deque

# Importar API v8 para busca de dados reais
try:
    from src.yahoo_finance_v8 import coletar_dados_yahoo_v8_custom_range
    API_V8_DISPONIVEL = True
except ImportError:
    API_V8_DISPONIVEL = False

# Importar banco de dados (suporta PostgreSQL + SQLite)
try:
    from database.db_manager import get_db
    DB_DISPONIVEL = True
except ImportError:
    DB_DISPONIVEL = False
    def get_db():
        return None


# Diretórios
ROOT_DIR = Path(__file__).parent.parent
LOGS_DIR = ROOT_DIR / "logs"
MONITORING_DIR = ROOT_DIR / "monitoring"
MONITORING_DIR.mkdir(exist_ok=True)

# Arquivo para armazenar previsões aguardando validação (fallback local)
PREDICTIONS_DB = MONITORING_DIR / "predictions_tracking.json"
PERFORMANCE_METRICS = MONITORING_DIR / "performance_metrics.json"


class PerformanceMonitor:
    """
    Monitora performance do modelo comparando previsões vs valores reais.
    
    Funcionalidades:
    - Armazena previsões para validação posterior
    - Coleta preços reais do mercado
    - Calcula métricas de erro (MAE, MAPE, RMSE)
    - Mantém histórico de performance
    - Detecta degradação do modelo
    
    IMPORTANTE: O db_manager.py já suporta PostgreSQL (quando DATABASE_URL está definida)
    com fallback automático para SQLite local.
    """
    
    def __init__(self, ticker: str = "B3SA3.SA", window_days: int = 7):
        """
        Inicializa o monitor de performance.
        
        Args:
            ticker: Símbolo da ação
            window_days: Janela móvel para cálculo de métricas (dias)
        """
        self.ticker = ticker
        self.window_days = window_days
        
        # Inicializar banco de dados (PostgreSQL ou SQLite - gerenciado pelo db_manager)
        self.db = None
        if DB_DISPONIVEL:
            try:
                self.db = get_db()
                if self.db and getattr(self.db, 'pg_enabled', False):
                    print("☁️ Usando PostgreSQL Render para persistência")
                elif self.db:
                    print("💾 Usando SQLite local para persistência")
            except Exception as e:
                print(f"⚠️ Banco de dados não disponível: {e}")
        
        # Carregar dados
        self.predictions_db = self._load_predictions_db()
        self.metrics_history = self._load_metrics_history()
    
    def _load_predictions_db(self) -> Dict:
        """
        Carrega banco de previsões aguardando validação.
        Hierarquia: Banco de dados (PostgreSQL/SQLite) > JSON local.
        
        Returns:
            Dicionário com previsões
        """
        # Prioridade 1: Banco de dados (PostgreSQL ou SQLite via db_manager)
        if self.db is not None:
            try:
                predictions = self.db.get_predictions(ticker=self.ticker, limit=500)
                if predictions:
                    db_type = "PostgreSQL" if getattr(self.db, 'pg_enabled', False) else "SQLite"
                    print(f"📊 Carregadas {len(predictions)} previsões do {db_type}")
                    return {"predictions": predictions}
            except Exception as e:
                print(f"⚠️ Erro ao carregar do banco: {e}")
        
        # Prioridade 2: Arquivo JSON local (fallback)
        if PREDICTIONS_DB.exists():
            with open(PREDICTIONS_DB, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"📁 Carregadas {len(data.get('predictions', []))} previsões do JSON local")
                return data
        
        print("📭 Nenhuma previsão encontrada")
        return {"predictions": []}
    
    def _save_predictions_db(self):
        """
        Salva banco de previsões.
        JSON local é mantido como backup adicional.
        """
        # Sempre salva no JSON local como backup
        try:
            with open(PREDICTIONS_DB, 'w', encoding='utf-8') as f:
                json.dump(self.predictions_db, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Erro ao salvar JSON local: {e}")
    
    def _save_prediction_to_db(self, prediction_entry: Dict) -> bool:
        """
        Salva uma previsão no banco de dados (PostgreSQL ou SQLite).
        
        Args:
            prediction_entry: Dicionário com dados da previsão
        
        Returns:
            True se salvo com sucesso
        """
        if self.db is None:
            return False
        
        try:
            saved = self.db.insert_prediction(
                request_id=prediction_entry.get("request_id", ""),
                ticker=self.ticker,
                timestamp=prediction_entry.get("timestamp", ""),
                predicted_value=prediction_entry.get("predicted_value", 0.0)
            )
            if saved:
                db_type = "PostgreSQL" if getattr(self.db, 'pg_enabled', False) else "SQLite"
                print(f"✅ Previsão salva no {db_type}")
                return True
        except Exception as e:
            print(f"⚠️ Erro ao salvar no banco: {e}")
        
        return False
    
    def _load_metrics_history(self) -> Dict:
        """
        Carrega histórico de métricas de performance.
        
        Returns:
            Dicionário com histórico
        """
        if PERFORMANCE_METRICS.exists():
            with open(PERFORMANCE_METRICS, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"daily_metrics": [], "summary": {}}
    
    def _save_metrics_history(self):
        """Salva histórico de métricas."""
        with open(PERFORMANCE_METRICS, 'w', encoding='utf-8') as f:
            json.dump(self.metrics_history, f, indent=2, ensure_ascii=False)
    
    def register_prediction(
        self,
        prediction_value: float,
        prediction_date: str = None,
        request_id: str = None
    ):
        """
        Registra uma previsão para validação futura.
        Salva no SQLite (persistente) e JSON (backup local).
        
        Args:
            prediction_value: Valor previsto
            prediction_date: Data da previsão (ISO format)
            request_id: ID da requisição
        """
        if prediction_date is None:
            prediction_date = datetime.now().isoformat()
        
        prediction_entry = {
            "request_id": request_id,
            "timestamp": prediction_date,
            "predicted_value": float(prediction_value),
            "validated": False,
            "actual_value": None,
            "error": None
        }
        
        # Salvar no banco de dados SQLite (persistência em produção)
        db_saved = self._save_prediction_to_db(prediction_entry)
        if db_saved:
            print(f"✅ Previsão {request_id[:8] if request_id else 'N/A'} salva no banco de dados")
        
        # Também salvar no JSON local (backup)
        self.predictions_db["predictions"].append(prediction_entry)
        self._save_predictions_db()
    
    def validate_predictions(self, days_back: int = 1) -> Dict:
        """
        Valida previsões comparando com valores reais do mercado.
        
        Args:
            days_back: Quantos dias atrás validar
        
        Returns:
            Resumo da validação
        """
        print(f"\n{'='*60}")
        print("🔍 VALIDAÇÃO DE PREVISÕES")
        print(f"{'='*60}")
        
        # Filtra previsões não validadas
        unvalidated = [
            p for p in self.predictions_db["predictions"] 
            if not p["validated"]
        ]
        
        if not unvalidated:
            print("✅ Nenhuma previsão pendente de validação")
            return {"validated": 0, "pending": 0}
        
        print(f"📊 Previsões pendentes: {len(unvalidated)}")
        
        # Obtém dados reais do mercado
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back + 5)  # Margem de segurança
        
        print(f"📈 Baixando dados reais de {self.ticker}...")
        data = None
        
        # Estratégia 1: API v8 (prioridade)
        if API_V8_DISPONIVEL:
            try:
                print(f"   🔄 Tentando Yahoo Finance API v8...")
                df = coletar_dados_yahoo_v8_custom_range(
                    ticker=self.ticker,
                    start_date=start_date.strftime("%Y-%m-%d"),
                    end_date=end_date.strftime("%Y-%m-%d")
                )
                if not df.empty:
                    data = df
                    print(f"   ✅ API v8: {len(data)} registros")
            except Exception as e:
                print(f"   ⚠️ API v8 falhou: {str(e)[:80]}")
        
        # Estratégia 2: yfinance (fallback)
        if data is None or data.empty:
            try:
                print(f"   🔄 Tentando yfinance...")
                data = yf.download(
                    self.ticker,
                    start=start_date,
                    end=end_date,
                    progress=False
                )
                if not data.empty:
                    print(f"   ✅ yfinance: {len(data)} registros")
            except Exception as e:
                print(f"   ❌ yfinance falhou: {str(e)[:80]}")
        
        # Validar se conseguiu dados
        if data is None or data.empty:
            error_msg = f"Não foi possível obter dados reais para validação"
            print(f"❌ {error_msg}")
            return {
                "error": error_msg,
                "validated": 0,
                "pending": len(unvalidated)
            }
        
        # CORREÇÃO: Normalizar índice do DataFrame para comparação correta
        # O índice pode ter timezone e/ou horário (ex: '2025-11-21 13:00:00')
        # Precisamos normalizar para apenas data (ex: '2025-11-21')
        if hasattr(data.index, 'tz') and data.index.tz is not None:
            data.index = data.index.tz_localize(None)
        data.index = pd.to_datetime(data.index).normalize()
        
        print(f"   📅 Datas disponíveis: {data.index[0].date()} a {data.index[-1].date()}")
        
        validated_count = 0
        skipped_future = 0
        not_found = 0
        
        # Valida cada previsão
        for prediction in unvalidated:
            pred_date = datetime.fromisoformat(prediction["timestamp"])
            
            # Busca preço real do dia seguinte
            next_day = pred_date + timedelta(days=1)
            next_day_normalized = pd.Timestamp(next_day.date())  # Apenas data, sem horário
            
            # Verificar se já passou tempo suficiente
            today_normalized = pd.Timestamp(datetime.now().date())
            if next_day_normalized > today_normalized:
                skipped_future += 1
                continue  # Pular previsões muito recentes
            
            # Tenta encontrar o preço real
            actual_value = None
            found_date = None
            for offset in range(5):  # Procura até 5 dias à frente (fins de semana/feriados)
                check_date = next_day_normalized + timedelta(days=offset)
                
                if check_date in data.index:
                    actual_value = float(data.loc[check_date, 'Close'])
                    found_date = check_date
                    break
            
            if actual_value is not None:
                # Calcula erro
                error = abs(prediction["predicted_value"] - actual_value)
                error_pct = (error / actual_value) * 100
                
                # Atualiza previsão no dicionário
                prediction["validated"] = True
                prediction["actual_value"] = actual_value
                prediction["error"] = error
                prediction["error_pct"] = error_pct
                prediction["validation_date"] = datetime.now().isoformat()
                
                # Atualiza no banco de dados (PostgreSQL ou SQLite)
                request_id = prediction.get("request_id", "")
                validation_date = prediction["validation_date"]
                
                # Atualizar no banco de dados
                if self.db is not None:
                    try:
                        self.db.update_prediction_validation(
                            request_id=request_id,
                            actual_value=actual_value,
                            error=error,
                            error_pct=error_pct,
                            validation_date=validation_date
                        )
                    except Exception as e:
                        print(f"⚠️ Erro ao validar no banco: {e}")
                
                validated_count += 1
                
                print(f"   ✅ {prediction['request_id'][:8]}: "
                      f"Previsto={prediction['predicted_value']:.2f}, "
                      f"Real={actual_value:.2f}, "
                      f"Erro={error_pct:.2f}%")
            else:
                not_found += 1
                print(f"   ⚠️  {prediction['request_id'][:8]}: Dados reais não encontrados para {next_day.date()}")
        
        # Salva atualizações no JSON (backup local)
        self._save_predictions_db()
        
        print(f"\n✅ Validadas: {validated_count} previsões")
        if skipped_future > 0:
            print(f"⏭️  Ignoradas: {skipped_future} previsões muito recentes (aguardando dia seguinte)")
        if not_found > 0:
            print(f"⚠️  Sem dados: {not_found} previsões (dados de mercado não disponíveis)")
        print(f"⏳ Pendentes: {len(unvalidated) - validated_count - skipped_future}")
        
        # Calcula métricas se houver validações
        if validated_count > 0:
            self.calculate_metrics()
        
        return {
            "validated": validated_count,
            "skipped_future": skipped_future,
            "not_found": not_found,
            "pending": len(unvalidated) - validated_count - skipped_future,
            "message": f"Validadas {validated_count}, {skipped_future} aguardando dados reais"
        }
    
    def calculate_metrics(self) -> Dict:
        """
        Calcula métricas de erro para previsões validadas.
        
        Returns:
            Dicionário com métricas
        """
        # Filtra previsões validadas
        validated = [
            p for p in self.predictions_db["predictions"] 
            if p["validated"] and p["error"] is not None
        ]
        
        if not validated:
            print("⚠️  Nenhuma previsão validada disponível")
            return {}
        
        # Ordena por data
        validated.sort(key=lambda x: x["timestamp"])
        
        # Pega últimos N dias
        recent = validated[-self.window_days:] if len(validated) > self.window_days else validated
        
        # Calcula métricas
        errors = [p["error"] for p in recent]
        error_pcts = [p["error_pct"] for p in recent]
        
        mae = np.mean(errors)
        mape = np.mean(error_pcts)
        rmse = np.sqrt(np.mean([e**2 for e in errors]))
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "window_days": len(recent),
            "mae": float(mae),
            "mape": float(mape),
            "rmse": float(rmse),
            "total_validated": len(validated),
            "min_error_pct": float(min(error_pcts)),
            "max_error_pct": float(max(error_pcts))
        }
        
        # Adiciona ao histórico
        self.metrics_history["daily_metrics"].append(metrics)
        
        # Atualiza resumo
        self.metrics_history["summary"] = {
            "last_update": metrics["timestamp"],
            "current_mae": metrics["mae"],
            "current_mape": metrics["mape"],
            "total_predictions_validated": len(validated)
        }
        
        self._save_metrics_history()
        
        print(f"\n{'='*60}")
        print("📊 MÉTRICAS DE PERFORMANCE")
        print(f"{'='*60}")
        print(f"Janela: Últimos {len(recent)} dias")
        print(f"MAE:  {mae:.4f}")
        print(f"MAPE: {mape:.2f}%")
        print(f"RMSE: {rmse:.4f}")
        print(f"Erro Mínimo: {min(error_pcts):.2f}%")
        print(f"Erro Máximo: {max(error_pcts):.2f}%")
        print(f"{'='*60}\n")
        
        return metrics
    
    def detect_degradation(self, threshold_mape: float = 5.0) -> bool:
        """
        Detecta se o modelo está degradando.
        
        Args:
            threshold_mape: Limiar de MAPE para alertar (%)
        
        Returns:
            True se detectou degradação
        """
        if not self.metrics_history["daily_metrics"]:
            return False
        
        current_metrics = self.metrics_history["daily_metrics"][-1]
        current_mape = current_metrics["mape"]
        
        if current_mape > threshold_mape:
            print(f"\n⚠️  ALERTA: Degradação detectada!")
            print(f"   MAPE atual ({current_mape:.2f}%) > "
                  f"Threshold ({threshold_mape:.2f}%)")
            return True
        
        return False
    
    def get_performance_trend(self, days: int = 7) -> Dict:
        """
        Analisa tendência de performance nos últimos dias.
        
        Args:
            days: Número de dias para análise
        
        Returns:
            Análise de tendência
        """
        metrics = self.metrics_history["daily_metrics"][-days:]
        
        if len(metrics) < 2:
            return {"trend": "insufficient_data"}
        
        mapes = [m["mape"] for m in metrics]
        
        # Calcula tendência (regressão linear simples)
        x = np.arange(len(mapes))
        slope = np.polyfit(x, mapes, 1)[0]
        
        trend = {
            "days_analyzed": len(mapes),
            "initial_mape": mapes[0],
            "final_mape": mapes[-1],
            "avg_mape": np.mean(mapes),
            "slope": float(slope),
            "trend": "improving" if slope < -0.1 else "degrading" if slope > 0.1 else "stable"
        }
        
        return trend


def main():
    """Função principal para execução standalone."""
    print("\n🔍 Monitor de Performance do Modelo B3SA3")
    print("="*60)
    
    monitor = PerformanceMonitor()
    
    # Valida previsões pendentes
    result = monitor.validate_predictions(days_back=7)
    
    # Calcula métricas
    if result.get("validated", 0) > 0:
        metrics = monitor.calculate_metrics()
        
        # Detecta degradação
        if monitor.detect_degradation(threshold_mape=5.0):
            print("\n⚠️  AÇÃO NECESSÁRIA: Considere re-treinar o modelo!")
        else:
            print("\n✅ Performance do modelo dentro do esperado")
        
        # Analisa tendência
        trend = monitor.get_performance_trend(days=7)
        if trend.get("trend") != "insufficient_data":
            print(f"\n📈 Tendência (7 dias): {trend['trend'].upper()}")
            print(f"   MAPE médio: {trend['avg_mape']:.2f}%")


if __name__ == "__main__":
    main()
