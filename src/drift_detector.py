"""
Sistema de Detecção de Drift de Dados

Monitora mudanças na distribuição dos dados de entrada e saídas do modelo.
Usa testes estatísticos e Evidently AI para detectar drift.
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from scipy import stats


# Diretórios
ROOT_DIR = Path(__file__).parent.parent
MONITORING_DIR = ROOT_DIR / "monitoring"
MONITORING_DIR.mkdir(exist_ok=True)

# Arquivo de referência (dados de treinamento)
REFERENCE_STATS = MONITORING_DIR / "reference_statistics.json"
DRIFT_REPORTS = MONITORING_DIR / "drift_reports.json"


class DriftDetector:
    """
    Detector de drift de dados usando métodos estatísticos.
    
    Funcionalidades:
    - Calcula estatísticas de referência dos dados de treinamento
    - Monitora distribuição dos dados de entrada em produção
    - Aplica testes estatísticos (Kolmogorov-Smirnov, etc.)
    - Detecta mudanças significativas
    - Gera alertas de drift
    """
    
    def __init__(self, significance_level: float = 0.05):
        """
        Inicializa o detector de drift.
        
        Args:
            significance_level: Nível de significância para testes (default: 0.05)
        """
        self.significance_level = significance_level
        self.reference_stats = self._load_reference_stats()
        self.drift_history = self._load_drift_history()
    
    def _load_reference_stats(self) -> Dict:
        """
        Carrega estatísticas de referência dos dados de treinamento.
        
        Returns:
            Dicionário com estatísticas de referência
        """
        if REFERENCE_STATS.exists():
            with open(REFERENCE_STATS, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_reference_stats(self):
        """Salva estatísticas de referência."""
        with open(REFERENCE_STATS, 'w', encoding='utf-8') as f:
            json.dump(self.reference_stats, f, indent=2, ensure_ascii=False)
    
    def _load_drift_history(self) -> Dict:
        """
        Carrega histórico de detecções de drift.
        
        Returns:
            Dicionário com histórico
        """
        if DRIFT_REPORTS.exists():
            with open(DRIFT_REPORTS, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"reports": []}
    
    def _save_drift_history(self):
        """Salva histórico de drift."""
        with open(DRIFT_REPORTS, 'w', encoding='utf-8') as f:
            json.dump(self.drift_history, f, indent=2, ensure_ascii=False)
    
    def set_reference_statistics(self, training_data: np.ndarray):
        """
        Calcula e armazena estatísticas de referência dos dados de treinamento.
        
        Args:
            training_data: Dados de treinamento (array numpy)
        """
        print(f"\n{'='*60}")
        print("📊 CALCULANDO ESTATÍSTICAS DE REFERÊNCIA")
        print(f"{'='*60}")
        
        stats_dict = {
            "timestamp": datetime.now().isoformat(),
            "n_samples": int(training_data.shape[0]),
            "mean": float(np.mean(training_data)),
            "std": float(np.std(training_data)),
            "min": float(np.min(training_data)),
            "max": float(np.max(training_data)),
            "median": float(np.median(training_data)),
            "q1": float(np.percentile(training_data, 25)),
            "q3": float(np.percentile(training_data, 75)),
            "iqr": float(np.percentile(training_data, 75) - np.percentile(training_data, 25))
        }
        
        self.reference_stats = stats_dict
        self._save_reference_stats()
        
        print(f"✅ Estatísticas calculadas:")
        print(f"   Amostras: {stats_dict['n_samples']}")
        print(f"   Média: {stats_dict['mean']:.4f}")
        print(f"   Desvio Padrão: {stats_dict['std']:.4f}")
        print(f"   Min/Max: {stats_dict['min']:.4f} / {stats_dict['max']:.4f}")
        print(f"{'='*60}\n")
    
    def detect_drift(
        self,
        current_data: np.ndarray,
        window_name: str = "current"
    ) -> Dict:
        """
        Detecta drift comparando dados atuais com referência.
        
        Args:
            current_data: Dados atuais para análise
            window_name: Nome da janela de dados
        
        Returns:
            Relatório de drift
        """
        if not self.reference_stats:
            return {
                "error": "Reference statistics not set. Run set_reference_statistics first."
            }
        
        print(f"\n{'='*60}")
        print(f"🔍 DETECÇÃO DE DRIFT: {window_name}")
        print(f"{'='*60}")
        
        # Calcula estatísticas dos dados atuais
        current_stats = {
            "mean": float(np.mean(current_data)),
            "std": float(np.std(current_data)),
            "min": float(np.min(current_data)),
            "max": float(np.max(current_data)),
            "median": float(np.median(current_data)),
            "n_samples": int(len(current_data))
        }
        
        # Compara estatísticas
        drift_detected = False
        alerts = []
        
        # 1. Teste de diferença de média (usando threshold)
        mean_diff_pct = abs(
            (current_stats["mean"] - self.reference_stats["mean"]) / 
            self.reference_stats["mean"]
        ) * 100
        
        if mean_diff_pct > 10:  # 10% de diferença
            drift_detected = True
            alerts.append(f"Média mudou {mean_diff_pct:.2f}%")
        
        # 2. Teste de diferença de desvio padrão
        std_diff_pct = abs(
            (current_stats["std"] - self.reference_stats["std"]) / 
            self.reference_stats["std"]
        ) * 100
        
        if std_diff_pct > 20:  # 20% de diferença
            drift_detected = True
            alerts.append(f"Desvio padrão mudou {std_diff_pct:.2f}%")
        
        # 3. Teste Kolmogorov-Smirnov (se temos dados suficientes)
        # Gera amostra de referência baseada em distribuição normal
        if current_data.shape[0] > 30:
            reference_sample = np.random.normal(
                self.reference_stats["mean"],
                self.reference_stats["std"],
                size=1000
            )
            
            ks_statistic, p_value = stats.ks_2samp(reference_sample, current_data)
            
            if p_value < self.significance_level:
                drift_detected = True
                alerts.append(
                    f"KS test: p-value={p_value:.4f} < {self.significance_level}"
                )
        
        # Monta relatório
        report = {
            "timestamp": datetime.now().isoformat(),
            "window_name": window_name,
            "drift_detected": drift_detected,
            "alerts": alerts,
            "current_stats": current_stats,
            "reference_stats": self.reference_stats,
            "comparisons": {
                "mean_diff_pct": float(mean_diff_pct),
                "std_diff_pct": float(std_diff_pct)
            }
        }
        
        # Adiciona ao histórico
        self.drift_history["reports"].append(report)
        self._save_drift_history()
        
        # Print resumo
        if drift_detected:
            print(f"⚠️  DRIFT DETECTADO!")
            for alert in alerts:
                print(f"   • {alert}")
        else:
            print(f"✅ Nenhum drift significativo detectado")
        
        print(f"\nComparações:")
        print(f"   Média: Ref={self.reference_stats['mean']:.4f}, "
              f"Atual={current_stats['mean']:.4f} "
              f"(Δ {mean_diff_pct:.2f}%)")
        print(f"   Std:   Ref={self.reference_stats['std']:.4f}, "
              f"Atual={current_stats['std']:.4f} "
              f"(Δ {std_diff_pct:.2f}%)")
        print(f"{'='*60}\n")
        
        return report
    
    def monitor_prediction_distribution(
        self,
        predictions: List[float],
        window_name: str = "recent_predictions"
    ) -> Dict:
        """
        Monitora distribuição das previsões do modelo.
        
        Args:
            predictions: Lista de valores previstos
            window_name: Nome da janela
        
        Returns:
            Análise da distribuição
        """
        if not predictions:
            return {"error": "No predictions provided"}
        
        pred_array = np.array(predictions)
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "window_name": window_name,
            "n_predictions": len(predictions),
            "mean": float(np.mean(pred_array)),
            "std": float(np.std(pred_array)),
            "min": float(np.min(pred_array)),
            "max": float(np.max(pred_array)),
            "median": float(np.median(pred_array)),
            "range": float(np.max(pred_array) - np.min(pred_array))
        }
        
        # Detecta anomalias (valores muito fora do comum)
        q1, q3 = np.percentile(pred_array, [25, 75])
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = pred_array[(pred_array < lower_bound) | (pred_array > upper_bound)]
        
        analysis["outliers"] = {
            "count": int(len(outliers)),
            "percentage": float(len(outliers) / len(predictions) * 100),
            "values": [float(x) for x in outliers.tolist()]
        }
        
        if analysis["outliers"]["count"] > 0:
            print(f"⚠️  {analysis['outliers']['count']} outliers detectados "
                  f"({analysis['outliers']['percentage']:.1f}%)")
        
        return analysis
    
    def get_drift_summary(self, days: int = 7) -> Dict:
        """
        Retorna resumo de detecções de drift.
        
        Args:
            days: Número de dias para análise
        
        Returns:
            Resumo de drift
        """
        recent_reports = self.drift_history["reports"][-days:]
        
        if not recent_reports:
            return {"message": "No drift reports available"}
        
        drift_count = sum(1 for r in recent_reports if r["drift_detected"])
        
        summary = {
            "period_days": days,
            "total_checks": len(recent_reports),
            "drift_detected_count": drift_count,
            "drift_rate": float(drift_count / len(recent_reports) * 100),
            "last_check": recent_reports[-1]["timestamp"] if recent_reports else None
        }
        
        return summary


def setup_reference_from_file(data_file: Path):
    """
    Configura estatísticas de referência a partir de arquivo CSV.
    
    Args:
        data_file: Caminho para arquivo com dados de treinamento
    """
    print(f"📂 Carregando dados de referência: {data_file}")
    
    # Carrega dados
    df = pd.read_csv(data_file)
    
    # Assume coluna 'Close' ou primeira coluna numérica
    if 'Close' in df.columns:
        data = df['Close'].values
    else:
        data = df.iloc[:, 0].values
    
    # Configura referência
    detector = DriftDetector()
    detector.set_reference_statistics(data)
    
    print(f"✅ Referência configurada com {len(data)} amostras")


def main():
    """Função principal para execução standalone."""
    print("\n🔍 Detector de Drift de Dados B3SA3")
    print("="*60)
    
    # Exemplo de uso
    detector = DriftDetector()
    
    # Verifica se há referência configurada
    if not detector.reference_stats:
        print("⚠️  Nenhuma referência configurada!")
        print("   Execute: python -c \"from drift_detector import setup_reference_from_file; "
              "setup_reference_from_file(Path('data/processed/train_data.csv'))\"")
        return
    
    # Mostra resumo
    summary = detector.get_drift_summary(days=7)
    print(f"\n📊 Resumo de Drift (últimos 7 dias):")
    print(f"   Total de checagens: {summary.get('total_checks', 0)}")
    print(f"   Drift detectado: {summary.get('drift_detected_count', 0)} vezes")
    print(f"   Taxa de drift: {summary.get('drift_rate', 0):.1f}%")


if __name__ == "__main__":
    main()
