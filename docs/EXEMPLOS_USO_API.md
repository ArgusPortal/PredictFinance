# 🚀 API de Previsão B3SA3.SA - Exemplos de Uso

## Endpoints Disponíveis

### 1. ✅ Health Check
```bash
curl https://b3sa3-api.onrender.com/
```

### 2. 📊 Informações do Modelo
```bash
curl https://b3sa3-api.onrender.com/info
```

### 3. 🔮 Previsão Automática (RECOMENDADO)

**O jeito mais fácil de usar a API!** Apenas informe o ticker:

```bash
curl -X POST https://b3sa3-api.onrender.com/predict/auto \
  -H "Content-Type: application/json" \
  -d '{"ticker": "B3SA3.SA"}'
```

**Outros exemplos:**
```bash
# Petrobras
curl -X POST https://b3sa3-api.onrender.com/predict/auto \
  -H "Content-Type: application/json" \
  -d '{"ticker": "PETR4.SA"}'

# Vale
curl -X POST https://b3sa3-api.onrender.com/predict/auto \
  -H "Content-Type: application/json" \
  -d '{"ticker": "VALE3.SA"}'

# Itaú
curl -X POST https://b3sa3-api.onrender.com/predict/auto \
  -H "Content-Type: application/json" \
  -d '{"ticker": "ITUB4.SA"}'
```

**Resposta:**
```json
{
  "preco_previsto": 12.85,
  "confianca": "alta",
  "mensagem": "Previsão para B3SA3.SA (B3 S.A. - Brasil, Bolsa, Balcão) gerada com sucesso. Modelo MAPE 1.53%. Dados: 2025-11-19 [ID: abc123]"
}
```

### 4. 🔮 Previsão com Dados Manuais

Se você já tem os dados OHLCV, pode enviá-los diretamente:

```bash
curl -X POST https://b3sa3-api.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{
    "dados": [
      [12.50, 12.70, 12.45, 12.65, 1500000],
      [12.65, 12.85, 12.60, 12.80, 1600000],
      ... (58 dias adicionais)
    ]
  }'
```

**Formato dos dados:**
- Cada linha = 1 dia
- 5 valores por dia: `[Open, High, Low, Close, Volume]`
- Total: 60 dias (os mais recentes)

---

## 📱 Python

### Usando `requests`

```python
import requests

# Previsão automática
url = "https://b3sa3-api.onrender.com/predict/auto"
payload = {"ticker": "B3SA3.SA"}
response = requests.post(url, json=payload)

print(response.json())
# {'preco_previsto': 12.85, 'confianca': 'alta', 'mensagem': '...'}
```

### Script Completo

```python
import requests
from datetime import datetime

def prever_preco(ticker: str) -> dict:
    """Faz previsão de preço para um ticker."""
    url = "https://b3sa3-api.onrender.com/predict/auto"
    
    try:
        response = requests.post(url, json={"ticker": ticker}, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"erro": str(e)}

# Usar
if __name__ == "__main__":
    tickers = ["B3SA3.SA", "PETR4.SA", "VALE3.SA"]
    
    print(f"🔮 Previsões - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
    
    for ticker in tickers:
        resultado = prever_preco(ticker)
        
        if "erro" in resultado:
            print(f"❌ {ticker}: {resultado['erro']}")
        else:
            preco = resultado['preco_previsto']
            print(f"✅ {ticker}: R$ {preco:.2f}")
```

---

## 🌐 JavaScript/Node.js

### Usando `fetch`

```javascript
// Previsão automática
const url = "https://b3sa3-api.onrender.com/predict/auto";
const payload = { ticker: "B3SA3.SA" };

fetch(url, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(payload)
})
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error("Erro:", error));
```

### Com `axios`

```javascript
const axios = require('axios');

async function preverPreco(ticker) {
  try {
    const response = await axios.post(
      'https://b3sa3-api.onrender.com/predict/auto',
      { ticker: ticker }
    );
    
    return response.data;
  } catch (error) {
    console.error(`Erro: ${error.message}`);
    return null;
  }
}

// Usar
preverPreco("B3SA3.SA").then(resultado => {
  console.log(`Previsão: R$ ${resultado.preco_previsto}`);
});
```

---

## 🧪 Testando Localmente

### 1. Verificar se API está online
```bash
curl https://b3sa3-api.onrender.com/health
```

### 2. Ver documentação interativa
Abra no navegador:
```
https://b3sa3-api.onrender.com/docs
```

### 3. Ver métricas do modelo
```bash
curl https://b3sa3-api.onrender.com/metrics
```

---

## ⚠️ Notas Importantes

### Tickers Brasileiros
- **Sempre adicione `.SA`** ao final (sufixo do Yahoo Finance para B3)
- Exemplos válidos: `B3SA3.SA`, `PETR4.SA`, `VALE3.SA`
- Se omitir `.SA`, a API adiciona automaticamente

### Horário de Dados
- API busca dados até o fechamento mais recente
- Mercado fecha às 18h (horário de Brasília)
- Dados de hoje só aparecem após fechamento

### Rate Limiting
- Render Free Tier pode ter limitações
- Para uso intensivo, considere instância paga

### Cold Start
- Primeiro request após inatividade pode demorar ~30s
- Requests subsequentes são instantâneos

---

## 🐛 Troubleshooting

### Erro 404 - Ticker não encontrado
```json
{"detail": "Ticker 'INVALID' não encontrado ou sem dados disponíveis"}
```
**Solução:** Verificar se ticker existe no Yahoo Finance

### Erro 400 - Dados insuficientes
```json
{"detail": "Dados insuficientes para 'TICKER'. Necessário: 60 dias, Disponível: 45 dias"}
```
**Solução:** Ticker muito novo ou pouco negociado. Usar outro ativo.

### Erro 503 - Serviço indisponível
```json
{"detail": "Modelo não está carregado. Aguarde a inicialização da API."}
```
**Solução:** API ainda está iniciando (cold start). Aguardar 30s e tentar novamente.

---

## 📚 Documentação Completa

- **Guia de Deploy:** `docs/DEPLOY_RENDER.md`
- **API Local:** `docs/FASE_7_GUIA.md`
- **Documentação Técnica:** `DOCUMENTACAO_TECNICA.md`

---

## 🤝 Suporte

Problemas? Abra uma issue no GitHub:
https://github.com/ArgusPortal/PredictFinance/issues
