# 📝 Changelog v2.1 - Janeiro 2026

## 🎯 Resumo das Alterações

Atualização focada em **estabilidade, monitoramento e persistência de dados** em produção.

---

## 🗄️ Banco de Dados

### PostgreSQL Render (NOVO)
- ✅ **Migração para novo banco**: `predictfinance_gb6k` (02/01/2026)
  - Banco anterior expirou após período free tier
  - Dados restaurados via dump/restore (18 previsões)
- ✅ **Persistência de previsões**: Sistema agora usa PostgreSQL como fonte primária
  - Tabela `predictions`: Rastreamento de todas as previsões
  - Tabela `daily_metrics`: Métricas agregadas por dia
- ✅ **Endpoint de diagnóstico**: `/debug/database` para verificar status

**Arquivos Alterados:**
- `render.yaml`: DATABASE_URL atualizada
- `database/postgres_manager.py`: URL default atualizada
- `database/db_manager.py`: Suporte dual SQLite + PostgreSQL

---

## 🔍 Drift Detection

### Correções Implementadas
- ✅ **API v8 como método primário**: Drift detection agora usa Yahoo Finance API v8
  - Mais confiável que yfinance em produção
  - Fallback para yfinance se API v8 falhar
  - Fallback para cache JSON em último caso
- ✅ **Bug fix conversão numpy**: Corrigido erro no teste Kolmogorov-Smirnov
  - Conversão explícita de numpy.ndarray para float
- ✅ **Atualização automática**: Drift reports agora atualizados diariamente via CI/CD

**Arquivos Alterados:**
- `api/main.py`: Endpoint `/monitoring/drift` refatorado
- `src/drift_detector.py`: Fix conversão numpy em teste KS
- `.github/workflows/daily_update_db.yml`: Adicionado `setup_drift_detection.py`

**Status Atual (02/01/2026):**
```json
{
  "drift_detected": true,
  "severity": "medium",
  "alerts": ["Volatilidade diminuiu 59.9%"],
  "cache_mode": false
}
```

---

## 📊 Sistema de Monitoramento

### Performance em Produção
- ✅ **18 previsões rastreadas** (9 validadas, 9 pendentes)
- ✅ **Integração com PostgreSQL**: Previsões agora persistem entre deploys
- ✅ **Dashboard Streamlit**: Interface mostra histórico completo

**Endpoint `/monitoring/performance`:**
```json
{
  "statistics": {
    "total_validated": 17,
    "total_pending": 1,
    "mape": 1.53,
    "mae": 0.20
  },
  "recent_predictions": [/* 18 previsões */]
}
```

---

## 🔄 CI/CD

### GitHub Actions
- ✅ **Daily Update**: Atualiza SQLite + drift reports diariamente (4h UTC)
- ✅ **Weekly Retrain**: Re-treino automático toda segunda-feira (3h UTC)
  - Último re-treino: 29/12/2025
  - Modelo atual: R² = 0.7757, MAPE = 2.0%

**Dependências Adicionadas:**
- `scipy`: Necessário para drift detection (testes estatísticos)

---

## 🚀 API Endpoints

### Novos Endpoints
- `/debug/database`: Diagnóstico de conexão com bancos de dados
  ```json
  {
    "postgres_enabled": true,
    "postgres_predictions": 18,
    "sqlite_predictions": 18,
    "db_manager_pg_enabled": true
  }
  ```

### Endpoints Atualizados
- `/monitoring/drift`: Agora usa API v8 como método primário
- `/monitoring/performance`: Busca previsões do PostgreSQL

---

## 📚 Documentação

### Arquivos Atualizados
- `README.md`: Informações sobre PostgreSQL e drift fix
- `docs/DATABASE_GUIDE.md`: Adicionado schema PostgreSQL
- `docs/CHANGELOG_V2.1.md`: Este documento

### Documentos para Atualização Futura
- `docs/DOCUMENTACAO_TECNICA.md`: Adicionar seção PostgreSQL
- `docs/INDEX.md`: Atualizar referências a banco de dados
- `docs/MONITORING_SYSTEM.md`: Adicionar detalhes de drift fix

---

## 🐛 Bugs Corrigidos

1. **Drift detection fixo em cache mode** (12 dias)
   - **Causa**: yfinance falhando em produção
   - **Solução**: API v8 como método primário

2. **Previsões não persistindo entre deploys**
   - **Causa**: Apenas JSON local sendo usado
   - **Solução**: PostgreSQL como fonte primária

3. **Erro numpy no drift_detector**
   - **Causa**: Conversão implícita falhou
   - **Solução**: Conversão explícita para float

---

## 🎯 Próximos Passos

### Melhorias Planejadas
- [ ] Adicionar testes automatizados para drift detection
- [ ] Implementar alertas via email/webhook quando drift > threshold
- [ ] Dashboard de métricas em tempo real no Grafana
- [ ] Backup automático do PostgreSQL

### Investigação
- [ ] Investigar queda no R² do modelo (0.935 → 0.7757)
  - Pode ser natural após mudanças de mercado
  - Re-treino semanal deve ajustar automaticamente

---

## 📌 Commits Principais

```
769fe53 - debug: adicionar endpoint /debug/database
558494b - ci: adicionar atualização de drift ao workflow diário
0b9cb43 - fix: corrigir conversão numpy em drift_detector
60f8250 - fix: atualizar PostgreSQL para novo banco Render + corrigir drift API v8
9fd812d - 🤖 Auto-retrain: Modelo atualizado - 2025-12-29
```

---

**Versão**: 2.1.0  
**Data**: 02 de Janeiro de 2026  
**Autor**: Argus  
**Status**: ✅ Produção Estável
