# 📋 Changelog - Implementação de Auto-Fetch e Correção de Formato

**Data:** 20/11/2025  
**Versão:** 2.0  
**Status:** ✅ Implementado

---

## 🎯 Objetivo

Implementar funcionalidade de busca automática de dados via Yahoo Finance e corrigir formato da API para usar 5 features OHLCV em vez de apenas preços de fechamento.

---

## ✨ Novidades

### 1. **Novo Endpoint `/predict/auto`**

Endpoint de previsão automática que busca dados do Yahoo Finance:

```bash
POST /predict/auto
{
  "ticker": "B3SA3.SA"
}
```

**Benefícios:**
- ✅ Usuário fornece apenas o ticker
- ✅ API busca automaticamente últimos 60 dias de dados OHLCV
- ✅ Elimina necessidade de fornecer 300 valores manualmente
- ✅ Sempre usa dados mais recentes disponíveis

### 2. **Formato Correto no `/predict`**

Endpoint existente agora aceita formato correto com 5 features:

```bash
POST /predict
{
  "dados": [
    [Open, High, Low, Close, Volume],  # Dia 1
    [Open, High, Low, Close, Volume],  # Dia 2
    ...                                 # 60 dias total
  ]
}
```

**Antes (incorreto):**
```json
{"prices": [12.5, 12.6, 12.7, ...]}  // Apenas Close (1 feature)
```

**Agora (correto):**
```json
{"dados": [[12.5, 12.7, 12.4, 12.6, 1500000], ...]}  // OHLCV (5 features)
```

---

## 📝 Arquivos Criados

| Arquivo | Descrição |
|---------|-----------|
| `api/data_fetcher.py` | Módulo de busca de dados via yfinance |
| `EXEMPLOS_USO_API.md` | Guia completo de uso da API (curl, Python, JS) |
| `test_production_v2.py` | Testes atualizados para novo formato |
| `CHANGELOG_V2.md` | Este arquivo |

---

## 🔧 Arquivos Modificados

### Backend

| Arquivo | Mudanças |
|---------|----------|
| `api/schemas.py` | ✅ PrevisaoInput agora aceita `dados: List[List[float]]` (60×5)<br>✅ Novo schema `PrevisaoAutoInput` com campo `ticker`<br>✅ Validações para OHLCV |
| `api/main.py` | ✅ Import de `data_fetcher` module<br>✅ Endpoint `/predict` atualizado para processar 5 features<br>✅ Novo endpoint `/predict/auto` implementado<br>✅ Correção na desnormalização (usar índice 3 para Close) |
| `requirements-render.txt` | ✅ Adicionado `yfinance==0.2.38` |

### Documentação

| Arquivo | Mudanças |
|---------|----------|
| `README.md` | ✅ Seção de uso rápido da API<br>✅ Menção à busca automática |
| `docs/FASE_7_GUIA.md` | ✅ Exemplo completo com 5 features<br>✅ Novo endpoint `/predict/auto`<br>✅ Explicação de formato OHLCV |
| `docs/DEPLOY_RENDER.md` | ✅ Atualizado para endpoint `/predict/auto`<br>✅ Removido exemplo incorreto |
| `DEPLOY_QUICKSTART.md` | ✅ Comando curl simplificado com `/predict/auto`<br>✅ Referência para exemplos completos |

---

## 🔄 Compatibilidade

### ⚠️ Breaking Changes

O endpoint `/predict` agora requer formato diferente:

**Antes:**
```python
{"prices": [12.5, 12.6, ...]}  # 60 valores
```

**Agora:**
```python
{"dados": [[O, H, L, C, V], ...]}  # 60 linhas × 5 colunas
```

### ✅ Migração

**Opção 1 (Recomendada):** Use o novo endpoint `/predict/auto`
```python
# Antes
response = requests.post(url + "/predict", json={"prices": precos})

# Agora (mais fácil!)
response = requests.post(url + "/predict/auto", json={"ticker": "B3SA3.SA"})
```

**Opção 2:** Adapte dados para formato OHLCV
```python
# Se você tem apenas Close prices, precisa buscar OHLCV completo
import yfinance as yf

ticker = yf.Ticker("B3SA3.SA")
df = ticker.history(period="60d")
dados = df[['Open', 'High', 'Low', 'Close', 'Volume']].tail(60).values.tolist()

response = requests.post(url + "/predict", json={"dados": dados})
```

---

## 🧪 Testes

### Executar Testes Locais

```bash
# Testes com novo formato
python test_production_v2.py
```

**Cobertura:**
- ✅ Health check
- ✅ Info do modelo
- ✅ Previsão automática (`/predict/auto`)
- ✅ Previsão manual (`/predict` com OHLCV)
- ✅ Múltiplos tickers
- ✅ Tratamento de erros

### Testes Manuais

```bash
# 1. Previsão automática (mais fácil)
curl -X POST https://b3sa3-api.onrender.com/predict/auto \
  -H "Content-Type: application/json" \
  -d '{"ticker": "B3SA3.SA"}'

# 2. Verificar documentação interativa
# Abrir no navegador: https://b3sa3-api.onrender.com/docs
```

---

## 🐛 Correções de Bugs

### 1. **Modelo Esperava 5 Features, API Recebia 1**

**Problema:**
- Modelo treinado com: `[Open, High, Low, Close, Volume]` (5 features)
- API recebia: `[Close]` apenas (1 feature)
- API replicava Close para as 5 posições (workaround incorreto)

**Solução:**
- API agora recebe 5 features corretamente
- Normalização usa todas as 5 features
- Predição usa índice 3 (Close) para extrair resultado

### 2. **Documentação com Exemplos Incorretos**

**Problema:**
- Todos os exemplos mostravam formato `{"prices": [...]}`
- Formato não correspondia ao modelo real

**Solução:**
- Atualizado todos os exemplos para formato OHLCV
- Adicionado endpoint `/predict/auto` que elimina necessidade de dados manuais

---

## 📊 Impacto

### Performance

- ⏱️ `/predict`: Sem mudança (~200ms)
- ⏱️ `/predict/auto`: +1-2s para busca no Yahoo Finance
- 💾 Memória: +5MB para yfinance
- 📦 Deploy: +10MB no build (yfinance + dependências)

### UX

**Antes:**
1. Usuário busca 60 dias de dados manualmente
2. Formata array com 60 valores Close
3. Envia para API

**Agora:**
1. Usuário envia apenas ticker
2. API faz tudo automaticamente ✨

---

## 🚀 Deployment

### Checklist Render.com

- [x] Atualizar `requirements-render.txt` com yfinance
- [x] Fazer commit e push para repositório
- [ ] Render detecta mudanças e faz rebuild automático
- [ ] Verificar logs do deploy
- [ ] Testar endpoints após deploy

### Comando de Deploy Manual

```bash
# Fazer commit
git add .
git commit -m "feat: Implementar auto-fetch e corrigir formato OHLCV"
git push origin main

# Render faz deploy automático
# Aguardar ~5-10 minutos
```

---

## 📚 Documentação de Referência

| Documento | Link |
|-----------|------|
| Exemplos de Uso | [`EXEMPLOS_USO_API.md`](EXEMPLOS_USO_API.md) |
| Guia de Deploy | [`docs/DEPLOY_RENDER.md`](docs/DEPLOY_RENDER.md) |
| Quick Start | [`DEPLOY_QUICKSTART.md`](DEPLOY_QUICKSTART.md) |
| Fase 7 (API) | [`docs/FASE_7_GUIA.md`](docs/FASE_7_GUIA.md) |

---

## ⚠️ Notas Importantes

### Limitações do Yahoo Finance

- ✋ Rate limiting: ~2000 requests/hora
- 📅 Dados apenas de dias úteis (sem fins de semana)
- ⏰ Dados atualizados após fechamento do mercado (18h BRT)
- 🔒 Tickers devem terminar com `.SA` para B3

### Render Free Tier

- 💤 Cold start: Primeiro request após 15min inatividade leva ~30s
- ⏱️ Timeout: 30s por request (pode ser curto para alguns tickers)
- 💾 Limite de memória: 512MB (suficiente para este projeto)

---

## 🔮 Próximos Passos (Futuro)

- [ ] Adicionar cache de dados do Yahoo Finance (Redis)
- [ ] Implementar endpoint `/predict/batch` para múltiplos tickers
- [ ] Adicionar suporte a intervalos customizados (1h, 1d, 1wk)
- [ ] Interface web para visualizar previsões
- [ ] Websocket para previsões em tempo real

---

## 👥 Contribuidores

- **ArgusPortal** - Implementação completa

---

## 📄 Licença

Este projeto segue a mesma licença do projeto principal PredictFinance.
