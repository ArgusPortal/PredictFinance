# ============================================
# Especificações Técnicas - PredictFinance
# Modelo LSTM para Previsão de Ações B3SA3.SA
# ============================================

## 1. CONTEXTO DO PROJETO

### 1.1 Objetivo Geral
Desenvolver um sistema completo de previsão de preços de fechamento diário das ações da B3 S.A. (B3SA3.SA) utilizando redes neurais LSTM (Long Short-Term Memory), desde a coleta de dados até o deploy de uma API REST em produção com monitoramento contínuo.

### 1.2 Justificativa
O preço de fechamento diário representa o consenso de mercado sobre o valor da ação ao final do pregão, sendo a métrica mais relevante para análise de tendências e tomada de decisão em investimentos. Modelos LSTM demonstram superior capacidade de capturar dependências temporais de longo prazo em séries temporais financeiras, conforme documentado na literatura acadêmica (arXiv, IEEE).

### 1.3 Ativo Alvo
- **Ticker**: B3SA3.SA (Yahoo Finance)
- **Empresa**: B3 S.A. - Brasil, Bolsa, Balcão
- **Mercado**: Bolsa de Valores de São Paulo (B3)
- **Tipo**: Ação Ordinária

---

## 2. ARQUITETURA DO SISTEMA

### 2.1 Visão Geral
```
┌─────────────────┐
│  Yahoo Finance  │
│   (yfinance)    │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Data Collection │ ──> data/raw/
│   & Cleaning    │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Data Preparation│ ──> data/processed/ + scaler
│   (LSTM Ready)  │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  LSTM Training  │ ──> models/
│   & Validation  │
└────────┬────────┘
         │
         v
┌─────────────────┐
│   Evaluation    │ ──> docs/evaluation/
│   & Metrics     │
└────────┬────────┘
         │
         v
┌─────────────────┐
│   FastAPI API   │ ──> Production
│   + Monitoring  │
└─────────────────┘
```

### 2.2 Componentes Principais

#### 2.2.1 Módulo de Coleta de Dados
- **Responsabilidade**: Obter dados históricos da B3SA3.SA
- **Fonte**: Yahoo Finance API via biblioteca yfinance
- **Período**: Mínimo de 5 anos de dados históricos
- **Frequência**: Dados diários (OHLCV - Open, High, Low, Close, Volume)
- **Saída**: `data/raw/b3sa3_historical.csv`

#### 2.2.2 Módulo de Preparação de Dados
- **Responsabilidade**: Transformar dados brutos em formato adequado para LSTM
- **Processos**:
  - Normalização (MinMaxScaler entre 0 e 1)
  - Criação de sequências temporais (janelas deslizantes)
  - Divisão treino/validação/teste (70%/15%/15%)
- **Saída**: 
  - `data/processed/X_train.npy`, `y_train.npy`
  - `data/processed/X_val.npy`, `y_val.npy`
  - `data/processed/X_test.npy`, `y_test.npy`
  - `models/scaler.pkl`

#### 2.2.3 Módulo de Modelagem LSTM
- **Responsabilidade**: Construir, treinar e salvar modelo LSTM
- **Arquitetura Proposta**:
  ```
  Input Layer (timesteps, features)
      ↓
  LSTM Layer 1 (128 units, return_sequences=True)
      ↓
  Dropout (0.2)
      ↓
  LSTM Layer 2 (64 units, return_sequences=True)
      ↓
  Dropout (0.2)
      ↓
  LSTM Layer 3 (32 units)
      ↓
  Dropout (0.2)
      ↓
  Dense Layer (1 unit) - Preço previsto
  ```
- **Hiperparâmetros Iniciais**:
  - Timesteps: 60 dias
  - Batch size: 32
  - Epochs: 100 (com early stopping)
  - Optimizer: Adam (learning_rate=0.001)
  - Loss: Mean Squared Error (MSE)
- **Saída**: `models/lstm_model.h5` ou `models/lstm_model/`

#### 2.2.4 Módulo de Avaliação
- **Responsabilidade**: Avaliar desempenho do modelo
- **Métricas**:
  - RMSE (Root Mean Square Error)
  - MAE (Mean Absolute Error)
  - MAPE (Mean Absolute Percentage Error)
  - R² Score
- **Visualizações**:
  - Gráfico Real vs. Previsto
  - Análise de Resíduos
  - Histórico de Loss durante treinamento
- **Saída**: `docs/evaluation/metrics.json`, gráficos PNG

#### 2.2.5 API FastAPI
- **Responsabilidade**: Disponibilizar previsões via REST API
- **Endpoints**:
  - `GET /` - Health check
  - `GET /info` - Informações do modelo
  - `POST /predict` - Realizar previsão
  - `GET /metrics` - Métricas do modelo
- **Formato de Entrada**: JSON com sequência de preços
- **Formato de Saída**: JSON com previsão e intervalo de confiança

---

## 3. ESPECIFICAÇÕES TÉCNICAS DETALHADAS

### 3.1 Fase 1: Coleta e Limpeza de Dados

#### 3.1.1 Fonte de Dados
- **API**: Yahoo Finance
- **Biblioteca**: yfinance v0.2.32+
- **Ticker**: B3SA3.SA

#### 3.1.2 Período de Dados
- **Início**: 5 anos antes da data atual
- **Fim**: Data mais recente disponível
- **Intervalo**: Diário (1d)

#### 3.1.3 Campos Coletados
1. **Date**: Data do pregão (índice)
2. **Open**: Preço de abertura
3. **High**: Preço máximo
4. **Low**: Preço mínimo
5. **Close**: Preço de fechamento (variável alvo)
6. **Volume**: Volume negociado
7. **Adj Close**: Preço de fechamento ajustado

#### 3.1.4 Tratamento de Dados
- **Valores Ausentes**:
  - Identificar dias sem pregão
  - Forward fill para preencher gaps curtos (máx. 3 dias)
  - Remover períodos com ausências prolongadas
- **Outliers**:
  - Detectar usando IQR (Interquartile Range)
  - Limitar a 3 desvios padrão da média
  - Documentar outliers removidos
- **Validação**:
  - Verificar monotonia crescente de datas
  - Garantir valores positivos para preços e volume
  - Verificar consistência: Low ≤ Open, Close ≤ High

#### 3.1.5 Análise Exploratória
- Estatísticas descritivas
- Gráfico de série temporal
- Decomposição (Tendência, Sazonalidade, Resíduo)
- Teste de estacionariedade (ADF Test)
- Matriz de correlação entre features

#### 3.1.6 Saída
- **Arquivo**: `data/raw/b3sa3_historical.csv`
- **Formato**: CSV com cabeçalho
- **Registro**: `docs/data_collection_log.json` com metadados

---

### 3.2 Fase 2: Preparação dos Dados para LSTM

#### 3.2.1 Normalização
- **Método**: MinMaxScaler do scikit-learn
- **Range**: [0, 1]
- **Aplicação**: Todas as features numéricas
- **Persistência**: Salvar scaler em `models/scaler.pkl` para uso em produção

#### 3.2.2 Engenharia de Features
- **Features Básicas**: Open, High, Low, Close, Volume
- **Features Derivadas** (opcional):
  - Retorno diário: (Close_t - Close_{t-1}) / Close_{t-1}
  - Média móvel: MA_7, MA_21
  - Volatilidade: Desvio padrão móvel

#### 3.2.3 Criação de Sequências
- **Método**: Janela deslizante (sliding window)
- **Tamanho da Janela (timesteps)**: 60 dias
- **Estrutura**:
  - X: Sequência de 60 dias consecutivos (features)
  - y: Preço de fechamento do dia seguinte (target)
- **Exemplo**:
  ```
  X[0] = dados[0:60]   → y[0] = dados[60]['Close']
  X[1] = dados[1:61]   → y[1] = dados[61]['Close']
  ...
  ```

#### 3.2.4 Divisão dos Dados
- **Treino**: 70% (primeiros dados cronologicamente)
- **Validação**: 15% (dados intermediários)
- **Teste**: 15% (dados mais recentes)
- **Importante**: Divisão temporal, não aleatória, para evitar data leakage

#### 3.2.5 Formato de Saída
- **Arrays NumPy**:
  - `X_train.shape = (n_samples_train, 60, n_features)`
  - `y_train.shape = (n_samples_train, 1)`
  - Similar para validação e teste
- **Salvamento**: Arquivos `.npy` em `data/processed/`

---

### 3.3 Fase 3: Construção e Treinamento do Modelo LSTM

#### 3.3.1 Arquitetura da Rede
```python
Model: "lstm_b3sa3_predictor"
_________________________________________________________________
Layer (type)                 Output Shape              Param #   
=================================================================
input (InputLayer)           (None, 60, n_features)    0         
_________________________________________________________________
lstm_1 (LSTM)                (None, 60, 128)           ~68k      
_________________________________________________________________
dropout_1 (Dropout)          (None, 60, 128)           0         
_________________________________________________________________
lstm_2 (LSTM)                (None, 60, 64)            ~49k      
_________________________________________________________________
dropout_2 (Dropout)          (None, 60, 64)            0         
_________________________________________________________________
lstm_3 (LSTM)                (None, 32)                ~12k      
_________________________________________________________________
dropout_3 (Dropout)          (None, 32)                0         
_________________________________________________________________
dense (Dense)                (None, 1)                 33        
=================================================================
Total params: ~130k
Trainable params: ~130k
```

#### 3.3.2 Configuração de Treinamento
- **Optimizer**: Adam
  - Learning rate: 0.001 (com decay opcional)
- **Loss Function**: Mean Squared Error (MSE)
- **Metrics**: MAE, MAPE
- **Batch Size**: 32
- **Epochs**: 100 (máximo)

#### 3.3.3 Callbacks
1. **EarlyStopping**:
   - Monitor: `val_loss`
   - Patience: 10 epochs
   - Restore best weights: True
   
2. **ModelCheckpoint**:
   - Salvar melhor modelo baseado em `val_loss`
   - Filepath: `models/best_lstm_model.h5`
   
3. **ReduceLROnPlateau**:
   - Monitor: `val_loss`
   - Factor: 0.5
   - Patience: 5
   
4. **TensorBoard** (opcional):
   - Log dir: `logs/tensorboard/`

#### 3.3.4 Validação
- Avaliar em conjunto de validação a cada epoch
- Evitar overfitting através de dropout e early stopping
- Monitorar convergência através de gráficos de loss

#### 3.3.5 Saída
- **Modelo Final**: `models/lstm_model.h5` ou SavedModel format
- **Histórico**: `models/training_history.json`
- **Gráficos**: `docs/training/loss_curves.png`

---

### 3.4 Fase 4: Avaliação de Desempenho

#### 3.4.1 Métricas de Avaliação

**RMSE (Root Mean Square Error)**
```
RMSE = √(Σ(y_real - y_pred)² / n)
```
- Penaliza erros grandes
- Unidade: mesma do preço (BRL)

**MAE (Mean Absolute Error)**
```
MAE = Σ|y_real - y_pred| / n
```
- Mais robusto a outliers
- Interpretação direta

**MAPE (Mean Absolute Percentage Error)**
```
MAPE = (100/n) × Σ|(y_real - y_pred) / y_real|
```
- Erro percentual
- Útil para comparação entre ativos

**R² Score**
```
R² = 1 - (SS_res / SS_tot)
```
- Proporção da variância explicada
- Range: (-∞, 1], ideal próximo de 1

#### 3.4.2 Análise de Resíduos
- **Resíduos**: erro = y_real - y_pred
- **Verificações**:
  - Distribuição normal (histograma, Q-Q plot)
  - Média próxima de zero
  - Homoscedasticidade (variância constante)
  - Ausência de autocorrelação (ACF plot)

#### 3.4.3 Visualizações
1. **Real vs. Previsto**:
   - Série temporal comparativa
   - Scatter plot com linha de identidade
   
2. **Análise de Erros**:
   - Distribuição de resíduos
   - Resíduos ao longo do tempo
   
3. **Performance Metrics**:
   - Tabela comparativa de métricas
   - Gráficos de barras

#### 3.4.4 Saída
- **Relatório JSON**: `docs/evaluation/metrics.json`
- **Gráficos**: `docs/evaluation/*.png`
- **Relatório Markdown**: `docs/evaluation/report.md`

---

### 3.5 Fase 5: Salvamento de Modelo e Scaler

#### 3.5.1 Persistência do Modelo
- **Formato 1**: HDF5 (`.h5`)
  ```python
  model.save('models/lstm_model.h5')
  ```
- **Formato 2**: SavedModel (pasta)
  ```python
  model.save('models/lstm_model/')
  ```

#### 3.5.2 Salvamento do Scaler
```python
import joblib
joblib.dump(scaler, 'models/scaler.pkl')
```

#### 3.5.3 Metadados do Modelo
Criar arquivo `models/model_metadata.json`:
```json
{
  "model_name": "LSTM B3SA3 Predictor",
  "version": "1.0.0",
  "created_at": "2025-11-02T10:00:00Z",
  "training_data": {
    "start_date": "2020-11-02",
    "end_date": "2025-11-02",
    "n_samples": 1200
  },
  "architecture": {
    "layers": ["LSTM(128)", "LSTM(64)", "LSTM(32)", "Dense(1)"],
    "timesteps": 60,
    "features": 5
  },
  "performance": {
    "rmse": 0.52,
    "mae": 0.38,
    "mape": 2.1,
    "r2_score": 0.94
  }
}
```

#### 3.5.4 Versionamento
- Usar tags semânticas: `v1.0.0`, `v1.1.0`, etc.
- Manter histórico de modelos: `models/v1.0.0/`, `models/v1.1.0/`

---

### 3.6 Fase 6: Desenvolvimento da API com FastAPI

#### 3.6.1 Estrutura da API
```
api/
├── main.py           # Aplicação principal
├── predictor.py      # Lógica de predição
├── schemas.py        # Schemas Pydantic
├── config.py         # Configurações
└── utils.py          # Funções auxiliares
```

#### 3.6.2 Endpoints

**1. Health Check**
```
GET /
Response: {"status": "healthy", "timestamp": "..."}
```

**2. Informações do Modelo**
```
GET /info
Response: {
  "model_version": "1.0.0",
  "ticker": "B3SA3.SA",
  "metrics": {...},
  "last_training": "..."
}
```

**3. Previsão**
```
POST /predict
Request Body: {
  "sequence": [12.5, 12.7, 12.9, ...] # 60 valores
}
Response: {
  "predicted_price": 13.2,
  "confidence_interval": {
    "lower": 12.8,
    "upper": 13.6
  },
  "timestamp": "..."
}
```

**4. Métricas**
```
GET /metrics
Response: {
  "rmse": 0.52,
  "mae": 0.38,
  "mape": 2.1,
  "r2_score": 0.94
}
```

#### 3.6.3 Schemas Pydantic
```python
from pydantic import BaseModel, Field
from typing import List, Dict

class PredictionRequest(BaseModel):
    sequence: List[float] = Field(..., min_items=60, max_items=60)

class PredictionResponse(BaseModel):
    predicted_price: float
    confidence_interval: Dict[str, float]
    timestamp: str
```

#### 3.6.4 Carregamento do Modelo
```python
import tensorflow as tf
import joblib

# Carregar modelo e scaler no startup
model = tf.keras.models.load_model('models/lstm_model.h5')
scaler = joblib.load('models/scaler.pkl')
```

#### 3.6.5 CORS e Segurança
- Configurar CORS para acesso externo
- Rate limiting (opcional)
- Validação de entrada rigorosa

---

### 3.7 Fase 7: Deploy da API

#### 3.7.1 Containerização com Docker
**Dockerfile**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 3.7.2 Opções de Deploy Gratuito
1. **Render** (Recomendado)
   - Deploy automático via GitHub
   - 750h gratuitas/mês
   - HTTPS automático
   
2. **Railway**
   - $5 crédito mensal
   - Deploy simples
   
3. **Heroku** (Free tier limitado)
   - Integração com GitHub
   - CLI amigável

#### 3.7.3 Variáveis de Ambiente
```env
MODEL_PATH=/app/models/lstm_model.h5
SCALER_PATH=/app/models/scaler.pkl
LOG_LEVEL=INFO
```

#### 3.7.4 Testes Pré-Deploy
```bash
# Local
docker build -t predictfinance .
docker run -p 8000:8000 predictfinance

# Testar endpoints
curl http://localhost:8000/
curl http://localhost:8000/info
```

---

### 3.8 Fase 8: Monitoramento e Documentação Final

#### 3.8.1 Monitoramento
- **Logs**: Usar Loguru para logging estruturado
- **Métricas de API**:
  - Número de requisições
  - Tempo de resposta médio
  - Taxa de erros
- **Drift Detection** (futuro):
  - Monitorar mudança na distribuição de dados
  - Alertas para retreinamento

#### 3.8.2 Dashboard (Opcional)
- Usar Streamlit ou Plotly Dash
- Visualizar previsões vs. real
- Métricas de desempenho em tempo real

#### 3.8.3 Documentação Final
1. **README.md** completo
2. **API Documentation** (Swagger automático)
3. **Guia de Instalação**
4. **Guia de Contribuição**
5. **Changelog**

#### 3.8.4 Vídeo Explicativo
Conteúdo sugerido:
1. Introdução ao projeto (1 min)
2. Demonstração da coleta de dados (2 min)
3. Explicação da arquitetura LSTM (3 min)
4. Treinamento e métricas (2 min)
5. Uso da API (2 min)
6. Total: ~10 minutos

---

## 4. CRONOGRAMA ESTIMADO

| Fase | Descrição | Duração Estimada |
|------|-----------|------------------|
| 1 | Coleta e limpeza de dados | 1 dia |
| 2 | Preparação de dados | 1 dia |
| 3 | Construção e treinamento LSTM | 2 dias |
| 4 | Avaliação de desempenho | 1 dia |
| 5 | Salvamento de artefatos | 0.5 dia |
| 6 | Desenvolvimento da API | 1.5 dias |
| 7 | Deploy | 1 dia |
| 8 | Monitoramento e documentação | 1 dia |
| **Total** | | **~9 dias** |

---

## 5. CRITÉRIOS DE SUCESSO

### 5.1 Métricas Mínimas Aceitáveis
- **MAPE**: < 5%
- **R² Score**: > 0.85
- **Tempo de Resposta da API**: < 200ms

### 5.2 Requisitos Funcionais
- ✅ API rodando em produção 24/7
- ✅ Documentação completa e clara
- ✅ Código versionado no GitHub
- ✅ Testes unitários com cobertura > 70%

### 5.3 Requisitos Não-Funcionais
- ✅ Reprodutibilidade total do pipeline
- ✅ Modularidade do código
- ✅ Logs estruturados
- ✅ Tratamento de erros robusto

---

## 6. RISCOS E MITIGAÇÕES

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Dados insuficientes | Baixa | Alto | Validar disponibilidade antes de iniciar |
| Overfitting do modelo | Média | Médio | Dropout, early stopping, validação cruzada temporal |
| API instável | Baixa | Alto | Testes extensivos, health checks |
| Mudança de API do Yahoo | Baixa | Alto | Implementar fallback, cache de dados |

---

## 7. REFERÊNCIAS TÉCNICAS

1. **LSTM para Séries Temporais**:
   - Hochreiter & Schmidhuber (1997) - Long Short-Term Memory
   - arXiv:2505.05325v1 - Advanced Stock Market Prediction Using LSTM
   
2. **Frameworks e Bibliotecas**:
   - TensorFlow/Keras Documentation
   - FastAPI Documentation
   - yfinance GitHub Repository
   
3. **Boas Práticas**:
   - Google ML Guide - Time Series Forecasting
   - Towards Data Science - LSTM Stock Prediction

---

**Versão**: 1.0.0  
**Última Atualização**: 02/11/2025  
**Autor**: ArgusPortal
