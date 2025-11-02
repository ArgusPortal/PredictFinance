"""
Script de Teste da API

Testa todos os endpoints da API de previsão B3SA3.SA.
"""

import requests
import json
import numpy as np
from pathlib import Path


# Configurações
API_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}


def testar_health_check():
    """Testa o endpoint de health check."""
    print("\n" + "=" * 60)
    print("1️⃣  Testando Health Check (GET /)")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Resposta:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ Health check passou!")
        else:
            print("❌ Health check falhou!")
            
    except Exception as e:
        print(f"❌ Erro: {e}")


def testar_health_alternativo():
    """Testa o endpoint alternativo de health check."""
    print("\n" + "=" * 60)
    print("2️⃣  Testando Health Check Alternativo (GET /health)")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Resposta:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ Health alternativo passou!")
        else:
            print("❌ Health alternativo falhou!")
            
    except Exception as e:
        print(f"❌ Erro: {e}")


def testar_info_modelo():
    """Testa o endpoint de informações do modelo."""
    print("\n" + "=" * 60)
    print("3️⃣  Testando Informações do Modelo (GET /info)")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_URL}/info")
        print(f"Status Code: {response.status_code}")
        print(f"Resposta:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ Info do modelo passou!")
        else:
            print("❌ Info do modelo falhou!")
            
    except Exception as e:
        print(f"❌ Erro: {e}")


def testar_metricas():
    """Testa o endpoint de métricas."""
    print("\n" + "=" * 60)
    print("4️⃣  Testando Métricas (GET /metrics)")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_URL}/metrics")
        print(f"Status Code: {response.status_code}")
        print(f"Resposta:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ Métricas passou!")
        else:
            print("❌ Métricas falhou!")
            
    except Exception as e:
        print(f"❌ Erro: {e}")


def testar_previsao_valida():
    """Testa o endpoint de previsão com dados válidos."""
    print("\n" + "=" * 60)
    print("5️⃣  Testando Previsão com Dados Válidos (POST /predict)")
    print("=" * 60)
    
    # Gerar 60 preços simulados próximos ao intervalo real (R$ 10-15)
    np.random.seed(42)
    base_price = 12.5
    prices = [base_price + np.random.randn() * 0.5 for _ in range(60)]
    
    payload = {
        "prices": prices
    }
    
    print(f"Enviando {len(prices)} preços...")
    print(f"Preço mínimo: R$ {min(prices):.2f}")
    print(f"Preço máximo: R$ {max(prices):.2f}")
    print(f"Preço médio: R$ {np.mean(prices):.2f}")
    
    try:
        response = requests.post(
            f"{API_URL}/predict",
            headers=HEADERS,
            json=payload
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Resposta:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ Previsão válida passou!")
        else:
            print("❌ Previsão válida falhou!")
            
    except Exception as e:
        print(f"❌ Erro: {e}")


def testar_previsao_invalida_quantidade():
    """Testa o endpoint com quantidade incorreta de preços."""
    print("\n" + "=" * 60)
    print("6️⃣  Testando Previsão com Quantidade Incorreta (POST /predict)")
    print("=" * 60)
    
    # Enviar apenas 30 preços (deveria ser 60)
    prices = [12.5] * 30
    
    payload = {
        "prices": prices
    }
    
    print(f"Enviando {len(prices)} preços (deveria ser 60)...")
    
    try:
        response = requests.post(
            f"{API_URL}/predict",
            headers=HEADERS,
            json=payload
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Resposta:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 422:  # Validation error
            print("✅ Validação de quantidade funcionou corretamente!")
        else:
            print("❌ Deveria retornar erro 422!")
            
    except Exception as e:
        print(f"❌ Erro: {e}")


def testar_previsao_invalida_valores():
    """Testa o endpoint com valores inválidos (negativos)."""
    print("\n" + "=" * 60)
    print("7️⃣  Testando Previsão com Valores Negativos (POST /predict)")
    print("=" * 60)
    
    # Enviar preços com valores negativos
    prices = [12.5] * 59 + [-10.0]
    
    payload = {
        "prices": prices
    }
    
    print(f"Enviando {len(prices)} preços (incluindo valor negativo)...")
    
    try:
        response = requests.post(
            f"{API_URL}/predict",
            headers=HEADERS,
            json=payload
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Resposta:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 422:  # Validation error
            print("✅ Validação de valores funcionou corretamente!")
        else:
            print("❌ Deveria retornar erro 422!")
            
    except Exception as e:
        print(f"❌ Erro: {e}")


def testar_documentacao():
    """Testa se a documentação Swagger está acessível."""
    print("\n" + "=" * 60)
    print("8️⃣  Testando Documentação Swagger (GET /docs)")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_URL}/docs")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Documentação Swagger acessível!")
            print(f"   Acesse: {API_URL}/docs")
        else:
            print("❌ Documentação não acessível!")
            
    except Exception as e:
        print(f"❌ Erro: {e}")


def executar_todos_testes():
    """Executa todos os testes."""
    print("\n" + "=" * 80)
    print(" " * 20 + "🧪 SUITE DE TESTES DA API")
    print("=" * 80)
    print(f"\n📍 API URL: {API_URL}")
    print(f"📅 Data: 02/11/2025")
    
    try:
        # Verificar se a API está rodando
        print("\n🔍 Verificando se a API está rodando...")
        response = requests.get(f"{API_URL}/", timeout=2)
        print("✅ API está respondendo!\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERRO: API não está rodando!")
        print("   Execute primeiro: python api/main.py")
        print("   Ou: uvicorn api.main:app --reload")
        return
    
    # Executar testes
    testar_health_check()
    testar_health_alternativo()
    testar_info_modelo()
    testar_metricas()
    testar_previsao_valida()
    testar_previsao_invalida_quantidade()
    testar_previsao_invalida_valores()
    testar_documentacao()
    
    # Resumo
    print("\n" + "=" * 80)
    print(" " * 25 + "📊 RESUMO DOS TESTES")
    print("=" * 80)
    print("\n✅ Todos os testes foram executados!")
    print(f"\n📖 Documentação interativa disponível em: {API_URL}/docs")
    print(f"📖 Documentação ReDoc disponível em: {API_URL}/redoc")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    executar_todos_testes()
