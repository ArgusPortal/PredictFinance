#!/usr/bin/env python3
"""
Teste para verificar serialização Arrow
"""

import pandas as pd
import pyarrow as pa

# Simular o DataFrame problemático (ANTES)
print("❌ TESTE 1: DataFrame com tipos mistos (int + string 'N/A')")
try:
    df_bad = pd.DataFrame({
        "Métrica": ["Total Validado", "Total Pendente", "MAPE"],
        "Valor": [0, 0, "N/A"]  # int + string = PROBLEMA
    })
    
    table = pa.Table.from_pandas(df_bad)
    print(f"   Erro esperado mas não aconteceu: {table}")
except Exception as e:
    print(f"   ✅ Erro capturado: {str(e)[:60]}...")

print()

# Solução 1: Converter tudo para string
print("✅ TESTE 2: DataFrame com tudo como string")
try:
    df_good1 = pd.DataFrame({
        "Métrica": ["Total Validado", "Total Pendente", "MAPE"],
        "Valor": ["0", "0", "—"]  # Tudo string = OK
    })
    
    table = pa.Table.from_pandas(df_good1)
    print(f"   ✅ Sucesso! {len(df_good1)} linhas serializadas")
except Exception as e:
    print(f"   ❌ Erro inesperado: {e}")

print()

# Solução 2: Usar None ao invés de string
print("✅ TESTE 3: DataFrame com None para valores ausentes")
try:
    df_good2 = pd.DataFrame({
        "Métrica": ["Total Validado", "Total Pendente", "MAPE"],
        "Valor": [0, 0, None]  # int + None = OK
    })
    
    table = pa.Table.from_pandas(df_good2)
    print(f"   ✅ Sucesso! {len(df_good2)} linhas serializadas")
    print(f"   Valor None vira: {df_good2['Valor'].iloc[2]}")
except Exception as e:
    print(f"   ❌ Erro inesperado: {e}")

print()
print("=" * 70)
print("📊 CONCLUSÃO:")
print("   - Misturar int + string causa erro Arrow")
print("   - Solução: converter tudo para string (str(valor))")
print("   - Caractere '—' (em-dash) funciona perfeitamente")
print("=" * 70)
