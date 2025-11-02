# PredictFinance - Previsão de Preços de Ações B3SA3.SA com LSTM

## 📋 Visão Geral do Projeto

Este projeto desenvolve um modelo preditivo de preços das ações da B3 S.A. (código **B3SA3.SA**) utilizando redes neurais **LSTM (Long Short-Term Memory)**. O objetivo principal é prever o **preço de fechamento diário** da ação, métrica que reflete o consenso de valor ao final de cada pregão.

O projeto contempla desde a coleta e preparação de dados históricos até o deploy de uma API REST para disponibilizar previsões em tempo real, incluindo monitoramento contínuo do modelo em produção.

---

## 🎯 Objetivo

Desenvolver um sistema completo de previsão de preços de ações que:
- Utilize dados históricos da B3SA3.SA para treinamento
- Empregue arquitetura LSTM para capturar padrões temporais
- Disponibilize previsões através de API REST
- Esteja em produção com monitoramento ativo

---

## 🏗️ Estrutura do Projeto

```
PredictFinance/
├── data/
│   ├── raw/              # Dados brutos coletados
│   └── processed/        # Dados processados e normalizados
├── models/               # Modelos treinados e scalers salvos
├── src/                  # Código-fonte do projeto
│   ├── data_collection.py
│   ├── data_preparation.py
│   ├── model_training.py
│   ├── model_evaluation.py
│   └── utils.py
├── api/                  # Código da API FastAPI
│   ├── main.py
│   ├── schemas.py
│   └── predictor.py
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

### **Fase 6: Desenvolvimento da API com FastAPI**
- Criação de endpoints REST para previsões
- Endpoint de health check e informações do modelo
- Documentação automática com Swagger/OpenAPI
- **Saída**: API funcional localmente

### **Fase 7: Deploy da API**
- Containerização com Docker
- Deploy em serviço gratuito (Render, Railway, ou similar)
- Configuração de variáveis de ambiente
- **Saída**: API em produção com endpoint público

### **Fase 8: Monitoramento e Documentação Final**
- Implementação de logs e métricas de monitoramento
- Criação de dashboard para acompanhamento
- Documentação completa do projeto
- Vídeo explicativo demonstrando o funcionamento
- **Saída**: Sistema completo documentado e operacional

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
