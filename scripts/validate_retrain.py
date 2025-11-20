"""
Script de Validação do Sistema de Re-treino
Verifica se todos os imports e dependências estão corretos
"""

import sys
from pathlib import Path

# Adicionar src ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

def main():
    print("🔍 Validando Sistema de Re-treino...\n")
    
    # 1. Validar imports
    print("1️⃣ Validando imports...")
    try:
        from src.data_collection import coletar_dados_historicos
        print("   ✅ src.data_collection.coletar_dados_historicos")
    except ImportError as e:
        print(f"   ❌ Erro: {e}")
        return False
    
    try:
        from src.data_preparation import (
            normalizar_dados,
            criar_sequencias,
            dividir_dados,
            salvar_dados_preparados
        )
        print("   ✅ src.data_preparation.normalizar_dados")
        print("   ✅ src.data_preparation.criar_sequencias")
        print("   ✅ src.data_preparation.dividir_dados")
        print("   ✅ src.data_preparation.salvar_dados_preparados")
    except ImportError as e:
        print(f"   ❌ Erro: {e}")
        return False
    
    try:
        from src.model_training import construir_modelo_lstm, treinar_modelo
        print("   ✅ src.model_training.construir_modelo_lstm")
        print("   ✅ src.model_training.treinar_modelo")
    except ImportError as e:
        print(f"   ❌ Erro: {e}")
        return False
    
    # 2. Validar assinatura da função
    print("\n2️⃣ Validando assinatura de coletar_dados_historicos...")
    import inspect
    sig = inspect.signature(coletar_dados_historicos)
    params = list(sig.parameters.keys())
    expected = ['ticker', 'anos']
    
    if params == expected:
        print(f"   ✅ Parâmetros corretos: {params}")
    else:
        print(f"   ❌ Parâmetros incorretos!")
        print(f"      Esperado: {expected}")
        print(f"      Encontrado: {params}")
        return False
    
    # 3. Validar estrutura de diretórios
    print("\n3️⃣ Validando estrutura de diretórios...")
    required_dirs = [
        ROOT_DIR / "data" / "raw",
        ROOT_DIR / "data" / "processed",
        ROOT_DIR / "models",
        ROOT_DIR / "models" / "backups"
    ]
    
    for dir_path in required_dirs:
        if dir_path.exists():
            print(f"   ✅ {dir_path.relative_to(ROOT_DIR)}")
        else:
            print(f"   ⚠️  {dir_path.relative_to(ROOT_DIR)} (será criado)")
    
    # 4. Validar arquivos essenciais
    print("\n4️⃣ Validando arquivos essenciais...")
    essential_files = [
        ROOT_DIR / "scripts" / "retrain_model.py",
        ROOT_DIR / "src" / "data_collection.py",
        ROOT_DIR / "src" / "data_preparation.py",
        ROOT_DIR / "src" / "model_training.py"
    ]
    
    for file_path in essential_files:
        if file_path.exists():
            print(f"   ✅ {file_path.relative_to(ROOT_DIR)}")
        else:
            print(f"   ❌ {file_path.relative_to(ROOT_DIR)} FALTANDO!")
            return False
    
    print("\n" + "="*60)
    print("✅ TODAS AS VALIDAÇÕES PASSARAM!")
    print("="*60)
    print("\n💡 O sistema de re-treino está pronto para uso.")
    print("\nPara testar:")
    print("  python scripts/retrain_model.py --dry-run")
    print("\nPara executar:")
    print("  python scripts/retrain_model.py")
    print("\nPara forçar substituição:")
    print("  python scripts/retrain_model.py --force")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
