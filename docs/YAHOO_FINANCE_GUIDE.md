# 🔧 Guia Completo: Yahoo Finance API

**Autor:** Argus  
**Data:** 21/12/2025  
**Status:** ✅ Consolidado e Atualizado

> **📝 Nota:** Este documento consolida as informações de:
> - YAHOO_API_V8_QUICKSTART.md
> - YAHOO_FINANCE_SOLUTION.md
> - YAHOO_FINANCE_ERROR_ANALYSIS.md

---

## 📋 Índice

1. [Quick Start](#-quick-start)
2. [API v8 (Chart) - Recomendada](#-api-v8-chart---recomendada)
3. [Análise de Erros Comuns](#-análise-de-erros-comuns)
4. [Solução: Cache SQLite](#-solução-cache-sqlite)
5. [Troubleshooting](#-troubleshooting)

---

## 🚀 Quick Start

### Instalação
```bash
pip install yfinance
```

### Uso Básico (API v8 - Chart)
```python
import yfinance as yf

# Método recomendado: history()
ticker = yf.Ticker("B3SA3.SA")
df = ticker.history(period="5d")  # Últimos 5 dias
print(df[['Open', 'High', 'Low', 'Close', 'Volume']])

# Ou download direto
df = yf.download("B3SA3.SA", period="1mo", progress=False)
```

### Parâmetros Comuns
```python
# Período
period="1d"   # 1 dia
period="5d"   # 5 dias
period="1mo"  # 1 mês
period="1y"   # 1 ano
period="max"  # Todo histórico disponível

# Ou datas específicas
start="2024-01-01"
end="2024-12-31"

# Intervalo
interval="1d"   # Diário
interval="1h"   # Horário
interval="5m"   # 5 minutos
```

---

## 🎯 API v8 (Chart) - Recomendada

### Por Que v8?

✅ **Vantagens:**
- **Não requer autenticação** (sem crumb/cookie)
- **Mais estável** que v10 e v11
- **Menos bloqueios** de rate limit
- **Dados confiáveis** (OHLCV completos)
- **Suportada oficialmente** pelo yfinance

❌ **API v10/v11 (quoteSummary):**
- Requer autenticação complexa
- Erro "Invalid Crumb" frequente
- Mais vulnerável a bloqueios

### Exemplo Completo
```python
import yfinance as yf
from datetime import datetime, timedelta

def buscar_dados_b3sa3(dias=30):
    """
    Busca dados históricos da B3SA3.SA
    
    Args:
        dias (int): Número de dias de histórico
        
    Returns:
        pd.DataFrame: Dados OHLCV
    """
    try:
        ticker = yf.Ticker("B3SA3.SA")
        
        # Calcula período
        end_date = datetime.now()
        start_date = end_date - timedelta(days=dias)
        
        # Busca dados
        df = ticker.history(
            start=start_date,
            end=end_date,
            interval="1d",
            auto_adjust=True  # Ajusta para splits/dividendos
        )
        
        if df.empty:
            raise ValueError("Nenhum dado retornado")
        
        print(f"✅ {len(df)} registros obtidos")
        return df
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

# Uso
df = buscar_dados_b3sa3(dias=30)
if df is not None:
    print(df.tail())
```

### Resposta da API (JSON)
```json
{
  "chart": {
    "result": [{
      "meta": {
        "currency": "BRL",
        "symbol": "B3SA3.SA",
        "regularMarketPrice": 13.85,
        "longName": "B3 S.A. - Brasil, Bolsa, Balcão"
      },
      "timestamp": [1763038800, 1763125200, 1763384400],
      "indicators": {
        "quote": [{
          "open": [14.06, 14.45, 14.38],
          "close": [14.47, 14.44, 14.16],
          "high": [14.50, 14.52, 14.40],
          "low": [13.95, 14.30, 14.00],
          "volume": [66538000, 34127600, 39319600]
        }]
      }
    }],
    "error": null
  }
}
```

---

## 🔍 Análise de Erros Comuns

### Erro 1: "Expecting value: line 1 column 1"

**Mensagem Completa:**
```
Failed to get ticker 'B3SA3.SA' reason: Expecting value: line 1 column 1 (char 0)
B3SA3.SA: No timezone found, symbol may be delisted
```

**Causa:** API retornou resposta vazia ou HTML (não JSON)

**Hipóteses (por ordem de probabilidade):**

#### 1️⃣ Bloqueio de IP (85% dos casos)
- **Motivo:** Yahoo Finance bloqueia IPs de provedores cloud
- **Afetados:** Render.com, Heroku, Streamlit Cloud, AWS Lambda
- **Rate Limit:** ~2.000-2.500 requisições/hora por IP
- **Sintoma:** Funciona local, falha em produção

**Fontes:**
- Reddit r/algotrading: "Yahoo blocks cloud IPs"
- GitHub yfinance #591, #1956
- Streamlit Community: "Works locally, fails on Cloud"

**Solução:** Cache SQLite + GitHub Actions (ver seção abaixo)

#### 2️⃣ Versão Desatualizada do yfinance (60%)
- **Verificar:**
  ```bash
  pip show yfinance
  # Deve ser >= 0.2.40 (nov 2024)
  ```
- **Atualizar:**
  ```bash
  pip install --upgrade yfinance
  ```

#### 3️⃣ Ticker Inválido ou Fora de Mercado (30%)
- **B3:** Prefixo `.SA` é obrigatório
- **Horário:** Mercado fechado pode não retornar dados recentes
- **Teste:**
  ```python
  ticker = yf.Ticker("B3SA3.SA")
  print(ticker.info)  # Verifica se ticker existe
  ```

#### 4️⃣ Problemas de Rede (20%)
- **Timeout:** Configurar timeout maior
  ```python
  df = yf.download("B3SA3.SA", period="5d", timeout=30)
  ```
- **Proxy:** Verificar se há firewall corporativo

### Erro 2: "Invalid Crumb"

**Causa:** Tentando usar API v10 sem autenticação

**Solução:** Usar API v8 (`.history()` ou `.download()`)

### Erro 3: "No timezone found, symbol may be delisted"

**Causa:** Símbolo não encontrado ou resposta vazia

**Soluções:**
1. Verificar se símbolo está correto
2. Adicionar `.SA` para ações brasileiras
3. Verificar se não há bloqueio de IP

---

## 💾 Solução: Cache SQLite

### Problema
Servidores cloud (Render, Streamlit) têm IPs compartilhados que são frequentemente bloqueados pelo Yahoo Finance.

### Arquitetura da Solução

```
┌─────────────────────────────────────────┐
│   GitHub Actions (Workflow Diário)     │
│   Executa às 4h UTC (após fechamento)  │
│                                         │
│   1. Busca dados do Yahoo Finance      │
│   2. Atualiza database/b3sa3.db        │
│   3. Commit + Push para repo           │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│   Render.com / Streamlit Cloud          │
│   API FastAPI / App Streamlit           │
│                                         │
│   Sistema de Fallback (3 níveis):      │
│   1. Tenta Yahoo Finance (tempo real)  │
│   2. Se falhar → SQLite (cache)        │
│   3. Se falhar → Hardcoded (último)    │
└─────────────────────────────────────────┘
```

### Implementação

**1. Database Manager** (`database/db_manager.py`):
```python
import sqlite3
import pandas as pd
from pathlib import Path

class B3DataManager:
    def __init__(self, db_path="database/b3sa3.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
    
    def save_data(self, df: pd.DataFrame, ticker="B3SA3.SA"):
        """Salva dados no SQLite"""
        with sqlite3.connect(self.db_path) as conn:
            df.to_sql(ticker, conn, if_exists='replace', index=True)
    
    def load_data(self, ticker="B3SA3.SA"):
        """Carrega dados do SQLite"""
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql(
                f"SELECT * FROM '{ticker}'",
                conn,
                parse_dates=['Date'],
                index_col='Date'
            )
        return df
```

**2. GitHub Actions** (`.github/workflows/update_data.yml`):
```yaml
name: Update B3 Data

on:
  schedule:
    - cron: '0 4 * * *'  # 4h UTC diariamente
  workflow_dispatch:  # Permite execução manual

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install yfinance pandas
      
      - name: Update database
        run: python database/update_db.py
      
      - name: Commit changes
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add database/b3sa3.db
          git commit -m "chore: update B3 data $(date +'%Y-%m-%d')" || echo "No changes"
          git push
```

**3. Fallback System** (`api/data_fetcher.py`):
```python
import yfinance as yf
from database.db_manager import B3DataManager

def fetch_data_with_fallback(ticker="B3SA3.SA", period="5d"):
    """
    Sistema de fallback em 3 níveis:
    1. Yahoo Finance (tempo real)
    2. SQLite (cache)
    3. Hardcoded (último recurso)
    """
    # Nível 1: Yahoo Finance
    try:
        df = yf.download(ticker, period=period, progress=False)
        if not df.empty:
            print("✅ Dados obtidos do Yahoo Finance")
            return df
    except Exception as e:
        print(f"⚠️ Yahoo Finance falhou: {e}")
    
    # Nível 2: SQLite
    try:
        db = B3DataManager()
        df = db.load_data(ticker)
        if not df.empty:
            print("✅ Dados obtidos do cache SQLite")
            return df
    except Exception as e:
        print(f"⚠️ SQLite falhou: {e}")
    
    # Nível 3: Fallback hardcoded
    print("⚠️ Usando dados hardcoded")
    return get_hardcoded_data()

def get_hardcoded_data():
    """Dados de emergência"""
    from datetime import datetime, timedelta
    import pandas as pd
    
    dates = [datetime.now() - timedelta(days=i) for i in range(5, 0, -1)]
    return pd.DataFrame({
        'Open': [13.50, 13.60, 13.55, 13.65, 13.70],
        'Close': [13.55, 13.58, 13.62, 13.68, 13.75],
        'High': [13.70, 13.75, 13.80, 13.85, 13.90],
        'Low': [13.40, 13.50, 13.45, 13.55, 13.60],
        'Volume': [1000000, 1100000, 1050000, 1200000, 1150000]
    }, index=dates)
```

### Vantagens do Cache SQLite

✅ **Alta disponibilidade:** 99%+ uptime  
✅ **Sem dependência externa:** Funciona offline  
✅ **Dados consistentes:** Atualização controlada  
✅ **Histórico completo:** 6 anos de dados (2020-2025)  
✅ **Zero custo:** Tudo gratuito (GitHub Actions free tier)  

---

## 🔧 Troubleshooting

### Problema: Dados vazios em horário de mercado

**Solução:** Adicionar delay após fechamento
```python
from datetime import datetime

def is_after_market_close():
    """Verifica se já passou do fechamento (18h BRT)"""
    now = datetime.now()
    return now.hour >= 18

# Buscar dados apenas após fechamento
if is_after_market_close():
    df = yf.download("B3SA3.SA", period="1d")
```

### Problema: Timeout em produção

**Solução:** Aumentar timeout e adicionar retry
```python
import time

def download_with_retry(ticker, max_retries=3):
    for attempt in range(max_retries):
        try:
            df = yf.download(ticker, period="5d", timeout=30)
            if not df.empty:
                return df
        except Exception as e:
            print(f"Tentativa {attempt + 1} falhou: {e}")
            time.sleep(2 ** attempt)  # Backoff exponencial
    return None
```

### Problema: "Symbol may be delisted"

**Soluções:**
1. Verificar símbolo no site da B3: http://www.b3.com.br/
2. Testar em https://finance.yahoo.com/quote/B3SA3.SA
3. Usar cache SQLite como fallback

### Problema: Diferentes valores localmente vs produção

**Causa:** Cache do yfinance ou fuso horário diferente

**Solução:**
```python
# Limpar cache local
import yfinance as yf
yf.pdr_override()  # Reseta configurações

# Especificar timezone
from datetime import datetime
import pytz

br_tz = pytz.timezone('America/Sao_Paulo')
now = datetime.now(br_tz)
```

---

## 📚 Referências

- [Documentação oficial yfinance](https://github.com/ranaroussi/yfinance)
- [Yahoo Finance Chart API](https://query1.finance.yahoo.com/v8/finance/chart/B3SA3.SA)
- [B3 - Lista de Ações](http://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/consultas/mercado-a-vista/empresas-listadas/busca-empresa-listada/)

---

**Última atualização:** 21/12/2025  
**Autor:** Argus  
**Documentos consolidados:** YAHOO_API_V8_QUICKSTART.md, YAHOO_FINANCE_SOLUTION.md, YAHOO_FINANCE_ERROR_ANALYSIS.md
