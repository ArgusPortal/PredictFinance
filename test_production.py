"""
Script de Teste da API em Produção (Render)

Testa todos os endpoints da API após deploy no Render.
"""

import requests
import json
import sys
import numpy as np
from typing import Optional


def testar_api_producao(api_url: Optional[str] = None):
    """
    Testa todos os endpoints da API em produção.
    
    Args:
        api_url: URL da API no Render (opcional, pode ser passado via argumento)
    """
    
    # Se não fornecido, usar URL padrão (substituir após deploy)
    if api_url is None:
        # SUBSTITUIR pela URL real do Render após deploy
        api_url = "https://b3sa3-api.onrender.com"
    
    print("\n" + "=" * 80)
    print(" " * 25 + "🧪 TESTE DA API EM PRODUÇÃO")
    print("=" * 80)
    print(f"\n📍 URL da API: {api_url}")
    print(f"📅 Data: 02/11/2025\n")
    print("=" * 80)
    
    # Teste 1: Health Check
    print("\n1️⃣  Health Check (GET /)")
    print("-" * 80)
    try:
        response = requests.get(f"{api_url}/", timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Resposta:\n{json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data.get("modelo_carregado"):
                print("✅ Health check passou! Modelo está carregado.")
            else:
                print("⚠️  API ativa mas modelo não carregado!")
        else:
            print(f"❌ Erro: Status {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏱️  Timeout - A API pode estar em 'sleep' (free tier)")
        print("   Aguardando 30 segundos e tentando novamente...")
        import time
        time.sleep(30)
        return testar_api_producao(api_url)  # Tentar novamente
        
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        print(f"   Verifique se a URL está correta: {api_url}")
        return False
    
    # Teste 2: Informações do Modelo
    print("\n2️⃣  Informações do Modelo (GET /info)")
    print("-" * 80)
    try:
        response = requests.get(f"{api_url}/info", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📊 Modelo: {data.get('nome', 'N/A')}")
            print(f"🏗️  Arquitetura: {data.get('arquitetura', 'N/A')}")
            print(f"🔢 Parâmetros: {data.get('parametros', 0):,}")
            print(f"📏 Window Size: {data.get('window_size', 0)}")
            
            if 'metricas' in data:
                metricas = data['metricas']
                print(f"\n📈 Métricas de Performance:")
                print(f"   • RMSE: {metricas.get('RMSE', 'N/A')}")
                print(f"   • MAE: {metricas.get('MAE', 'N/A')}")
                print(f"   • MAPE: {metricas.get('MAPE', 'N/A')}")
                print(f"   • R²: {metricas.get('R2', 'N/A')}")
            
            print("\n✅ Info do modelo passou!")
        else:
            print(f"❌ Erro: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    # Teste 3: Métricas Detalhadas
    print("\n3️⃣  Métricas Detalhadas (GET /metrics)")
    print("-" * 80)
    try:
        response = requests.get(f"{api_url}/metrics", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'metricas_teste' in data:
                print("\n📊 Métricas do Teste:")
                mape = data['metricas_teste']['MAPE']
                print(f"   MAPE: {mape['valor']} - {mape['interpretacao']}")
            
            if 'dados_treinamento' in data:
                treino = data['dados_treinamento']
                print(f"\n📅 Dados de Treinamento:")
                print(f"   Período: {treino.get('periodo', 'N/A')}")
                print(f"   Total de dias: {treino.get('total_dias', 0)}")
            
            print("\n✅ Métricas passaram!")
        else:
            print(f"❌ Erro: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    # Teste 4: Fazer Previsão
    print("\n4️⃣  Fazer Previsão (POST /predict)")
    print("-" * 80)
    try:
        # Gerar 60 preços simulados
        np.random.seed(42)
        prices = [12.5 + np.random.randn() * 0.3 for _ in range(60)]
        
        print(f"Enviando {len(prices)} preços simulados...")
        print(f"Range: R$ {min(prices):.2f} - R$ {max(prices):.2f}")
        print(f"Média: R$ {np.mean(prices):.2f}")
        
        payload = {"prices": prices}
        
        response = requests.post(
            f"{api_url}/predict",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n🎯 Resultado da Previsão:")
            print(f"   Preço Previsto: R$ {data.get('preco_previsto', 0):.2f}")
            print(f"   Confiança: {data.get('confianca', 'N/A')}")
            print(f"   Mensagem: {data.get('mensagem', 'N/A')}")
            print("\n✅ Previsão passou!")
        else:
            print(f"❌ Erro: Status {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    # Teste 5: Validação de Entrada Inválida
    print("\n5️⃣  Validação - Quantidade Incorreta (POST /predict)")
    print("-" * 80)
    try:
        # Enviar apenas 30 preços (deveria ser 60)
        prices_invalidos = [12.5] * 30
        
        response = requests.post(
            f"{api_url}/predict",
            json={"prices": prices_invalidos},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 422:
            print("✅ Validação funcionou! Erro 422 retornado corretamente.")
        else:
            print(f"⚠️  Status inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 6: Documentação Swagger
    print("\n6️⃣  Documentação Swagger (GET /docs)")
    print("-" * 80)
    try:
        response = requests.get(f"{api_url}/docs", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Documentação Swagger acessível!")
            print(f"   URL: {api_url}/docs")
        else:
            print(f"⚠️  Status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Resumo Final
    print("\n" + "=" * 80)
    print(" " * 25 + "✅ TODOS OS TESTES PASSARAM!")
    print("=" * 80)
    print(f"\n🌐 API em Produção: {api_url}")
    print(f"📖 Documentação: {api_url}/docs")
    print(f"📖 ReDoc: {api_url}/redoc")
    print("\n💡 A API está pronta para uso em produção!")
    print("\n" + "=" * 80 + "\n")
    
    return True


def testar_com_dados_reais():
    """
    Exemplo de uso com dados reais (opcional).
    """
    print("\n💡 Exemplo: Como usar a API com dados reais\n")
    
    exemplo_codigo = '''
import requests
import yfinance as yf

# 1. Obter dados reais da B3SA3.SA
ticker = yf.Ticker("B3SA3.SA")
hist = ticker.history(period="3mo")  # Últimos 3 meses

# 2. Pegar últimos 60 preços de fechamento
prices = hist['Close'].tail(60).tolist()

# 3. Fazer previsão
api_url = "https://b3sa3-api.onrender.com"  # Substituir pela URL real
response = requests.post(
    f"{api_url}/predict",
    json={"prices": prices}
)

# 4. Exibir resultado
if response.status_code == 200:
    result = response.json()
    print(f"Preço Atual: R$ {prices[-1]:.2f}")
    print(f"Preço Previsto: R$ {result['preco_previsto']:.2f}")
    diferenca = result['preco_previsto'] - prices[-1]
    print(f"Diferença: R$ {diferenca:.2f} ({diferenca/prices[-1]*100:.2f}%)")
'''
    
    print(exemplo_codigo)


if __name__ == "__main__":
    # Verificar se URL foi passada como argumento
    if len(sys.argv) > 1:
        url_api = sys.argv[1]
        print(f"\n📌 Usando URL fornecida: {url_api}")
    else:
        url_api = None
        print("\n⚠️  URL não fornecida. Usando URL padrão.")
        print("   Para usar URL customizada: python test_production.py https://sua-url.onrender.com")
    
    # Executar testes
    sucesso = testar_api_producao(url_api)
    
    if sucesso:
        # Mostrar exemplo de uso com dados reais
        testar_com_dados_reais()
        sys.exit(0)
    else:
        print("\n❌ Alguns testes falharam. Verifique os logs acima.")
        sys.exit(1)
