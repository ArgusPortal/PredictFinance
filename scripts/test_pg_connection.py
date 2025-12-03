"""Script rápido para testar conexão com o banco (Postgres/SQLite)

Ele usa `database.get_db()` para inserir uma previsão de teste e buscá-la.

Execute:
python scripts/test_pg_connection.py
"""
import os
from datetime import datetime

# Ajustar path para importar pacote local
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from database.db_manager import get_db


def main():
    db = get_db()
    print("DATABASE_URL:", os.getenv('DATABASE_URL'))

    req_id = f"test-{int(datetime.now().timestamp())}"
    ts = datetime.now().isoformat()
    ticker = os.getenv('TICKER', 'B3SA3.SA')
    predicted = 123.45

    print(f"Inserindo previsão de teste {req_id}...")
    ok = db.insert_prediction(request_id=req_id, ticker=ticker, timestamp=ts, predicted_value=predicted)
    print("Inserção OK?", ok)

    print("Buscando últimas previsões (limit 5)...")
    preds = db.get_predictions(ticker=ticker, limit=5)
    print("Encontradas:", len(preds))
    for p in preds:
        print(p)

    # Se possível, tentar validar (somente para teste)
    if preds:
        first = preds[0]
        print("Tentando validar primeira previsão (simulada)...")
        validated = db.update_prediction_validation(
            request_id=first['request_id'],
            actual_value=predicted + 1.0,
            error=1.0,
            error_pct=0.81,
            validation_date=datetime.now().isoformat()
        )
        print("Validação OK?", validated)


if __name__ == '__main__':
    main()
