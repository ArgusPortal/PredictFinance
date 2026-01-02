# 📚 Índice de Documentação - PredictFinance

**Versão:** 2.1.0  
**Última atualização:** 02/01/2026

## 🆕 Novidades v2.1 (Janeiro 2026)

- 🗄️ **PostgreSQL Render**: Persistência em produção (18+ registros)
- 🔍 **Drift Detection API v8**: Método hierárquico com 3 fallbacks
- 📊 **Dual Persistence**: PostgreSQL + JSON backup
- 📄 **CHANGELOG_V2.1.md**: Novo documento com todas as mudanças
- 🔧 **DATABASE_GUIDE.md**: Guia completo de PostgreSQL

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

### ✅ Fase 8: Monitoramento do Modelo em Produção
**Arquivo**: [`FASE_8_GUIA.md`](FASE_8_GUIA.md)

**Conteúdo**:
- Logging estruturado de requisições (PredictionLogger, MetricsLogger)
- Monitoramento de performance (validação previsões vs valores reais)
- **Detecção de drift com janela deslizante** (7 dias vs 30 dias anteriores)
- Sistema de alertas automáticos (Slack, email, logs)
- Monitoramento de uptime (health check + UptimeRobot)
- Automação com cron jobs / GitHub Actions

**⚠️ IMPORTANTE - Drift Detection:**
- ✅ **Abordagem correta:** Janela deslizante (detecta mudanças abruptas recentes)
- ❌ **Abordagem incorreta:** Comparar dados de treino (2020-2023) com produção (2025)
- Toda documentação atualizada em 21/12/2025

**Scripts**: 
- `api/monitoring.py` (logging system)
- `src/performance_monitor.py` (performance tracking)
- `src/drift_detector.py` (janela deslizante - ATUALIZADO)
- `src/alert_system.py` (alertas)
- `run_daily_monitoring.py` (execução diária)
- `test_monitoring.py` (testes do sistema)
- `setup_drift_detection.py` (análise de drift)

**Saídas**: 
- Logs em `logs/predictions.log` e `logs/metrics.log`
- Métricas em `monitoring/performance_metrics.json`
- Relatórios em `monitoring/drift_reports.json`
- Alertas em `monitoring/alert_history.json`
- Resumo diário em `monitoring/daily_summary.json`

**Arquivos Criados**:
- `requirements-monitoring.txt` (evidently, scipy, requests)
- `api/monitoring.py` (280+ linhas)
- `src/performance_monitor.py` (380+ linhas)
- `src/drift_detector.py` (350+ linhas)
- `src/alert_system.py` (340+ linhas)
- `run_daily_monitoring.py` (230+ linhas)
- `test_monitoring.py` (250+ linhas)
- `setup_monitoring.py` (180+ linhas)
- `docs/FASE_8_GUIA.md` (1200+ linhas - documentação completa)

**Performance Alcançada**: ✅ EXCELENTE
- Sistema completo de observabilidade em produção
- Logging 100% das requisições com estatísticas
- Validação automática de previsões vs valores reais
- Detecção proativa de drift e degradação
- Alertas configuráveis via múltiplos canais
- Uptime monitoring 24/7
- Automação completa via scripts diários

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

### Documentação Técnica Completa

**Arquivo**: [`DOCUMENTACAO_TECNICA.md`](DOCUMENTACAO_TECNICA.md)

**Conteúdo**:
- Documentação técnica completa pós-implementação (2,227 linhas)
- Arquitetura LSTM implementada (2 camadas: 64→32 units)
- Resultados reais alcançados:
  - MAPE = 1.53% (meta < 5%)
  - R² = 0.935 (meta > 0.85)
- Detalhamento de todas as 8 fases implementadas
- Análise exploratória e estatísticas descritivas
- Curvas de aprendizado e gráficos de resultado
- Referências acadêmicas (arXiv, IEEE)

**Público**: Desenvolvedores, pesquisadores, analistas técnicos

**Quando usar**: Para entender a implementação real, arquitetura final, resultados alcançados

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
├── FASE_6_GUIA.md                    ✅ Guia da Fase 6 (API)
├── FASE_7_GUIA.md                    ✅ Guia da Fase 7 (Deploy)
├── FASE_8_GUIA.md                    ✅ Guia da Fase 8 (Monitoramento) - v2.1
├── FASE_8_RESUMO.md                  ✅ Resumo da Fase 8 - v2.1
├── DOCUMENTACAO_TECNICA.md            ✅ Documentação técnica - v2.1.0
├── RESUMO_PROJETO.md                 ✅ Resumo executivo - v2.1
├── INSTRUCOES_EXECUCAO.md            ✅ Setup e comandos
├── CHANGELOG_V2.1.md                 🆕 Mudanças v2.1 (Janeiro 2026)
├── DATABASE_GUIDE.md                 🆕 Guia PostgreSQL Render
├── API_V8_INTEGRATION.md             ✅ Integração API v8 - v2.1
├── MONITORING_SYSTEM.md              ✅ Sistema de monitoramento - v2.1
├── MONITORING_QUICKSTART.md          ✅ Quick start - v2.1
├── ARQUITETURA_MONITORAMENTO.md      ✅ Arquitetura - v2.1
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
- [DOCUMENTACAO_TECNICA.md](DOCUMENTACAO_TECNICA.md)
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

## � Documentação Adicional

### Guias Quick Start
- [`MONITORING_QUICKSTART.md`](MONITORING_QUICKSTART.md) - Comandos rápidos para monitoramento
- [`DEPLOY_QUICKSTART.md`](DEPLOY_QUICKSTART.md) - Deploy rápido em produção
- [`YAHOO_FINANCE_GUIDE.md`](YAHOO_FINANCE_GUIDE.md) - ✅ **CONSOLIDADO** - Guia completo Yahoo Finance API

### Arquitetura e Sistemas
- [`ARQUITETURA_MONITORAMENTO.md`](ARQUITETURA_MONITORAMENTO.md) - Diagramas do sistema de monitoramento
- [`MONITORING_SYSTEM.md`](MONITORING_SYSTEM.md) - Sistema completo de monitoramento
- [`DOCUMENTACAO_TECNICA.md`](DOCUMENTACAO_TECNICA.md) - Documentação técnica completa

### Relatórios
- [`RELATORIO_APRESENTACAO.md`](RELATORIO_APRESENTACAO.md) - Relatório com métricas para apresentação (ATUALIZADO 21/12/2025)

### Troubleshooting
- [`RETRAIN_TROUBLESHOOTING.md`](RETRAIN_TROUBLESHOOTING.md) - Solução de problemas no retreino
- [`YAHOO_FINANCE_GUIDE.md`](YAHOO_FINANCE_GUIDE.md) - Guia completo e troubleshooting Yahoo Finance

### Análise de Documentação
- [`DOCUMENTACAO_OBSOLETA.md`](DOCUMENTACAO_OBSOLETA.md) - Análise de documentos obsoletos/duplicados (21/12/2025)

---

## 🔄 Atualizações Recentes (21/12/2025)

### Drift Detection - Janela Deslizante

**Problema Corrigido:**
- ❌ Abordagem anterior comparava dados de treino (2020-2023) com produção (2025)
- ❌ Resultado: Sempre mostrava drift alto (~28% média) devido à evolução natural do mercado
- ❌ Conclusão incorreta: "Modelo está degradando"

**Solução Implementada:**
- ✅ Janela deslizante: últimos 7 dias vs 30 dias anteriores
- ✅ Detecta mudanças ABRUPTAS e RECENTES, não evolução gradual
- ✅ Thresholds: 5% para média, 50% para volatilidade
- ✅ Integrado com API: `GET /monitoring/drift`
- ✅ Streamlit: Tab "🌊 Drift Detection" atualizada

**Documentos Atualizados:**
1. ✅ [RELATORIO_APRESENTACAO.md](RELATORIO_APRESENTACAO.md) - Seção 9 reescrita
2. ✅ [MONITORING_SYSTEM.md](MONITORING_SYSTEM.md) - Fluxo atualizado
3. ✅ [MONITORING_QUICKSTART.md](MONITORING_QUICKSTART.md) - Novos comandos
4. ✅ [FASE_8_GUIA.md](FASE_8_GUIA.md) - Explicação completa da janela deslizante
5. ✅ [ARQUITETURA_MONITORAMENTO.md](ARQUITETURA_MONITORAMENTO.md) - Diagramas atualizados
6. ✅ [README.md](../README.md) - Endpoint de drift adicionado

**Documentos Consolidados/Removidos:**
- ❌ FASE_12_MONITORAMENTO.md → Conteúdo estava duplicado com FASE_8_GUIA.md
- ✅ [YAHOO_FINANCE_GUIDE.md](YAHOO_FINANCE_GUIDE.md) → Consolidou:
  - ❌ YAHOO_API_V8_QUICKSTART.md
  - ❌ YAHOO_FINANCE_SOLUTION.md
  - ❌ YAHOO_FINANCE_ERROR_ANALYSIS.md

---

## ✅ Status do Projeto

**Progresso Geral**: 100% (8/8 fases concluídas)

| Fase | Status | Documentação |
|------|--------|--------------|
| Fase 1 | ✅ Concluída | [FASE_1_GUIA.md](FASE_1_GUIA.md) |
| Fase 2 | ✅ Concluída | [FASE_2_GUIA.md](FASE_2_GUIA.md) |
| Fase 3 | ✅ Concluída | [FASE_3_GUIA.md](FASE_3_GUIA.md) |
| Fase 4 | ✅ Concluída | [FASE_4_GUIA.md](FASE_4_GUIA.md) |
| Fase 5 | ✅ Concluída | [FASE_5_GUIA.md](FASE_5_GUIA.md) |
| Fase 6 | ✅ Concluída | [FASE_6_GUIA.md](FASE_6_GUIA.md) |
| Fase 7 | ✅ Concluída | [FASE_7_GUIA.md](FASE_7_GUIA.md) |
| Fase 8 | ✅ Concluída | [FASE_8_GUIA.md](FASE_8_GUIA.md) - ATUALIZADO |

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Consulte o guia específico da fase
2. Verifique a seção de Troubleshooting
3. Consulte [INSTRUCOES_EXECUCAO.md](INSTRUCOES_EXECUCAO.md)
4. Revise [DOCUMENTACAO_OBSOLETA.md](DOCUMENTACAO_OBSOLETA.md) para status de documentos

---

**Última Atualização**: 02/11/2025  
**Versão da Documentação**: 1.0.0  
**Autor**: ArgusPortal
