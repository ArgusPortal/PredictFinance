# 🔄 Scripts de Automação

Pasta contendo scripts para manutenção e automação do modelo.

## 📄 Arquivos

### `retrain_model.py`
Script principal de re-treino automático do modelo LSTM.

**Uso:**
```bash
# Teste (não substitui modelo)
python scripts/retrain_model.py --dry-run

# Re-treino normal (substitui se aprovado)
python scripts/retrain_model.py

# Forçar substituição
python scripts/retrain_model.py --force

# Outro ticker
python scripts/retrain_model.py --ticker PETR4.SA --years 3
```

**O que faz:**
1. Coleta dados atualizados do Yahoo Finance
2. Treina novo modelo LSTM
3. Compara métricas com modelo atual
4. Faz backup do modelo antigo
5. Substitui se métricas aprovarem
6. Salva métricas e logs

## 🤖 GitHub Actions

O script é executado automaticamente via `.github/workflows/weekly_retrain.yml`:
- **Quando**: Toda segunda-feira às 3h UTC
- **Como**: GitHub Actions na nuvem (grátis)
- **Resultado**: Commit automático se aprovado

## 📚 Documentação Completa

Ver `docs/AUTO_RETRAIN.md` para guia completo.
