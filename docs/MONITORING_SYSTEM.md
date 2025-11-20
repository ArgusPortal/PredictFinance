# 🔍 Sistema de Monitoramento de Performance em Produção

## 📋 Visão Geral

O sistema de monitoramento rastreia automaticamente todas as previsões realizadas pelo modelo e as compara com os valores reais do mercado, calculando métricas de performance e detectando degradação.

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUXO DE MONITORAMENTO                    │
└─────────────────────────────────────────────────────────────┘

1️⃣ REGISTRO AUTOMÁTICO
   ┌──────────────────────┐
   │  POST /predict/auto  │  Usuário faz previsão
   └──────────┬───────────┘
              │
              ▼
   ┌──────────────────────────────┐
   │ PerformanceMonitor.register  │  Registra previsão
   │  - prediction_value          │
   │  - timestamp                 │
   │  - request_id                │
   └──────────┬───────────────────┘
              │
              ▼
   ┌──────────────────────────────┐
   │ monitoring/                  │
   │   predictions_tracking.json  │  Armazena para validação
   └──────────────────────────────┘


2️⃣ VALIDAÇÃO (Manual ou Automática)
   ┌──────────────────────────────┐
   │ POST /monitoring/validate    │  Trigger de validação
   └──────────┬───────────────────┘
              │
              ▼
   ┌──────────────────────────────┐
   │ PerformanceMonitor.validate  │
   │  1. Busca previsões pending  │
   │  2. Download dados reais     │
   │     (yfinance)               │
   │  3. Calcula erros            │
   │  4. Atualiza tracking        │
   └──────────┬───────────────────┘
              │
              ▼
   ┌──────────────────────────────┐
   │ monitoring/                  │
   │   performance_metrics.json   │  Histórico de métricas
   └──────────────────────────────┘


3️⃣ ANÁLISE E DASHBOARD
   ┌──────────────────────────────┐
   │ GET /monitoring/performance  │  Streamlit consulta
   └──────────┬───────────────────┘
              │
              ▼
   ┌──────────────────────────────┐
   │ Dashboard Streamlit          │
   │  - Métricas: MAE, MAPE, RMSE │
   │  - Gráficos de tendência     │
   │  - Tabela de previsões       │
   │  - Alertas de degradação     │
   └──────────────────────────────┘
```

---

## 📡 Endpoints da API

### 1. POST /monitoring/register

Registra uma previsão para validação futura.

**Parâmetros:**
```json
{
  "prediction_value": 12.85,
  "ticker": "B3SA3.SA",
  "request_id": "abc123-def456"
}
```

**Resposta:**
```json
{
  "status": "success",
  "message": "Previsão registrada para monitoramento",
  "prediction_value": 12.85,
  "timestamp": "2025-11-20T14:30:00"
}
```

**Uso:** Chamado automaticamente pelo `/predict/auto`

---

### 2. GET /monitoring/performance

Retorna métricas de performance do modelo em produção.

**Parâmetros:**
- `ticker` (opcional): Símbolo da ação (default: B3SA3.SA)

**Resposta:**
```json
{
  "ticker": "B3SA3.SA",
  "timestamp": "2025-11-20T14:30:00",
  "summary": {
    "last_update": "2025-11-20T12:00:00",
    "current_mae": 0.25,
    "current_mape": 1.85,
    "total_predictions_validated": 45
  },
  "statistics": {
    "total_validated": 45,
    "total_pending": 12,
    "mae": 0.25,
    "mape": 1.85,
    "rmse": 0.31,
    "min_error_pct": 0.15,
    "max_error_pct": 4.20,
    "avg_predicted": 12.50,
    "avg_actual": 12.48
  },
  "daily_metrics": [
    {
      "timestamp": "2025-11-19T00:00:00",
      "window_days": 7,
      "mae": 0.23,
      "mape": 1.75,
      "rmse": 0.29,
      "total_validated": 40
    }
  ],
  "recent_predictions": [
    {
      "request_id": "abc123-def456",
      "timestamp": "2025-11-19T10:30:00",
      "predicted": 12.85,
      "actual": 12.80,
      "error_pct": 0.39,
      "validated": true
    }
  ]
}
```

---

### 3. POST /monitoring/validate

Executa validação de previsões pendentes.

**Parâmetros:**
```json
{
  "ticker": "B3SA3.SA",
  "days_back": 7
}
```

**Resposta:**
```json
{
  "status": "success",
  "ticker": "B3SA3.SA",
  "timestamp": "2025-11-20T14:30:00",
  "validation_result": {
    "validated": 8,
    "pending": 4
  },
  "degradation_detected": false,
  "message": "Validação concluída com sucesso"
}
```

**Uso:** Chamado manualmente ou via cron job

---

## 📊 Dashboard Streamlit

Acesse: **🔍 Monitoramento** no menu lateral

### Seções

#### 1. 📊 Resumo de Performance

**Métricas principais:**
- Previsões Validadas
- Previsões Pendentes
- MAPE Produção (com indicador de qualidade)
- MAE Produção

**Indicadores de qualidade:**
- < 2%: Excelente ✅
- 2-5%: Bom ✅
- > 5%: Requer atenção ⚠️

#### 2. 📈 Evolução de Performance

**3 Tabs:**

**Tab 1: MAPE ao Longo do Tempo**
- Gráfico de linha com MAPE diário
- Threshold de 5% em linha tracejada
- Análise de tendência automática

**Tab 2: MAE e RMSE**
- Gráfico comparativo de erros
- Evolução temporal das métricas

**Tab 3: Análise de Erros**
- Erro mínimo e máximo
- Preço médio previsto vs real
- Delta percentual

#### 3. 📋 Previsões Recentes

**Tabela interativa:**
- ID da previsão (8 caracteres)
- Data/Hora
- Valor Previsto (R$)
- Valor Real (R$)
- Erro (%)
- Status (✅ Validado / ⏳ Pendente)

**Filtros:**
- Todas / Validadas / Pendentes
- Limite de exibição (5-50)

#### 4. 🔄 Validação Manual

**Funcionalidades:**
- Slider para selecionar período (1-30 dias)
- Botão "Executar Validação"
- Resultado em tempo real
- Alerta de degradação

**Seção informativa:**
- Como funciona o monitoramento
- Métricas explicadas
- Thresholds de qualidade

---

## 🗂️ Estrutura de Dados

### predictions_tracking.json

```json
{
  "predictions": [
    {
      "request_id": "abc123-def456",
      "timestamp": "2025-11-20T10:30:00",
      "predicted_value": 12.85,
      "validated": false,
      "actual_value": null,
      "error": null
    },
    {
      "request_id": "xyz789-ghi012",
      "timestamp": "2025-11-19T15:20:00",
      "predicted_value": 12.70,
      "validated": true,
      "actual_value": 12.68,
      "error": 0.02,
      "error_pct": 0.16,
      "validation_date": "2025-11-20T08:00:00"
    }
  ]
}
```

### performance_metrics.json

```json
{
  "daily_metrics": [
    {
      "timestamp": "2025-11-20T00:00:00",
      "window_days": 7,
      "mae": 0.25,
      "mape": 1.85,
      "rmse": 0.31,
      "total_validated": 45,
      "min_error_pct": 0.15,
      "max_error_pct": 4.20
    }
  ],
  "summary": {
    "last_update": "2025-11-20T00:00:00",
    "current_mae": 0.25,
    "current_mape": 1.85,
    "total_predictions_validated": 45
  }
}
```

---

## 🔧 Configuração

### Classe PerformanceMonitor

```python
from src.performance_monitor import PerformanceMonitor

# Inicializar monitor
monitor = PerformanceMonitor(
    ticker="B3SA3.SA",
    window_days=7  # Janela móvel para métricas
)

# Registrar previsão
monitor.register_prediction(
    prediction_value=12.85,
    prediction_date="2025-11-20T10:30:00",
    request_id="abc123"
)

# Validar previsões
result = monitor.validate_predictions(days_back=7)

# Calcular métricas
metrics = monitor.calculate_metrics()

# Detectar degradação
degraded = monitor.detect_degradation(threshold_mape=5.0)
```

---

## ⚙️ Automação

### 1. GitHub Actions (Recomendado)

Criar `.github/workflows/monitoring_validation.yml`:

```yaml
name: Validação de Performance

on:
  schedule:
    - cron: '0 12 * * *'  # Diariamente às 12:00 UTC
  workflow_dispatch:  # Manual trigger

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Validar Previsões
        run: |
          python -c "
          from src.performance_monitor import PerformanceMonitor
          monitor = PerformanceMonitor()
          monitor.validate_predictions(days_back=7)
          "
      
      - name: Commit metrics
        run: |
          git config --global user.name 'github-actions'
          git config --global user.email 'actions@github.com'
          git add monitoring/*.json
          git commit -m 'chore: atualizar métricas de performance' || echo 'No changes'
          git push
```

### 2. Cron Job (Linux/Mac)

```bash
# Editar crontab
crontab -e

# Adicionar linha (diariamente às 12:00)
0 12 * * * cd /path/to/PredictFinance && python run_daily_monitoring.py
```

### 3. Task Scheduler (Windows)

```powershell
# Script: validate_performance.ps1
cd C:\path\to\PredictFinance
& python -c "from src.performance_monitor import PerformanceMonitor; m = PerformanceMonitor(); m.validate_predictions()"

# Agendar no Task Scheduler:
# - Trigger: Diariamente às 12:00
# - Action: powershell.exe -File validate_performance.ps1
```

---

## 📈 Métricas Explicadas

### MAE (Mean Absolute Error)

**Fórmula:**
```
MAE = (1/n) * Σ|y_real - y_previsto|
```

**Interpretação:**
- Erro médio em reais (R$)
- Métrica simples e intuitiva
- Mesmo peso para todos os erros

**Exemplo:**
- MAE = 0.25 → Erro médio de R$ 0,25 por previsão

---

### MAPE (Mean Absolute Percentage Error)

**Fórmula:**
```
MAPE = (100/n) * Σ|(y_real - y_previsto) / y_real|
```

**Interpretação:**
- Erro médio em percentual (%)
- Independente da escala
- Fácil comparação entre modelos

**Benchmark:**
- < 2%: Excelente ✅
- 2-5%: Bom ✅
- 5-10%: Razoável ⚠️
- > 10%: Ruim ❌

**Exemplo:**
- MAPE = 1.85% → Erro médio de 1,85% do valor real

---

### RMSE (Root Mean Squared Error)

**Fórmula:**
```
RMSE = √[(1/n) * Σ(y_real - y_previsto)²]
```

**Interpretação:**
- Penaliza erros grandes
- Sensível a outliers
- Mesma unidade que MAE (R$)

**Uso:**
- Detecta previsões muito ruins
- Complementa MAE

---

## 🚨 Detecção de Degradação

### Critérios

1. **MAPE > Threshold** (default: 5%)
   - Alerta quando erro médio ultrapassa limite
   - Threshold configurável

2. **Tendência de Piora**
   - Regressão linear do MAPE
   - Slope positivo = degradação

3. **Erro Máximo Elevado**
   - Outliers frequentes
   - Max error > 10%

### Ações Recomendadas

Quando degradação for detectada:

1. ✅ **Re-treinar o modelo** com dados recentes
2. ✅ **Verificar qualidade dos dados** de entrada
3. ✅ **Ajustar hiperparâmetros** se necessário
4. ✅ **Aumentar window_size** para mais contexto
5. ✅ **Adicionar features** relevantes

---

## 🔗 Integração com Produção

### Render.com

O sistema funciona automaticamente no Render:

1. **Registro**: Todas as previsões via `/predict/auto` são registradas
2. **Armazenamento**: JSON files em `monitoring/` (persist disk)
3. **Validação**: Via endpoint `/monitoring/validate` ou cron job externo

**Configuração no render.yaml:**

```yaml
services:
  - type: web
    name: predictfinance-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn api.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.10.5
    disk:
      name: monitoring-data
      mountPath: /opt/render/project/src/monitoring
      sizeGB: 1
```

### Streamlit Cloud

Dashboard de monitoramento disponível em:
**https://predictfinance.streamlit.app/** → 🔍 Monitoramento

---

## 📊 Casos de Uso

### 1. Monitoramento Passivo

```python
# API registra automaticamente
# Usuário visualiza dashboard no Streamlit
```

**Fluxo:**
1. Usuário faz previsão na página 🔮 Previsão
2. API registra automaticamente no sistema
3. Validação automática via cron (diária)
4. Dashboard atualizado em tempo real

---

### 2. Análise de Performance

```python
# Analista de ML verifica métricas
import requests

response = requests.get("http://localhost:8000/monitoring/performance")
data = response.json()

print(f"MAPE: {data['statistics']['mape']}%")
print(f"Total validadas: {data['statistics']['total_validated']}")
```

---

### 3. Alertas de Produção

```python
# Sistema de alerta automático
from src.performance_monitor import PerformanceMonitor

monitor = PerformanceMonitor()
monitor.validate_predictions()

if monitor.detect_degradation(threshold_mape=5.0):
    # Enviar alerta (email, Slack, PagerDuty)
    send_alert("ATENÇÃO: Modelo degradado! MAPE > 5%")
```

---

## 🧪 Testes

### Teste Local

```bash
# 1. Iniciar API
python run_api.py

# 2. Fazer previsão
curl -X POST http://localhost:8000/predict/auto \
  -H "Content-Type: application/json" \
  -d '{"ticker":"B3SA3.SA"}'

# 3. Verificar registro
curl http://localhost:8000/monitoring/performance

# 4. Validar (após dia seguinte)
curl -X POST http://localhost:8000/monitoring/validate

# 5. Ver dashboard
streamlit run app_streamlit.py
# Acessar: 🔍 Monitoramento
```

---

## 📝 Logs

### Estrutura de Logs

```
monitoring/
├── predictions_tracking.json  # Previsões aguardando validação
└── performance_metrics.json   # Histórico de métricas calculadas

logs/
├── predictions.log           # Log estruturado de previsões
└── metrics.log              # Log de métricas de API
```

### Exemplo de Log Entry

```json
{
  "timestamp": "2025-11-20T10:30:15.123Z",
  "request_id": "abc123-def456",
  "ticker": "B3SA3.SA",
  "prediction": 12.85,
  "processing_time_ms": 245,
  "data_source": "yahoo_finance",
  "model_version": "lstm_v1"
}
```

---

## ⚡ Performance

### Impacto no Endpoint

- **Overhead**: < 5ms por requisição
- **Storage**: ~100KB por 1000 previsões
- **Validação**: 2-5s por lote de 20 previsões

### Otimizações

1. **Registro assíncrono** (não bloqueia resposta)
2. **Validação em batch** (não individual)
3. **Cache de dados reais** (evita downloads repetidos)

---

## 🔒 Segurança

- ✅ Endpoints protegidos por mesma autenticação da API
- ✅ Validação de inputs (ticker, dates, thresholds)
- ✅ Rate limiting para evitar abuso
- ✅ Logs auditáveis para rastreabilidade

---

## 📚 Referências

- [Performance Monitoring Best Practices](https://ml-ops.org/content/mlops-principles)
- [Model Drift Detection](https://towardsdatascience.com/machine-learning-model-drift-9cc43ad530d6)
- [Production ML Systems](https://developers.google.com/machine-learning/guides/rules-of-ml)

---

## 🎯 Roadmap Futuro

- [ ] **Alertas automáticos** via email/Slack
- [ ] **Detecção de concept drift** avançada
- [ ] **A/B testing** de modelos
- [ ] **Integração com Prometheus/Grafana**
- [ ] **Análise de feature importance** em produção
- [ ] **Retraining automático** quando degradação detectada

---

## ✅ Checklist de Implementação

- [x] Endpoint `/monitoring/register`
- [x] Endpoint `/monitoring/performance`
- [x] Endpoint `/monitoring/validate`
- [x] Integração automática no `/predict/auto`
- [x] Dashboard Streamlit completo
- [x] Classe `PerformanceMonitor`
- [x] Sistema de arquivos JSON
- [x] Detecção de degradação
- [x] Análise de tendências
- [x] Documentação completa
- [ ] Testes unitários
- [ ] Alertas automáticos
- [ ] CI/CD integration

---

**Versão:** 1.0 (Fase 12)  
**Data:** 20/11/2025  
**Autor:** ArgusPortal
