"""
Script de Teste Rápido da API - Executa Servidor e Testes

Este script inicia a API e executa testes básicos.
"""

import time
import subprocess
import sys
import requests
import json
from pathlib import Path

def testar_api():
    """Testa os endpoints principais da API."""
    base_url = "http://localhost:8000"
    
    print("\n" + "=" * 70)
    print(" " * 20 + "🧪 TESTANDO API")
    print("=" * 70)
    
    # Aguardar API iniciar
    print("\n⏳ Aguardando API inicializar...")
    max_tentativas = 30
    for i in range(max_tentativas):
        try:
            response = requests.get(f"{base_url}/", timeout=1)
            if response.status_code == 200:
                print("✅ API está respondendo!\n")
                break
        except:
            time.sleep(1)
            print(f"   Tentativa {i+1}/{max_tentativas}...", end='\r')
    else:
        print("\n❌ API não respondeu a tempo.")
        return False
    
    # Teste 1: Health Check
    print("1️⃣  Health Check (GET /)")
    print("-" * 70)
    try:
        response = requests.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Resposta: {json.dumps(data, indent=2, ensure_ascii=False)}")
        print(f"✅ Passou!\n")
    except Exception as e:
        print(f"❌ Erro: {e}\n")
        return False
    
    # Teste 2: Info do Modelo
    print("2️⃣  Informações do Modelo (GET /info)")
    print("-" * 70)
    try:
        response = requests.get(f"{base_url}/info")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Nome: {data['nome']}")
        print(f"Arquitetura: {data['arquitetura']}")
        print(f"Parâmetros: {data['parametros']:,}")
        print(f"Window Size: {data['window_size']}")
        print(f"✅ Passou!\n")
    except Exception as e:
        print(f"❌ Erro: {e}\n")
        return False
    
    # Teste 3: Métricas
    print("3️⃣  Métricas (GET /metrics)")
    print("-" * 70)
    try:
        response = requests.get(f"{base_url}/metrics")
        print(f"Status: {response.status_code}")
        data = response.json()
        metricas = data['metricas_teste']
        print(f"RMSE: {metricas['RMSE']['valor']}")
        print(f"MAE: {metricas['MAE']['valor']}")
        print(f"MAPE: {metricas['MAPE']['valor']} - {metricas['MAPE']['interpretacao']}")
        print(f"R²: {metricas['R2']['valor']}")
        print(f"✅ Passou!\n")
    except Exception as e:
        print(f"❌ Erro: {e}\n")
        return False
    
    # Teste 4: Previsão Válida
    print("4️⃣  Previsão com Dados Válidos (POST /predict)")
    print("-" * 70)
    try:
        # Gerar 60 preços simulados
        import numpy as np
        np.random.seed(42)
        prices = [12.5 + np.random.randn() * 0.3 for _ in range(60)]
        
        print(f"Enviando {len(prices)} preços...")
        print(f"Range: R$ {min(prices):.2f} - R$ {max(prices):.2f}")
        
        response = requests.post(
            f"{base_url}/predict",
            json={"prices": prices}
        )
        
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"\n🎯 Preço Previsto: R$ {data['preco_previsto']:.2f}")
        print(f"Confiança: {data['confianca']}")
        print(f"Mensagem: {data['mensagem']}")
        print(f"✅ Passou!\n")
    except Exception as e:
        print(f"❌ Erro: {e}\n")
        return False
    
    # Teste 5: Validação de Quantidade Incorreta
    print("5️⃣  Validação - Quantidade Incorreta (POST /predict)")
    print("-" * 70)
    try:
        prices = [12.5] * 30  # Apenas 30 preços
        
        response = requests.post(
            f"{base_url}/predict",
            json={"prices": prices}
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 422:
            print(f"✅ Validação funcionou! Erro 422 retornado corretamente.\n")
        else:
            print(f"❌ Deveria retornar erro 422!\n")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}\n")
        return False
    
    # Teste 6: Validação de Valores Negativos
    print("6️⃣  Validação - Valores Negativos (POST /predict)")
    print("-" * 70)
    try:
        prices = [12.5] * 59 + [-10.0]
        
        response = requests.post(
            f"{base_url}/predict",
            json={"prices": prices}
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 422:
            print(f"✅ Validação funcionou! Erro 422 retornado corretamente.\n")
        else:
            print(f"❌ Deveria retornar erro 422!\n")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}\n")
        return False
    
    # Resumo
    print("=" * 70)
    print(" " * 20 + "✅ TODOS OS TESTES PASSARAM!")
    print("=" * 70)
    print(f"\n📖 Documentação Swagger: {base_url}/docs")
    print(f"📖 Documentação ReDoc: {base_url}/redoc")
    print("\n" + "=" * 70 + "\n")
    
    return True


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print(" " * 10 + "🚀 TESTE RÁPIDO DA API B3SA3.SA")
    print("=" * 70)
    print("\n⚠️  IMPORTANTE: Execute este script com a API já rodando!")
    print("   Em outro terminal, execute:")
    print("   $ uvicorn api.main:app --host 0.0.0.0 --port 8000\n")
    print("=" * 70)
    
    input("\n▶️  Pressione ENTER quando a API estiver rodando...")
    
    sucesso = testar_api()
    
    if sucesso:
        print("✅ Fase 6 - API FastAPI implementada e testada com sucesso!")
        sys.exit(0)
    else:
        print("❌ Alguns testes falharam. Verifique os logs acima.")
        sys.exit(1)
