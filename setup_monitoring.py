"""
Setup Inicial do Sistema de Monitoramento (Fase 8)

Configura estatísticas de referência para detecção de drift.
Execute ANTES de colocar monitoramento em produção.
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path

# Add root to path
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

from src.drift_detector import DriftDetector
from src.alert_system import AlertSystem, AlertThresholds


def setup_drift_reference():
    """Configura estatísticas de referência para drift detection."""
    print("\n" + "="*70)
    print("🔧 SETUP: Configuração de Referência para Drift Detection")
    print("="*70)
    
    # Busca arquivo de dados processados
    data_dir = ROOT_DIR / "data" / "processed"
    
    # Lista arquivos CSV disponíveis
    csv_files = list(data_dir.glob("*.csv"))
    
    if not csv_files:
        print("\n❌ Nenhum arquivo CSV encontrado em data/processed/")
        print("   Execute primeiro: python src/data_collection.py")
        return False
    
    print(f"\n📂 Arquivos encontrados:")
    for i, f in enumerate(csv_files, 1):
        print(f"   {i}. {f.name}")
    
    # Usa o primeiro (mais recente)
    data_file = csv_files[0]
    print(f"\n✅ Usando: {data_file.name}")
    
    # Carrega dados
    print(f"📊 Carregando dados...")
    df = pd.read_csv(data_file)
    
    # Usa coluna Close para referência
    if 'Close' not in df.columns:
        print(f"\n❌ Coluna 'Close' não encontrada")
        print(f"   Colunas disponíveis: {df.columns.tolist()}")
        return False
    
    close_prices = df['Close'].values
    
    print(f"   Total de amostras: {len(close_prices)}")
    print(f"   Range: R$ {close_prices.min():.2f} - R$ {close_prices.max():.2f}")
    print(f"   Média: R$ {close_prices.mean():.2f}")
    
    # Configura detector
    detector = DriftDetector()
    detector.set_reference_statistics(close_prices)
    
    print(f"\n✅ Estatísticas de referência configuradas!")
    print(f"   Arquivo: monitoring/reference_statistics.json")
    
    return True


def setup_alert_thresholds():
    """Configura thresholds de alerta."""
    print("\n" + "="*70)
    print("🔧 SETUP: Configuração de Thresholds de Alerta")
    print("="*70)
    
    thresholds = AlertThresholds(
        mae_threshold=2.0,           # MAE máximo (R$)
        mape_threshold=5.0,          # MAPE máximo (%)
        drift_mean_pct=10.0,         # Mudança de média (%)
        drift_std_pct=20.0,          # Mudança de desvio (%)
        error_rate_threshold=0.05    # Taxa de erro (5%)
    )
    
    alert_system = AlertSystem(thresholds)
    
    print(f"\n✅ Thresholds configurados:")
    print(f"   MAE Máximo: R$ {thresholds.mae_threshold:.2f}")
    print(f"   MAPE Máximo: {thresholds.mape_threshold:.1f}%")
    print(f"   Drift Média: {thresholds.drift_mean_pct:.1f}%")
    print(f"   Drift Std: {thresholds.drift_std_pct:.1f}%")
    print(f"   Error Rate: {thresholds.error_rate_threshold*100:.1f}%")
    
    print(f"\n   Arquivo de config: monitoring/alert_config.json")
    
    return True


def verify_directories():
    """Verifica/cria diretórios necessários."""
    print("\n" + "="*70)
    print("🔧 SETUP: Verificação de Diretórios")
    print("="*70)
    
    dirs = [
        ROOT_DIR / "logs",
        ROOT_DIR / "monitoring"
    ]
    
    for d in dirs:
        if not d.exists():
            d.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ Criado: {d.relative_to(ROOT_DIR)}/")
        else:
            print(f"   ✓ Existe: {d.relative_to(ROOT_DIR)}/")
    
    return True


def test_monitoring_components():
    """Testa componentes básicos do monitoramento."""
    print("\n" + "="*70)
    print("🧪 TESTE: Componentes de Monitoramento")
    print("="*70)
    
    try:
        # 1. Test logging
        from api.monitoring import get_prediction_logger
        logger = get_prediction_logger()
        print(f"   ✅ PredictionLogger: OK")
        
        # 2. Test performance monitor
        from src.performance_monitor import PerformanceMonitor
        monitor = PerformanceMonitor()
        print(f"   ✅ PerformanceMonitor: OK")
        
        # 3. Test drift detector
        from src.drift_detector import DriftDetector
        detector = DriftDetector()
        print(f"   ✅ DriftDetector: OK")
        
        # 4. Test alert system
        from src.alert_system import AlertSystem
        alerts = AlertSystem()
        print(f"   ✅ AlertSystem: OK")
        
        print(f"\n✅ Todos os componentes funcionando!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao testar componentes: {e}")
        return False


def main():
    """Executa setup completo."""
    print("\n" + "="*70)
    print("🚀 SETUP INICIAL - SISTEMA DE MONITORAMENTO (FASE 8)")
    print("="*70)
    print("\nEste script configura o sistema de monitoramento pela primeira vez.")
    print("Execute apenas UMA VEZ antes de colocar em produção.\n")
    
    input("Pressione ENTER para continuar...")
    
    success = True
    
    # 1. Verifica diretórios
    if not verify_directories():
        success = False
    
    # 2. Configura drift reference
    if not setup_drift_reference():
        success = False
    
    # 3. Configura alert thresholds
    if not setup_alert_thresholds():
        success = False
    
    # 4. Testa componentes
    if not test_monitoring_components():
        success = False
    
    # Resumo final
    print("\n" + "="*70)
    if success:
        print("✅ SETUP CONCLUÍDO COM SUCESSO!")
        print("="*70)
        print("\n📋 Próximos passos:")
        print("   1. Execute os testes: python test_monitoring.py")
        print("   2. Teste manualmente: python run_daily_monitoring.py")
        print("   3. Configure automação (cron/GitHub Actions)")
        print("   4. (Opcional) Configure Slack webhook para alertas")
        print("\n📖 Documentação completa: docs/FASE_8_GUIA.md")
    else:
        print("❌ SETUP INCOMPLETO")
        print("="*70)
        print("\n⚠️  Verifique os erros acima e tente novamente.")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
