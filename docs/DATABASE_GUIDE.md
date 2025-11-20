# 📊 Guia do Sistema de Banco de Dados SQLite

## Visão Geral

O sistema utiliza SQLite como cache local de dados históricos OHLCV (Open, High, Low, Close, Volume) para solucionar o problema de bloqueio do Yahoo Finance em ambientes de produção.

### Problema Resolvido

**Situação**: Yahoo Finance bloqueia requisições de IPs compartilhados (Render, Vercel, etc.) com erros 429 e "No timezone found".

**Solução**: Sistema de fallback em 3 níveis:
1. 🌐 **Yahoo Finance** (tentativa com retry)
2. 💾 **SQLite Cache** (fallback primário - NOVO)
3. 📦 **Dados Hardcoded** (último recurso - 60 dias de B3SA3.SA)

## Arquitetura

```
PredictFinance/
├── database/
│   ├── __init__.py          # Exports do módulo
│   ├── db_manager.py        # Classe MarketDataDB
│   ├── populate_db.py       # Script de população inicial
│   ├── update_db.py         # Script de atualização diária
│   ├── README.md            # Documentação técnica
│   └── market_data.db       # Banco SQLite (gerado)
│
├── .github/workflows/
│   └── daily_update_db.yml  # Cron job diário (4h UTC)
│
└── api/
    ├── main.py              # GET /data/historical/{ticker}
    └── data_fetcher.py      # Integração com SQLite fallback
```

## Schema do Banco de Dados

```sql
CREATE TABLE IF NOT EXISTS stock_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    date TEXT NOT NULL,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(ticker, date)
);

CREATE INDEX idx_ticker_date ON stock_data(ticker, date DESC);
CREATE INDEX idx_ticker ON stock_data(ticker);
```

### Características

- **Tamanho**: ~500 KB para 5 anos de dados de um ticker
- **Performance**: Indexes em ticker + date para queries rápidas
- **Integridade**: UNIQUE constraint previne duplicatas
- **Auditoria**: Campo created_at para rastreamento

## Uso Básico

### 1️⃣ População Inicial

```bash
# Popular com 5 anos de B3SA3.SA (padrão)
python database/populate_db.py

# Popular ticker específico
python database/populate_db.py --ticker PETR4.SA --years 3

# Exemplo de saída:
# 🚀 Populando banco de dados SQLite
# ========================================
# Ticker: B3SA3.SA
# Período: 5 anos (2020-01-15 até 2025-01-15)
# 📥 Buscando dados do Yahoo Finance...
# ✅ Dados obtidos: 1250 registros
# ✅ Validação OK
# 💾 1250 novos registros inseridos
```

### 2️⃣ Atualização Manual

```bash
# Atualizar com dados mais recentes
python database/update_db.py

# Atualizar ticker específico
python database/update_db.py --ticker VALE3.SA

# Exemplo de saída:
# 📅 Última data no banco: 2025-01-14
# 📥 Buscando dados de 2025-01-15 até 2025-01-16
# ✅ 1 novo registro inserido
# 📊 Total: 1251 registros
```

### 3️⃣ Uso Programático

```python
from database import get_db

# Obter instância do banco (singleton)
db = get_db()

# Inserir dados
import pandas as pd
df = pd.DataFrame(...)  # OHLCV com DatetimeIndex
db.insert_data('B3SA3.SA', df)

# Buscar últimos 60 dias
data_array, df = db.get_data('B3SA3.SA', dias=60)

# Buscar período específico
df = db.get_data_by_period(
    ticker='B3SA3.SA',
    start_date='2024-01-01',
    end_date='2024-12-31'
)

# Verificar frescor dos dados
ultima_data = db.get_latest_date('B3SA3.SA')
print(f"Última data: {ultima_data}")

# Estatísticas
stats = db.get_stats('B3SA3.SA')
print(f"Total: {stats['total_records']} registros")
print(f"Período: {stats['oldest_date']} até {stats['latest_date']}")
```

## API Endpoints

### GET /data/historical/{ticker}

Retorna dados históricos do cache SQLite para período específico.

**Parâmetros:**
- `ticker` (path): Símbolo da ação (ex: B3SA3.SA)
- `start_date` (query): Data inicial YYYY-MM-DD
- `end_date` (query): Data final YYYY-MM-DD

**Exemplo:**

```bash
# Buscar dados de 2024
curl "http://localhost:8000/data/historical/B3SA3.SA?start_date=2024-01-01&end_date=2024-12-31"
```

**Resposta:**

```json
{
  "ticker": "B3SA3.SA",
  "period": {
    "start": "2024-01-01",
    "end": "2024-12-31"
  },
  "count": 252,
  "data": [
    {
      "date": "2024-01-02",
      "open": 13.45,
      "high": 13.67,
      "low": 13.41,
      "close": 13.58,
      "volume": 42350000
    },
    ...
  ]
}
```

**Erros:**

- `503`: Banco de dados não disponível
- `400`: Formato de data inválido
- `404`: Nenhum dado encontrado para o período
- `500`: Erro interno ao consultar banco

## Atualização Automática

### GitHub Actions (Cron Diário)

O workflow `.github/workflows/daily_update_db.yml` executa automaticamente:

- **Horário**: Todos os dias às 4h UTC (1h BRT - após fechamento do mercado)
- **Função**: Busca dados novos desde última data e atualiza banco
- **Commit**: Faz commit e push automático das mudanças

**Gatilhos:**

1. **Cron Schedule**: Execução automática diária
2. **Manual Dispatch**: Execução manual via GitHub Actions UI

**Execução Manual:**

1. Vá em GitHub → Actions → "Daily Database Update"
2. Clique em "Run workflow"
3. (Opcional) Digite ticker diferente de B3SA3.SA
4. Clique em "Run workflow"

### Fluxo do Cron Job

```
1. Checkout do código
2. Setup Python 3.11
3. Instalar yfinance, pandas
4. Verificar se market_data.db existe
   ├─ NÃO → Criar com populate_db.py (5 anos)
   └─ SIM → Continuar
5. Executar update_db.py
6. Verificar mudanças no .db
   ├─ SIM → Commit + Push
   └─ NÃO → Nada a fazer
7. Notificar sucesso/falha
```

## Integração com data_fetcher.py

O módulo `api/data_fetcher.py` usa o SQLite como fallback primário:

```python
# Fluxo de busca de dados
def buscar_dados_historicos(ticker, dias):
    # 1️⃣ Tenta Yahoo Finance (3 tentativas com backoff)
    for tentativa in range(3):
        df = buscar_yahoo(ticker, dias)
        if not df.empty:
            return df
    
    # 2️⃣ FALLBACK: SQLite Cache (NOVO)
    if DB_DISPONIVEL:
        df = db.get_data(ticker, dias)
        if df is not None:
            print(f"✅ Dados obtidos do cache SQLite")
            return df
    
    # 3️⃣ FALLBACK: Dados Hardcoded (último recurso)
    if ticker == "B3SA3.SA":
        return fallback_data.get_fallback_b3sa3()
    
    # ❌ Nenhum fallback disponível
    raise HTTPException(503, detail="Dados indisponíveis")
```

## Monitoramento e Manutenção

### Verificar Status do Banco

```bash
# Listar estatísticas
python -c "
from database import get_db
db = get_db()
stats = db.get_stats('B3SA3.SA')
print(f'Total: {stats[\"total_records\"]} registros')
print(f'Período: {stats[\"oldest_date\"]} até {stats[\"latest_date\"]}')
"
```

### Limpar Dados de um Ticker

```python
from database import get_db

db = get_db()
db.delete_ticker('B3SA3.SA')
print("✅ Dados removidos")
```

### Recriar Banco Completo

```bash
# Remover banco existente
rm database/market_data.db

# Recriar com 5 anos
python database/populate_db.py --ticker B3SA3.SA --years 5
```

### Logs de Atualização

Verificar logs do GitHub Actions:

1. Vá em GitHub → Actions → "Daily Database Update"
2. Clique na última execução
3. Verifique logs de "update-database"

## Troubleshooting

### ❌ Problema: "No module named 'database'"

**Causa**: Módulo database não encontrado

**Solução**:
```bash
# Verificar estrutura
ls -la database/
# Deve ter: __init__.py, db_manager.py, populate_db.py, update_db.py

# Verificar imports
python -c "from database import get_db; print('OK')"
```

### ❌ Problema: Yahoo Finance retorna dados vazios

**Causa**: Bloqueio temporário ou ticker inválido

**Solução**:
```bash
# Testar manualmente
python -c "
import yfinance as yf
ticker = yf.Ticker('B3SA3.SA')
df = ticker.history(period='5d')
print(df)
"

# Se vazio, aguardar ou usar outro ticker
# O sistema usará cache SQLite automaticamente
```

### ❌ Problema: Banco não atualiza automaticamente

**Causa**: Workflow GitHub Actions não configurado

**Solução**:
1. Verificar arquivo `.github/workflows/daily_update_db.yml` existe
2. Verificar permissões do GitHub Actions:
   - Settings → Actions → General
   - Workflow permissions → Read and write permissions
3. Executar manualmente uma vez para testar

### ❌ Problema: API retorna 503 "Banco não disponível"

**Causa**: market_data.db não existe

**Solução**:
```bash
# Criar banco
python database/populate_db.py

# Verificar criação
ls -lh database/market_data.db

# Testar API
curl http://localhost:8000/data/historical/B3SA3.SA?start_date=2024-01-01&end_date=2024-12-31
```

### ❌ Problema: Dados muito antigos (> 1 dia)

**Causa**: Cron job não está rodando

**Solução**:
```bash
# Atualizar manualmente
python database/update_db.py

# Verificar última execução do cron
# GitHub → Actions → últimas execuções

# Executar manualmente se necessário
# GitHub → Actions → Daily Database Update → Run workflow
```

## Performance

### Benchmarks

- **População inicial**: ~30-60s para 5 anos de dados (1250 registros)
- **Query 60 dias**: < 10ms
- **Query 1 ano**: < 50ms
- **Insert 1 dia**: < 5ms
- **Tamanho disco**: 500 KB para 5 anos

### Otimizações

1. **Indexes**: ticker + date para queries rápidas
2. **Batch Insert**: Insere múltiplos registros de uma vez
3. **UNIQUE Constraint**: Previne duplicatas sem verificação manual
4. **Connection Pooling**: Singleton pattern evita múltiplas conexões

## Migração para Outros Tickers

```bash
# Adicionar PETR4.SA
python database/populate_db.py --ticker PETR4.SA --years 5

# Adicionar VALE3.SA
python database/populate_db.py --ticker VALE3.SA --years 3

# Atualizar todos diariamente
python database/update_db.py --ticker PETR4.SA
python database/update_db.py --ticker VALE3.SA
```

**Nota**: Para múltiplos tickers, considere modificar `update_db.py` para suportar `--all`:

```python
# Implementação futura
if args.all:
    tickers = db.get_all_tickers()  # Método a implementar
    for ticker in tickers:
        atualizar_ticker(ticker)
```

## Deployment

### Render.com

O banco é versionado no Git e automaticamente deployado:

1. Commit `market_data.db` após população inicial
2. Render detecta mudanças e faz redeploy
3. Cron do GitHub Actions atualiza diariamente

### Alternativa: Popular em Produção

Se não quiser versionar o .db:

1. Adicione `database/market_data.db` ao `.gitignore`
2. Configure comando de build no Render:
   ```bash
   python database/populate_db.py && pip install -r requirements.txt
   ```
3. Cron do GitHub Actions não fará push (apenas local)

## Backup e Recuperação

### Backup Manual

```bash
# Copiar banco
cp database/market_data.db database/backups/market_data_$(date +%Y%m%d).db

# Verificar integridade
sqlite3 database/market_data.db "PRAGMA integrity_check;"
```

### Recuperação

```bash
# Restaurar de backup
cp database/backups/market_data_20250115.db database/market_data.db

# Ou recriar do zero
rm database/market_data.db
python database/populate_db.py --years 5
```

## FAQ

**Q: O banco precisa ser versionado no Git?**
A: Recomendado. Com 500KB para 5 anos, é viável e serve como backup.

**Q: Quantos tickers posso armazenar?**
A: Ilimitado. Cada ticker adiciona ~500KB para 5 anos.

**Q: O que acontece se Yahoo Finance bloquear permanentemente?**
A: O sistema continua funcionando com o cache SQLite. Dados novos podem ser adicionados manualmente ou de outras fontes.

**Q: Posso usar PostgreSQL ao invés de SQLite?**
A: Sim, mas SQLite é mais simples para este caso de uso (cache local, leitura pesada, poucos writes).

**Q: Como adicionar mais features (ex: Dividendos)?**
A: Modifique schema em `db_manager.py`, adicione colunas, atualize `populate_db.py` e `update_db.py`.

**Q: O cron rodará em horário de mercado?**
A: Configurado para 4h UTC (1h BRT) após fechamento. Dados de hoje só aparecem no próximo dia.

## Roadmap

- [ ] Implementar `get_all_tickers()` em db_manager.py
- [ ] Suporte a `--all` em update_db.py
- [ ] Adicionar compressão do banco (zstd) se > 10MB
- [ ] Métricas de uso (queries/s, cache hit rate)
- [ ] Dashboard de status do cache
- [ ] Suporte a múltiplos intervalos (1h, 1d, 1wk)
- [ ] Integração com outras fontes de dados (Alpha Vantage, IEX)

## Contato

Para dúvidas ou sugestões sobre o sistema de banco de dados, abra uma issue no GitHub.

---

**Versão**: 1.0.0  
**Última Atualização**: 2025-01-15  
**Autor**: PredictFinance Team
