# Database Module

Gerenciamento de cache SQLite para dados históricos de mercado.

## 📁 Arquivos

- `db_manager.py` - Classe principal para gerenciar SQLite
- `populate_db.py` - Script para popular banco inicial
- `market_data.db` - Banco SQLite (gerado automaticamente)

## 🚀 Quick Start

### 1. Popular Banco (Primeira Vez)

```bash
# Popular com B3SA3.SA (5 anos)
python database/populate_db.py

# Outro ticker
python database/populate_db.py --ticker PETR4.SA --years 3
```

### 2. Usar no Código

```python
from database.db_manager import get_db

db = get_db()

# Buscar últimos 60 dias
data_array, df = db.get_data('B3SA3.SA', dias=60)

# Buscar período específico
df = db.get_data_by_period(
    'B3SA3.SA',
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 12, 31)
)

# Ver estatísticas
stats = db.get_stats('B3SA3.SA')
print(stats)
```

## 📊 Schema

```sql
CREATE TABLE stock_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    date DATE NOT NULL,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, date)
);

-- Índices para performance
CREATE INDEX idx_ticker_date ON stock_data(ticker, date DESC);
CREATE INDEX idx_ticker ON stock_data(ticker);
```

## 🔄 Atualização Diária

Ver `.github/workflows/daily_update_db.yml` para atualização automática.

## 💾 Tamanho

**B3SA3.SA com ~6 anos (2020-2025):**
- Total: 1468 registros
- Tamanho: ~284 KB
- Performance: < 10ms para queries

Muito leve e facilmente versionável!
