"""
Script de Diagnóstico: Yahoo Finance Error
Testa todas as hipóteses e identifica a causa do erro
"""

import yfinance as yf
import requests
from datetime import datetime, timedelta
import json

print("=" * 70)
print("🔍 DIAGNÓSTICO: Yahoo Finance - B3SA3.SA")
print("=" * 70)

# Teste 1: Verificar versão do yfinance
print("\n1️⃣ Testando versão do yfinance...")
try:
    import yfinance
    version = yfinance.__version__
    print(f"   ✅ Versão instalada: {version}")
    if version < "0.2.40":
        print(f"   ⚠️  ATENÇÃO: Versão antiga! Recomendado: >= 0.2.40")
    else:
        print(f"   ✅ Versão atualizada!")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Teste 2: Endpoint JSON direto (v8)
print("\n2️⃣ Testando endpoint v8 (query2.finance.yahoo.com)...")
url_v8 = "https://query2.finance.yahoo.com/v8/finance/chart/B3SA3.SA?interval=1d&range=5d"
try:
    response = requests.get(url_v8, timeout=10)
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            if "chart" in data and data["chart"]["result"]:
                print(f"   ✅ API v8 funcionando! Dados recebidos.")
            else:
                print(f"   ⚠️  Resposta vazia ou inválida")
                print(f"   Resposta: {response.text[:200]}")
        except json.JSONDecodeError:
            print(f"   ❌ ERRO: Resposta não é JSON válido")
            print(f"   Conteúdo: {response.text[:200]}")
    elif response.status_code in [403, 429, 999]:
        print(f"   ❌ IP BLOQUEADO! (Status {response.status_code})")
    else:
        print(f"   ⚠️  Erro HTTP: {response.status_code}")
        print(f"   Conteúdo: {response.text[:200]}")
        
except requests.exceptions.Timeout:
    print(f"   ⏱️  TIMEOUT: Servidor não respondeu em 10s")
except requests.exceptions.ConnectionError:
    print(f"   🔌 ERRO DE CONEXÃO: Não foi possível conectar")
except Exception as e:
    print(f"   ❌ Erro inesperado: {e}")

# Teste 3: Endpoint alternativo (v10)
print("\n3️⃣ Testando endpoint v10 (quoteSummary)...")
url_v10 = "https://query2.finance.yahoo.com/v10/finance/quoteSummary/B3SA3.SA?modules=price"
try:
    response = requests.get(url_v10, timeout=10)
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            if "quoteSummary" in data:
                print(f"   ✅ API v10 funcionando!")
            else:
                print(f"   ⚠️  Resposta inesperada: {response.text[:200]}")
        except json.JSONDecodeError:
            print(f"   ❌ Resposta não é JSON: {response.text[:200]}")
    elif response.status_code in [403, 429, 999]:
        print(f"   ❌ IP BLOQUEADO! (Status {response.status_code})")
    else:
        print(f"   ⚠️  Erro: {response.status_code}")
        
except requests.exceptions.Timeout:
    print(f"   ⏱️  TIMEOUT: Servidor não respondeu")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Teste 4: yfinance download direto
print("\n4️⃣ Testando yfinance.download()...")
try:
    data_fim = datetime.now()
    data_inicio = data_fim - timedelta(days=7)
    
    dados = yf.download(
        "B3SA3.SA",
        start=data_inicio,
        end=data_fim,
        progress=False
    )
    
    if not dados.empty:
        print(f"   ✅ yfinance funcionando! {len(dados)} registros coletados")
        print(f"   Período: {dados.index[0]} a {dados.index[-1]}")
    else:
        print(f"   ⚠️  DataFrame vazio retornado")
        
except Exception as e:
    error_msg = str(e)
    print(f"   ❌ ERRO: {error_msg}")
    
    if "Expecting value" in error_msg:
        print(f"   🔍 DIAGNÓSTICO: JSONDecodeError - Resposta vazia ou inválida")
        print(f"   💡 CAUSA PROVÁVEL: IP bloqueado ou rate limit")
    elif "No timezone" in error_msg:
        print(f"   🔍 DIAGNÓSTICO: Problema de timezone")
        print(f"   💡 CAUSA PROVÁVEL: Mudança na estrutura de dados do Yahoo")
    elif "404" in error_msg or "delisted" in error_msg:
        print(f"   🔍 DIAGNÓSTICO: Ticker não encontrado")
        print(f"   💡 CAUSA PROVÁVEL: Símbolo inválido (improvável para B3SA3.SA)")
    else:
        print(f"   🔍 DIAGNÓSTICO: Erro desconhecido")

# Teste 5: Ticker object
print("\n5️⃣ Testando yfinance.Ticker()...")
try:
    ticker = yf.Ticker("B3SA3.SA")
    info = ticker.info
    
    if info and len(info) > 5:
        print(f"   ✅ Ticker.info funcionando!")
        print(f"   Nome: {info.get('longName', 'N/A')}")
        print(f"   Símbolo: {info.get('symbol', 'N/A')}")
    else:
        print(f"   ⚠️  Info vazio ou incompleto")
        print(f"   Conteúdo: {info}")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Teste 6: Verificar cache
print("\n6️⃣ Verificando cache do yfinance...")
try:
    cache_dir = yf.cache.get_cache_dir()
    print(f"   Cache dir: {cache_dir}")
    print(f"   💡 Limpar cache: yf.cache.clear()")
except Exception as e:
    print(f"   ⚠️  Não foi possível acessar cache: {e}")

# Diagnóstico Final
print("\n" + "=" * 70)
print("📊 DIAGNÓSTICO FINAL")
print("=" * 70)

print("""
🎯 INTERPRETAÇÃO DOS RESULTADOS:

1. Se TODOS os testes falharam:
   → IP BLOQUEADO pelo Yahoo Finance
   → Solução: Usar SQLite como cache (JÁ IMPLEMENTADO)

2. Se endpoints funcionam MAS yfinance falha:
   → Versão desatualizada do yfinance
   → Solução: pip install --upgrade yfinance

3. Se apenas endpoint v8 falha:
   → Yahoo desativou endpoint v8
   → Solução: yfinance atualiza automaticamente

4. Se funcionou localmente mas falha no Render:
   → IP do Render bloqueado
   → Solução: GitHub Actions + SQLite (JÁ IMPLEMENTADO)

5. Se "Expecting value" aparece:
   → Resposta vazia/inválida da API
   → Causa: Rate limit ou bloqueio silencioso

✅ SISTEMA ATUAL JÁ ESTÁ PROTEGIDO:
   - SQLite como cache principal
   - GitHub Actions atualizando banco diariamente
   - Independente do Yahoo Finance em produção
""")

print("\n📝 Para testar os links manualmente no navegador:")
print("\n   Link 1 (Site):")
print("   https://finance.yahoo.com/quote/B3SA3.SA")
print("\n   Link 2 (API v8 - JSON):")
print("   https://query2.finance.yahoo.com/v8/finance/chart/B3SA3.SA?interval=1d&range=5d")
print("\n   Link 3 (API v10 - JSON):")
print("   https://query2.finance.yahoo.com/v10/finance/quoteSummary/B3SA3.SA?modules=price")

print("\n" + "=" * 70)
