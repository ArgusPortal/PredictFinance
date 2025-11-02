# 📚 Índice de Documentação - PredictFinance

## Guias de Execução das Fases

Este diretório contém a documentação completa do projeto **PredictFinance**, incluindo guias detalhados para execução de cada fase, especificações técnicas e instruções de deployment.

---

## 📖 Guias por Fase

### ✅ Fase 1: Coleta e Limpeza de Dados
**Arquivo**: [`FASE_1_GUIA.md`](FASE_1_GUIA.md)

**Conteúdo**:
- Coleta de dados históricos da B3SA3.SA via yfinance
- Tratamento de valores ausentes e outliers
- Análise exploratória de dados
- Validação de qualidade dos dados

**Script**: `src/data_collection.py`  
**Saídas**: `data/raw/b3sa3_historical.csv`, gráficos de análise

---

### ✅ Fase 2: Preparação dos Dados para LSTM
**Arquivo**: [`FASE_2_GUIA.md`](FASE_2_GUIA.md)

**Conteúdo**:
- Normalização com MinMaxScaler
- Criação de sequências temporais (60 timesteps)
- Divisão em treino/validação/teste (70/15/15)
- Salvamento de arrays processados

**Script**: `src/data_preparation.py`  
**Saídas**: Arrays NumPy em `data/processed/`, `models/scaler.pkl`

---

### ✅ Fase 3: Construção da Arquitetura LSTM
**Arquivo**: [`FASE_3_GUIA.md`](FASE_3_GUIA.md)

**Conteúdo**:
- Definição da arquitetura LSTM (2 camadas + Dropout)
- Configuração de 30,369 parâmetros treináveis
- Compilação com Adam optimizer e MSE loss
- Documentação da estrutura do modelo

**Script**: `src/model_builder.py`  
**Saídas**: `models/model_architecture.json`, documentação em `docs/model_architecture/`

---

### ✅ Fase 4: Treinamento e Avaliação do Modelo
**Arquivo**: [`FASE_4_GUIA.md`](FASE_4_GUIA.md)

**Conteúdo**:
- Treinamento com Early Stopping e callbacks
- 49 épocas executadas (50 configuradas)
- Cálculo de métricas: RMSE (R$ 0.26), MAE (R$ 0.20), MAPE (1.53%), R² (0.9351)
- Geração de curvas de aprendizado e gráficos de predição

**Script**: `src/model_training.py`  
**Saídas**: `models/lstm_model_best.h5`, resultados em `docs/training/`

**Performance Alcançada**: ✅ EXCELENTE
- MAPE < 2% (meta: < 5%)
- R² > 0.93 (meta: > 0.85)

---

### ✅ Fase 5: Persistência e Verificação do Modelo
**Arquivo**: [`FASE_5_GUIA.md`](FASE_5_GUIA.md)

**Conteúdo**:
- Verificação de artefatos (modelo 0.39 MB, scaler 0.86 KB)
- Testes de carregamento e predição
- Geração de metadados para API
- Documentação completa de deployment

**Script**: `src/model_persistence.py`  
**Saídas**: Metadados em `docs/deployment/`, README de deployment

---

### ✅ Fase 6: Desenvolvimento da API com FastAPI
**Arquivo**: [`FASE_6_GUIA.md`](FASE_6_GUIA.md)

**Conteúdo**:
- Criação de aplicação FastAPI
- Implementação de endpoints REST (5 endpoints)
- Validação com Pydantic (PrevisaoInput/Output)
- Carregamento de modelo no startup (lifespan)
- Documentação automática Swagger/ReDoc
- Testes completos da API

**Scripts**: `api/main.py`, `api/schemas.py`, `run_api.py`  
**Saídas**: API rodando em http://localhost:8000, testes em `docs/api/`

**Performance Alcançada**: ✅ EXCELENTE
- 5 endpoints funcionais (/, /health, /info, /metrics, /predict)
- Validações Pydantic robustas
- Documentação automática completa
- 8 testes automatizados passando

---

### ✅ Fase 7: Deploy da API no Render.com
**Arquivo**: [`FASE_7_GUIA.md`](FASE_7_GUIA.md)

**Conteúdo**:
- Preparação de dependências otimizadas (requirements-render.txt)
- Configuração render.yaml e Procfile
- Deploy no Render.com (Free Tier)
- Obtenção de URL pública HTTPS
- Testes completos em produção
- Monitoramento e troubleshooting

**Scripts**: `test_production.py`  
**Saídas**: API pública em https://b3sa3-api.onrender.com

**Arquivos Criados**:
- `requirements-render.txt` (tensorflow-cpu otimizado)
- `render.yaml` (configuração do serviço)
- `Procfile` (comando de start)
- `test_production.py` (testes automatizados)
- `docs/DEPLOY_RENDER.md` (680+ linhas)
- `DEPLOY_QUICKSTART.md` (guia rápido)

---

### ⏳ Fase 8: Monitoramento e Finalização
**Status**: Pendente

**Objetivo**:
- Containerização com Docker
- Deploy em serviço gratuito (Render/Railway)
- Configuração de variáveis de ambiente
- Testes em produção

**Próximos Passos**: Criar `Dockerfile`, deploy em cloud

---

### ⏳ Fase 8: Monitoramento e Documentação Final
**Status**: Pendente

**Objetivo**:
- Implementar logging estruturado
- Criar dashboard de monitoramento (Streamlit)
- Vídeo explicativo (10 minutos)
- Documentação final completa

**Próximos Passos**: Sistema de logs, dashboard, vídeo

---

## 📊 Documentos Técnicos

### Especificações Técnicas
**Arquivo**: [`especificacoes_tecnicas.md`](especificacoes_tecnicas.md)

**Conteúdo**:
- Arquitetura completa do sistema
- Cronograma de 9 dias úteis
- Requisitos técnicos detalhados
- Diagrama de fluxo de dados

---

### Resumo do Projeto
**Arquivo**: [`RESUMO_PROJETO.md`](RESUMO_PROJETO.md)

**Conteúdo**:
- Visão geral executiva
- Status atual do projeto (62.5% concluído)
- Métricas alcançadas
- Próximas etapas

---

### Instruções de Execução
**Arquivo**: [`INSTRUCOES_EXECUCAO.md`](INSTRUCOES_EXECUCAO.md)

**Conteúdo**:
- Setup do ambiente
- Instalação de dependências
- Comandos de execução sequenciais
- Troubleshooting comum

---

## 📁 Estrutura de Diretórios de Documentação

```
docs/
├── FASE_1_GUIA.md                    ✅ Guia da Fase 1
├── FASE_2_GUIA.md                    ✅ Guia da Fase 2
├── FASE_3_GUIA.md                    ✅ Guia da Fase 3
├── FASE_4_GUIA.md                    ✅ Guia da Fase 4
├── FASE_5_GUIA.md                    ✅ Guia da Fase 5
├── especificacoes_tecnicas.md        ✅ Especificações completas
├── RESUMO_PROJETO.md                 ✅ Resumo executivo
├── INSTRUCOES_EXECUCAO.md            ✅ Setup e comandos
├── INDEX.md                          ✅ Este arquivo
│
├── data_collection/                  📊 Logs e gráficos da Fase 1
│   ├── data_collection_log.json
│   └── exploratory_analysis.png
│
├── data_preparation/                 📊 Logs e gráficos da Fase 2
│   ├── data_preparation_log.json
│   └── data_preparation_viz.png
│
├── model_architecture/               🏗️ Arquitetura do modelo
│   ├── model_info.json
│   └── model_summary.txt
│
├── training/                         📈 Resultados do treinamento
│   ├── training_results.json
│   ├── curvas_aprendizado.png
│   └── resultado_teste.png
│
└── deployment/                       🚀 Metadados para API
    ├── model_deployment_metadata.json
    ├── api_metadata.json
    └── README.md
```

---

## 🎯 Navegação Rápida

### Por Objetivo

**Quero executar o projeto do zero:**
1. [INSTRUCOES_EXECUCAO.md](INSTRUCOES_EXECUCAO.md) - Setup inicial
2. [FASE_1_GUIA.md](FASE_1_GUIA.md) - Coletar dados
3. [FASE_2_GUIA.md](FASE_2_GUIA.md) - Preparar dados
4. [FASE_3_GUIA.md](FASE_3_GUIA.md) - Construir arquitetura
5. [FASE_4_GUIA.md](FASE_4_GUIA.md) - Treinar modelo
6. [FASE_5_GUIA.md](FASE_5_GUIA.md) - Verificar artefatos

**Quero entender a arquitetura:**
- [especificacoes_tecnicas.md](especificacoes_tecnicas.md)
- [FASE_3_GUIA.md](FASE_3_GUIA.md)
- [model_architecture/model_info.json](model_architecture/model_info.json)

**Quero ver os resultados:**
- [FASE_4_GUIA.md](FASE_4_GUIA.md)
- [training/training_results.json](training/training_results.json)
- [training/resultado_teste.png](training/resultado_teste.png)

**Quero fazer deploy:**
- [FASE_5_GUIA.md](FASE_5_GUIA.md)
- [deployment/README.md](deployment/README.md)
- [deployment/api_metadata.json](deployment/api_metadata.json)

---

## 📝 Comandos Rápidos

### Executar Todas as Fases Concluídas
```bash
# Fase 1: Coleta de dados
python src/data_collection.py

# Fase 2: Preparação dos dados
python src/data_preparation.py

# Fase 3: Construção da arquitetura
python src/model_builder.py

# Fase 4: Treinamento e avaliação
python src/model_training.py

# Fase 5: Verificação e metadados
python src/model_persistence.py
```

### Verificar Saídas
```bash
# Verificar dados coletados
ls -lh data/raw/

# Verificar dados processados
ls -lh data/processed/

# Verificar modelos
ls -lh models/

# Verificar documentação gerada
ls -lh docs/*/
```

---

## 🔗 Links Úteis

### Repositórios e Código
- **GitHub**: [ArgusPortal/PredictFinance](https://github.com/ArgusPortal/PredictFinance)
- **Branch Principal**: `main`

### Referências Técnicas
- [Keras LSTM Documentation](https://keras.io/api/layers/recurrent_layers/lstm/)
- [Scikit-learn MinMaxScaler](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MinMaxScaler.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Yahoo Finance API (yfinance)](https://pypi.org/project/yfinance/)

---

## ✅ Status do Projeto

**Progresso Geral**: 75% (6/8 fases concluídas)

| Fase | Status | Documentação |
|------|--------|--------------|
| Fase 1 | ✅ Concluída | [FASE_1_GUIA.md](FASE_1_GUIA.md) |
| Fase 2 | ✅ Concluída | [FASE_2_GUIA.md](FASE_2_GUIA.md) |
| Fase 3 | ✅ Concluída | [FASE_3_GUIA.md](FASE_3_GUIA.md) |
| Fase 4 | ✅ Concluída | [FASE_4_GUIA.md](FASE_4_GUIA.md) |
| Fase 5 | ✅ Concluída | [FASE_5_GUIA.md](FASE_5_GUIA.md) |
| Fase 6 | ✅ Concluída | [FASE_6_GUIA.md](FASE_6_GUIA.md) |
| Fase 7 | ⏳ Pendente | A ser criado |
| Fase 8 | ⏳ Pendente | A ser criado |

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Consulte o guia específico da fase
2. Verifique a seção de Troubleshooting
3. Consulte [INSTRUCOES_EXECUCAO.md](INSTRUCOES_EXECUCAO.md)

---

**Última Atualização**: 02/11/2025  
**Versão da Documentação**: 1.0.0  
**Autor**: ArgusPortal
