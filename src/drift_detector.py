"""
Sistema de Detecção de Drift de Dados - Janela Deslizante

Monitora mudanças RECENTES na distribuição dos dados de entrada.
Usa abordagem de janela deslizante para séries temporais financeiras.

IMPORTANTE: Em séries temporais, comparar dados de 2020 com 2025 sempre
mostrará drift alto devido à evolução natural do mercado. Por isso,
usamos janela deslizante para detectar mudanças ABRUPTAS e RECENTES.

Abordagem:
- Janela de Referência: últimos 30-60 dias anteriores
- Janela Atual: últimos 7 dias
- Objetivo: Detectar mudanças abruptas, não evolução gradual
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from scipy import stats


# Diretórios
ROOT_DIR = Path(__file__).parent.parent
MONITORING_DIR = ROOT_DIR / "monitoring"
MONITORING_DIR.mkdir(exist_ok=True)

# Arquivos de persistência
REFERENCE_STATS = MONITORING_DIR / "reference_statistics.json"
DRIFT_REPORTS = MONITORING_DIR / "drift_reports.json"


class SlidingWindowDriftDetector:
    """
    Detector de drift com janela deslizante para séries temporais.
    
    Abordagem:
    - Compara janela recente (7 dias) com janela de referência (30-60 dias anteriores)
    - Detecta mudanças ABRUPTAS, não evolução gradual do mercado
    - Thresholds ajustados para volatilidade normal do mercado
    """
    
    def __init__(
        self,
        reference_window_days: int = 30,
        current_window_days: int = 7,
        mean_threshold_pct: float = 5.0,  # 5% para mudanças de curto prazo
        std_threshold_pct: float = 50.0,   # 50% para detectar mudanças de volatilidade
        significance_level: float = 0.05
    ):
        """
        Inicializa o detector de drift.
        
        Args:
            reference_window_days: Dias para janela de referência (default: 30)
            current_window_days: Dias para janela atual (default: 7)
            mean_threshold_pct: Threshold para mudança de média (default: 5%)
            std_threshold_pct: Threshold para mudança de volatilidade (default: 50%)
            significance_level: Nível de significância para teste KS (default: 0.05)
        """
        self.reference_window_days = reference_window_days
        self.current_window_days = current_window_days
        self.mean_threshold_pct = mean_threshold_pct
        self.std_threshold_pct = std_threshold_pct
        self.significance_level = significance_level
        
        self.reference_stats = self._load_reference_stats()
        self.drift_history = self._load_drift_history()
    
    def _load_reference_stats(self) -> Dict:
        """Carrega estatísticas de referência."""
        if REFERENCE_STATS.exists():
            with open(REFERENCE_STATS, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_reference_stats(self):
        """Salva estatísticas de referência."""
        with open(REFERENCE_STATS, 'w', encoding='utf-8') as f:
            json.dump(self.reference_stats, f, indent=2, ensure_ascii=False)
    
    def _load_drift_history(self) -> Dict:
        """Carrega histórico de drift."""
        if DRIFT_REPORTS.exists():
            with open(DRIFT_REPORTS, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"reports": [], "approach": "sliding_window"}
    
    def _save_drift_history(self):
        """Salva histórico de drift."""
        with open(DRIFT_REPORTS, 'w', encoding='utf-8') as f:
            json.dump(self.drift_history, f, indent=2, ensure_ascii=False)
    
    def _calculate_stats(self, data: np.ndarray) -> Dict:
        """Calcula estatísticas de uma janela de dados."""
        return {
            "n_samples": int(len(data)),
            "mean": float(np.mean(data)),
            "std": float(np.std(data)),
            "min": float(np.min(data)),
            "max": float(np.max(data)),
            "median": float(np.median(data)),
            "q1": float(np.percentile(data, 25)),
            "q3": float(np.percentile(data, 75)),
            "iqr": float(np.percentile(data, 75) - np.percentile(data, 25))
        }
    
    def update_reference_from_recent_data(self, df: pd.DataFrame, price_column: str = 'Close'):
        """
        Atualiza referência usando dados recentes (janela deslizante).
        
        Args:
            df: DataFrame com dados históricos (index deve ser datetime)
            price_column: Nome da coluna de preço
        """
        print(f"\n{'='*60}")
        print("📊 ATUALIZANDO REFERÊNCIA (JANELA DESLIZANTE)")
        print(f"{'='*60}")
        
        # Ordenar por data
        df = df.sort_index()
        
        # Janela de referência: de (current_window + reference_window) até current_window dias atrás
        end_ref = len(df) - self.current_window_days
        start_ref = max(0, end_ref - self.reference_window_days)
        
        reference_data = df.iloc[start_ref:end_ref][price_column].values
        
        if len(reference_data) < 10:
            print("❌ Dados insuficientes para janela de referência")
            return
        
        # Calcula estatísticas
        stats_dict = self._calculate_stats(reference_data)
        stats_dict["timestamp"] = datetime.now().isoformat()
        stats_dict["window_type"] = "sliding"
        stats_dict["reference_days"] = self.reference_window_days
        stats_dict["current_days"] = self.current_window_days
        
        # Período da referência
        if hasattr(df.index[start_ref], 'strftime'):
            stats_dict["period_start"] = df.index[start_ref].strftime('%Y-%m-%d')
            stats_dict["period_end"] = df.index[end_ref-1].strftime('%Y-%m-%d')
        
        self.reference_stats = stats_dict
        self._save_reference_stats()
        
        print(f"✅ Referência atualizada (janela deslizante):")
        print(f"   Período: {stats_dict.get('period_start', 'N/A')} a {stats_dict.get('period_end', 'N/A')}")
        print(f"   Amostras: {stats_dict['n_samples']} dias")
        print(f"   Média: R$ {stats_dict['mean']:.2f}")
        print(f"   Volatilidade (Std): R$ {stats_dict['std']:.2f}")
        print(f"{'='*60}\n")
    
    def detect_drift_sliding_window(
        self,
        df: pd.DataFrame,
        price_column: str = 'Close'
    ) -> Dict:
        """
        Detecta drift usando janela deslizante.
        
        Compara:
        - Janela de referência: últimos 30-60 dias ANTES da janela atual
        - Janela atual: últimos 7 dias
        
        Args:
            df: DataFrame com dados históricos
            price_column: Coluna de preço
        
        Returns:
            Relatório de drift
        """
        print(f"\n{'='*60}")
        print("🔍 DETECÇÃO DE DRIFT (JANELA DESLIZANTE)")
        print(f"{'='*60}")
        
        # Ordenar por data
        df = df.sort_index()
        
        # Janela atual: últimos N dias
        current_data = df.iloc[-self.current_window_days:][price_column].values
        
        # Janela de referência: antes da janela atual
        end_ref = len(df) - self.current_window_days
        start_ref = max(0, end_ref - self.reference_window_days)
        reference_data = df.iloc[start_ref:end_ref][price_column].values
        
        if len(current_data) < 3 or len(reference_data) < 10:
            return {"error": "Dados insuficientes para análise de drift"}
        
        # Calcula estatísticas
        current_stats = self._calculate_stats(current_data)
        reference_stats = self._calculate_stats(reference_data)
        
        # Compara estatísticas
        drift_detected = False
        alerts = []
        
        # 1. Mudança de média (threshold mais baixo para curto prazo)
        mean_diff_pct = abs(
            (current_stats["mean"] - reference_stats["mean"]) / 
            reference_stats["mean"]
        ) * 100
        
        if mean_diff_pct > self.mean_threshold_pct:
            drift_detected = True
            direction = "subiu" if current_stats["mean"] > reference_stats["mean"] else "caiu"
            alerts.append(f"Preço médio {direction} {mean_diff_pct:.1f}% vs período anterior")
        
        # 2. Mudança de volatilidade
        std_diff_pct = abs(
            (current_stats["std"] - reference_stats["std"]) / 
            reference_stats["std"]
        ) * 100
        
        if std_diff_pct > self.std_threshold_pct:
            drift_detected = True
            direction = "aumentou" if current_stats["std"] > reference_stats["std"] else "diminuiu"
            alerts.append(f"Volatilidade {direction} {std_diff_pct:.1f}%")
        
        # 3. Teste Kolmogorov-Smirnov (se dados suficientes)
        ks_result = None
        if len(current_data) >= 5 and len(reference_data) >= 20:
            ks_statistic, p_value = stats.ks_2samp(reference_data, current_data)
            # Garantir que são floats (podem vir como numpy arrays)
            ks_stat_float = float(ks_statistic) if hasattr(ks_statistic, '__float__') else float(ks_statistic.item()) if hasattr(ks_statistic, 'item') else float(ks_statistic)
            p_value_float = float(p_value) if hasattr(p_value, '__float__') else float(p_value.item()) if hasattr(p_value, 'item') else float(p_value)
            ks_result = {"statistic": ks_stat_float, "p_value": p_value_float}
            
            if p_value_float < self.significance_level:
                # Não marcar como drift apenas pelo KS em janelas pequenas
                # pois pode haver falsos positivos
                if mean_diff_pct > 3 or std_diff_pct > 30:
                    drift_detected = True
                    alerts.append(f"Distribuição diferente (KS p={p_value_float:.4f})")
        
        # Período atual e referência
        if hasattr(df.index[-1], 'strftime'):
            current_period = f"{df.index[-self.current_window_days].strftime('%d/%m')} a {df.index[-1].strftime('%d/%m')}"
            ref_period = f"{df.index[start_ref].strftime('%d/%m')} a {df.index[end_ref-1].strftime('%d/%m')}"
        else:
            current_period = f"Últimos {self.current_window_days} dias"
            ref_period = f"{self.reference_window_days} dias anteriores"
        
        # Monta relatório
        report = {
            "timestamp": datetime.now().isoformat(),
            "approach": "sliding_window",
            "drift_detected": drift_detected,
            "severity": "high" if mean_diff_pct > 10 or std_diff_pct > 100 else "medium" if drift_detected else "none",
            "alerts": alerts,
            "current_window": {
                "period": current_period,
                "days": self.current_window_days,
                "stats": current_stats
            },
            "reference_window": {
                "period": ref_period,
                "days": self.reference_window_days,
                "stats": reference_stats
            },
            "comparisons": {
                "mean_diff_pct": float(mean_diff_pct),
                "std_diff_pct": float(std_diff_pct),
                "ks_test": ks_result
            },
            "thresholds": {
                "mean_threshold_pct": self.mean_threshold_pct,
                "std_threshold_pct": self.std_threshold_pct
            }
        }
        
        # Adiciona ao histórico (mantém últimos 100)
        self.drift_history["reports"].append(report)
        if len(self.drift_history["reports"]) > 100:
            self.drift_history["reports"] = self.drift_history["reports"][-100:]
        self._save_drift_history()
        
        # Print resumo
        print(f"\n📅 Janela Atual: {current_period}")
        print(f"   Média: R$ {current_stats['mean']:.2f}")
        print(f"   Volatilidade: R$ {current_stats['std']:.2f}")
        
        print(f"\n📅 Janela Referência: {ref_period}")
        print(f"   Média: R$ {reference_stats['mean']:.2f}")
        print(f"   Volatilidade: R$ {reference_stats['std']:.2f}")
        
        print(f"\n📊 Comparação:")
        print(f"   Δ Média: {mean_diff_pct:.1f}% (threshold: {self.mean_threshold_pct}%)")
        print(f"   Δ Volatilidade: {std_diff_pct:.1f}% (threshold: {self.std_threshold_pct}%)")
        
        if drift_detected:
            print(f"\n⚠️  DRIFT DETECTADO!")
            for alert in alerts:
                print(f"   • {alert}")
        else:
            print(f"\n✅ Sem drift significativo - Mercado estável")
        
        print(f"{'='*60}\n")
        
        return report
    
    def get_drift_summary(self, n_reports: int = 10) -> Dict:
        """Retorna resumo das últimas análises de drift."""
        recent = self.drift_history.get("reports", [])[-n_reports:]
        
        if not recent:
            return {"message": "Nenhuma análise de drift registrada"}
        
        drift_count = sum(1 for r in recent if r.get("drift_detected", False))
        
        return {
            "approach": "sliding_window",
            "total_checks": len(recent),
            "drift_detected_count": drift_count,
            "drift_rate": float(drift_count / len(recent) * 100) if recent else 0,
            "last_check_timestamp": recent[-1].get("timestamp") if recent else None,
            "last_drift_detected": recent[-1].get("drift_detected") if recent else None,
            "configuration": {
                "reference_window_days": self.reference_window_days,
                "current_window_days": self.current_window_days,
                "mean_threshold_pct": self.mean_threshold_pct,
                "std_threshold_pct": self.std_threshold_pct
            }
        }


# Alias para compatibilidade
DriftDetector = SlidingWindowDriftDetector


def analyze_drift_from_yahoo(ticker: str = "B3SA3.SA") -> Dict:
    """
    Analisa drift usando dados atuais do Yahoo Finance.
    
    Args:
        ticker: Símbolo da ação
    
    Returns:
        Relatório de drift
    """
    import yfinance as yf
    
    print(f"\n🔍 Analisando drift para {ticker}...")
    
    # Busca dados dos últimos 90 dias
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)
    
    if df.empty:
        return {"error": f"Não foi possível obter dados para {ticker}"}
    
    # Cria detector e analisa
    detector = SlidingWindowDriftDetector(
        reference_window_days=30,
        current_window_days=7,
        mean_threshold_pct=5.0,
        std_threshold_pct=50.0
    )
    
    return detector.detect_drift_sliding_window(df, 'Close')


def main():
    """Executa análise de drift com dados atuais."""
    print("\n" + "="*60)
    print("🔍 ANÁLISE DE DRIFT - JANELA DESLIZANTE")
    print("="*60)
    
    result = analyze_drift_from_yahoo("B3SA3.SA")
    
    if "error" in result:
        print(f"❌ Erro: {result['error']}")
    else:
        print("\n📋 Resultado salvo em monitoring/drift_reports.json")


if __name__ == "__main__":
    main()
