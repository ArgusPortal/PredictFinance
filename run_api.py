"""
Executor da API - Fase 6

Script para executar a API FastAPI do modelo B3SA3.SA.
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 80)
    print(" " * 25 + "🚀 API B3SA3.SA - LSTM")
    print("=" * 80)
    print("\n📍 Endpoints disponíveis:")
    print("   • GET  /           - Health check")
    print("   • GET  /health     - Health check alternativo")
    print("   • GET  /info       - Informações do modelo")
    print("   • GET  /metrics    - Métricas de performance")
    print("   • POST /predict    - Fazer previsão")
    print("\n📖 Documentação:")
    print("   • Swagger UI: http://localhost:8000/docs")
    print("   • ReDoc:      http://localhost:8000/redoc")
    print("\n" + "=" * 80)
    print("\n🚀 Iniciando servidor...\n")
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Desabilitar reload para testes
        log_level="info"
    )
