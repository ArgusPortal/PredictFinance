---
applyTo: '*nao faça nada além do solicitado, caso tenha melhorias a acrescentar, pergunte antes*'
---

# PredictFinance - Instruções de Deploy

## 📋 Visão Geral do Projeto

Sistema de previsão de preços de ações B3SA3.SA usando LSTM com:
- **API REST** (FastAPI) com busca automática de dados via Yahoo Finance
- **Frontend** (Streamlit) com dashboards interativos e análise técnica com IA (Gemini)
- Modelo treinado: MAPE 1.53%, R² 0.9986

---

## 🚀 Deploy da API (FastAPI)

### Produção Atual
- **URL**: https://b3sa3-api.onrender.com
- **Plataforma**: Render.com (Free Tier)
- **Status**: ✅ Ativo

### Arquivos Necessários
```
api/
├── main.py          # Aplicação FastAPI principal
├── schemas.py       # Modelos Pydantic
├── predictor.py     # Lógica de previsão (auto-fetch Yahoo Finance)
└── __init__.py

models/
├── lstm_model_best.h5  # Modelo treinado (0.39 MB)
└── scaler.pkl           # MinMaxScaler (0.86 KB)

requirements-render.txt  # Dependências otimizadas (tensorflow-cpu)
render.yaml             # Configuração do Render
Procfile                # Comando de start
```

### Comandos de Deploy

#### 1. Verificar Status Local
```bash
# Testar API localmente
python run_api.py

# Verificar endpoints
curl http://localhost:8000/health
curl http://localhost:8000/info
```

#### 2. Deploy no Render.com
```bash
# Commit alterações
git add .
git commit -m "feat: atualizar API"
git push origin main
```

**Configuração no Render Dashboard:**
- Name: `b3sa3-api`
- Environment: `Python 3`
- Build Command: `pip install -r requirements-render.txt`
- Start Command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- Plan: Free
- Auto-Deploy: Yes

#### 3. Variáveis de Ambiente (Render Dashboard)
Nenhuma variável obrigatória. API busca dados automaticamente do Yahoo Finance.

#### 4. Testar Produção
```bash
# Health check
curl https://b3sa3-api.onrender.com/health

# Previsão automática
curl -X POST https://b3sa3-api.onrender.com/predict/auto \
  -H "Content-Type: application/json" \
  -d '{"ticker": "B3SA3.SA"}'
```

### Endpoints Disponíveis
- `GET /` - Documentação
- `GET /health` - Health check
- `GET /info` - Informações do modelo
- `GET /metrics` - Métricas de performance
- `POST /predict` - Previsão com dados fornecidos
- `POST /predict/auto` - Previsão automática (busca Yahoo Finance)

### Monitoramento
- Logs estruturados em `api_server.log`
- Métricas de latência e drift
- UptimeRobot para uptime
- Sistema de alertas configurável

---

## 🎨 Deploy do Frontend (Streamlit)

### Produção Atual
- **Status**: 🔧 Local apenas (requer API rodando)
- **Porta**: 8501
- **Dependências**: Streamlit 1.29.0, Plotly 5.18.0, Google Generative AI 0.8.5

### Arquivos Necessários
```
app_streamlit.py        # Aplicação principal (1783 linhas)
run_streamlit.py        # Script helper de execução

.streamlit/
└── config.toml         # Configurações do Streamlit

requirements.txt        # Dependências completas
.env                    # Variáveis de ambiente (GEMINI_API_KEY)
```

### Comandos de Execução Local

#### 1. Configurar Ambiente
```bash
# Ativar ambiente virtual
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Configurar .env (copiar de .env.example)
GEMINI_API_KEY=your_api_key_here
API_BASE_URL=http://localhost:8000  # ou URL produção
```

#### 2. Iniciar Serviços
```bash
# Terminal 1: API
python run_api.py

# Terminal 2: Streamlit
streamlit run app_streamlit.py
# ou
python run_streamlit.py
```

#### 3. Acessar Aplicação
- URL: http://localhost:8501
- Auto-reload: Sim (detecta mudanças no código)

### Páginas e Funcionalidades

#### 🏠 Dashboard
- Métricas principais do modelo (MAPE, R², MAE, RMSE)
- Cards com performance
- Links de navegação rápida

#### 📊 Análise Descritiva
- Busca de dados históricos (Yahoo Finance)
- Estatísticas descritivas completas
- Gráficos interativos:
  - Candlestick com médias móveis
  - Volume de negociação
  - Volatilidade histórica
  - Matriz de correlação
  - Distribuição de retornos
- Download CSV

#### 🎯 Métricas do Modelo
4 abas organizadas:
- **Métricas de Teste**: Gráficos de resultado, interpretação
- **Curvas de Aprendizado**: Loss e MAE por época
- **Hiperparâmetros**: Justificativa de cada parâmetro
- **Arquitetura**: Estrutura completa da rede LSTM

#### 🔮 Previsões
- Integração com API (endpoint `/predict/auto`)
- Input: ticker da ação
- Output: preço previsto, intervalo de confiança, métricas
- Visualização gráfica dos últimos 60 dias + previsão

#### 📈 Análise Técnica
**Indicadores:**
- Bollinger Bands (período 20, desvio 2)
- MACD (12, 26, 9)
- RSI (14 períodos)

**Gráficos Interativos:**
- Candlestick com Bollinger Bands
- MACD (linha, sinal, histograma)
- RSI com zonas de sobrecompra/sobrevenda

**IA Generativa (Gemini 2.0 Flash):**
- Botão "📊 Gerar Relatório com IA"
- Análise completa dos indicadores técnicos
- Recomendações de compra/venda/manter
- Identificação de tendências e padrões
- **Apresentação Visual:**
  - Header estilizado com gradiente
  - 4 cards de métricas (preço, RSI, MACD, volatilidade)
  - RSI colorido (🔴 >70, 🟢 <30, 🟡 neutro)
  - Container estilizado para relatório
  - Box de disclaimer destacado
  - Botão para limpar relatório
- Persistência via session_state (não perde ao interagir)

### Variáveis de Ambiente (.env)
```bash
# Obrigatório para Análise Técnica com IA
GEMINI_API_KEY=your_gemini_api_key

# URL da API (opcional, padrão: http://localhost:8000)
API_BASE_URL=https://b3sa3-api.onrender.com
```

### Deploy em Produção (Streamlit Cloud)

#### Opção 1: Streamlit Community Cloud (Recomendado)
```bash
# 1. Criar arquivo requirements.txt específico
streamlit==1.29.0
plotly==5.18.0
pandas==2.1.4
yfinance==0.2.35
requests==2.31.0
python-dotenv==1.0.1
google-generativeai==0.8.5

# 2. Push para GitHub
git add app_streamlit.py requirements.txt .streamlit/
git commit -m "feat: deploy streamlit"
git push origin main

# 3. Acessar https://share.streamlit.io/
# 4. Conectar repositório: ArgusPortal/PredictFinance
# 5. Main file: app_streamlit.py
# 6. Configurar Secrets (Settings > Secrets):
GEMINI_API_KEY = "your_key"
API_BASE_URL = "https://b3sa3-api.onrender.com"

# 7. Deploy (automático)
```

#### Opção 2: Render.com
```yaml
# render.yaml (adicionar serviço)
- type: web
  name: b3sa3-streamlit
  env: python
  buildCommand: pip install -r requirements.txt
  startCommand: streamlit run app_streamlit.py --server.port=$PORT --server.address=0.0.0.0
  envVars:
    - key: GEMINI_API_KEY
      sync: false
    - key: API_BASE_URL
      value: https://b3sa3-api.onrender.com
```

### Troubleshooting

#### Problema: "Connection Error" ao fazer previsão
**Solução**: Verificar se API está rodando
```bash
curl http://localhost:8000/health
```

#### Problema: "Invalid API Key" na Análise Técnica
**Solução**: Verificar .env
```bash
cat .env | grep GEMINI_API_KEY
```

#### Problema: Gráficos não aparecem
**Solução**: Limpar cache
```bash
streamlit cache clear
```

#### Problema: Session state perdido
**Solução**: Código já implementado com session_state. Verificar linha 1354-1368 em app_streamlit.py

---

## 📦 Estrutura de Dependências

### API (requirements-render.txt)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
tensorflow-cpu==2.15.0  # Otimizado para CPU
scikit-learn==1.3.2
yfinance==0.2.35
pandas==2.1.4
numpy==1.24.3
pydantic==2.5.0
python-dotenv==1.0.1
```

### Frontend (requirements.txt)
```
streamlit==1.29.0
plotly==5.18.0
requests==2.31.0
pandas==2.1.4
yfinance==0.2.35
python-dotenv==1.0.1
google-generativeai==0.8.5  # Para IA na Análise Técnica
```

---

## 🔧 Comandos Úteis

### Desenvolvimento Local
```bash
# Testar API
python run_api.py
curl http://localhost:8000/health

# Testar Streamlit
streamlit run app_streamlit.py

# Verificar dependências
pip list | grep -E "streamlit|fastapi|tensorflow"

# Rodar testes
python test_production.py  # API
python test_local.py       # Local
```

### Monitoramento
```bash
# Logs da API
tail -f api_server.log

# Logs do Streamlit
# Aparece no terminal onde foi executado

# Verificar uso de memória
ps aux | grep -E "uvicorn|streamlit"
```

---

## ⚠️ Notas Importantes

1. **API deve estar rodando** para Streamlit funcionar (páginas Previsões e Análise Técnica)
2. **GEMINI_API_KEY obrigatória** apenas para funcionalidade de IA na Análise Técnica
3. **Render Free Tier** hiberna após 15min de inatividade (primeiro request pode demorar 30s)
4. **Session state** implementado para persistir relatórios de IA entre interações
5. **Modelo Gemini**: gemini-2.0-flash (gemini-pro deprecado desde abril/2025)
6. **Dados automáticos**: API busca últimos 60 dias do Yahoo Finance sem configuração

---

## 📚 Documentação Adicional

- **API**: Ver `EXEMPLOS_USO_API.md` para casos de uso
- **Streamlit**: Ver `GUIA_STREAMLIT.md` para detalhes de funcionalidades
- **Deploy**: Ver `DEPLOY_QUICKSTART.md` para passo a passo completo
- **Monitoramento**: Ver `MONITORING_QUICKSTART.md` para observabilidade