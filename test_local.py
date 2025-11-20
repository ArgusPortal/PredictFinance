"""
Teste rápido do endpoint /predict/auto em localhost
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("🧪 Testando endpoint /predict/auto localmente\n")

# Teste 1: Health check
print("1. Health check...")
try:
    response = requests.get(f"{BASE_URL}/api", timeout=5)
    print(f"   ✅ Status: {response.status_code}")
except Exception as e:
    print(f"   ❌ Erro: {e}")
    exit(1)

# Teste 2: Previsão automática
print("\n2. Previsão automática para B3SA3.SA...")
try:
    response = requests.post(
        f"{BASE_URL}/predict/auto",
        json={"ticker": "B3SA3.SA"},
        timeout=30
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Preço Previsto: R$ {data['preco_previsto']:.2f}")
        print(f"   Confiança: {data['confianca']}")
        print(f"   Mensagem: {data['mensagem'][:100]}...")
    else:
        print(f"   ❌ Erro: {response.text}")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")
    exit(1)

# Teste 3: Previsão manual com dados OHLCV
print("\n3. Previsão manual com dados OHLCV simulados...")
try:
    import numpy as np
    np.random.seed(42)
    
    dados = []
    preco_base = 12.5
    
    for i in range(60):
        variacao = np.random.randn() * 0.2
        preco_base += variacao
        close = preco_base
        open_price = close + np.random.randn() * 0.1
        high = max(open_price, close) + abs(np.random.randn() * 0.05)
        low = min(open_price, close) - abs(np.random.randn() * 0.05)
        volume = int(1000000 + np.random.randn() * 200000)
        
        dados.append([
            round(open_price, 2),
            round(high, 2),
            round(low, 2),
            round(close, 2),
            max(0, volume)
        ])
    
    response = requests.post(
        f"{BASE_URL}/predict",
        json={"dados": dados},
        timeout=30
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Preço Previsto: R$ {data['preco_previsto']:.2f}")
        print(f"   Confiança: {data['confianca']}")
    else:
        print(f"   ❌ Erro: {response.text}")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Teste 4: Previsão com dados de exemplo
print("\n4. Previsão com dados de exemplo (GET /predict/example)...")
try:
    response = requests.get(
        f"{BASE_URL}/predict/example",
        timeout=10
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Preço Previsto: R$ {data['preco_previsto']:.2f}")
        print(f"   Confiança: {data['confianca']}")
        print(f"   Mensagem: {data['mensagem'][:80]}...")
    else:
        print(f"   ⚠️  Erro: {response.text[:100]}")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")

print("\n✅ Testes locais concluídos!")
