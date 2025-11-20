# PredictFinance - Previsão de Preços de Ações B3SA3.SA com LSTM

[![Streamlit App](https://img.shields.io/badge/Streamlit-Live%20Demo-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://predictfinance.streamlit.app/)
[![API Docs](https://img.shields.io/badge/API-Swagger%20Docs-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)](https://b3sa3-api.onrender.com/docs)

## 📋 Visão Geral do Projeto

Este projeto desenvolve um modelo preditivo de preços das ações da B3 S.A. (código **B3SA3.SA**) utilizando redes neurais **LSTM (Long Short-Term Memory)**. O objetivo principal é prever o **preço de fechamento diário** da ação, métrica que reflete o consenso de valor ao final de cada pregão.

O projeto contempla desde a coleta e preparação de dados históricos até o deploy de uma API REST para disponibilizar previsões em tempo real, incluindo monitoramento contínuo do modelo em produção.

**✨ Novidades v2.0:**
- 💾 **Cache SQLite**: 6 anos de histórico (2020-2025) com fallback automático
- 🚀 **API FastAPI**: Busca automática de dados com sistema de 3 níveis (Yahoo → SQLite → Hardcoded)
- 🎨 **Interface Streamlit**: Dashboards interativos com análise descritiva e técnica
- 🔄 **Atualização Automática**: GitHub Actions atualiza banco diariamente às 4h UTC
- 📊 **Novo Endpoint**: `/data/historical` para consultas customizadas de período
- 🔍 **Monitoramento de Performance**: Sistema completo de validação de previsões em produção

---

## 🌐 Aplicações em Produção

### 🎨 Interface Streamlit
**URL:** [https://predictfinance.streamlit.app/](https://predictfinance.streamlit.app/)

Interface web interativa com dashboards completos para análise e previsão.

### ⚡ API REST
**URL:** [https://b3sa3-api.onrender.com/docs](https://b3sa3-api.onrender.com/docs)

API FastAPI com documentação Swagger interativa para integração em sistemas.

---

## 🚀 Uso Rápido

### 🖥️ Interface Streamlit (Recomendado)

**🌐 Online:** [https://predictfinance.streamlit.app/](https://predictfinance.streamlit.app/)

**💻 Local:**
```bash
# Terminal 1: Iniciar API
python run_api.py

# Terminal 2: Iniciar Streamlit
streamlit run app_streamlit.py
```

Acesse: `http://localhost:8501`

**Funcionalidades:**
- 🏠 Dashboard com métricas do modelo
- 📊 Análise descritiva com gráficos interativos (candlestick, volume, volatilidade, correlação)
- 🎯 Métricas detalhadas do modelo LSTM com 4 abas:
  - 📊 Gráficos de resultado do teste (série temporal + scatter)
  - 📈 Curvas de aprendizado do treinamento (loss + MAE)
  - ⚙️ Hiperparâmetros explicados e justificados
  - 🏗️ Arquitetura completa com cálculo de parâmetros
- 🔮 Previsões em tempo real
- 📈 Análise técnica (RSI, MACD, Bollinger Bands)
- 🔍 **Monitoramento de Performance**: Dashboard com métricas de validação em produção

📚 **Guia completo:** [`GUIA_STREAMLIT.md`](GUIA_STREAMLIT.md)

### 🌐 API REST

#### Previsão Automática

```bash
# Previsão com fallback automático (Yahoo → SQLite → Hardcoded)
curl -X POST https://b3sa3-api.onrender.com/predict/auto \
  -H "Content-Type: application/json" \
  -d '{"ticker": "B3SA3.SA"}'
```

#### Dados Históricos do Cache SQLite

```bash
# Buscar dados de um período específico
curl "https://b3sa3-api.onrender.com/data/historical/B3SA3.SA?start_date=2024-01-01&end_date=2024-12-31"
```

#### Monitoramento de Performance

```bash
# Consultar métricas de performance em produção
curl "https://b3sa3-api.onrender.com/monitoring/performance"

# Validar previsões pendentes
curl -X POST "https://b3sa3-api.onrender.com/monitoring/validate?days_back=7"
```

**Resposta:**
```json
{
  "preco_previsto": 12.85,
  "confianca": "alta",
  "mensagem": "Previsão para B3SA3.SA gerada com sucesso. Modelo MAPE 1.53%..."
}
```

📚 **Mais exemplos:** Veja [`EXEMPLOS_USO_API.md`](EXEMPLOS_USO_API.md) para Python, JavaScript e outros casos de uso.  
📊 **Monitoramento:** Veja [`docs/MONITORING_SYSTEM.md`](docs/MONITORING_SYSTEM.md) para sistema completo de validação.

---

## 🎯 Objetivo

Desenvolver um sistema completo de previsão de preços de ações que:
- Utilize dados históricos da B3SA3.SA (5 features: Open, High, Low, Close, Volume)
- Empregue arquitetura LSTM para capturar padrões temporais
- **Busque dados automaticamente via Yahoo Finance**
- Disponibilize previsões através de API REST
- Esteja em produção com monitoramento ativo

---

## 🏗️ Estrutura do Projeto

```
PredictFinance/
├── data/
│   ├── raw/              # Dados brutos coletados
│   └── processed/        # Dados processados e normalizados
├── database/             # Sistema de cache SQLite
│   ├── db_manager.py     # Gerenciador do banco
│   ├── populate_db.py    # Script de população inicial
│   ├── update_db.py      # Atualização diária
│   └── market_data.db    # Banco SQLite (~284 KB, 6 anos)
├── models/               # Modelos treinados e scalers salvos
├── src/                  # Código-fonte do projeto
│   ├── data_collection.py
│   ├── data_preparation.py
│   ├── model_training.py
│   ├── model_evaluation.py
│   └── utils.py
├── api/                  # Código da API FastAPI
│   ├── main.py            # Endpoints (inclui /data/historical)
│   ├── schemas.py
│   ├── data_fetcher.py    # Busca com fallback (Yahoo → SQLite)
│   └── fallback_data.py   # Dados hardcoded (60 dias)
├── app_streamlit.py      # Interface web
├── .github/workflows/    # GitHub Actions
│   ├── weekly_retrain.yml
│   └── daily_update_db.yml # Atualiza banco diariamente
├── notebooks/            # Jupyter notebooks para análise exploratória
├── docs/                 # Documentação técnica
├── tests/                # Testes unitários
├── requirements.txt      # Dependências do projeto
├── .env.example         # Exemplo de variáveis de ambiente
├── Dockerfile           # Containerização da aplicação
└── README.md            # Este arquivo
```

---

## 📊 Fases do Projeto

### **Fase 1: Coleta e Limpeza de Dados** ✅
- Obtenção de dados históricos da B3SA3.SA via Yahoo Finance (yfinance)
- Tratamento de valores ausentes, outliers e inconsistências
- Análise exploratória inicial dos dados
- **Saída**: Dados limpos salvos em `data/raw/`
- 📖 **[Ver Guia Detalhado](docs/FASE_1_GUIA.md)**

### **Fase 2: Preparação dos Dados para LSTM** ✅
- Normalização dos dados usando MinMaxScaler
- Criação de sequências temporais (janelas deslizantes)
- Divisão em conjuntos de treino, validação e teste
- **Saída**: Dados preparados em `data/processed/` e scaler salvo
- 📖 **[Ver Guia Detalhado](docs/FASE_2_GUIA.md)**

### **Fase 3: Construção da Arquitetura LSTM** ✅
- Definição da arquitetura da rede neural LSTM
- Configuração de hiperparâmetros (camadas, neurônios, dropout)
- Compilação com otimizador Adam e função de perda MSE
- **Saída**: Arquitetura do modelo documentada em `models/` e `docs/`
- 📖 **[Ver Guia Detalhado](docs/FASE_3_GUIA.md)**

### **Fase 4: Treinamento e Avaliação do Modelo** ✅
- Treinamento com early stopping e callbacks
- Cálculo de métricas: RMSE, MAE, MAPE, R²
- Geração de gráficos comparativos (real vs. previsto)
- Análise de curvas de aprendizado
- **Saída**: Modelo treinado salvo em `models/`, métricas em `docs/training/`
- 📖 **[Ver Guia Detalhado](docs/FASE_4_GUIA.md)**

### **Fase 5: Persistência e Verificação do Modelo** ✅
- Verificação de artefatos (modelo .h5 e scaler .pkl)
- Testes de carregamento e predição
- Geração de metadados para API
- Documentação completa de deployment
- **Saída**: Artefatos validados e metadados em `docs/deployment/`
- 📖 **[Ver Guia Detalhado](docs/FASE_5_GUIA.md)**

### **Fase 6: Desenvolvimento da API com FastAPI** ✅
- Criação de aplicação FastAPI com endpoints REST
- Endpoint POST /predict para fazer previsões
- Endpoints auxiliares: /, /health, /info, /metrics
- Validação de dados com Pydantic
- Documentação automática com Swagger/OpenAPI
- **Saída**: API funcional localmente com 5 endpoints, testes completos
- 📖 **[Ver Guia Detalhado](docs/FASE_6_GUIA.md)**

### **Fase 7: Deploy da API** ✅
- Preparação de dependências otimizadas (tensorflow-cpu)
- Configuração render.yaml e Procfile
- Deploy no Render.com (Free Tier)
- Obtenção de URL pública HTTPS
- Testes completos em produção
- **Saída**: API acessível publicamente em `https://b3sa3-api.onrender.com`
- 📖 **[Ver Guia Detalhado](docs/FASE_7_GUIA.md)**

### **Fase 8: Monitoramento do Modelo em Produção** ✅
- Logging estruturado de todas as requisições (estatísticas + latência)
- Monitoramento de performance (validação de previsões vs valores reais)
- Detecção de drift de dados (testes estatísticos + Evidently AI)
- Sistema de alertas automáticos (thresholds configuráveis)
- Monitoramento de uptime (health check + UptimeRobot)
- Script de monitoramento diário automatizado
- **Saída**: Sistema completo de observabilidade em produção 24/7
- 📖 **[Ver Guia Detalhado](docs/FASE_8_GUIA.md)**

### **Fase 9: Interface Streamlit** ✅
- Desenvolvimento de interface web interativa
- Dashboards com métricas, gráficos e visualizações
- Análise descritiva e técnica de ativos
- Previsões em tempo real com relatórios IA
- **Saída**: Aplicação Streamlit completa em `app_streamlit.py`
- 📖 **[Ver Guia Detalhado](GUIA_STREAMLIT.md)**

### **Fase 10: Sistema de Cache SQLite** ✅
- Banco de dados SQLite com 6 anos de histórico (2020-2025)
- Sistema de fallback em 3 níveis (Yahoo → SQLite → Hardcoded)
- Endpoint `/data/historical` para consultas customizadas
- Atualização automática diária via GitHub Actions (4h UTC)
- Scripts de população e manutenção
- **Saída**: Banco populado (1468 registros, 284 KB), workflows automatizados
- 📖 **[Ver Guia Completo](docs/DATABASE_GUIDE.md)**

### **Fase 11: Deploy Completo** 🔄
- **API**: Render.com (FastAPI + LSTM + SQLite)
- **Frontend**: Streamlit Cloud (Interface web)
- Workflows GitHub Actions (retrain semanal + update DB diário)
- Monitoramento e logs em produção
- 📖 **[Deploy API](DEPLOY_QUICKSTART.md)** | **[Deploy Streamlit](docs/DEPLOY_STREAMLIT.md)**

---

## 🛠️ Tecnologias e Ferramentas

### **Linguagem Principal**
- Python 3.10+

### **Bibliotecas por Fase**

#### Coleta e Manipulação de Dados
- `yfinance` - Obtenção de dados financeiros
- `pandas` - Manipulação de DataFrames
- `numpy` - Operações numéricas

#### Pré-processamento
- `scikit-learn` - MinMaxScaler, métricas de avaliação
- `pandas` - Transformação de dados

#### Modelagem
- `tensorflow` / `keras` - Construção e treinamento da LSTM
- `matplotlib` / `seaborn` - Visualizações
- `plotly` - Gráficos interativos

#### Persistência
- `joblib` - Salvamento de scaler
- `tensorflow` - Salvamento de modelo

#### API e Deploy
- `fastapi` - Framework web assíncrono
- `uvicorn` - Servidor ASGI
- `pydantic` - Validação de dados
- `python-dotenv` - Gerenciamento de variáveis de ambiente

#### Monitoramento (Fase 8)
- `evidently` - Drift detection e model monitoring
- `scipy` - Testes estatísticos (Kolmogorov-Smirnov)
- `requests` - Alertas via Slack webhooks
- `yfinance` - Coleta de valores reais para validação

#### Testes e Qualidade
- `pytest` - Testes unitários
- `black` - Formatação de código
- `flake8` - Linting

---

## 🚀 Como Executar o Projeto

### **Pré-requisitos**
```bash
# Python 3.10 ou superior
python --version

# Git instalado
git --version
```

### **1. Clonar o Repositório**
```bash
git clone https://github.com/ArgusPortal/PredictFinance.git
cd PredictFinance
```

### **2. Criar Ambiente Virtual**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### **3. Instalar Dependências**
```bash
pip install -r requirements.txt
```

### **4. Executar as Fases do Projeto**
```bash
# Fase 1: Coleta de dados
python src/data_collection.py

# Fase 2: Preparação de dados
python src/data_preparation.py

# Fase 3: Treinamento do modelo
python src/model_training.py

# Fase 4: Avaliação
python src/model_evaluation.py
```

### **5. Executar a API Localmente**
```bash
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Acesse a documentação interativa em: `http://localhost:8000/docs`

---

## 📈 Métricas de Avaliação

O modelo será avaliado utilizando as seguintes métricas:

- **RMSE (Root Mean Square Error)**: Mede a raiz quadrada da média dos erros ao quadrado
- **MAE (Mean Absolute Error)**: Média dos valores absolutos dos erros
- **MAPE (Mean Absolute Percentage Error)**: Erro percentual médio absoluto
- **R² Score**: Coeficiente de determinação

---

## 🔄 Reutilização de Resultados

Cada fase do projeto é construída sobre os resultados da fase anterior:

1. **Fase 1 → Fase 2**: Dados limpos são normalizados e transformados em sequências
2. **Fase 2 → Fase 3**: Sequências preparadas alimentam o treinamento da LSTM
3. **Fase 3 → Fase 4**: Modelo treinado é avaliado com dados de teste
4. **Fase 4 → Fase 5**: Modelo validado é salvo para produção
5. **Fase 5 → Fase 6**: Modelo salvo é carregado pela API
6. **Fase 6 → Fase 7**: API local é containerizada e deployada
7. **Fase 7 → Fase 8**: API em produção é monitorada continuamente

---

## 📝 Princípios do Projeto

- **Reprodutibilidade**: Todos os scripts são determinísticos e documentados
- **Modularidade**: Cada fase é independente e reutilizável
- **Automação**: Execução sequencial das fases sem intervenção manual
- **Qualidade**: Código formatado, testado e documentado
- **Formalidade**: Documentação em português formal e técnico

---

## 📚 Documentação Adicional

- [Especificações Técnicas](docs/especificacoes_tecnicas.md)
- [Guia de Instalação](docs/instalacao.md)
- [API Reference](docs/api_reference.md)
- [Metodologia LSTM](docs/metodologia_lstm.md)

---

## 🤝 Contribuições

Este é um projeto educacional e de demonstração. Contribuições são bem-vindas através de pull requests.

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

---

## 👤 Autor

**ArgusPortal**
- GitHub: [@ArgusPortal](https://github.com/ArgusPortal)

---

## 🎓 Referências

- LSTMs para séries temporais financeiras (arXiv)
- Documentação oficial TensorFlow/Keras
- Yahoo Finance API
- FastAPI Documentation

---

**Status do Projeto**: 🟢 Em Desenvolvimento Ativo

**Última Atualização**: 02/11/2025
