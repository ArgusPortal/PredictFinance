# 🔍 Análise do Erro Yahoo Finance: "Expecting value: line 1 column 1"

**Data**: 20/11/2025  
**Erro Reportado**:
```
Failed to get ticker 'B3SA3.SA' reason: Expecting value: line 1 column 1 (char 0)
B3SA3.SA: No timezone found, symbol may be delisted
```

---

## 📊 Hipóteses Identificadas

### ✅ **Hipótese 1: Bloqueio de IP pelo Yahoo Finance** (MAIS PROVÁVEL)
**Probabilidade**: 85%

**Evidências**:
- Yahoo Finance bloqueia IPs de provedores de cloud (Render, Heroku, Streamlit Cloud)
- Rate limit não oficial: ~2.000-2.500 requisições/hora por IP
- IPs compartilhados em cloud são "queimados" rapidamente
- Retorna resposta vazia (HTTP 403/999 silencioso) causando JSON decode error

**Fontes**:
- Reddit r/algotrading: "Yahoo blocks ~2,000 req/hour per IP"
- Streamlit Community: "YFRateLimitError only on Streamlit Cloud, works locally"
- GitHub yfinance issues #591, #1956

**Solução**:
- ✅ Usar banco SQLite como cache (JÁ IMPLEMENTADO)
- ✅ Workflow GitHub Actions para popular banco diariamente (JÁ IMPLEMENTADO)
- Adicionar retry com backoff exponencial
- Usar proxies rotativos (custoso)
- Migrar para API oficial do Yahoo (pago)

---

### ✅ **Hipótese 2: Versão Desatualizada do yfinance**
**Probabilidade**: 60%

**Evidências**:
- Yahoo muda estrutura da API frequentemente
- StackOverflow: "Update module to newer version"
- Error "Expecting value" indica mudança na resposta da API

**Verificação**:
```bash
pip show yfinance
# Versão atual: checar se < 0.2.40 (novembro 2024)
```

**Solução**:
```bash
pip install --upgrade yfinance
```

---

### ✅ **Hipótese 3: Símbolo Inválido ou Delisted**
**Probabilidade**: 10%

**Evidências**:
- Mensagem: "symbol may be delisted"
- B3SA3.SA é uma ação válida e ativa na B3

**Verificação Manual**:
- Testar no site: https://finance.yahoo.com/quote/B3SA3.SA
- Testar endpoint direto (ver seção abaixo)

**Descartável se**: Site mostra dados normalmente

---

### ✅ **Hipótese 4: Problema de Timezone/Encoding**
**Probabilidade**: 20%

**Evidências**:
- "No timezone found" sugere problema na conversão de datas
- Ações brasileiras têm timezone America/Sao_Paulo

**Solução**:
```python
import yfinance as yf
ticker = yf.Ticker("B3SA3.SA")
hist = ticker.history(period="1d", auto_adjust=False)
# Forçar timezone
hist.index = hist.index.tz_localize('America/Sao_Paulo')
```

---

### ✅ **Hipótese 5: Crumb/Cookie Inválido**
**Probabilidade**: 40%

**Evidências**:
- Yahoo usa sistema de crumbs para autenticação
- Error comum: "Invalid Crumb"
- yfinance gerencia automaticamente, mas pode falhar

**Solução**:
```python
# Limpar cache do yfinance
import yfinance as yf
yf.cache.clear()

# Forçar nova sessão
ticker = yf.Ticker("B3SA3.SA")
ticker.session.close()
ticker.session = None
```

---

### ✅ **Hipótese 6: Firewall/Antivirus Bloqueando**
**Probabilidade**: 5%

**Evidências**:
- Render.com pode ter firewall restritivo
- Alguns IPs podem estar em blacklist

**Verificação**:
```bash
curl -I https://query2.finance.yahoo.com/v8/finance/chart/B3SA3.SA
# Se retornar 403/999: bloqueio confirmado
```

---

### ✅ **Hipótese 7: Horário de Manutenção do Yahoo**
**Probabilidade**: 15%

**Evidências**:
- Yahoo Finance tem janelas de manutenção
- Geralmente madrugada US (tarde BR)

**Verificação**:
- Testar em horários diferentes
- Checar status: https://downdetector.com/status/yahoo/

---

## 🔗 Links para Teste Manual

### 1. **Testar no Site Yahoo Finance**
```
https://finance.yahoo.com/quote/B3SA3.SA
```
- ✅ Se carregar: ação válida, problema é na API
- ❌ Se der erro: ação pode estar delisted (improvável)

---

### 2. **Testar Endpoint JSON Direto (v8)**
```
https://query2.finance.yahoo.com/v8/finance/chart/B3SA3.SA?interval=1d&range=5d
```
**O que esperar**:
- ✅ JSON com dados: API funcionando
- ❌ Página "Will be right back": Bloqueio temporário
- ❌ Vazio/404: IP bloqueado ou ação inválida
- ❌ {"error": ...}: Problema de autenticação

---

### 3. **Testar Endpoint Alternativo (v10)**
```
https://query2.finance.yahoo.com/v10/finance/quoteSummary/B3SA3.SA?modules=price
```
**O que esperar**:
- ✅ JSON com "price": Endpoint v10 funcionando
- ❌ "Unauthorized": Crumb inválido
- ❌ Vazio: IP bloqueado

---

### 4. **Testar com Proxy (caso tenha VPN)**
```
https://query1.finance.yahoo.com/v8/finance/chart/B3SA3.SA
```
**Tente com**:
- query1.finance.yahoo.com
- query2.finance.yahoo.com
- fc.yahoo.com (fallback)

---

### 5. **Testar Histórico Completo**
```
https://query2.finance.yahoo.com/v8/finance/chart/B3SA3.SA?period1=1609459200&period2=1700524800&interval=1d
```
**Parâmetros**:
- period1: 01/01/2021 (timestamp)
- period2: 21/11/2023 (timestamp)
- interval: 1d (diário)

---

## 🛠️ Soluções Recomendadas

### ✅ **Solução Imediata** (JÁ IMPLEMENTADA)
Usar banco SQLite como cache:
```python
# Ao invés de:
dados = yf.download("B3SA3.SA", start=start, end=end)

# Usar:
from database.db_manager import DatabaseManager
db = DatabaseManager()
dados = db.get_data("B3SA3.SA", start_date=start, end_date=end)
```

**Vantagens**:
- ✅ Independente do Yahoo Finance
- ✅ Rápido (sem requisições HTTP)
- ✅ Confiável (dados já validados)
- ✅ Workflow automatizado (GitHub Actions)

---

### ⚡ **Solução Robusta**: Retry com Backoff
```python
import time
from functools import wraps

def retry_yahoo_request(max_attempts=3, backoff_factor=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if "Expecting value" in str(e) or "No timezone" in str(e):
                        if attempt < max_attempts - 1:
                            wait = backoff_factor ** attempt
                            print(f"⚠️  Tentativa {attempt+1} falhou. Aguardando {wait}s...")
                            time.sleep(wait)
                        else:
                            print(f"❌ Todas as {max_attempts} tentativas falharam")
                            raise
                    else:
                        raise
        return wrapper
    return decorator

@retry_yahoo_request(max_attempts=3)
def coletar_dados_historicos(ticker, anos):
    # ... código existente
    pass
```

---

### 🌐 **Solução Alternativa**: yahoo_fin
Se o bloqueio persistir, considerar biblioteca alternativa:
```bash
pip install yahoo_fin
```

```python
from yahoo_fin import stock_info as si

# Obter dados históricos
dados = si.get_data("B3SA3.SA", start_date="2020-01-01")
```

**Vantagens**:
- Usa web scraping ao invés da API
- Menos suscetível a bloqueios
- Mantém mesma estrutura de dados

---

### 🔐 **Solução Profissional**: API Oficial
**Alpha Vantage** (15 anos de histórico):
```
https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=B3SA3.SAO&apikey=YOUR_KEY
```

**Brapi** (API brasileira):
```
https://brapi.dev/api/quote/B3SA3
```

---

## 📝 Checklist de Diagnóstico

Execute os testes na ordem:

- [ ] 1. Acessar https://finance.yahoo.com/quote/B3SA3.SA
  - ✅ Funciona: Prosseguir
  - ❌ Erro: Ação pode estar com problema

- [ ] 2. Testar endpoint JSON direto (link acima)
  - ✅ JSON retornado: yfinance desatualizado
  - ❌ Vazio/403: IP bloqueado

- [ ] 3. Verificar versão do yfinance
  ```bash
  pip show yfinance
  ```
  - Se < 0.2.40: Atualizar

- [ ] 4. Testar localmente (não no Render)
  - ✅ Funciona local: Confirmado bloqueio de IP
  - ❌ Falha local: Problema na biblioteca/código

- [ ] 5. Verificar logs do Render
  - Procurar por HTTP 403, 429, 999
  - Verificar horário do erro

- [ ] 6. Testar com proxy/VPN (se disponível)
  - ✅ Funciona: IP bloqueado confirmado

---

## 🎯 Recomendação Final

**Para Produção no Render**:
1. ✅ **Continuar usando SQLite** como fonte primária (JÁ IMPLEMENTADO)
2. ✅ **Manter GitHub Actions** atualizando banco diariamente (JÁ IMPLEMENTADO)
3. ⚡ **Adicionar retry com backoff** no workflow do Actions (se falhar)
4. 📊 **Monitorar** taxa de sucesso das requisições
5. 🔄 **Fallback**: Se SQLite vazio, tentar yahoo_fin como backup

**O sistema atual já está protegido contra bloqueios do Yahoo Finance!**

---

## 📚 Referências

1. **GitHub yfinance**: https://github.com/ranaroussi/yfinance/issues/591
2. **StackOverflow**: https://stackoverflow.com/questions/68331065/
3. **Reddit algotrading**: Rate limits discussion
4. **YouTube**: Brandon Jacobson - Yahoo Finance API Workarounds
5. **Streamlit Forum**: YFRateLimitError discussions

---

**Última atualização**: 20/11/2025
