# 🎯 INSTRUÇÕES PARA EXECUÇÃO AUTOMATIZADA DO PROJETO PREDICTFINANCE

## 📌 Visão Geral

Este documento contém as instruções operacionais para execução automatizada de todas as fases do projeto **PredictFinance**. Cada fase deve ser executada sequencialmente, utilizando os resultados da fase anterior.

---

## 🏁 INÍCIO DO PROJETO

### Contexto
O projeto desenvolve um modelo preditivo de preços das ações da **B3 S.A. (B3SA3.SA)** usando redes neurais **LSTM**. O foco é prever o **preço de fechamento diário**, métrica que reflete o consenso de valor ao fim de cada pregão.

### Objetivo
Criar um sistema completo de previsão de preços, desde a coleta de dados até uma API REST deployada em produção com monitoramento contínuo.

### Fases do Projeto
1. ✅ **Coleta e limpeza de dados** → `data/raw/`
2. ⏳ **Preparação dos dados para LSTM** → `data/processed/` + scaler
3. ⏳ **Construção e treinamento do modelo LSTM** → `models/`
4. ⏳ **Avaliação de desempenho** → `docs/evaluation/`
5. ⏳ **Salvamento de modelo e scaler** → Artefatos versionados
6. ⏳ **Construção da API com FastAPI** → API local
7. ⏳ **Deploy da API** → Produção (Render/Railway)
8. ⏳ **Monitoramento e documentação final** → Vídeo explicativo

### Reutilização de Resultados
Cada fase utiliza as saídas da fase anterior:
- **Fase 1 → Fase 2**: CSV limpo → Dados normalizados e sequências
- **Fase 2 → Fase 3**: Sequências → Modelo treinado
- **Fase 3 → Fase 4**: Modelo → Métricas de avaliação
- **Fase 4 → Fase 5**: Modelo validado → Salvamento para produção
- **Fase 5 → Fase 6**: Modelo salvo → API carrega artefatos
- **Fase 6 → Fase 7**: API local → Deploy em nuvem
- **Fase 7 → Fase 8**: API produção → Monitoramento contínuo

---

## 📦 PREPARAÇÃO DO AMBIENTE

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

---

## 🚀 EXECUÇÃO DAS FASES

### ✅ FASE 1: COLETA E LIMPEZA DE DADOS

**Status**: ✅ **IMPLEMENTADA E PRONTA PARA EXECUÇÃO**

#### Comando de Execução
```bash
python src/data_collection.py
```

#### Saídas Esperadas
- `data/raw/b3sa3_historical.csv`
- `docs/data_collection/data_collection_log.json`
- `docs/data_collection/analise_exploratoria.png`
- `docs/data_collection/matriz_correlacao.png`

#### Documentação Detalhada
Consulte: `docs/FASE_1_GUIA.md`

---

### ⏳ FASE 2-8: A IMPLEMENTAR

Consulte `README.md` e `docs/especificacoes_tecnicas.md` para detalhes completos de todas as fases.

---

## 📋 STATUS ATUAL

- ✅ Estrutura do projeto criada
- ✅ Documentação completa
- ✅ Fase 1 implementada
- ⏳ Aguardando execução da Fase 1 e implementação das demais fases

---

**Versão**: 1.0.0  
**Data**: 02/11/2025  
**Autor**: ArgusPortal
