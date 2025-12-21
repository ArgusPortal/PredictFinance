"""
Script para ativar o Sistema de Detecção de Drift

Este script:
1. Carrega os dados de treinamento
2. Gera as estatísticas de referência (baseline)
3. Inicializa os arquivos de monitoramento de drift

Autor: GitHub Copilot
Data: 21/12/2025
"""

import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

# Adiciona o diretório src ao path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from drift_detector import DriftDetector

def setup_drift_detection():
    """Configura o sistema de detecção de drift com dados de treinamento."""
    
    print("\n" + "="*70)
    print("🔧 ATIVAÇÃO DO SISTEMA DE DETECÇÃO DE DRIFT")
    print("="*70 + "\n")
    
    # Caminhos dos arquivos
    raw_data_path = ROOT_DIR / "data" / "raw" / "b3sa3_historical.csv"
    y_train_path = ROOT_DIR / "data" / "processed" / "y_train.npy"
    
    # Verifica se os arquivos existem
    if not raw_data_path.exists():
        print(f"❌ Arquivo não encontrado: {raw_data_path}")
        return False
    
    # Carrega dados históricos para informações
    print(f"📂 Carregando dados históricos: {raw_data_path}")
    df = pd.read_csv(raw_data_path, index_col=0, parse_dates=True)
    
    print(f"   ✅ Registros carregados: {len(df)}")
    print(f"   📅 Período: {df.index[0].strftime('%Y-%m-%d')} a {df.index[-1].strftime('%Y-%m-%d')}")
    
    # Armazena preços reais para referência
    close_prices = df['Close'].values
    
    # Inicializa o detector
    detector = DriftDetector(significance_level=0.05)
    
    # IMPORTANTE: Usa dados NORMALIZADOS como referência (mesmo formato da produção)
    # Os dados de treino já estão normalizados pelo MinMaxScaler
    if y_train_path.exists():
        print(f"\n📂 Carregando dados de treino normalizados: {y_train_path}")
        y_train = np.load(y_train_path)
        print(f"   ✅ Amostras de treino (normalizadas): {len(y_train)}")
        
        # Configura estatísticas de referência com dados NORMALIZADOS
        print(f"\n📊 Calculando estatísticas de referência (dados normalizados)...")
        detector.set_reference_statistics(y_train.flatten())
        
        # Valida usando dados de teste
        y_test_path = ROOT_DIR / "data" / "processed" / "y_test.npy"
        if y_test_path.exists():
            y_test = np.load(y_test_path)
            print(f"\n🔍 Executando validação inicial com dados de teste...")
            report = detector.detect_drift(y_test.flatten(), "test_validation")
            
            if not report.get("drift_detected"):
                print("   ✅ Validação inicial OK - Sem drift significativo")
            else:
                print("   ⚠️ Drift detectado entre treino e teste")
    else:
        # Fallback: normaliza dados brutos manualmente
        print(f"\n📊 Calculando estatísticas de referência (dados brutos)...")
        detector.set_reference_statistics(close_prices)
    
    # Cria arquivo de drift reports vazio se não existir
    drift_reports_path = ROOT_DIR / "monitoring" / "drift_reports.json"
    if not drift_reports_path.exists():
        with open(drift_reports_path, 'w', encoding='utf-8') as f:
            json.dump({
                "reports": [],
                "initialized_at": datetime.now().isoformat(),
                "status": "active"
            }, f, indent=2)
        print(f"\n✅ Arquivo de relatórios criado: {drift_reports_path}")
    
    # Mostra resumo final
    print("\n" + "="*70)
    print("✅ SISTEMA DE DRIFT DETECTION ATIVADO COM SUCESSO!")
    print("="*70)
    
    # Carrega estatísticas salvas para exibir
    ref_stats = detector.reference_stats
    
    print(f"""
📋 Resumo da Configuração:
   • Dados de referência: {ref_stats.get('n_samples', 'N/A')} amostras normalizadas
   • Período original: {df.index[0].strftime('%Y-%m-%d')} a {df.index[-1].strftime('%Y-%m-%d')}
   • Nível de significância: 5%
   • Arquivo de referência: monitoring/reference_statistics.json
   • Arquivo de relatórios: monitoring/drift_reports.json

📊 Estatísticas de Referência (Valores Normalizados 0-1):
   • Média: {ref_stats.get('mean', 0):.4f}
   • Desvio Padrão: {ref_stats.get('std', 0):.4f}
   • Mínimo: {ref_stats.get('min', 0):.4f}
   • Máximo: {ref_stats.get('max', 0):.4f}
   • Mediana: {ref_stats.get('median', 0):.4f}

📊 Preços Reais de Referência (R$):
   • Média: R$ {np.mean(close_prices):.2f}
   • Desvio Padrão: R$ {np.std(close_prices):.2f}
   • Mínimo: R$ {np.min(close_prices):.2f}
   • Máximo: R$ {np.max(close_prices):.2f}

🔍 O sistema está pronto para detectar:
   • Mudanças na distribuição dos dados de entrada
   • Desvios significativos nas previsões
   • Drift conceitual ao longo do tempo
""")
    
    return True


if __name__ == "__main__":
    success = setup_drift_detection()
    sys.exit(0 if success else 1)
