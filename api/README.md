# API de Previsão B3SA3.SA - FastAPI

## 📋 Visão Geral

Esta API REST fornece previsões de preços de ações da B3 S.A. (B3SA3.SA) utilizando um modelo LSTM (Long Short-Term Memory) treinado.

## 🚀 Características

- ✅ **FastAPI** - Framework moderno e de alta performance
- ✅ **Validação Automática** - Pydantic para validação de dados
- ✅ **Documentação Interativa** - Swagger UI e ReDoc
- ✅ **Modelo LSTM** - Rede neural treinada com 1.246 dias de dados
- ✅ **Alta Precisão** - MAPE de 1.53% no conjunto de teste

## 📦 Instalação

As dependências já estão instaladas no ambiente virtual do projeto. Se necessário:

```bash
# Ativar ambiente virtual
source .venv/Scripts/activate  # Windows Git Bash
# ou
.venv\Scripts\activate  # Windows CMD

# Instalar dependências (se necessário)
pip install fastapi uvicorn[standard]
```

## 🏃 Como Executar

### Método 1: Diretamente com Python

```bash
# A partir do diretório raiz do projeto
python api/main.py
```

### Método 2: Com Uvicorn

```bash
# A partir do diretório raiz do projeto
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Método 3: Com Uvicorn (modo produção)

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

A API estará disponível em: **http://localhost:8000**

## 📖 Documentação Interativa

Após iniciar a API, acesse:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 Endpoints

### 1. Health Check

**GET /** ou **GET /health**

Verifica se a API está operacional.

**Resposta:**
```json
{
  "status": "ativo",
  "mensagem": "API de previsão B3SA3.SA operacional",
  "versao": "1.0.0",
  "modelo_carregado": true
}
```

### 2. Informações do Modelo

**GET /info**

Retorna informações detalhadas sobre o modelo LSTM.

**Resposta:**
```json
{
  "nome": "LSTM_B3SA3_Predictor",
  "arquitetura": "LSTM - 2 camadas (64 → 32 unidades) + Dropout (0.2)",
  "parametros": 30369,
  "metricas": {
    "RMSE": "R$ 0.26",
    "MAE": "R$ 0.20",
    "MAPE": "1.53%",
    "R2": "0.9351"
  },
  "window_size": 60,
  "features": ["Open", "High", "Low", "Close", "Volume"]
}
```

### 3. Métricas de Performance

**GET /metrics**

Retorna métricas detalhadas de performance do modelo.

**Resposta:**
```json
{
  "metricas_teste": {
    "RMSE": {
      "valor": "R$ 0.26",
      "descricao": "Raiz do Erro Quadrático Médio"
    },
    "MAE": {
      "valor": "R$ 0.20",
      "descricao": "Erro Absoluto Médio"
    },
    "MAPE": {
      "valor": "1.53%",
      "descricao": "Erro Percentual Absoluto Médio",
      "interpretacao": "EXCELENTE (< 2%)"
    },
    "R2": {
      "valor": "0.9351",
      "descricao": "Coeficiente de Determinação",
      "interpretacao": "Modelo explica 93.51% da variância"
    }
  },
  "parametros_modelo": {
    "window_size": 60,
    "num_features": 5,
    "camadas": "LSTM(64) + Dropout(0.2) + LSTM(32) + Dense(1)",
    "total_parametros": 30369
  },
  "dados_treinamento": {
    "periodo": "2020-11-03 a 2025-10-31",
    "total_dias": 1246,
    "sequencias_geradas": 1186,
    "divisao": {
      "treino": "70% (830 sequências)",
      "validacao": "15% (177 sequências)",
      "teste": "15% (179 sequências)"
    }
  }
}
```

### 4. Fazer Previsão

**POST /predict**

Gera previsão do próximo preço de fechamento.

**Requisição:**
```json
{
  "prices": [12.5, 12.6, 12.7, ..., 13.2]  // Exatamente 60 preços
}
```

**Validações:**
- ✅ Deve conter exatamente 60 preços
- ✅ Todos os preços devem ser positivos (> 0)
- ✅ Preços devem ser números válidos (float)

**Resposta de Sucesso (200):**
```json
{
  "preco_previsto": 13.45,
  "confianca": "alta",
  "mensagem": "Previsão gerada com sucesso. Modelo com MAPE de 1.53% no teste."
}
```

**Resposta de Erro (422):**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "prices"],
      "msg": "É necessário fornecer exatamente 60 preços. Recebidos: 30",
      "input": [...]
    }
  ]
}
```

## 🧪 Testes

Execute a suite de testes completa:

```bash
# A partir do diretório raiz do projeto
python api/test_api.py
```

### Testes Incluídos:

1. ✅ Health check (GET /)
2. ✅ Health check alternativo (GET /health)
3. ✅ Informações do modelo (GET /info)
4. ✅ Métricas (GET /metrics)
5. ✅ Previsão válida (POST /predict)
6. ✅ Validação de quantidade incorreta
7. ✅ Validação de valores negativos
8. ✅ Documentação Swagger acessível

## 📝 Exemplos de Uso

### Exemplo com cURL

```bash
# Health check
curl http://localhost:8000/

# Informações do modelo
curl http://localhost:8000/info

# Fazer previsão
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "prices": [12.5, 12.6, 12.7, 12.8, 12.9, 13.0, 13.1, 13.2, 13.3, 13.4,
               13.5, 13.6, 13.7, 13.8, 13.9, 14.0, 14.1, 14.2, 14.3, 14.4,
               14.5, 14.6, 14.7, 14.8, 14.9, 15.0, 14.9, 14.8, 14.7, 14.6,
               14.5, 14.4, 14.3, 14.2, 14.1, 14.0, 13.9, 13.8, 13.7, 13.6,
               13.5, 13.4, 13.3, 13.2, 13.1, 13.0, 12.9, 12.8, 12.7, 12.6,
               12.5, 12.4, 12.3, 12.2, 12.1, 12.0, 11.9, 11.8, 11.7, 11.6]
  }'
```

### Exemplo com Python (requests)

```python
import requests

# Fazer previsão
url = "http://localhost:8000/predict"
prices = [12.5 + i * 0.1 for i in range(60)]  # 60 preços simulados

response = requests.post(url, json={"prices": prices})
print(response.json())

# Saída:
# {
#   "preco_previsto": 13.45,
#   "confianca": "alta",
#   "mensagem": "Previsão gerada com sucesso. Modelo com MAPE de 1.53% no teste."
# }
```

### Exemplo com JavaScript (fetch)

```javascript
// Fazer previsão
const prices = Array.from({length: 60}, (_, i) => 12.5 + i * 0.1);

fetch('http://localhost:8000/predict', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ prices: prices })
})
.then(response => response.json())
.then(data => console.log(data));
```

## 🔧 Estrutura do Projeto

```
api/
├── __init__.py          # Inicialização do módulo
├── main.py              # Aplicação FastAPI principal
├── schemas.py           # Modelos Pydantic (validação)
├── test_api.py          # Suite de testes
└── README.md            # Esta documentação
```

## ⚙️ Configurações

### Variáveis de Ambiente (opcional)

Você pode criar um arquivo `.env` na raiz do projeto:

```env
API_HOST=0.0.0.0
API_PORT=8000
MODEL_PATH=models/lstm_model_best.h5
SCALER_PATH=models/scaler.pkl
```

### Parâmetros do Modelo

- **Window Size**: 60 dias
- **Features**: 5 (Open, High, Low, Close, Volume)
- **Arquitetura**: LSTM(64) → Dropout(0.2) → LSTM(32) → Dense(1)
- **Parâmetros Treináveis**: 30.369

## 📊 Performance

- **RMSE**: R$ 0.26
- **MAE**: R$ 0.20
- **MAPE**: 1.53% ⭐ (EXCELENTE)
- **R²**: 0.9351 (93.51% de explicação da variância)

## 🚨 Tratamento de Erros

A API retorna códigos HTTP apropriados:

- **200 OK**: Requisição bem-sucedida
- **422 Unprocessable Entity**: Erro de validação dos dados
- **500 Internal Server Error**: Erro no servidor
- **503 Service Unavailable**: Modelo não carregado

## 🔒 Segurança

Para produção, considere adicionar:

- Autenticação (API Key, OAuth2)
- Rate limiting
- HTTPS/TLS
- CORS configurado corretamente
- Logging de requisições

## 📈 Próximos Passos

- [ ] Deploy em serviço de nuvem (Fase 7)
- [ ] Adicionar autenticação
- [ ] Implementar cache de previsões
- [ ] Criar dashboard de monitoramento (Fase 8)
- [ ] Adicionar testes unitários

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique os logs da API
2. Teste os endpoints com o script `test_api.py`
3. Consulte a documentação Swagger em `/docs`

## 📄 Licença

Este projeto faz parte do sistema PredictFinance desenvolvido para previsão de preços de ações B3SA3.SA.

---

**Versão**: 1.0.0  
**Última Atualização**: 02/11/2025  
**Autor**: ArgusPortal
