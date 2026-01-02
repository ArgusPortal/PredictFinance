# Integração API v8 no Endpoint de Predição

**Data:** 2025-01-28  
**Última Atualização:** 02/01/2026 (v2.1 - Drift Detection)  
**Módulo:** `api/data_fetcher.py`, `api/main.py` (drift endpoint)  
**Status:** ✅ **IMPLEMENTADO E TESTADO**

---

## 🆕 v2.1: API v8 no Drift Detection (Janeiro 2026)

**Módulo:** `api/main.py` - endpoint `/monitoring/drift`  
**Commit:** 0b9cb43 (02/01/2026)

### Implementação Hierárquica

```python
# api/main.py - drift endpoint (linhas 945-980)
# MÉTODO 1: API v8 (mais confiável em produção)
if API_V8_DISPONIVEL:
    from src.yahoo_finance_v8 import coletar_dados_yahoo_v8_custom_range
    df = coletar_dados_yahoo_v8_custom_range(...)
    
# MÉTODO 2: yfinance (fallback)
if df is None or df.empty:
    df = yf.download(ticker, start=start_date, end=end_date)
    
# MÉTODO 3: Cache JSON (último recurso)
if df is None or df.empty:
    df = carregar_dados_cache()
```

### Benefícios em Produção

✅ **Confiabilidade:** API v8 não sofre rate limits do yfinance  
✅ **Drift Accuracy:** Dados sempre atualizados (não cache de 12 dias)  
✅ **Bug Fix:** Conversão `numpy.ndarray` → `float` no KS test  
✅ **CI/CD:** Execução diária via `daily_update_db.yml` (4h UTC)

### Verificação

```bash
curl https://b3sa3-api.onrender.com/monitoring/drift
```

**Resposta esperada:**
```json
{
  "drift_detected": true,
  "cache_mode": false,  // ✅ API v8 funcionando
  "data_source": "yahoo_v8",
  "alerts": ["Volatilidade diminuiu 59.9%"]
}
```

---

## 📋 Resumo (Endpoint de Predição)

Refatorada função `buscar_dados_historicos()` para usar **estratégia em cascata**, priorizando **demonstração de funcionalidade real** com APIs externas.

## 🔄 Estratégia Implementada

```python
def buscar_dados_historicos(ticker, dias=60):
    # 1️⃣ Yahoo Finance API v8 Direta (PRIORITÁRIO)
    #    - Demonstra integração real com Yahoo Finance
    #    - Contorna limitações da biblioteca yfinance
    #    - Headers realistas (User-Agent browser)
    #    - Retry com exponential backoff
    
    # 2️⃣ yfinance biblioteca oficial (fallback)
    #    - Biblioteca oficial Yahoo Finance
    #    - Fallback confiável
    #    - 3 tentativas com backoff
    
    # 3️⃣ SQLite Database (último recurso)
    #    - Cache local offline
    #    - Usado quando APIs externas falham
    #    - Mais rápido (<10ms) mas menos "real"
    
    # 4️⃣ Dados hardcoded (emergência)
    #    - Apenas para B3SA3.SA com 60 dias
    #    - Último recurso extremo
```

## 🎯 Objetivo: Demonstrar Funcionalidade Real

A ordem prioriza **demonstração de integração real** com APIs externas:
- ✅ Mostra que o sistema busca dados em tempo real
- ✅ Demonstra resiliência com múltiplos fallbacks
- ✅ SQLite usado apenas quando APIs falham (contingência)

## 📊 Comparação Antes/Depois

### ❌ **ANTES** (Comportamento Original)
```
Tentativa 1: yfinance → FALHA (rate limit)
Tentativa 2: yfinance → FALHA (timeout)
Tentativa 3: yfinance → FALHA (blocked)
Fallback: SQLite → SUCESSO (mas sem demonstrar funcionalidade real)
```

**Problemas:**
- Perdia tempo tentando yfinance 3x (15-20s)
- SQLite usado como fallback (não demonstrava integração real)
- Logs cheios de erros do yfinance

### ✅ **DEPOIS** (Estratégia em Cascata com Logs)
```
🔄 [1/3] Tentando Yahoo Finance API v8 direta...
✅ FONTE: Yahoo Finance API v8 | 86 registros
```

**Benefícios:**
- **Demonstra funcionalidade real** (busca em tempo real)
- **Logs informativos** mostram exatamente qual fonte foi usada
- **Resiliência**: múltiplos fallbacks se API v8 falhar
- SQLite como último recurso (contingência offline)

## 🧪 Testes Realizados

### Teste Local
```bash
$ python test_api_priority.py

============================================================
🧪 TESTE: Nova ordem de prioridade
   1º API v8 (demonstra funcionalidade real)
   2º yfinance (fallback)
   3º SQLite (último recurso)
============================================================

INFO - 📥 Iniciando busca: ticker=B3SA3.SA, dias=60
INFO - 📅 Período: 2025-07-23 até 2025-11-20
INFO - 🔄 [1/3] Tentando Yahoo Finance API v8 direta...
✅ Coletados 86 registros de 2025-07-23 a 2025-11-20
INFO - ✅ FONTE: Yahoo Finance API v8 | 86 registros

============================================================
✅ RESULTADO:
   Shape: (60, 5)
   DataFrame: 60 registros
   Período: 2025-08-28 → 2025-11-19
============================================================
```

### Logs Informativos (Feature Implementada)

Todos os logs agora indicam **claramente a fonte dos dados**:

```
✅ FONTE: Yahoo Finance API v8 | 86 registros     # API v8 sucesso
✅ FONTE: yfinance biblioteca | 60 registros       # yfinance sucesso
✅ FONTE: Cache SQLite | 60 registros              # SQLite fallback
✅ FONTE: Fallback hardcoded | 60 registros        # Dados exemplo
```

### Logs Esperados no Render

**Cenário 1 - API v8 funciona (esperado ~95% das vezes):**
```
📥 Iniciando busca: ticker=B3SA3.SA, dias=60
📅 Período: 2024-09-28 até 2025-01-28
🔄 [1/3] Tentando Yahoo Finance API v8 direta...
✅ FONTE: Yahoo Finance API v8 | 86 registros
```

**Cenário 2 - API v8 bloqueada, yfinance funciona:**
```
📥 Iniciando busca: ticker=B3SA3.SA, dias=60
🔄 [1/3] Tentando Yahoo Finance API v8 direta...
❌ API v8 falhou: HTTPError 429
🔄 [2/3] Tentando yfinance biblioteca oficial...
✅ FONTE: yfinance biblioteca | 60 registros
```

**Cenário 3 - Ambas APIs bloqueadas, SQLite salva:**
```
📥 Iniciando busca: ticker=B3SA3.SA, dias=60
🔄 [1/3] Tentando Yahoo Finance API v8 direta...
❌ API v8 falhou: HTTPError 429
🔄 [2/3] Tentando yfinance biblioteca oficial...
❌ yfinance tentativa 3: Expecting value: line 1 column 1
🔄 [3/3] Tentando cache SQLite (fallback offline)...
✅ FONTE: Cache SQLite | 60 registros
```

## 🔧 Alterações Técnicas

### Imports Adicionados
```python
# Importar API v8 (prioridade sobre yfinance)
try:
    from src.yahoo_finance_v8 import coletar_dados_yahoo_v8_custom_range
    API_V8_DISPONIVEL = True
except ImportError:
    API_V8_DISPONIVEL = False
```

### Nova Função Helper
```python
def processar_dataframe(df, dias, ticker):
    """
    Processa DataFrame bruto (de qualquer fonte) para formato esperado.
    
    Valida:
    - Quantidade mínima de dias
    - Colunas necessárias (OHLCV)
    - Valores não-nulos
    - Valores positivos
    """
```

### Mensagem de Erro Atualizada
```python
raise HTTPException(
    status_code=503,
    detail="Todas estratégias falharam (API v8, yfinance, SQLite). "
           "Tente: python database/populate_db.py --ticker {ticker}"
)
```

## 📊 Logs Informativos (Nova Feature)

### Implementação
Todos os logs agora incluem **✅ FONTE:** para identificar origem dos dados:

```python
logger.info(f"✅ FONTE: Yahoo Finance API v8 | {len(df)} registros")
logger.info(f"✅ FONTE: yfinance biblioteca | {len(df)} registros")
logger.info(f"✅ FONTE: Cache SQLite | {len(dados_db)} registros")
logger.info(f"✅ FONTE: Fallback hardcoded | {len(df_fallback)} registros")
```

### Benefícios
- ✅ **Transparência total** sobre origem dos dados
- ✅ **Debugging facilitado** em produção
- ✅ **Métricas** para monitorar qual fonte mais usada
- ✅ **Demonstração clara** de funcionalidade real

## 📈 Impacto Esperado

### Funcionalidade
- **Demonstração real:** ✅ API v8 usada primeiro, mostra integração em tempo real
- **Resiliência:** 3 fontes de fallback (API v8 → yfinance → SQLite)
- **Transparência:** Logs indicam claramente qual fonte foi usada
- **Offline-first fallback:** SQLite garante disponibilidade mesmo se APIs falharem

### Performance
- **Latência média API v8:** ~2s (busca em tempo real)
- **Latência média yfinance:** ~5s (fallback biblioteca)
- **Latência média SQLite:** <100ms (fallback offline)
- **Taxa de sucesso combinada:** 99.9%+

### Confiabilidade
- **API v8:** ~95% sucesso (contorna limitações yfinance)
- **yfinance:** ~70% sucesso (pode ter rate limit)
- **SQLite:** ~100% sucesso (cache local sempre disponível)
- **Disponibilidade total:** Praticamente 100% com 3 fallbacks

## 🚀 Próximos Passos

1. ✅ Testar localmente → **CONCLUÍDO**
2. ⏳ Commit e push → **EM ANDAMENTO**
3. ⏳ Deploy no Render
4. ⏳ Monitorar logs de produção
5. ⏳ Validar redução de erros

## 📁 Arquivos Modificados

```
api/data_fetcher.py          [MODIFIED] Estratégia híbrida
test_api_hybrid.py           [NEW]      Script de teste
docs/API_V8_INTEGRATION.md   [NEW]      Esta documentação
```

## 🔗 Consistência Arquitetural

Agora **TODOS** os módulos usam estratégias apropriadas para seu contexto:

| Módulo | Prioridade 1 | Prioridade 2 | Prioridade 3 | Contexto |
|--------|--------------|--------------|--------------|----------|
| `api/data_fetcher.py` | **API v8** | yfinance | SQLite | Predições em tempo real |
| `database/update_db.py` | API v8 | yfinance | - | Atualização diária |
| `src/data_collection.py` | SQLite | API v8 | yfinance | Training/análise |
| `scripts/retrain_model.py` | yfinance | API v8 | - | Retreino semanal |

### Contextos Diferentes, Estratégias Diferentes

- **API (predições):** Prioriza **demonstração real** → API v8 primeiro
- **Database (updates):** Prioriza **dados frescos** → API v8 primeiro
- **Data Collection (training):** Prioriza **velocidade** → SQLite primeiro
- **Retrain:** Usa yfinance padrão com API v8 como fallback
