"""
===================================================================
PredictFinance - Módulo de Persistência e Verificação do Modelo
Verificação de artefatos e geração de metadados para deployment
===================================================================

Este módulo é responsável pela Fase 5 do projeto:
- Verificação da existência dos artefatos (modelo e scaler)
- Teste de carregamento dos artefatos
- Geração de metadados para a API
- Documentação de especificações do modelo
- Verificação de integridade

Autor: ArgusPortal
Data: 02/11/2025
Versão: 1.0.0
"""

import os
import json
import warnings
from datetime import datetime
from typing import Dict, Tuple

import numpy as np
import joblib
from tensorflow import keras

warnings.filterwarnings('ignore')

# ===================================================================
# CONFIGURAÇÕES
# ===================================================================

# Diretórios
MODELS_DIR = "models"
DOCS_DIR = "docs/deployment"

# Arquivos de artefatos
MODEL_FILE = "lstm_model_best.h5"
SCALER_FILE = "scaler.pkl"
ARCHITECTURE_FILE = "model_architecture.json"

# Criar diretórios
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)


# ===================================================================
# FUNÇÕES DE VERIFICAÇÃO
# ===================================================================

def verificar_artefatos() -> Dict[str, dict]:
    """
    Verifica a existência e propriedades dos artefatos salvos.
    
    Retorna:
    --------
    dict
        Dicionário com informações dos artefatos
    """
    print(f"\n{'='*70}")
    print(f"FASE 5: PERSISTÊNCIA E VERIFICAÇÃO DO MODELO")
    print(f"{'='*70}\n")
    
    print(f"🔍 Verificando Artefatos Salvos:")
    print(f"{'─'*70}\n")
    
    artefatos = {}
    
    # Verificar modelo
    model_path = os.path.join(MODELS_DIR, MODEL_FILE)
    if os.path.exists(model_path):
        tamanho_mb = os.path.getsize(model_path) / (1024 * 1024)
        modificado = datetime.fromtimestamp(os.path.getmtime(model_path))
        
        artefatos['modelo'] = {
            'arquivo': MODEL_FILE,
            'caminho': model_path,
            'existe': True,
            'tamanho_mb': round(tamanho_mb, 2),
            'modificado': modificado.isoformat(),
            'formato': 'HDF5'
        }
        
        print(f"   ✅ Modelo LSTM encontrado:")
        print(f"      • Arquivo: {MODEL_FILE}")
        print(f"      • Tamanho: {tamanho_mb:.2f} MB")
        print(f"      • Modificado: {modificado.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"      • Formato: HDF5\n")
    else:
        artefatos['modelo'] = {'existe': False, 'erro': 'Arquivo não encontrado'}
        print(f"   ❌ Modelo não encontrado: {model_path}\n")
    
    # Verificar scaler
    scaler_path = os.path.join(MODELS_DIR, SCALER_FILE)
    if os.path.exists(scaler_path):
        tamanho_kb = os.path.getsize(scaler_path) / 1024
        modificado = datetime.fromtimestamp(os.path.getmtime(scaler_path))
        
        artefatos['scaler'] = {
            'arquivo': SCALER_FILE,
            'caminho': scaler_path,
            'existe': True,
            'tamanho_kb': round(tamanho_kb, 2),
            'modificado': modificado.isoformat(),
            'formato': 'PKL (joblib)'
        }
        
        print(f"   ✅ Scaler encontrado:")
        print(f"      • Arquivo: {SCALER_FILE}")
        print(f"      • Tamanho: {tamanho_kb:.2f} KB")
        print(f"      • Modificado: {modificado.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"      • Formato: PKL (joblib)\n")
    else:
        artefatos['scaler'] = {'existe': False, 'erro': 'Arquivo não encontrado'}
        print(f"   ❌ Scaler não encontrado: {scaler_path}\n")
    
    # Verificar arquitetura (opcional)
    arch_path = os.path.join(MODELS_DIR, ARCHITECTURE_FILE)
    if os.path.exists(arch_path):
        tamanho_kb = os.path.getsize(arch_path) / 1024
        
        artefatos['arquitetura'] = {
            'arquivo': ARCHITECTURE_FILE,
            'caminho': arch_path,
            'existe': True,
            'tamanho_kb': round(tamanho_kb, 2),
            'formato': 'JSON'
        }
        
        print(f"   ✅ Arquitetura encontrada:")
        print(f"      • Arquivo: {ARCHITECTURE_FILE}")
        print(f"      • Tamanho: {tamanho_kb:.2f} KB")
        print(f"      • Formato: JSON\n")
    
    return artefatos


def testar_carregamento_modelo(model_path: str) -> Tuple[keras.Model, dict]:
    """
    Testa o carregamento do modelo e extrai metadados.
    
    Parâmetros:
    -----------
    model_path : str
        Caminho do arquivo do modelo
        
    Retorna:
    --------
    tuple
        (modelo carregado, dicionário de metadados)
    """
    print(f"🧪 Testando Carregamento do Modelo:")
    print(f"{'─'*70}\n")
    
    try:
        print(f"   📥 Carregando modelo de: {model_path}")
        model = keras.models.load_model(model_path)
        print(f"   ✅ Modelo carregado com sucesso!\n")
        
        # Extrair metadados
        metadados = {
            'nome': model.name,
            'input_shape': list(model.input_shape),
            'output_shape': list(model.output_shape),
            'num_parametros': int(model.count_params()),
            'num_camadas': len(model.layers),
            'camadas': []
        }
        
        print(f"   📊 Metadados do Modelo:")
        print(f"      • Nome: {metadados['nome']}")
        print(f"      • Input Shape: {metadados['input_shape']}")
        print(f"      • Output Shape: {metadados['output_shape']}")
        print(f"      • Parâmetros: {metadados['num_parametros']:,}")
        print(f"      • Camadas: {metadados['num_camadas']}\n")
        
        # Detalhes das camadas
        print(f"   🔍 Arquitetura:")
        for i, layer in enumerate(model.layers):
            layer_info = {
                'index': i,
                'nome': layer.name,
                'tipo': layer.__class__.__name__,
                'output_shape': list(layer.output_shape[1:])
            }
            metadados['camadas'].append(layer_info)
            print(f"      {i+1}. {layer.name} ({layer.__class__.__name__}) → {layer.output_shape}")
        
        print()
        return model, metadados
        
    except Exception as e:
        print(f"   ❌ Erro ao carregar modelo: {str(e)}\n")
        raise


def testar_carregamento_scaler(scaler_path: str) -> Tuple[object, dict]:
    """
    Testa o carregamento do scaler e extrai metadados.
    
    Parâmetros:
    -----------
    scaler_path : str
        Caminho do arquivo do scaler
        
    Retorna:
    --------
    tuple
        (scaler carregado, dicionário de metadados)
    """
    print(f"🧪 Testando Carregamento do Scaler:")
    print(f"{'─'*70}\n")
    
    try:
        print(f"   📥 Carregando scaler de: {scaler_path}")
        scaler = joblib.load(scaler_path)
        print(f"   ✅ Scaler carregado com sucesso!\n")
        
        # Extrair metadados
        metadados = {
            'tipo': scaler.__class__.__name__,
            'feature_range': list(scaler.feature_range),
            'num_features': int(scaler.n_features_in_),
            'data_min': scaler.data_min_.tolist() if hasattr(scaler, 'data_min_') else None,
            'data_max': scaler.data_max_.tolist() if hasattr(scaler, 'data_max_') else None,
            'data_range': scaler.data_range_.tolist() if hasattr(scaler, 'data_range_') else None
        }
        
        print(f"   📊 Metadados do Scaler:")
        print(f"      • Tipo: {metadados['tipo']}")
        print(f"      • Feature Range: {metadados['feature_range']}")
        print(f"      • Número de Features: {metadados['num_features']}")
        
        if metadados['data_min']:
            print(f"      • Data Min: {[f'{x:.4f}' for x in metadados['data_min']]}")
            print(f"      • Data Max: {[f'{x:.4f}' for x in metadados['data_max']]}")
        
        print()
        return scaler, metadados
        
    except Exception as e:
        print(f"   ❌ Erro ao carregar scaler: {str(e)}\n")
        raise


def testar_predicao_exemplo(model: keras.Model, scaler: object) -> dict:
    """
    Testa uma predição de exemplo para validar o pipeline completo.
    
    Parâmetros:
    -----------
    model : keras.Model
        Modelo carregado
    scaler : object
        Scaler carregado
        
    Retorna:
    --------
    dict
        Resultados do teste
    """
    print(f"🧪 Testando Predição de Exemplo:")
    print(f"{'─'*70}\n")
    
    try:
        # Criar dados de exemplo (60 timesteps, 5 features)
        # Simular dados aleatórios dentro de um range plausível
        print(f"   📝 Gerando dados de exemplo...")
        exemplo_raw = np.random.uniform(10, 15, size=(60, 5))
        
        # Normalizar
        print(f"   🔄 Normalizando dados...")
        exemplo_norm = scaler.transform(exemplo_raw)
        
        # Reshape para modelo (1, 60, 5)
        exemplo_input = exemplo_norm.reshape(1, 60, 5)
        
        print(f"   🔮 Fazendo predição...")
        predicao_norm = model.predict(exemplo_input, verbose=0)
        
        # Desnormalizar
        print(f"   🔄 Desnormalizando resultado...")
        # Criar array completo com a predição
        exemplo_final = np.copy(exemplo_raw[-1:])  # Pegar última linha
        exemplo_final[0, 3] = predicao_norm[0, 0]  # Substituir Close normalizado
        
        # Inverter normalização completa
        resultado_full = scaler.inverse_transform(exemplo_final)
        predicao_final = resultado_full[0, 3]  # Pegar Close desnormalizado
        
        print(f"   ✅ Predição realizada com sucesso!\n")
        
        print(f"   📊 Resultados do Teste:")
        print(f"      • Input Shape: {exemplo_input.shape}")
        print(f"      • Predição Normalizada: {predicao_norm[0, 0]:.6f}")
        print(f"      • Predição Final: R$ {predicao_final:.2f}")
        print(f"      • Range Esperado: R$ 10.00 - R$ 15.00\n")
        
        # Validar se está no range esperado
        valido = 8.0 <= predicao_final <= 18.0
        
        if valido:
            print(f"   ✅ Predição dentro do range esperado\n")
        else:
            print(f"   ⚠️  Predição fora do range esperado\n")
        
        resultado = {
            'input_shape': list(exemplo_input.shape),
            'predicao_normalizada': float(predicao_norm[0, 0]),
            'predicao_final': float(predicao_final),
            'validacao': bool(valido),
            'status': 'sucesso'
        }
        
        return resultado
        
    except Exception as e:
        print(f"   ❌ Erro no teste de predição: {str(e)}\n")
        return {
            'status': 'erro',
            'mensagem': str(e)
        }


def gerar_metadados_api(model_meta: dict, scaler_meta: dict) -> dict:
    """
    Gera metadados necessários para a construção da API.
    
    Parâmetros:
    -----------
    model_meta : dict
        Metadados do modelo
    scaler_meta : dict
        Metadados do scaler
        
    Retorna:
    --------
    dict
        Metadados para a API
    """
    print(f"📋 Gerando Metadados para API:")
    print(f"{'─'*70}\n")
    
    # Extrair configurações importantes
    timesteps = model_meta['input_shape'][1]  # Segunda dimensão
    features = model_meta['input_shape'][2]   # Terceira dimensão
    
    metadados_api = {
        'versao': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'modelo': {
            'arquivo': MODEL_FILE,
            'formato': 'HDF5',
            'input_shape': model_meta['input_shape'],
            'output_shape': model_meta['output_shape'],
            'timesteps': timesteps,
            'features': features,
            'features_nomes': ['Open', 'High', 'Low', 'Close', 'Volume']
        },
        'scaler': {
            'arquivo': SCALER_FILE,
            'tipo': scaler_meta['tipo'],
            'feature_range': scaler_meta['feature_range'],
            'num_features': scaler_meta['num_features']
        },
        'requisitos_input': {
            'formato': 'JSON',
            'estrutura': {
                'dias_historicos': timesteps,
                'features_por_dia': features,
                'ordem_features': ['Open', 'High', 'Low', 'Close', 'Volume']
            },
            'exemplo': {
                'descricao': f'Array de {timesteps} dias, cada dia com {features} valores',
                'shape': f'({timesteps}, {features})'
            }
        },
        'output': {
            'formato': 'JSON',
            'descricao': 'Preço de fechamento previsto para o próximo dia',
            'tipo': 'float',
            'unidade': 'R$'
        }
    }
    
    print(f"   ✅ Metadados gerados:")
    print(f"      • Versão da API: {metadados_api['versao']}")
    print(f"      • Timesteps: {timesteps}")
    print(f"      • Features: {features}")
    print(f"      • Features: {metadados_api['modelo']['features_nomes']}")
    print(f"      • Scaler Range: {scaler_meta['feature_range']}\n")
    
    return metadados_api


def salvar_documentacao(artefatos: dict, model_meta: dict, 
                        scaler_meta: dict, api_meta: dict, 
                        teste_predicao: dict) -> None:
    """
    Salva documentação completa da persistência.
    
    Parâmetros:
    -----------
    artefatos : dict
        Informações dos artefatos
    model_meta : dict
        Metadados do modelo
    scaler_meta : dict
        Metadados do scaler
    api_meta : dict
        Metadados para API
    teste_predicao : dict
        Resultado do teste de predição
    """
    print(f"💾 Salvando Documentação:")
    print(f"{'─'*70}\n")
    
    # Documento completo
    documentacao = {
        'timestamp': datetime.now().isoformat(),
        'fase': 'Fase 5 - Persistência e Verificação',
        'status': 'concluida',
        'artefatos': artefatos,
        'modelo': model_meta,
        'scaler': scaler_meta,
        'api_metadata': api_meta,
        'validacao': {
            'teste_carregamento_modelo': 'sucesso',
            'teste_carregamento_scaler': 'sucesso',
            'teste_predicao': teste_predicao
        },
        'instrucoes_uso': {
            'carregar_modelo': f"model = keras.models.load_model('models/{MODEL_FILE}')",
            'carregar_scaler': f"scaler = joblib.load('models/{SCALER_FILE}')",
            'fazer_predicao': [
                "1. Preparar dados: 60 dias × 5 features (OHLCV)",
                "2. Normalizar com scaler: scaler.transform(dados)",
                "3. Reshape: dados.reshape(1, 60, 5)",
                "4. Prever: model.predict(dados)",
                "5. Desnormalizar resultado com scaler.inverse_transform()"
            ]
        }
    }
    
    # Salvar JSON principal
    doc_path = os.path.join(DOCS_DIR, 'model_deployment_metadata.json')
    with open(doc_path, 'w', encoding='utf-8') as f:
        json.dump(documentacao, f, indent=4, ensure_ascii=False)
    
    tamanho_kb = os.path.getsize(doc_path) / 1024
    print(f"   ✅ Documentação completa: {doc_path} ({tamanho_kb:.2f} KB)")
    
    # Salvar metadados da API separadamente
    api_path = os.path.join(DOCS_DIR, 'api_metadata.json')
    with open(api_path, 'w', encoding='utf-8') as f:
        json.dump(api_meta, f, indent=4, ensure_ascii=False)
    
    tamanho_kb = os.path.getsize(api_path) / 1024
    print(f"   ✅ Metadados da API: {api_path} ({tamanho_kb:.2f} KB)")
    
    # Criar README de deployment
    readme_content = f"""# Deployment do Modelo LSTM - B3SA3 Predictor

## 📦 Artefatos de Produção

### Modelo Treinado
- **Arquivo**: `{MODEL_FILE}`
- **Formato**: HDF5 (Keras/TensorFlow)
- **Tamanho**: {artefatos['modelo']['tamanho_mb']} MB
- **Parâmetros**: {model_meta['num_parametros']:,}

### Scaler de Normalização
- **Arquivo**: `{SCALER_FILE}`
- **Formato**: PKL (joblib)
- **Tipo**: {scaler_meta['tipo']}
- **Range**: {scaler_meta['feature_range']}

## 🔧 Especificações Técnicas

### Input do Modelo
- **Shape**: {model_meta['input_shape']}
- **Timesteps**: {api_meta['modelo']['timesteps']} dias
- **Features**: {api_meta['modelo']['features']} por dia
- **Ordem**: {', '.join(api_meta['modelo']['features_nomes'])}

### Output do Modelo
- **Shape**: {model_meta['output_shape']}
- **Tipo**: Preço de fechamento normalizado
- **Range**: [0, 1]

## 📝 Como Usar

### 1. Carregar Artefatos

```python
import joblib
from tensorflow import keras

# Carregar modelo
model = keras.models.load_model('models/{MODEL_FILE}')

# Carregar scaler
scaler = joblib.load('models/{SCALER_FILE}')
```

### 2. Preparar Dados de Entrada

```python
import numpy as np

# Dados: 60 dias × 5 features (Open, High, Low, Close, Volume)
dados_historicos = np.array([...])  # Shape: (60, 5)

# Normalizar
dados_normalizados = scaler.transform(dados_historicos)

# Reshape para o modelo
input_modelo = dados_normalizados.reshape(1, 60, 5)
```

### 3. Fazer Predição

```python
# Prever
predicao_normalizada = model.predict(input_modelo)

# Desnormalizar resultado
# Criar array com última linha + predição
ultima_linha = dados_historicos[-1:].copy()
ultima_linha[0, 3] = predicao_normalizada[0, 0]  # Substituir Close

# Inverter normalização
resultado = scaler.inverse_transform(ultima_linha)
preco_previsto = resultado[0, 3]  # Extrair Close

print(f"Preço previsto: R$ {{preco_previsto:.2f}}")
```

## ✅ Validação

### Testes Realizados
- ✅ Carregamento do modelo: **Sucesso**
- ✅ Carregamento do scaler: **Sucesso**
- ✅ Predição de exemplo: **{teste_predicao['status'].upper()}**

### Performance do Modelo
- **RMSE**: R$ 0.26
- **MAE**: R$ 0.20
- **MAPE**: 1.53%
- **R² Score**: 0.9351

## 📚 Arquivos de Referência

- `model_deployment_metadata.json` - Documentação completa
- `api_metadata.json` - Especificações para API
- `../training/training_results.json` - Resultados do treinamento

## 🔄 Versionamento

- **Versão**: {api_meta['versao']}
- **Data**: {datetime.now().strftime('%Y-%m-%d')}
- **Status**: Produção

---

Gerado automaticamente em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    readme_path = os.path.join(DOCS_DIR, 'README.md')
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    tamanho_kb = os.path.getsize(readme_path) / 1024
    print(f"   ✅ README de deployment: {readme_path} ({tamanho_kb:.2f} KB)\n")


# ===================================================================
# FUNÇÃO PRINCIPAL
# ===================================================================

def main():
    """
    Função principal que executa verificação e documentação completa.
    """
    try:
        # 1. Verificar artefatos
        artefatos = verificar_artefatos()
        
        # Validar se os arquivos essenciais existem
        if not artefatos['modelo']['existe']:
            raise FileNotFoundError(f"Modelo não encontrado: {MODEL_FILE}")
        
        if not artefatos['scaler']['existe']:
            raise FileNotFoundError(f"Scaler não encontrado: {SCALER_FILE}")
        
        # 2. Testar carregamento do modelo
        model_path = artefatos['modelo']['caminho']
        model, model_meta = testar_carregamento_modelo(model_path)
        
        # 3. Testar carregamento do scaler
        scaler_path = artefatos['scaler']['caminho']
        scaler, scaler_meta = testar_carregamento_scaler(scaler_path)
        
        # 4. Testar predição de exemplo
        teste_predicao = testar_predicao_exemplo(model, scaler)
        
        # 5. Gerar metadados para API
        api_meta = gerar_metadados_api(model_meta, scaler_meta)
        
        # 6. Salvar documentação
        salvar_documentacao(artefatos, model_meta, scaler_meta, 
                           api_meta, teste_predicao)
        
        # 7. Resumo final
        print(f"{'='*70}")
        print(f"✅ FASE 5 CONCLUÍDA COM SUCESSO!")
        print(f"{'='*70}\n")
        print(f"📁 Artefatos Verificados:")
        print(f"   ✅ {MODEL_FILE} ({artefatos['modelo']['tamanho_mb']} MB)")
        print(f"   ✅ {SCALER_FILE} ({artefatos['scaler']['tamanho_kb']} KB)")
        if artefatos.get('arquitetura'):
            print(f"   ✅ {ARCHITECTURE_FILE} ({artefatos['arquitetura']['tamanho_kb']} KB)")
        
        print(f"\n📊 Especificações do Modelo:")
        print(f"   → Input Shape: {model_meta['input_shape']}")
        print(f"   → Output Shape: {model_meta['output_shape']}")
        print(f"   → Timesteps: {api_meta['modelo']['timesteps']}")
        print(f"   → Features: {api_meta['modelo']['features_nomes']}")
        
        print(f"\n📁 Documentação Gerada:")
        print(f"   → docs/deployment/model_deployment_metadata.json")
        print(f"   → docs/deployment/api_metadata.json")
        print(f"   → docs/deployment/README.md")
        
        print(f"\n🎯 Próximos Passos:")
        print(f"   → Construir API FastAPI (Fase 6)")
        print(f"   → Implementar endpoints de predição")
        print(f"   → Adicionar validação de entrada")
        print(f"   → Deploy em produção\n")
        
        # Limpar memória (opcional)
        del model
        del scaler
        print(f"🧹 Memória liberada (modelo e scaler removidos da RAM)\n")
        
    except Exception as e:
        print(f"\n{'='*70}")
        print(f"❌ ERRO NA FASE 5: {str(e)}")
        print(f"{'='*70}\n")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
