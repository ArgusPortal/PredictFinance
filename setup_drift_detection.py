"""
Script para Análise de Drift - Janela Deslizante

Este script:
1. Busca dados recentes do Yahoo Finance
2. Executa análise de drift com janela deslizante
3. Compara últimos 7 dias com 30 dias anteriores

Abordagem correta para séries temporais:
- NÃO compara com dados históricos antigos
- Detecta mudanças ABRUPTAS e RECENTES
- Thresholds ajustados para volatilidade normal do mercado

Autor: Argus
Data: 21/12/2025
"""

import sys
from pathlib import Path

# Adiciona o diretório src ao path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from drift_detector import analyze_drift_from_yahoo, SlidingWindowDriftDetector


def setup_drift_detection():
    """Executa análise de drift com dados atuais do mercado."""
    
    print("\n" + "="*70)
    print("🔧 ANÁLISE DE DRIFT - JANELA DESLIZANTE")
    print("="*70)
    print("""
📊 Abordagem:
   • Janela Atual: últimos 7 dias
   • Janela Referência: 30 dias anteriores
   • Objetivo: Detectar mudanças ABRUPTAS, não evolução gradual

💡 Por que janela deslizante?
   Em séries temporais financeiras, comparar 2020 com 2025 sempre
   mostrará diferenças grandes (inflação, mudanças de mercado).
   Isso NÃO indica problema no modelo!
   
   Usamos janela deslizante para detectar mudanças RECENTES que
   podem afetar a qualidade das previsões.
""")
    
    # Executa análise
    result = analyze_drift_from_yahoo("B3SA3.SA")
    
    if "error" in result:
        print(f"\n❌ Erro: {result['error']}")
        return False
    
    # Resumo final
    print("\n" + "="*70)
    print("📋 RESUMO DA ANÁLISE")
    print("="*70)
    
    drift_detected = result.get('drift_detected', False)
    severity = result.get('severity', 'none')
    alerts = result.get('alerts', [])
    comparisons = result.get('comparisons', {})
    
    if drift_detected:
        if severity == 'high':
            print("🚨 STATUS: DRIFT SIGNIFICATIVO DETECTADO")
        else:
            print("⚠️  STATUS: Drift moderado detectado")
        print("\nAlertas:")
        for alert in alerts:
            print(f"   • {alert}")
    else:
        print("✅ STATUS: Mercado estável - Sem drift significativo")
    
    print(f"""
📊 Métricas:
   • Δ Preço Médio: {comparisons.get('mean_diff_pct', 0):.1f}% (threshold: 5%)
   • Δ Volatilidade: {comparisons.get('std_diff_pct', 0):.1f}% (threshold: 50%)

📁 Arquivos atualizados:
   • monitoring/drift_reports.json
   • monitoring/reference_statistics.json
""")
    
    return True


if __name__ == "__main__":
    success = setup_drift_detection()
    sys.exit(0 if success else 1)
