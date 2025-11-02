# 📘 Guia de Execução - Fase 6: Construção da API com FastAPI

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Pré-requisitos](#pré-requisitos)
3. [Objetivos da Fase](#objetivos-da-fase)
4. [Estrutura de Arquivos](#estrutura-de-arquivos)
5. [Execução Passo a Passo](#execução-passo-a-passo)
6. [Saídas Esperadas](#saídas-esperadas)
7. [Testes da API](#testes-da-api)
8. [Conceitos Técnicos](#conceitos-técnicos)
9. [Troubleshooting](#troubleshooting)
10. [Checklist de Conclusão](#checklist-de-conclusão)
11. [Referências](#referências)

---

## 🎯 Visão Geral

A **Fase 6** implementa uma API REST usando **FastAPI** para servir o modelo LSTM treinado e fazer previsões de preços da ação B3SA3.SA. Esta fase transforma o modelo em um serviço web acessível via HTTP.

**Duração Estimada**: 1-2 horas  
**Complexidade**: Intermediária  
**Tecnologias**: FastAPI, Uvicorn, Pydantic, TensorFlow, NumPy

---

## ✅ Pré-requisitos

### Fases Anteriores

- ✅ Fase 1: Coleta de dados concluída
- ✅ Fase 2: Preparação de dados concluída
- ✅ Fase 3: Arquitetura do modelo construída
- ✅ Fase 4: Modelo treinado e avaliado
- ✅ Fase 5: Modelo e scaler salvos

### Artefatos Necessários

```
models/
├── lstm_model_best.h5    # Modelo treinado (0.39 MB)
└── scaler.pkl             # Scaler MinMaxScaler (0.86 KB)
```

### Dependências

Já instaladas no ambiente virtual:

```
fastapi==0.109.2
uvicorn[standard]==0.27.1
pydantic==2.x
tensorflow==2.15.1
numpy==1.24.4
joblib==1.5.2
```

---

## 🎯 Objetivos da Fase

1. ✅ Criar aplicação FastAPI
2. ✅ Implementar carregamento de modelo no startup
3. ✅ Definir esquemas Pydantic para validação
4. ✅ Implementar endpoint de previsão (POST /predict)
5. ✅ Implementar endpoints auxiliares (health, info, metrics)
6. ✅ Gerar documentação automática (Swagger/ReDoc)
7. ✅ Testar API localmente
8. ✅ Documentar uso da API

---

## 📁 Estrutura de Arquivos

### Arquivos Criados

```
api/
├── __init__.py              # Inicialização do módulo
├── main.py                  # Aplicação FastAPI principal
├── schemas.py               # Modelos Pydantic (validação)
├── test_api.py              # Suite de testes completa
├── quick_test.py            # Teste rápido
└── README.md                # Documentação da API

run_api.py                   # Script facilitador de execução

docs/api/
└── RELATORIO_TESTES_FASE6.md  # Relatório de testes
```

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────┐
│             Cliente HTTP                         │
│  (Browser, cURL, Python, JavaScript, etc.)      │
└────────────────┬────────────────────────────────┘
                 │ HTTP Request
                 ▼
┌─────────────────────────────────────────────────┐
│           FastAPI Application                    │
│  ┌───────────────────────────────────────────┐  │
│  │  Routers & Endpoints                      │  │
│  │  - GET  /       (Health Check)            │  │
│  │  - GET  /info   (Model Info)              │  │
│  │  - POST /predict (Make Prediction)        │  │
│  └───────────────┬───────────────────────────┘  │
│                  │                               │
│  ┌───────────────▼───────────────────────────┐  │
│  │  Pydantic Validation                      │  │
│  │  - PrevisaoInput (60 prices)              │  │
│  │  - PrevisaoOutput (predicted price)       │  │
│  └───────────────┬───────────────────────────┘  │
│                  │                               │
│  ┌───────────────▼───────────────────────────┐  │
│  │  Prediction Pipeline                      │  │
│  │  1. Validate input (60 prices)            │  │
│  │  2. Normalize with scaler                 │  │
│  │  3. Reshape for LSTM (1, 60, 5)           │  │
│  │  4. Model prediction                      │  │
│  │  5. Denormalize output                    │  │
│  │  6. Format response                       │  │
│  └───────────────┬───────────────────────────┘  │
└──────────────────┼──────────────────────────────┘
                   │
    ┌──────────────┴──────────────┐
    │                             │
    ▼                             ▼
┌────────────┐            ┌────────────┐
│   Model    │            │  Scaler    │
│ LSTM (.h5) │            │ (.pkl)     │
└────────────┘            └────────────┘
```

---

## 🚀 Execução Passo a Passo

### Passo 1: Verificar Artefatos

Certifique-se de que os artefatos do modelo existem:

```bash
# A partir do diretório raiz do projeto
ls -lh models/

# Saída esperada:
# lstm_model_best.h5     (0.39 MB)
# scaler.pkl             (0.86 KB)
# model_architecture.json
```

### Passo 2: Ativar Ambiente Virtual

```bash
# Windows (Git Bash)
source .venv/Scripts/activate

# Windows (CMD)
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### Passo 3: Iniciar a API

#### Opção A: Script Facilitador

```bash
python run_api.py
```

#### Opção B: Uvicorn Direto

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

#### Opção C: Modo Desenvolvimento (com auto-reload)

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Passo 4: Verificar Inicialização

Você deverá ver a seguinte saída:

```
============================================================
   API de Previsão B3SA3.SA - LSTM
============================================================

🚀 Iniciando servidor de desenvolvimento...

INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
INFO:     Waiting for application startup.

🚀 Iniciando API...
📂 Carregando artefatos do modelo...
   └─ Carregando modelo: C:\...\models\lstm_model_best.h5
   ✅ Modelo carregado com sucesso!
   └─ Carregando scaler: C:\...\models\scaler.pkl
   ✅ Scaler carregado com sucesso!
✅ API pronta para receber requisições!

INFO:     Application startup complete.
```

**Tempo esperado de inicialização**: ~3 segundos

---

## 📤 Saídas Esperadas

### 1. API Rodando

- **URL**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 2. Endpoints Disponíveis

#### GET / (Health Check)

**Requisição**:
```bash
curl http://localhost:8000/
```

**Resposta** (HTTP 200):
```json
{
  "status": "ativo",
  "mensagem": "API de previsão B3SA3.SA operacional",
  "versao": "1.0.0",
  "modelo_carregado": true
}
```

#### GET /info (Informações do Modelo)

**Requisição**:
```bash
curl http://localhost:8000/info
```

**Resposta** (HTTP 200):
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

#### GET /metrics (Métricas Detalhadas)

**Requisição**:
```bash
curl http://localhost:8000/metrics
```

**Resposta** (HTTP 200):
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
  }
}
```

#### POST /predict (Fazer Previsão)

**Requisição**:
```bash
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

**Resposta** (HTTP 200):
```json
{
  "preco_previsto": 11.52,
  "confianca": "alta",
  "mensagem": "Previsão gerada com sucesso. Modelo com MAPE de 1.53% no teste."
}
```

---

## 🧪 Testes da API

### Teste Manual Rápido

Abra o navegador em:

```
http://localhost:8000/docs
```

Use a interface Swagger UI para:
1. Testar endpoint GET /
2. Testar endpoint GET /info
3. Testar endpoint POST /predict com dados de exemplo

### Teste Automatizado

Em outro terminal (mantendo a API rodando):

```bash
# Ativar ambiente
source .venv/Scripts/activate

# Executar suite de testes
python api/test_api.py
```

**Saída esperada**:

```
================================================================================
                        🧪 SUITE DE TESTES DA API
================================================================================

📍 API URL: http://localhost:8000
📅 Data: 02/11/2025

🔍 Verificando se a API está rodando...
✅ API está respondendo!

============================================================
1️⃣  Testando Health Check (GET /)
============================================================
Status Code: 200
Resposta:
{
  "status": "ativo",
  "mensagem": "API de previsão B3SA3.SA operacional",
  "versao": "1.0.0",
  "modelo_carregado": true
}
✅ Health check passou!

[... demais testes ...]

================================================================================
                          ✅ TODOS OS TESTES PASSARAM!
================================================================================

📖 Documentação interativa disponível em: http://localhost:8000/docs
📖 Documentação ReDoc disponível em: http://localhost:8000/redoc
```

### Teste com Python

Criar arquivo `test_manual.py`:

```python
import requests

# Teste 1: Health check
response = requests.get("http://localhost:8000/")
print("Health:", response.json())

# Teste 2: Fazer previsão
prices = [12.5 + i * 0.05 for i in range(60)]  # 60 preços simulados
response = requests.post(
    "http://localhost:8000/predict",
    json={"prices": prices}
)
print("Previsão:", response.json())
```

Executar:
```bash
python test_manual.py
```

---

## 📚 Conceitos Técnicos

### 1. FastAPI

**O que é?**
Framework web moderno para construir APIs com Python 3.7+, baseado em padrões como OpenAPI e JSON Schema.

**Por que FastAPI?**
- ⚡ Alta performance (comparável a NodeJS e Go)
- 🔒 Validação automática de dados
- 📖 Documentação automática (Swagger/ReDoc)
- 🎯 Type hints nativos do Python
- ⚙️ Suporte assíncrono nativo

### 2. Pydantic

**O que é?**
Biblioteca para validação de dados usando type hints do Python.

**Como funciona?**
```python
class PrevisaoInput(BaseModel):
    prices: List[float] = Field(min_length=60, max_length=60)
    
    @field_validator('prices')
    @classmethod
    def validar_precos(cls, v: List[float]) -> List[float]:
        if any(p <= 0 for p in v):
            raise ValueError('Preços devem ser positivos')
        return v
```

**Benefícios**:
- ✅ Validação automática
- ✅ Mensagens de erro claras
- ✅ Conversão automática de tipos
- ✅ Documentação automática

### 3. Ciclo de Vida da API (Lifespan)

**Conceito**:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: executado uma vez ao iniciar
    global model, scaler
    model = load_model("modelo.h5")
    scaler = joblib.load("scaler.pkl")
    
    yield  # API rodando
    
    # Shutdown: executado ao encerrar
    model = None
    scaler = None
```

**Vantagens**:
- 🚀 Modelo carregado uma vez (não a cada requisição)
- 💾 Economia de memória e tempo
- 🔄 Gerenciamento limpo de recursos

### 4. Pipeline de Predição

**Fluxo**:

```
Input (60 preços)
    ↓
Validação Pydantic (quantidade, valores positivos)
    ↓
Conversão para NumPy array (60, 1)
    ↓
Normalização com scaler [0, 1]
    ↓
Reshape para formato LSTM (1, 60, 5)
    ↓
Predição com modelo LSTM
    ↓
Desnormalização (escala original)
    ↓
Formatação da resposta JSON
    ↓
Output (preço previsto)
```

### 5. Códigos HTTP

| Código | Significado | Quando Usar |
|--------|-------------|-------------|
| 200 OK | Sucesso | Previsão gerada com sucesso |
| 422 Unprocessable Entity | Erro de validação | Entrada inválida (não 60 preços, valores negativos) |
| 500 Internal Server Error | Erro no servidor | Falha ao processar predição |
| 503 Service Unavailable | Serviço indisponível | Modelo não carregado |

---

## 🔧 Troubleshooting

### Problema 1: Erro "Address already in use"

**Sintoma**:
```
ERROR:    [Errno 48] Address already in use
```

**Solução**:
```bash
# Encontrar processo na porta 8000
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Matar processo
kill <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows

# Ou usar porta diferente
uvicorn api.main:app --port 8001
```

### Problema 2: Modelo não encontrado

**Sintoma**:
```
FileNotFoundError: Modelo não encontrado: models/lstm_model_best.h5
```

**Solução**:
```bash
# Verificar se arquivos existem
ls models/

# Re-executar Fase 4 se necessário
python src/model_training.py
```

### Problema 3: Erro de validação Pydantic

**Sintoma**:
```json
{
  "detail": [
    {
      "type": "value_error",
      "msg": "É necessário fornecer exatamente 60 preços"
    }
  ]
}
```

**Solução**:
- Certifique-se de enviar **exatamente 60 preços**
- Todos os valores devem ser **positivos** (> 0)
- Formato deve ser lista de floats

### Problema 4: ImportError tensorflow

**Sintoma**:
```
ImportError: No module named 'tensorflow'
```

**Solução**:
```bash
# Ativar ambiente virtual
source .venv/Scripts/activate

# Reinstalar tensorflow se necessário
pip install tensorflow==2.15.1
```

### Problema 5: Warnings do TensorFlow

**Sintoma**:
```
WARNING:tensorflow:From ...: The name tf.losses.sparse_softmax_cross_entropy is deprecated
```

**Solução**:
- ⚠️ **Warnings normais** - não afetam funcionalidade
- Podem ser ignorados
- Para suprimir: `export TF_CPP_MIN_LOG_LEVEL=2`

---

## ✅ Checklist de Conclusão

Marque conforme completar:

### Implementação

- [ ] API FastAPI criada (`api/main.py`)
- [ ] Esquemas Pydantic definidos (`api/schemas.py`)
- [ ] Endpoint GET / implementado
- [ ] Endpoint GET /health implementado
- [ ] Endpoint GET /info implementado
- [ ] Endpoint GET /metrics implementado
- [ ] Endpoint POST /predict implementado
- [ ] Modelo carregado no startup
- [ ] Scaler carregado no startup
- [ ] Validações Pydantic funcionando

### Testes

- [ ] API iniciada com sucesso
- [ ] Health check respondendo (GET /)
- [ ] Info do modelo respondendo (GET /info)
- [ ] Métricas respondendo (GET /metrics)
- [ ] Previsão com dados válidos funcionando
- [ ] Validação de quantidade incorreta funcionando
- [ ] Validação de valores negativos funcionando
- [ ] Documentação Swagger acessível (/docs)

### Documentação

- [ ] README.md da API criado
- [ ] Exemplos de uso documentados
- [ ] Códigos de erro documentados
- [ ] Formato de entrada documentado
- [ ] Relatório de testes criado

### Verificação Final

Execute:

```bash
# 1. Iniciar API
uvicorn api.main:app --host 0.0.0.0 --port 8000

# 2. Em outro terminal, executar testes
python api/test_api.py

# 3. Verificar documentação
# Abrir http://localhost:8000/docs no navegador
```

**Critérios de Sucesso**:
- ✅ Todos os 8 testes passaram
- ✅ Documentação Swagger acessível
- ✅ Previsões retornando valores razoáveis (R$ 10-15)
- ✅ Sem erros críticos (warnings OK)

---

## 📖 Referências

### Documentação Oficial

- **FastAPI**: https://fastapi.tiangolo.com/
- **Pydantic**: https://docs.pydantic.dev/
- **Uvicorn**: https://www.uvicorn.org/
- **TensorFlow**: https://www.tensorflow.org/api_docs/python/tf/keras

### Tutoriais

- [FastAPI Tutorial - First Steps](https://fastapi.tiangolo.com/tutorial/first-steps/)
- [Pydantic Models](https://fastapi.tiangolo.com/tutorial/body/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

### Exemplos de Código

Ver arquivos do projeto:
- `api/main.py` - Aplicação completa
- `api/schemas.py` - Modelos Pydantic
- `api/test_api.py` - Suite de testes
- `api/README.md` - Documentação completa

---

## 🎯 Próximos Passos

Após concluir a Fase 6:

### Fase 7: Deploy da API
- Criar Dockerfile
- Deploy em Render/Railway
- Configurar variáveis de ambiente
- Testar API em produção

### Fase 8: Monitoramento e Finalização
- Implementar logging estruturado
- Dashboard de monitoramento
- Vídeo explicativo
- Documentação final

---

**Elaborado por**: Sistema PredictFinance  
**Data**: 02/11/2025  
**Versão**: 1.0.0  
**Status**: ✅ Fase 6 Concluída
