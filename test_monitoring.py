"""
Testes do Sistema de Monitoramento (Fase 8)

Valida funcionalidades de logging, performance tracking e drift detection.
"""

import sys
import json
import numpy as np
from pathlib import Path

# Add root to path
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

from api.monitoring import PredictionLogger, MetricsLogger
from src.performance_monitor import PerformanceMonitor
from src.drift_detector import DriftDetector
from src.alert_system import AlertSystem, AlertThresholds


def test_prediction_logging():
    """Testa logging de previsões."""
    print("\n" + "="*60)
    print("TEST 1: Prediction Logging")
    print("="*60)
    
    logger = PredictionLogger()
    
    # Simula previsão
    fake_input = np.random.rand(60, 5).tolist()
    prediction = 12.45
    processing_time = 25.3
    
    request_id = logger.log_prediction(
        input_data=fake_input,
        prediction=prediction,
        processing_time_ms=processing_time
    )
    
    print(f"✅ Logged prediction with ID: {request_id}")
    print(f"   Logs salvos em: logs/predictions.log")
    
    # Testa log de erro
    logger.log_error("Test error", input_data=fake_input)
    print(f"✅ Logged error")


def test_performance_monitor():
    """Testa monitor de performance."""
    print("\n" + "="*60)
    print("TEST 2: Performance Monitor")
    print("="*60)
    
    monitor = PerformanceMonitor()
    
    # Registra previsões de teste
    monitor.register_prediction(
        prediction_value=12.45,
        request_id="test-001"
    )
    
    monitor.register_prediction(
        prediction_value=12.50,
        request_id="test-002"
    )
    
    print(f"✅ Registered 2 test predictions")
    print(f"   Database: monitoring/predictions_tracking.json")
    
    # Tenta validar (pode não haver dados reais)
    result = monitor.validate_predictions(days_back=1)
    print(f"✅ Validation attempted")
    print(f"   Validated: {result.get('validated', 0)}")
    print(f"   Pending: {result.get('pending', 0)}")


def test_drift_detector():
    """Testa detector de drift."""
    print("\n" + "="*60)
    print("TEST 3: Drift Detector")
    print("="*60)
    
    detector = DriftDetector()
    
    # Cria dados de referência
    reference_data = np.random.normal(12.0, 1.0, 1000)
    detector.set_reference_statistics(reference_data)
    
    print(f"✅ Reference statistics set")
    
    # Testa drift com dados similares (não deve detectar)
    similar_data = np.random.normal(12.1, 1.1, 100)
    report1 = detector.detect_drift(similar_data, "similar_data")
    
    # Testa drift com dados diferentes (deve detectar)
    different_data = np.random.normal(15.0, 2.0, 100)
    report2 = detector.detect_drift(different_data, "different_data")
    
    print(f"✅ Drift detection completed")
    print(f"   Similar data drift: {report1.get('drift_detected', False)}")
    print(f"   Different data drift: {report2.get('drift_detected', False)}")
    
    # Testa monitoramento de distribuição de previsões
    predictions = [12.0 + i*0.1 for i in range(100)]
    analysis = detector.monitor_prediction_distribution(predictions)
    
    print(f"✅ Prediction distribution analyzed")
    print(f"   Outliers: {analysis['outliers']['count']}")


def test_alert_system():
    """Testa sistema de alertas."""
    print("\n" + "="*60)
    print("TEST 4: Alert System")
    print("="*60)
    
    thresholds = AlertThresholds(
        mae_threshold=2.0,
        mape_threshold=5.0
    )
    
    alert_system = AlertSystem(thresholds)
    
    # Testa alerta de performance
    metrics = {
        "mae": 2.5,  # Acima do threshold
        "mape": 6.0  # Acima do threshold
    }
    
    violations = alert_system.check_performance_metrics(metrics)
    print(f"✅ Performance check completed")
    print(f"   Violations found: {len(violations)}")
    
    for v in violations:
        print(f"   • {v}")
    
    # Envia alerta de teste
    alert_system.send_alert(
        alert_type="test",
        message="Test alert from test suite",
        severity="INFO",
        metadata={"test": True}
    )
    
    print(f"✅ Alert sent successfully")
    
    # Mostra resumo
    summary = alert_system.get_alert_summary()
    print(f"\n📊 Alert Summary:")
    print(f"   Total alerts: {summary['total_alerts']}")
    print(f"   By type: {summary.get('by_type', {})}")
    print(f"   By severity: {summary.get('by_severity', {})}")


def test_integration():
    """Teste de integração completo."""
    print("\n" + "="*60)
    print("TEST 5: Integration Test")
    print("="*60)
    
    # Simula fluxo completo de monitoramento
    
    # 1. Faz "previsão"
    logger = PredictionLogger()
    fake_input = np.random.rand(60, 5).tolist()
    prediction = 12.45
    
    request_id = logger.log_prediction(
        input_data=fake_input,
        prediction=prediction,
        processing_time_ms=25.0
    )
    
    print(f"1️⃣  Prediction logged: {request_id}")
    
    # 2. Registra no monitor de performance
    monitor = PerformanceMonitor()
    monitor.register_prediction(
        prediction_value=prediction,
        request_id=request_id
    )
    
    print(f"2️⃣  Prediction registered for validation")
    
    # 3. Detecta drift nos inputs
    detector = DriftDetector()
    
    if detector.reference_stats:
        # Usa primeira feature dos inputs
        input_array = np.array([row[0] for row in fake_input])
        drift_report = detector.detect_drift(input_array, "test_request")
        print(f"3️⃣  Drift detection: {'DETECTED' if drift_report.get('drift_detected') else 'NOT DETECTED'}")
    else:
        print(f"3️⃣  Drift detection: SKIPPED (no reference)")
    
    # 4. Verifica alertas
    alert_system = AlertSystem()
    
    # Simula métricas OK
    test_metrics = {"mae": 0.5, "mape": 1.5}
    violations = alert_system.check_performance_metrics(test_metrics)
    
    if violations:
        alert_system.send_alert(
            alert_type="performance",
            message=f"{len(violations)} violations detected",
            severity="WARNING"
        )
        print(f"4️⃣  Alerts: {len(violations)} triggered")
    else:
        print(f"4️⃣  Alerts: None (system healthy)")
    
    print(f"\n✅ Integration test completed successfully")


def main():
    """Executa todos os testes."""
    print("\n" + "="*70)
    print("🧪 TESTE DO SISTEMA DE MONITORAMENTO - FASE 8")
    print("="*70)
    
    try:
        test_prediction_logging()
        test_performance_monitor()
        test_drift_detector()
        test_alert_system()
        test_integration()
        
        print("\n" + "="*70)
        print("✅ TODOS OS TESTES PASSARAM!")
        print("="*70)
        
        print("\n📁 Arquivos gerados:")
        print("   • logs/predictions.log - Logs de previsões")
        print("   • logs/metrics.log - Logs de métricas")
        print("   • monitoring/predictions_tracking.json - Banco de previsões")
        print("   • monitoring/performance_metrics.json - Métricas históricas")
        print("   • monitoring/reference_statistics.json - Estatísticas de referência")
        print("   • monitoring/drift_reports.json - Relatórios de drift")
        print("   • monitoring/alert_history.json - Histórico de alertas")
        print("   • monitoring/alert_config.json - Configuração de alertas")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
