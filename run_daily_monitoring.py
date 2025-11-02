"""
Script de Monitoramento Diário do Modelo em Produção

Executa verificações diárias de:
- Performance (compara previsões vs valores reais)
- Drift de dados
- Alertas de degradação

Agende este script para rodar diariamente (cron, Task Scheduler, etc.)
"""

import sys
from pathlib import Path
from datetime import datetime

# Adiciona root ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from src.performance_monitor import PerformanceMonitor
from src.drift_detector import DriftDetector
from src.alert_system import AlertSystem, AlertThresholds
import json


def run_daily_monitoring():
    """
    Executa monitoramento diário completo.
    """
    print("\n" + "="*70)
    print("🔍 MONITORAMENTO DIÁRIO DO MODELO B3SA3")
    print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # 1. VALIDAÇÃO DE PERFORMANCE
    print("\n" + "-"*70)
    print("1️⃣  VALIDAÇÃO DE PERFORMANCE")
    print("-"*70)
    
    perf_monitor = PerformanceMonitor(window_days=7)
    
    # Valida previsões dos últimos 7 dias
    validation_result = perf_monitor.validate_predictions(days_back=7)
    
    if validation_result.get("validated", 0) > 0:
        # Calcula métricas
        metrics = perf_monitor.calculate_metrics()
        
        # Analisa tendência
        trend = perf_monitor.get_performance_trend(days=7)
        
        print(f"\n📈 Tendência de Performance:")
        if trend.get("trend") != "insufficient_data":
            trend_emoji = {
                "improving": "📈",
                "stable": "➡️ ",
                "degrading": "📉"
            }.get(trend["trend"], "❓")
            
            print(f"   {trend_emoji} Status: {trend['trend'].upper()}")
            print(f"   MAPE Inicial: {trend['initial_mape']:.2f}%")
            print(f"   MAPE Final: {trend['final_mape']:.2f}%")
            print(f"   MAPE Médio: {trend['avg_mape']:.2f}%")
    else:
        print("⏳ Nenhuma previsão disponível para validação")
        metrics = {}
        trend = {}
    
    # 2. DETECÇÃO DE DRIFT
    print("\n" + "-"*70)
    print("2️⃣  DETECÇÃO DE DRIFT DE DADOS")
    print("-"*70)
    
    drift_detector = DriftDetector()
    
    # Verifica se há dados de referência
    if not drift_detector.reference_stats:
        print("⚠️  Estatísticas de referência não configuradas")
        print("   Configure com: setup_reference_from_file()")
        drift_report = {}
    else:
        # Obtém resumo de drift
        drift_summary = drift_detector.get_drift_summary(days=7)
        
        print(f"📊 Resumo de Drift (últimos 7 dias):")
        print(f"   Checagens: {drift_summary.get('total_checks', 0)}")
        print(f"   Drift detectado: {drift_summary.get('drift_detected_count', 0)} vezes")
        print(f"   Taxa de drift: {drift_summary.get('drift_rate', 0):.1f}%")
        
        drift_report = drift_summary
    
    # 3. VERIFICAÇÃO DE ALERTAS
    print("\n" + "-"*70)
    print("3️⃣  VERIFICAÇÃO DE THRESHOLDS E ALERTAS")
    print("-"*70)
    
    # Configura sistema de alertas
    thresholds = AlertThresholds(
        mae_threshold=2.0,
        mape_threshold=5.0,
        drift_mean_pct=10.0,
        drift_std_pct=20.0
    )
    
    alert_system = AlertSystem(thresholds)
    
    alerts_triggered = []
    
    # Verifica métricas de performance
    if metrics:
        perf_violations = alert_system.check_performance_metrics(metrics)
        
        if perf_violations:
            for violation in perf_violations:
                alert_system.send_alert(
                    alert_type="performance_degradation",
                    message=violation,
                    severity="WARNING",
                    metadata=metrics
                )
                alerts_triggered.append(violation)
    
    # Verifica drift
    if drift_report and drift_report.get("drift_rate", 0) > 50:
        alert_system.send_alert(
            alert_type="data_drift",
            message=f"Alta taxa de drift detectada: {drift_report['drift_rate']:.1f}%",
            severity="WARNING",
            metadata=drift_report
        )
        alerts_triggered.append(f"Drift rate: {drift_report['drift_rate']:.1f}%")
    
    # Mostra resumo de alertas
    if alerts_triggered:
        print(f"⚠️  {len(alerts_triggered)} alerta(s) disparado(s):")
        for alert in alerts_triggered:
            print(f"   • {alert}")
    else:
        print("✅ Nenhum alerta disparado - sistema dentro do esperado")
    
    # 4. RESUMO FINAL
    print("\n" + "="*70)
    print("📊 RESUMO DO MONITORAMENTO")
    print("="*70)
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "performance": {
            "validated_predictions": validation_result.get("validated", 0),
            "current_mape": metrics.get("mape", "N/A"),
            "trend": trend.get("trend", "N/A")
        },
        "drift": {
            "checks_last_7d": drift_report.get("total_checks", 0),
            "drift_detected_count": drift_report.get("drift_detected_count", 0),
            "drift_rate": drift_report.get("drift_rate", 0)
        },
        "alerts": {
            "total_triggered": len(alerts_triggered),
            "messages": alerts_triggered
        }
    }
    
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    
    # Salva resumo
    summary_file = ROOT_DIR / "monitoring" / "daily_summary.json"
    summary_file.parent.mkdir(exist_ok=True)
    
    # Carrega histórico
    if summary_file.exists():
        with open(summary_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
    else:
        history = {"daily_summaries": []}
    
    history["daily_summaries"].append(summary)
    history["last_update"] = summary["timestamp"]
    
    # Mantém apenas últimos 30 dias
    history["daily_summaries"] = history["daily_summaries"][-30:]
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resumo salvo em: {summary_file}")
    
    # 5. RECOMENDAÇÕES
    print("\n" + "="*70)
    print("💡 RECOMENDAÇÕES")
    print("="*70)
    
    if metrics.get("mape", 0) > 5:
        print("⚠️  AÇÃO NECESSÁRIA: MAPE alto - considere re-treinar o modelo")
        print("   Passos:")
        print("   1. Execute: python src/data_collection.py")
        print("   2. Execute: python src/data_preparation.py")
        print("   3. Execute: python src/model_training.py")
        print("   4. Faça novo deploy no Render")
    
    elif trend.get("trend") == "degrading":
        print("⚠️  ATENÇÃO: Tendência de degradação detectada")
        print("   Monitore diariamente e prepare re-treinamento se piorar")
    
    elif drift_report.get("drift_rate", 0) > 50:
        print("⚠️  ATENÇÃO: Alta taxa de drift nos dados")
        print("   O modelo pode estar recebendo dados fora do padrão de treinamento")
        print("   Considere re-treinar com dados mais recentes")
    
    else:
        print("✅ Sistema operando normalmente")
        print("   Mantenha monitoramento diário")
    
    print("\n" + "="*70)
    print("✅ Monitoramento concluído!")
    print("="*70 + "\n")


if __name__ == "__main__":
    run_daily_monitoring()
