# 📝 Atualizações Pendentes na Documentação - v2.1

**Data**: 02/01/2026  
**Status**: 🟡 Em Progresso

---

## ✅ Documentos JÁ Atualizados

1. **README.md**
   - ✅ Adicionado PostgreSQL Render
   - ✅ Atualizado sistema de fallback (API v8 → yfinance → SQLite)
   - ✅ Novo endpoint `/debug/database`
   - ✅ Drift detection corrigido

2. **docs/DATABASE_GUIDE.md**
   - ✅ Schema PostgreSQL adicionado
   - ✅ Tabelas `predictions` e `daily_metrics`
   - ✅ Configuração Render explicada
   - ✅ Endpoint de diagnóstico

3. **docs/CHANGELOG_V2.1.md**
   - ✅ Criado documento completo
   - ✅ Todas mudanças documentadas

4. **docs/DOCUMENTACAO_TECNICA.md**
   - ✅ Versão atualizada para 2.1.0
   - ✅ Data atualizada

---

## 🔄 Documentos QUE PRECISAM SER ATUALIZADOS

### 1. **docs/MONITORING_SYSTEM.md** - CRÍTICO

**Mudanças necessárias:**

#### Seção: Arquitetura
- [ ] Adicionar PostgreSQL no diagrama de fluxo
- [ ] Mostrar `predictions` persistindo no PostgreSQL
- [ ] Atualizar fallback do drift (API v8 primeiro)

**Texto atual menciona**:
```
│ monitoring/                  │
│   predictions_tracking.json  │  Armazena para validação
```

**Deve mencionar**:
```
│ PostgreSQL Render            │
│   predictions table (18 reg) │  Persist

ência primária
│ monitoring/                  │
│   predictions_tracking.json  │  Backup local
```

#### Seção: Detecção de Drift
- [ ] Mencionar API v8 como método primário
- [ ] Fallback para yfinance
- [ ] Fallback para cache JSON

**Linha ~85-95**: Atualizar fluxo de busca de dados

#### Adicionar nova seção: PostgreSQL
```markdown
## 🗄️ PostgreSQL - Persistência em Produção

### Configuração
- Banco: `predictfinance_gb6k` (Render)
- Tabelas: `predictions`, `daily_metrics`
- URL configurada via `DATABASE_URL`

### Vantagens
- ✅ Dados persistem entre deploys
- ✅ Queries mais rápidas que JSON
- ✅ Suporta concorrência
- ✅ Integridade referencial
```

---

### 2. **docs/ARQUITETURA_MONITORAMENTO.md** - ALTO

**Mudanças necessárias:**

#### Diagrama principal (linha 1-70)
- [ ] Adicionar caixa "PostgreSQL Render"
- [ ] Mostrar conexão API → PostgreSQL
- [ ] Mostrar conexão PerformanceMonitor → PostgreSQL

**Substituir**:
```
│  logs/                       │
│  predictions.log ✅          │
```

**Por**:
```
│  PostgreSQL (Render)         │
│    predictions: 18 ✅        │
│    daily_metrics: 0          │
│  logs/ (backup)              │
│    predictions.log           │
```

#### Seção Drift Detection (linha 70-100)
- [ ] Atualizar método de busca para API v8
- [ ] Mostrar fallback hierárquico

---

### 3. **docs/RESUMO_PROJETO.md** - MÉDIO

**Mudanças necessárias:**

#### Seção "O QUE FOI IMPLEMENTADO"
- [ ] Atualizar versão para 2.1.0
- [ ] Adicionar PostgreSQL na arquitetura
- [ ] Mencionar drift fix

**Linha ~20**: Adicionar:
```
├── database/
│   ├── postgres_manager.py      ✅ PostgreSQL Render
│   ├── db_manager.py            ✅ Dual SQLite + PostgreSQL
```

#### Nova seção: "Atualizações v2.1"
```markdown
## 🆕 Atualizações v2.1 (Janeiro 2026)

### PostgreSQL Integration
- ✅ Migração para `predictfinance_gb6k`
- ✅ Persistência de previsões
- ✅ 18 previsões rastreadas

### Drift Detection Fix
- ✅ API v8 como método primário
- ✅ Bug numpy.ndarray corrigido
- ✅ Atualização diária via CI/CD
```

---

### 4. **docs/FASE_8_GUIA.md** - MÉDIO

**Mudanças necessárias:**

#### Linha 1-10: Header
- [ ] Atualizar "Última atualização" para 02/01/2026

#### Seção "Componentes do Sistema"
- [ ] Adicionar menção ao PostgreSQL
- [ ] Atualizar diagram de arquitetura

**Linha ~100**: Adicionar subseção:
```markdown
### 5.1 PostgreSQL Backend (NOVO em v2.1)

O sistema agora usa PostgreSQL para persistência:

**Vantagens**:
- Dados sobrevivem a deploys
- Performance superior a JSON
- Queries SQL otimizadas

**Tabelas**:
- `predictions`: Rastreamento de previsões
- `daily_metrics`: Métricas agregadas
```

---

### 5. **docs/FASE_8_RESUMO.md** - MÉDIO

**Mudanças necessárias:**

#### Seção "Arquivos Criados"
- [ ] Adicionar `database/postgres_manager.py`
- [ ] Mencionar dual persistence (PostgreSQL + JSON)

**Linha ~45**: Adicionar:
```markdown
### 6. Gerenciador PostgreSQL (v2.1)
```
database/postgres_manager.py        # 200 linhas
├── PostgresManager                  # Classe principal
├── Conexão com Render              
├── DDL automático de tabelas
└── Operações CRUD
```

---

### 6. **docs/API_V8_INTEGRATION.md** - BAIXO

**Mudanças necessárias:**

#### Linha 1-5: Header
- [ ] Atualizar status para mencionar uso em drift

**Linha ~30**: Adicionar nota:
```markdown
## 🆕 Atualização v2.1: Drift Detection

A API v8 agora é usada também no drift detection (`/monitoring/drift`):

```python
# api/main.py - Endpoint /monitoring/drift
# MÉTODO 1: API v8 (mais confiável)
if API_V8_DISPONIVEL:
    df = coletar_dados_yahoo_v8_custom_range(...)
```

**Benefício**: Drift detection não fica mais em cache mode.
```

---

### 7. **docs/RELATORIO_APRESENTACAO.md** - BAIXO

**Mudanças necessárias:**

#### Linha 1-10: Header
- [ ] Atualizar "Data do Relatório" para 02/01/2026
- [ ] Versão: 2.1.0

#### Seção "Métricas de Performance"
- [ ] Atualizar com dados do PostgreSQL
- [ ] Mencionar 18 previsões rastreadas

**Linha ~100**: Adicionar:
```markdown
### 3.2 Métricas em Produção (PostgreSQL)

| Métrica | Valor Atual |
|---------|-------------|
| **Previsões Registradas** | 18 |
| **Previsões Validadas** | 17 |
| **Previsões Pendentes** | 1 |
| **MAPE Produção** | 1.53% |
| **Última Validação** | 30/12/2025 |
```

---

### 8. **docs/MONITORING_QUICKSTART.md** - BAIXO

**Mudanças necessárias:**

#### Seção "Verificar Performance"
- [ ] Adicionar comando para verificar PostgreSQL

**Linha ~80**: Adicionar:
```bash
# Verificar PostgreSQL (produção)
curl "https://b3sa3-api.onrender.com/debug/database" | python -m json.tool

# Saída esperada:
# {
#   "postgres_enabled": true,
#   "postgres_predictions": 18,
#   "db_manager_pg_enabled": true
# }
```

---

### 9. **docs/INDEX.md** - BAIXO

**Mudanças necessárias:**

#### Seção "Guias por Fase"
- [ ] Atualizar referências à Fase 8
- [ ] Mencionar PostgreSQL em sistema de monitoramento

**Linha ~150**: Adicionar:
```markdown
**Atualização v2.1**:
- PostgreSQL Render para persistência
- Drift detection com API v8
- 18+ previsões rastreadas em produção
```

---

### 10. **docs/AUTO_RETRAIN.md** - MUITO BAIXO

**Mudanças necessárias:**

#### Seção "Métricas Atuais"
- [ ] Atualizar com último re-treino (29/12/2025)
- [ ] Mencionar degradação R² (0.935 → 0.7757)

**Linha ~200**: Adicionar nota:
```markdown
## ⚠️ Nota sobre Degradação do Modelo

O modelo apresentou queda no R² de 0.935 para 0.7757 após re-treino de 29/12/2025.

**Possíveis causas**:
- Mudanças naturais do mercado no final do ano
- Volatilidade diminuiu 62.4% (detectado por drift)
- Período de férias com menos liquidez

**Ação tomada**:
- Re-treino semanal continuará ajustando
- Monitoramento ativo de performance
- MAPE ainda aceitável (2.0% < 5%)
```

---

## 📊 Priorização

### Crítico (Fazer AGORA)
1. **MONITORING_SYSTEM.md** - Documento central do sistema
2. **ARQUITETURA_MONITORAMENTO.md** - Diagramas desatualizados

### Alto (Fazer HOJE)
3. **RESUMO_PROJETO.md** - Visão geral
4. **FASE_8_GUIA.md** - Guia principal da fase

### Médio (Fazer Esta Semana)
5. **FASE_8_RESUMO.md**
6. **API_V8_INTEGRATION.md**

### Baixo (Opcional)
7. **RELATORIO_APRESENTACAO.md**
8. **MONITORING_QUICKSTART.md**
9. **INDEX.md**
10. **AUTO_RETRAIN.md**

---

## ✅ Checklist Final

Antes de fazer commit:

- [ ] Todos os documentos críticos atualizados
- [ ] Diagramas refletindo arquitetura atual
- [ ] Versões e datas atualizadas
- [ ] Links funcionando
- [ ] Exemplos testados
- [ ] Métricas corretas

---

**Progresso Geral**: 4/14 documentos (29%)  
**Meta**: 100% antes do commit
