# ⚡ Quick Start - Sistema de Monitoramento (Fase 8)

**Autor:** Argus  
**Última atualização:** 02/01/2026 (v2.1)  
**Novidades:** PostgreSQL, Drift API v8, Dual Persistence

Comandos rápidos para configurar e usar o sistema de monitoramento.

---

## 🆕 Novidades v2.1 (Janeiro 2026)

- 🗄️ **PostgreSQL Render**: 18+ previsões rastreadas em produção
- 🔍 **Drift API v8**: Método hierárquico com 3 fallbacks
- 📊 **Dual Persistence**: PostgreSQL + JSON backup
- 🔧 **Debug Endpoint**: `/debug/database` para diagnóstico

---

## 🚀 Setup Inicial (Execute UMA VEZ)

```bash
# 1. Instalar dependências
pip install -r requirements-monitoring.txt

# 2. Executar setup automático
python setup_monitoring.py

# 3. Executar testes
python test_monitoring.py

# ✅ Sistema configurado!
```

---

## 📊 Uso Diário

### Execução Manual

```bash
# Monitoramento completo
python run_daily_monitoring.py
```

### Automação Linux/Mac (Cron)

```bash
# Editar crontab
crontab -e

# Adicionar (executa diariamente às 12:00)
0 12 * * * cd /path/to/PredictFinance && python run_daily_monitoring.py >> monitoring.log 2>&1
```

### Automação Windows (Task Scheduler)

```powershell
# Criar script PowerShell: daily_monitoring.ps1
cd C:\path\to\PredictFinance
& "C:\path\to\python.exe" run_daily_monitoring.py

# Task Scheduler:
# - Trigger: Daily 12:00 PM
# - Action: powershell.exe -File C:\path\to\daily_monitoring.ps1
```

### Automação GitHub Actions (Cloud, Grátis)

```bash
# Arquivo já criado (se precisar):
# .github/workflows/monitoring.yml

# Push para ativar
git push origin main
```

---

## 🔍 Verificar Logs

```bash
# Logs de previsões
cat logs/predictions.log | tail -n 20
cat logs/predictions.log | grep "prediction" | tail -n 10

# Logs de métricas
cat logs/metrics.log

# Resumo diário
cat monitoring/daily_summary.json | python -m json.tool
```

---
## 🗄️ Verificar PostgreSQL (v2.1)

### Debug Endpoint (Produção)

```bash
# Verificar conexão PostgreSQL
curl https://b3sa3-api.onrender.com/debug/database
```

**Saída esperada:**
```json
{
  "environment": "production",
  "postgres_enabled": true,
  "db_manager_pg_enabled": true,
  "postgres_predictions": 18,
  "postgres_metrics": 0,
  "json_predictions": 18,
  "json_daily_metrics": 14
}
```

### Consultar Previsões

```bash
# Consultar previsões em produção
curl https://b3sa3-api.onrender.com/monitoring/performance | python -m json.tool

# Verificar total de previsões
curl -s https://b3sa3-api.onrender.com/monitoring/performance | \
  python -c "import sys, json; data=json.load(sys.stdin); print(f'Total: {data[\"summary\"][\"total_predictions_validated\"]} previsões')"
```

### Conexão Local (Desenvolvimento)

```bash
# Testar conexão PostgreSQL
python scripts/test_pg_connection.py

# Usar DATABASE_URL de render.yaml
export DATABASE_URL="postgresql://predictfinance_gb6k_user:...@dpg-d5c2tcruibrs73cs32pg-a.ohio-postgres.render.com/predictfinance_gb6k"
```

---
## 📈 Verificar Performance

```bash
# Métricas atuais
python -c "
import json
with open('monitoring/performance_metrics.json') as f:
    data = json.load(f)
    summary = data.get('summary', {})
    print(f'MAE:  {summary.get(\"current_mae\", \"N/A\")}')
    print(f'MAPE: {summary.get(\"current_mape\", \"N/A\")}%')
"

# Ou simplesmente
cat monitoring/performance_metrics.json | python -m json.tool | grep -A 5 "summary"
```

---

## 🌊 Verificar Drift (Janela Deslizante)

```bash
# Análise de drift atualizada
python setup_drift_detection.py

# Ou via API (se disponível)
curl "http://localhost:8000/monitoring/drift"

# Verificar histórico de análises
cat monitoring/drift_reports.json | python -m json.tool | tail -n 50

# Ver última análise com Python
python -c "
import json
with open('monitoring/drift_reports.json') as f:
    data = json.load(f)
    if data.get('reports'):
        last = data['reports'][-1]
        print(f'Data: {last[\"timestamp\"]}')
        print(f'Drift detectado: {last[\"drift_detected\"]}')
        print(f'Severidade: {last.get(\"severity\", \"none\")}')
        print(f'Alertas: {len(last.get(\"alerts\", []))}')
"
```

---

## 🔔 Verificar Alertas

```bash
# Últimos alertas
python -c "
import json
with open('monitoring/alert_history.json') as f:
    data = json.load(f)
    alerts = data.get('alerts', [])
    print(f'Total de alertas: {len(alerts)}')
    if alerts:
        last = alerts[-1]
        print(f'Último: [{last[\"severity\"]}] {last[\"message\"]} ({last[\"timestamp\"]})')
"

# Alertas das últimas 24h
python -c "
from src.alert_system import AlertSystem
alert_system = AlertSystem()
recent = alert_system.get_recent_alerts(hours=24)
print(f'Alertas (24h): {len(recent)}')
for alert in recent:
    print(f'  [{alert[\"severity\"]}] {alert[\"message\"]}')
"
```

---

## 🧪 Testes

```bash
# Teste completo do sistema
python test_monitoring.py

# Teste individual - Logging
python -c "
from api.monitoring import get_prediction_logger
import numpy as np
logger = get_prediction_logger()
fake_input = np.random.rand(60, 5).tolist()
request_id = logger.log_prediction(fake_input, 12.45, 25.0)
print(f'✅ Logged: {request_id}')
"

# Teste individual - Performance Monitor
python -c "
from src.performance_monitor import PerformanceMonitor
monitor = PerformanceMonitor()
monitor.register_prediction(12.50, request_id='test-001')
print('✅ Prediction registered')
"

# Teste individual - Drift Detector
python -c "
from src.drift_detector import DriftDetector
import numpy as np
detector = DriftDetector()
ref_data = np.random.normal(12.0, 1.0, 1000)
detector.set_reference_statistics(ref_data)
print('✅ Reference configured')
"

# Teste individual - Alert System
python -c "
from src.alert_system import AlertSystem
alert_system = AlertSystem()
alert_system.send_alert('test', 'Test alert', 'INFO')
print('✅ Alert sent')
"
```

---

## 🔧 Configurações

### Configurar Slack Webhook

```bash
python -c "
from src.alert_system import configure_slack_webhook
configure_slack_webhook('https://hooks.slack.com/services/YOUR/WEBHOOK/URL')
print('✅ Slack webhook configurado')
"
```

### Verificar Configuração

```bash
# Alert config
cat monitoring/alert_config.json | python -m json.tool

# Reference stats
cat monitoring/reference_statistics.json | python -m json.tool
```

### Re-configurar Estatísticas de Referência

```bash
python -c "
from src.drift_detector import setup_reference_from_file
from pathlib import Path
data_file = Path('data/processed/B3SA3_2020-11-03_2025-10-31.csv')
setup_reference_from_file(data_file)
print('✅ Reference re-configured')
"
```

---

## 🚀 Deploy

```bash
# 1. Commit mudanças
git add .
git commit -m "feat: Sistema de monitoramento (Fase 8)"

# 2. Push para Render
git push origin main

# 3. Aguardar deploy (~5 min)
# Render faz deploy automático

# 4. Verificar logs do Render
# Dashboard → Logs
```

---

## 🌐 Produção

### Testar API em Produção

```bash
# Health check
curl https://b3sa3-api.onrender.com/health

# Fazer previsão (com logging automático)
curl -X POST https://b3sa3-api.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{
    "prices": [12.1, 12.2, 12.15, ... (60 valores)]
  }'
```

### Verificar Logs de Produção

```bash
# Via dashboard do Render:
# 1. Acesse dashboard.render.com
# 2. Selecione seu serviço
# 3. Logs → Ver em tempo real

# Logs incluirão:
# INFO | {"request_id": "abc123", "event": "prediction", ...}
```

---

## 📊 Monitoramento de Uptime

### Configurar UptimeRobot

1. **Acesse**: https://uptimerobot.com
2. **Add Monitor**:
   - URL: `https://b3sa3-api.onrender.com/health`
   - Type: HTTP(S)
   - Interval: 5 minutes
   - Alert: Seu email

### Verificar Status

```bash
# Manual
curl https://b3sa3-api.onrender.com/health

# Esperado:
# {
#   "status": "healthy",
#   "model_loaded": true,
#   "scaler_loaded": true
# }
```

---

## 🗂️ Estrutura de Arquivos

```bash
# Listar logs
ls -lh logs/

# Listar dados de monitoramento
ls -lh monitoring/

# Tamanho total
du -sh logs/ monitoring/
```

---

## 🧹 Manutenção

### Limpar Logs Antigos

```bash
# Backup primeiro
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/

# Limpar logs (mantém últimos 100 linhas)
tail -n 100 logs/predictions.log > logs/predictions.log.tmp
mv logs/predictions.log.tmp logs/predictions.log

tail -n 100 logs/metrics.log > logs/metrics.log.tmp
mv logs/metrics.log.tmp logs/metrics.log
```

### Resetar Dados de Monitoramento

```bash
# ⚠️  CUIDADO: Apaga todo o histórico!

# Backup primeiro
tar -czf monitoring_backup_$(date +%Y%m%d).tar.gz monitoring/

# Reset
rm monitoring/*.json

# Re-configurar
python setup_monitoring.py
```

---

## 📚 Documentação

```bash
# Ler guia completo
cat docs/FASE_8_GUIA.md

# Abrir no VS Code
code docs/FASE_8_GUIA.md

# Ver resumo
cat FASE_8_RESUMO.md

# Ver arquitetura
cat ARQUITETURA_MONITORAMENTO.md
```

---

## 🆘 Troubleshooting

### Problema: Logs não aparecem

```bash
# Verificar permissões
ls -l logs/

# Criar manualmente
mkdir -p logs
chmod 755 logs

# Testar
python -c "
from api.monitoring import get_prediction_logger
logger = get_prediction_logger()
print('✅ Logger initialized')
"
```

### Problema: yfinance não retorna dados

```bash
# Testar manualmente
python -c "
import yfinance as yf
from datetime import datetime, timedelta
end = datetime.now()
start = end - timedelta(days=7)
data = yf.download('B3SA3.SA', start=start, end=end)
print(data.tail())
"
```

### Problema: Drift detector sem referência

```bash
# Verificar
cat monitoring/reference_statistics.json

# Se vazio, configurar
python setup_monitoring.py
```

### Problema: JSON corrompido

```bash
# Verificar sintaxe
cat monitoring/predictions_tracking.json | python -m json.tool

# Se erro, resetar
echo '{"predictions": []}' > monitoring/predictions_tracking.json
```

---

## 📊 One-Liners Úteis

```bash
# Contar previsões registradas
cat monitoring/predictions_tracking.json | python -c "import json, sys; data=json.load(sys.stdin); print(len(data['predictions']))"

# Última previsão validada
cat monitoring/predictions_tracking.json | python -c "import json, sys; data=json.load(sys.stdin); validated=[p for p in data['predictions'] if p['validated']]; print(validated[-1] if validated else 'None')"

# Média de MAPE dos últimos 7 dias
cat monitoring/performance_metrics.json | python -c "import json, sys; data=json.load(sys.stdin); metrics=data['daily_metrics'][-7:]; print(sum(m['mape'] for m in metrics)/len(metrics) if metrics else 'N/A')"

# Taxa de drift
cat monitoring/drift_reports.json | python -c "import json, sys; data=json.load(sys.stdin); reports=data['reports'][-7:]; drift_count=sum(1 for r in reports if r['drift_detected']); print(f'{drift_count}/{len(reports)} ({drift_count/len(reports)*100:.1f}%)' if reports else '0/0')"

# Últimos 5 alertas
cat monitoring/alert_history.json | python -c "import json, sys; data=json.load(sys.stdin); alerts=data['alerts'][-5:]; [print(f'[{a[\"severity\"]}] {a[\"message\"]}') for a in alerts]"
```

---

## 🎯 Checklist Rápido

**Setup Inicial**:
- [ ] `pip install -r requirements-monitoring.txt`
- [ ] `python setup_monitoring.py`
- [ ] `python test_monitoring.py`

**Produção**:
- [ ] `git push origin main` (deploy)
- [ ] UptimeRobot configurado
- [ ] Cron job / GitHub Actions configurado

**Diário**:
- [ ] `python run_daily_monitoring.py`
- [ ] Verificar alertas
- [ ] Analisar métricas

**Semanal**:
- [ ] Backup de logs e monitoring/
- [ ] Revisar tendências de performance
- [ ] Verificar taxa de drift

**Mensal**:
- [ ] Limpar logs antigos
- [ ] Analisar histórico de alertas
- [ ] Re-treinar modelo (se necessário)

---

**Criado por**: GitHub Copilot  
**Data**: Novembro 2025  
**Projeto**: PredictFinance - Fase 8  
**Versão**: 1.0  
