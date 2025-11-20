# Guia de Uso - Aplicação Streamlit

## 🚀 Como Executar

### 1. Instalar Dependências
```bash
# Ativar ambiente virtual
.venv/Scripts/activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install streamlit==1.29.0 plotly==5.18.0
```

### 2. Iniciar a API (Terminal 1)
```bash
python run_api.py
```
A API estará disponível em: `http://localhost:8000`

### 3. Iniciar o Streamlit (Terminal 2)
```bash
# Opção 1: Comando direto
streamlit run app_streamlit.py

# Opção 2: Script helper
python run_streamlit.py
```
O Streamlit abrirá automaticamente em: `http://localhost:8501`

---

## 📱 Funcionalidades da Aplicação

### 🏠 Página Inicial
- Dashboard com métricas principais do modelo
- Visão geral da performance (MAPE, R², MAE, RMSE)
- Comparação com benchmarks
- Quick start para navegação rápida

### 📊 Análise Descritiva
**Funcionalidades:**
- Busca de dados históricos via Yahoo Finance
- Estatísticas descritivas completas (média, mediana, desvio padrão, etc.)
- Gráficos interativos:
  - 📈 Candlestick com médias móveis (MA20, MA50)
  - 📊 Volume de negociação com cores (alta/baixa)
  - 🔔 Volatilidade histórica anualizada
  - 📉 Matriz de correlação entre features (OHLCV)
  - 📊 Distribuição de retornos diários
- Download dos dados em CSV

**Como usar:**
1. Digite o ticker (ex: B3SA3.SA, PETR4.SA)
2. Selecione o período (1 mês a 5 anos)
3. Clique em "Buscar Dados"
4. Explore as abas com diferentes visualizações

### 🎯 Métricas do Modelo
**Funcionalidades organizadas em 4 abas:**

#### 📊 Aba: Métricas de Teste
- Métricas principais em cards (MAPE, R², MAE, RMSE)
- **Gráfico de resultado_teste.png:**
  - Série temporal: Preços reais vs previstos
  - Scatter plot: Correlação entre valores
  - Box com métricas consolidadas
- Interpretação detalhada dos gráficos
- Comparação com benchmarks (Excelente/Bom/Aceitável)
- Guia de interpretação das métricas

#### 📈 Aba: Curvas de Aprendizado
- **Gráfico de curvas_aprendizado.png:**
  - Loss (MSE) - treino e validação
  - MAE - treino e validação
- Interpretação de convergência e overfitting
- Estatísticas de treinamento:
  - Épocas executadas vs configuradas
  - Loss final (treino e validação)
  - MAE final (treino e validação)
  - Melhor época identificada
- **Gráfico interativo Plotly:**
  - Evolução do loss ao longo das épocas
  - Marcação da melhor época
  - Hover com detalhes

#### ⚙️ Aba: Hiperparâmetros
- **Parâmetros de Treinamento:**
  - Épocas (50) - justificativa completa
  - Batch Size (32) - por que esse valor
  - Early Stopping Patience (10) - explicação
- **Arquitetura da Rede:**
  - LSTM Layer 1 (64 unidades) - motivo da escolha
  - Dropout (0.2) - como previne overfitting
  - LSTM Layer 2 (32 unidades) - redução gradual
  - Dense Layer (1 unidade) - camada de saída
- **Otimizador Adam:**
  - Learning rate e vantagens
  - Parâmetros beta₁, beta₂, epsilon
- **Função de Perda MSE:**
  - Por que MSE é adequado para regressão
  - Comparação com MAE
- **Callbacks utilizados:**
  - Early Stopping
  - Model Checkpoint
  - Reduce LR on Plateau
- **Justificativa detalhada:**
  - Por que cada hiperparâmetro foi escolhido
  - Como funciona especificamente para dados financeiros
  - Resultados obtidos: MAPE 1.53% e R² 0.935

#### 🏗️ Aba: Arquitetura
- **Gráficos de estrutura:**
  - Barras: Unidades por camada
  - Barras: Parâmetros treináveis por camada
- **Resumo ASCII da arquitetura**
- **Cálculo detalhado de parâmetros LSTM:**
  - Fórmula de cálculo
  - Breakdown por camada
- **Informações dos dados:**
  - Dataset original (período, total de dias)
  - Sequências geradas (treino/val/teste)
  - Window size e overlap
- **Gráfico de pizza:** Divisão dos dados

**Métricas disponíveis:**
- **MAPE:** 1.53% (Excelente - erro percentual médio)
- **R²:** 0.9351 (Excelente - capacidade de explicação)
- **MAE:** R$ 0.20 (erro absoluto médio em reais)
- **RMSE:** R$ 0.26 (penaliza erros grandes)

### 🔮 Previsão
**Duas opções disponíveis:**

#### 🚀 Busca Automática
- Digite qualquer ticker da B3 (adiciona .SA automaticamente)
- Botões rápidos para ações populares
- Sistema busca automaticamente os últimos 60 dias via Yahoo Finance
- Gera previsão com:
  - Preço previsto em R$
  - Nível de confiança
  - Variação esperada (%)
  - Tendência (Alta/Baixa/Neutra)
  - Gráfico dos últimos 60 dias
  - Análise detalhada da previsão

#### 📊 Dados de Exemplo
- Usa dados pré-carregados do conjunto de teste
- Teste rápido sem necessidade de buscar dados
- Ideal para validação e demonstração

### 📈 Análise Técnica
**Indicadores disponíveis:**
- **Bollinger Bands:** Identifica volatilidade e pontos de reversão
- **SMA 20 e 50:** Médias móveis simples para tendências
- **MACD:** Convergência/Divergência de médias móveis
- **RSI:** Índice de Força Relativa (sobrecompra/sobrevenda)

**Análise de sinais:**
- ✅ Sinais de compra (verde)
- ⚠️ Sinais de venda (vermelho)
- ➡️ Sinais neutros (azul)

**Como usar:**
1. Digite o ticker
2. Selecione o período (1 mês a 2 anos)
3. Clique em "Analisar"
4. Visualize gráficos e indicadores
5. Confira análise automática de sinais

---

## 🎨 Design e UX

### Características visuais:
- 🎨 Tema moderno com gradiente roxo
- 📱 Design responsivo (funciona em mobile)
- 🖱️ Gráficos interativos (Plotly)
- ⚡ Feedback visual em tempo real
- 🔄 Loading spinners durante processamento
- 📊 Cards com métricas destacadas
- 🎯 Navegação intuitiva via sidebar

### Elementos interativos:
- Hover em gráficos para detalhes
- Zoom e pan nos gráficos
- Download de gráficos como PNG
- Botões de ação destacados
- Inputs com validação em tempo real

---

## 🔧 Configuração Avançada

### Porta customizada
```bash
streamlit run app_streamlit.py --server.port=8502
```

### Desabilitar auto-reload
```bash
streamlit run app_streamlit.py --server.runOnSave=false
```

### Modo headless (sem abrir browser)
```bash
streamlit run app_streamlit.py --server.headless=true
```

### Configuração no arquivo `.streamlit/config.toml`
```toml
[server]
port = 8501
headless = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

---

## 📊 Endpoints da API Utilizados

A aplicação Streamlit consome os seguintes endpoints:

1. **GET /info** - Informações do modelo
2. **GET /metrics** - Métricas de performance
3. **POST /predict/auto** - Previsão automática
4. **GET /predict/example** - Previsão com dados de exemplo

---

## ⚠️ Troubleshooting

### Erro: "API Offline"
**Solução:** Verifique se a API está rodando em `http://localhost:8000`
```bash
# Terminal 1
python run_api.py
```

### Erro: "Port already in use"
**Solução:** Altere a porta do Streamlit
```bash
streamlit run app_streamlit.py --server.port=8502
```

### Erro: "No data found for ticker"
**Solução:** 
- Verifique se o ticker existe na B3
- Para ações brasileiras, use o formato: `TICKER.SA`
- Exemplos válidos: B3SA3.SA, PETR4.SA, VALE3.SA

### Erro: "Module not found"
**Solução:** Instale as dependências
```bash
pip install -r requirements-render.txt
```

### Gráficos não aparecem
**Solução:** Limpe o cache do Streamlit
```bash
streamlit cache clear
```

---

## 🎯 Casos de Uso

### 1. Análise Rápida de Ação
```
1. Abra o Streamlit
2. Vá para "Análise Descritiva"
3. Digite o ticker (ex: PETR4.SA)
4. Explore gráficos e estatísticas
5. Baixe os dados em CSV
```

### 2. Gerar Previsão
```
1. Vá para "Previsão"
2. Digite o ticker ou clique em exemplo rápido
3. Clique em "Gerar Previsão"
4. Analise resultado e tendência
```

### 3. Análise Técnica Completa
```
1. Vá para "Análise Técnica"
2. Digite o ticker e período
3. Analise indicadores (RSI, MACD, Bollinger)
4. Confira sinais de trading
```

### 4. Verificar Performance do Modelo
```
1. Vá para "Métricas do Modelo"
2. Veja MAPE, R², MAE, RMSE
3. Compare com benchmarks
4. Entenda arquitetura LSTM
```

---

## 📝 Notas Importantes

1. **Dados em tempo real:** Usa Yahoo Finance, pode haver delay de ~15 minutos
2. **Rate limits:** Yahoo Finance limita ~2000 requisições/hora
3. **Timeout:** Requisições podem levar até 45 segundos (busca de dados)
4. **Cache:** Streamlit faz cache de funções para performance
5. **Memória:** Aplicação usa ~500MB de RAM (modelo LSTM carregado na API)

---

## 🚀 Deploy em Produção

### Render.com
1. Adicione `streamlit` aos `requirements-render.txt` ✅ (já feito)
2. Configure start command:
   ```bash
   streamlit run app_streamlit.py --server.port=$PORT --server.address=0.0.0.0
   ```
3. Configure variável de ambiente:
   ```
   API_BASE_URL=https://sua-api.onrender.com
   ```

### Streamlit Cloud
1. Faça push do código para GitHub
2. Acesse https://share.streamlit.io/
3. Conecte o repositório
4. Deploy automático!

---

## 📚 Recursos Adicionais

- [Documentação Streamlit](https://docs.streamlit.io/)
- [Plotly Documentation](https://plotly.com/python/)
- [yfinance Documentation](https://github.com/ranaroussi/yfinance)

---

## ✨ Próximas Melhorias

- [ ] Comparação entre múltiplos tickers
- [ ] Alertas de preço (price alerts)
- [ ] Backtesting de estratégias
- [ ] Exportar relatórios em PDF
- [ ] Integração com mais indicadores técnicos
- [ ] Dashboard de portfolio
- [ ] Notificações por email

---

**Desenvolvido por:** ArgusPortal  
**Versão:** 2.0  
**Data:** 20/11/2025
