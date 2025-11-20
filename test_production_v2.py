"""
Script de Testes de Produção da API - Versão 2.0
Testa os novos endpoints com formato correto de 5 features
"""

import requests
import numpy as np
import sys
from typing import Optional

# URL da API em produção
API_URL = "https://b3sa3-api.onrender.com"


def print_header(text: str):
    """Imprime cabeçalho formatado."""
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")


def print_section(text: str):
    """Imprime seção formatada."""
    print(f"\n{text}")
    print(f"{'-'*80}")


def test_health_check() -> bool:
    """Testa endpoint de health check."""
    print_section("1️⃣  Health Check (GET /)")
    
    try:
        response = requests.get(f"{API_URL}/", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ API Status:")
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   Mensagem: {data.get('mensagem', 'N/A')}")
            print(f"   Versão: {data.get('versao', 'N/A')}")
            print(f"   Modelo Carregado: {data.get('modelo_carregado', False)}")
            return True
        else:
            print(f"❌ Erro: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_info_endpoint() -> bool:
    """Testa endpoint de informações do modelo."""
    print_section("2️⃣  Informações do Modelo (GET /info)")
    
    try:
        response = requests.get(f"{API_URL}/info", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Informações do Modelo:")
            print(f"   Nome: {data.get('nome', 'N/A')}")
            print(f"   Arquitetura: {data.get('arquitetura', 'N/A')}")
            print(f"   Parâmetros: {data.get('parametros', 0):,}")
            print(f"   Window Size: {data.get('window_size', 0)} dias")
            print(f"   Features: {', '.join(data.get('features', []))}")
            
            metricas = data.get('metricas', {})
            print(f"\n   📊 Métricas de Performance:")
            for metrica, valor in metricas.items():
                print(f"      {metrica}: {valor}")
            
            return True
        else:
            print(f"❌ Erro: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_predict_auto() -> bool:
    """Testa endpoint de previsão automática."""
    print_section("3️⃣  Previsão Automática (POST /predict/auto) - NOVO!")
    
    try:
        ticker = "B3SA3.SA"
        print(f"Buscando dados para: {ticker}")
        print("A API vai buscar automaticamente 60 dias de dados OHLCV do Yahoo Finance...")
        
        payload = {"ticker": ticker}
        
        response = requests.post(
            f"{API_URL}/predict/auto",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=45  # Maior timeout para busca de dados
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n🎯 Resultado da Previsão:")
            print(f"   Preço Previsto: R$ {data.get('preco_previsto', 0):.2f}")
            print(f"   Confiança: {data.get('confianca', 'N/A')}")
            print(f"   Mensagem: {data.get('mensagem', 'N/A')[:100]}...")
            print("\n✅ Previsão automática passou!")
            return True
        else:
            print(f"❌ Erro: Status {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_predict_manual() -> bool:
    """Testa endpoint de previsão com dados manuais (formato correto: 5 features)."""
    print_section("4️⃣  Previsão Manual (POST /predict) - Formato Correto OHLCV")
    
    try:
        # Gerar 60 dias de dados OHLCV simulados
        print("Gerando 60 dias de dados OHLCV simulados...")
        np.random.seed(42)
        
        dados = []
        preco_base = 12.5
        
        for i in range(60):
            # Simular movimento de preço
            variacao = np.random.randn() * 0.2
            preco_base += variacao
            
            # Gerar OHLCV realista
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
                max(0, volume)  # Volume não pode ser negativo
            ])
        
        print(f"   Total de dias: {len(dados)}")
        print(f"   Primeiro dia: Open={dados[0][0]}, High={dados[0][1]}, Low={dados[0][2]}, Close={dados[0][3]}, Vol={dados[0][4]}")
        print(f"   Último dia: Open={dados[-1][0]}, High={dados[-1][1]}, Low={dados[-1][2]}, Close={dados[-1][3]}, Vol={dados[-1][4]}")
        print(f"   Range Close: R$ {min(d[3] for d in dados):.2f} - R$ {max(d[3] for d in dados):.2f}")
        
        payload = {"dados": dados}
        
        response = requests.post(
            f"{API_URL}/predict",
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
            print(f"   Mensagem: {data.get('mensagem', 'N/A')[:100]}...")
            print("\n✅ Previsão manual passou!")
            return True
        else:
            print(f"❌ Erro: Status {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_predict_auto_outros_tickers() -> bool:
    """Testa previsão automática com outros tickers."""
    print_section("5️⃣  Previsão Automática - Outros Tickers")
    
    tickers = ["PETR4.SA", "VALE3.SA", "ITUB4.SA"]
    resultados = []
    
    for ticker in tickers:
        try:
            print(f"\n   Testando {ticker}...")
            payload = {"ticker": ticker}
            
            response = requests.post(
                f"{API_URL}/predict/auto",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=45
            )
            
            if response.status_code == 200:
                data = response.json()
                preco = data.get('preco_previsto', 0)
                print(f"   ✅ {ticker}: R$ {preco:.2f}")
                resultados.append(True)
            else:
                print(f"   ⚠️  {ticker}: Status {response.status_code}")
                resultados.append(False)
        
        except Exception as e:
            print(f"   ❌ {ticker}: Erro - {e}")
            resultados.append(False)
    
    sucesso = sum(resultados)
    total = len(resultados)
    
    print(f"\n   Resultado: {sucesso}/{total} tickers testados com sucesso")
    
    return sucesso >= 2  # Pelo menos 2 devem funcionar


def test_error_handling() -> bool:
    """Testa tratamento de erros."""
    print_section("6️⃣  Tratamento de Erros")
    
    erros_detectados = 0
    
    # Teste 1: Ticker inválido
    print("\n   Teste 1: Ticker inválido...")
    try:
        response = requests.post(
            f"{API_URL}/predict/auto",
            json={"ticker": "INVALID_TICKER_XYZ"},
            timeout=30
        )
        if response.status_code in [400, 404]:
            print(f"   ✅ Erro detectado corretamente: {response.status_code}")
            erros_detectados += 1
        else:
            print(f"   ⚠️  Resposta inesperada: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro no teste: {e}")
    
    # Teste 2: Dados insuficientes (menos de 60 dias)
    print("\n   Teste 2: Dados insuficientes...")
    try:
        dados_poucos = [[12.5, 12.6, 12.4, 12.55, 1000000] for _ in range(30)]
        response = requests.post(
            f"{API_URL}/predict",
            json={"dados": dados_poucos},
            timeout=30
        )
        if response.status_code == 422:  # Validation error
            print(f"   ✅ Erro de validação detectado: {response.status_code}")
            erros_detectados += 1
        else:
            print(f"   ⚠️  Resposta inesperada: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro no teste: {e}")
    
    # Teste 3: Features incorretas
    print("\n   Teste 3: Número incorreto de features...")
    try:
        dados_errados = [[12.5, 12.6, 12.4] for _ in range(60)]  # Apenas 3 features
        response = requests.post(
            f"{API_URL}/predict",
            json={"dados": dados_errados},
            timeout=30
        )
        if response.status_code == 422:
            print(f"   ✅ Erro de validação detectado: {response.status_code}")
            erros_detectados += 1
        else:
            print(f"   ⚠️  Resposta inesperada: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro no teste: {e}")
    
    print(f"\n   Resultado: {erros_detectados}/3 erros detectados corretamente")
    
    return erros_detectados >= 2


def run_all_tests():
    """Executa todos os testes."""
    print_header("🧪 TESTES DE PRODUÇÃO - API B3SA3.SA v2.0")
    print(f"URL Base: {API_URL}")
    
    resultados = {
        "Health Check": test_health_check(),
        "Info Modelo": test_info_endpoint(),
        "Previsão Automática": test_predict_auto(),
        "Previsão Manual": test_predict_manual(),
        "Outros Tickers": test_predict_auto_outros_tickers(),
        "Tratamento Erros": test_error_handling()
    }
    
    # Sumário final
    print_header("📊 SUMÁRIO DOS TESTES")
    
    total = len(resultados)
    passou = sum(resultados.values())
    
    for teste, resultado in resultados.items():
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"   {teste:30s} {status}")
    
    print(f"\n{'='*80}")
    print(f"   RESULTADO FINAL: {passou}/{total} testes passaram")
    print(f"{'='*80}\n")
    
    return passou == total


if __name__ == "__main__":
    sucesso = run_all_tests()
    sys.exit(0 if sucesso else 1)
