"""
Script para Popular Database SQLite com Dados Históricos

Busca dados do Yahoo Finance e popula banco local SQLite
para uso como fallback quando API falhar.

Uso:
    python database/populate_db.py [--ticker B3SA3.SA] [--years 5]
"""

import sys
from pathlib import Path
import argparse
import time

# Adicionar root ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

import yfinance as yf
from datetime import datetime, timedelta
from database.db_manager import get_db

def buscar_e_popular(ticker: str, years: int = 5):
    """
    Busca dados do Yahoo Finance e popula banco
    
    Args:
        ticker: Símbolo da ação (ex: B3SA3.SA)
        years: Anos de histórico para buscar
    """
    print("=" * 60)
    print(f"🔄 POPULAÇÃO DO DATABASE")
    print("=" * 60)
    print(f"📈 Ticker: {ticker}")
    print(f"📅 Período: {years} anos")
    print(f"🕐 Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # 1. Verificar status atual do banco
        db = get_db()
        stats = db.get_stats(ticker)
        
        if stats['has_data']:
            print(f"\n📊 Dados Existentes:")
            print(f"   Total: {stats['total_records']} registros")
            print(f"   Período: {stats['oldest_date']} até {stats['newest_date']}")
            
            resposta = input("\n⚠️  Deseja sobrescrever? (s/N): ")
            if resposta.lower() != 's':
                print("❌ Cancelado pelo usuário")
                return False
            
            # Deletar dados antigos
            print(f"\n🗑️  Removendo dados antigos...")
            db.delete_ticker(ticker)
        
        # 2. Buscar dados do Yahoo Finance
        print(f"\n📥 Buscando dados do Yahoo Finance...")
        print(f"   Pode levar alguns minutos...")
        
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=years * 365)
        
        stock = yf.Ticker(ticker)
        
        # Tentar com retry
        max_tentativas = 3
        df = None
        
        for tentativa in range(max_tentativas):
            try:
                print(f"   Tentativa {tentativa + 1}/{max_tentativas}...", end=" ")
                
                df = stock.history(
                    start=data_inicio,
                    end=data_fim,
                    interval='1d',
                    auto_adjust=False,
                    timeout=60
                )
                
                if not df.empty:
                    print("✅")
                    break
                else:
                    print("⚠️ Vazio")
                
            except Exception as e:
                print(f"❌ Erro: {str(e)[:50]}")
                if tentativa < max_tentativas - 1:
                    wait_time = 2 ** (tentativa + 1)
                    print(f"   Aguardando {wait_time}s...")
                    time.sleep(wait_time)
        
        if df is None or df.empty:
            print("\n❌ FALHA: Não foi possível buscar dados do Yahoo Finance")
            print("   Possíveis causas:")
            print("   - Ticker inválido")
            print("   - Yahoo Finance bloqueou seu IP")
            print("   - Problema de conexão")
            print("\n💡 Solução alternativa:")
            print("   1. Use VPN")
            print("   2. Aguarde algumas horas")
            print("   3. Execute em outra máquina")
            return False
        
        print(f"\n✅ {len(df)} registros baixados")
        print(f"   Período: {df.index[0].date()} até {df.index[-1].date()}")
        
        # 3. Validar dados
        print(f"\n🔍 Validando dados...")
        
        # Verificar colunas necessárias
        colunas_necessarias = ['Open', 'High', 'Low', 'Close', 'Volume']
        colunas_faltando = [c for c in colunas_necessarias if c not in df.columns]
        
        if colunas_faltando:
            print(f"❌ Colunas faltando: {colunas_faltando}")
            return False
        
        # Verificar valores nulos
        nulos = df[colunas_necessarias].isnull().sum()
        if nulos.any():
            print(f"⚠️  Valores nulos encontrados:")
            print(nulos[nulos > 0])
            print(f"   Removendo linhas com nulos...")
            df = df.dropna(subset=colunas_necessarias)
            print(f"   Restam {len(df)} registros")
        
        # Verificar valores inválidos
        invalidos = (df[['Open', 'High', 'Low', 'Close']] <= 0).any(axis=1).sum()
        if invalidos > 0:
            print(f"⚠️  {invalidos} linhas com valores ≤ 0")
            print(f"   Removendo...")
            df = df[(df[['Open', 'High', 'Low', 'Close']] > 0).all(axis=1)]
            print(f"   Restam {len(df)} registros")
        
        print("✅ Dados válidos")
        
        # 4. Inserir no banco
        print(f"\n💾 Inserindo no banco SQLite...")
        inserted = db.insert_data(ticker, df)
        
        if inserted == 0:
            print("❌ Nenhum registro inserido")
            return False
        
        # 5. Verificar resultado
        print(f"\n✅ {inserted} registros inseridos com sucesso!")
        
        stats_final = db.get_stats(ticker)
        print(f"\n📊 Status Final do Database:")
        print(f"   Total: {stats_final['total_records']} registros")
        print(f"   Período: {stats_final['oldest_date']} até {stats_final['newest_date']}")
        
        # 6. Testar busca
        print(f"\n🧪 Testando busca (últimos 60 dias)...")
        data_array, df_teste = db.get_data(ticker, dias=60)
        
        if data_array is not None:
            print(f"✅ Teste OK: {data_array.shape[0]} dias recuperados")
        else:
            print(f"⚠️  Teste falhou: dados insuficientes")
        
        print("\n" + "=" * 60)
        print("✅ POPULAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print(f"🕐 Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💾 Database: {db.db_path}")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO FATAL:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Popular database SQLite com dados históricos'
    )
    parser.add_argument(
        '--ticker',
        default='B3SA3.SA',
        help='Ticker da ação (default: B3SA3.SA)'
    )
    parser.add_argument(
        '--years',
        type=int,
        default=5,
        help='Anos de histórico (default: 5)'
    )
    
    args = parser.parse_args()
    
    sucesso = buscar_e_popular(args.ticker, args.years)
    
    if sucesso:
        print("\n✅ Pronto para usar!")
        print("   A API agora usará o banco SQLite como fallback")
        return 0
    else:
        print("\n❌ População falhou")
        return 1


if __name__ == "__main__":
    sys.exit(main())
