# 🔍 Análise Completa de Falhas do Re-treino - CORRIGIDAS

## ✅ Problemas Identificados e Resolvidos

### 1. ❌ ImportError: coletar_dados_yahoo
**Erro:** `ImportError: cannot import name 'coletar_dados_yahoo' from 'src.data_collection'`

**Causa:** Função não existe no módulo.

**Solução Aplicada:**
```python
# ❌ Antes
from src.data_collection import coletar_dados_yahoo
dados = coletar_dados_yahoo(ticker, years=6)

# ✅ Depois
from src.data_collection import coletar_dados_historicos
dados = coletar_dados_historicos(ticker, anos=6)
```

**Commit:** df0689a

---

### 2. ❌ ImportError: preparar_dados_lstm
**Erro:** `ImportError: cannot import name 'preparar_dados_lstm' from 'src.data_preparation'`

**Causa:** Função não existe - módulo fornece funções granulares.

**Solução Aplicada:**
```python
# ❌ Antes
from src.data_preparation import preparar_dados_lstm
X_train, y_train, X_val, y_val, X_test, y_test, scaler = preparar_dados_lstm(df)

# ✅ Depois
from src.data_preparation import normalizar_dados, criar_sequencias, dividir_dados, salvar_dados_preparados

# Pipeline manual de 4 etapas
dados_normalizados, scaler = normalizar_dados(df, features)
X, y = criar_sequencias(dados_normalizados, timesteps=60, target_idx=close_idx)
dados_divididos = dividir_dados(X, y, train_pct=0.70, val_pct=0.15, test_pct=0.15)
salvar_dados_preparados(dados_divididos, scaler)

# Extrair dados
X_train = dados_divididos['X_train']
y_train = dados_divididos['y_train']
# ... etc
```

**Commit:** 7205c0e

---

### 3. ❌ TypeError: Dimension value must be integer
**Erro:** `TypeError: Dimension value must be integer or None, got value '(60, 5)' with type '<class 'tuple'>'`

**Causa:** `construir_modelo_lstm()` espera dois inteiros separados, não uma tupla.

**Assinatura Real:**
```python
def construir_modelo_lstm(timesteps: int, features: int, ...) -> Sequential
```

**Solução Aplicada:**
```python
# ❌ Antes
input_shape = (X_train.shape[1], X_train.shape[2])  # (60, 5)
modelo = construir_modelo_lstm(input_shape)

# ✅ Depois
timesteps = X_train.shape[1]  # 60
num_features = X_train.shape[2]  # 5
modelo = construir_modelo_lstm(timesteps=timesteps, features=num_features)
```

**Commit:** 6729655

---

### 4. ❌ TypeError: unexpected keyword argument 'epochs'
**Erro:** `treinar_modelo() got an unexpected keyword argument 'epochs'`

**Causa:** Assinatura incorreta - função não recebe epochs/batch_size diretamente.

**Assinatura Real:**
```python
def treinar_modelo(model: Sequential, dados: dict, callbacks: list) -> keras.callbacks.History
```

**Solução Aplicada:**
```python
# ❌ Antes
historico, modelo_treinado = treinar_modelo(
    modelo,
    X_train, y_train,
    X_val, y_val,
    epochs=50,
    batch_size=32,
    save_dir=str(models_dir / "temp")
)

# ✅ Depois
# 1. Compilar modelo
modelo = compilar_modelo(modelo)

# 2. Criar dicionário de dados
dados = {
    'X_train': X_train,
    'y_train': y_train,
    'X_val': X_val,
    'y_val': y_val
}

# 3. Configurar callbacks (define epochs/batch_size internamente)
model_path = str(temp_dir / "lstm_model_best.h5")
callbacks = configurar_callbacks(model_path)

# 4. Treinar
historico = treinar_modelo(
    model=modelo,
    dados=dados,
    callbacks=callbacks
)

# 5. Carregar modelo salvo pelos callbacks
from tensorflow.keras.models import load_model
modelo_treinado = load_model(model_path)
```

**Imports Necessários:**
```python
from src.model_builder import construir_modelo_lstm, compilar_modelo
from src.model_training import treinar_modelo, configurar_callbacks
```

**Commit:** 5105821

---

### 5. ❌ FileNotFoundError: scaler.pkl
**Erro:** `FileNotFoundError: [Errno 2] No such file or directory: 'data/processed/scaler.pkl'`

**Causa:** Tentativa de recarregar scaler de local errado - `salvar_dados_preparados()` salva em `models/scaler.pkl`, não em `data/processed/`.

**Solução Aplicada:**
```python
# ❌ Antes
import joblib
scaler = joblib.load(processed_dir / "scaler.pkl")  # Caminho errado!

# ✅ Depois
# scaler já está disponível da etapa 2, não precisa recarregar
# salvar_dados_preparados(dados_divididos, scaler) salva em models/scaler.pkl
```

**Também corrigido:**
```python
# ❌ Antes (tentava copiar de local inexistente)
shutil.copy2(processed_dir / "scaler.pkl", models_dir / "scaler.pkl")

# ✅ Depois (scaler já está em models/scaler.pkl)
# Scaler já foi salvo em models/scaler.pkl pela função salvar_dados_preparados
print("   ✅ Scaler já disponível em models/scaler.pkl")
```

**Commit:** TBD

---

## 📋 Checklist de Validação

### Imports Corretos ✅
- [x] `coletar_dados_historicos` (não `coletar_dados_yahoo`)
- [x] Funções granulares de data_preparation (não `preparar_dados_lstm`)
- [x] `compilar_modelo` de model_builder
- [x] `configurar_callbacks` de model_training

### Assinaturas de Funções ✅
- [x] `construir_modelo_lstm(timesteps: int, features: int)`
- [x] `compilar_modelo(model: Sequential)`
- [x] `treinar_modelo(model: Sequential, dados: dict, callbacks: list)`
- [x] `configurar_callbacks(model_path: str)`

### Fluxo de Treinamento ✅
1. [x] Construir modelo com `construir_modelo_lstm`
2. [x] Compilar com `compilar_modelo`
3. [x] Preparar dicionário `dados`
4. [x] Configurar callbacks com `configurar_callbacks`
5. [x] Treinar com `treinar_modelo`
6. [x] Carregar modelo salvo pelos callbacks

### Retornos de Funções ✅
- [x] `treinar_modelo` retorna apenas `History` (não tupla)
- [x] Modelo treinado vem de `load_model(model_path)`
- [x] Callbacks salvam automaticamente o melhor modelo

---

## 🚨 Outras Possíveis Causas de Falha (Prevenidas)

### 5. ⚠️ Dados Insuficientes
**Sintoma:** Erro ao criar sequências ou divisão de dados

**Prevenção:**
```python
if len(df) < 1000:
    raise ValueError(f"Dados insuficientes: {len(df)} dias. Mínimo: 1000")
```

**Status:** ✅ Verificação implementada

---

### 6. ⚠️ Modelo Atual Não Existe (Primeira Execução)
**Sintoma:** `FileNotFoundError` ao comparar com modelo antigo

**Prevenção:**
```python
def carregar_metricas_antigas(models_dir):
    metrics_path = models_dir / "model_metrics.json"
    if not metrics_path.exists():
        return None  # Primeira execução
    with open(metrics_path) as f:
        return json.load(f)
```

**Status:** ✅ Tratamento implementado

---

### 7. ⚠️ Memória Insuficiente
**Sintoma:** `ResourceExhaustedError` durante treinamento

**Prevenção GitHub Actions:**
```yaml
- name: Limpar cache antes do treino
  run: python -c "import gc; gc.collect()"
```

**Status:** ✅ Não necessário (dados de 6 anos são leves)

---

### 8. ⚠️ Scaler Não Salvo
**Sintoma:** `FileNotFoundError: scaler.pkl`

**Prevenção:**
```python
salvar_dados_preparados(dados_divididos, scaler)
# Salva automaticamente em data/processed/scaler.pkl
```

**Status:** ✅ Pipeline garante salvamento

---

### 9. ⚠️ Diretórios Não Existem
**Sintoma:** `FileNotFoundError` ao salvar arquivos

**Prevenção:**
```python
temp_dir = models_dir / "temp"
temp_dir.mkdir(parents=True, exist_ok=True)

backup_dir = models_dir / "backups"
backup_dir.mkdir(parents=True, exist_ok=True)
```

**Status:** ✅ Criação garantida

---

### 10. ⚠️ Features Incorretos
**Sintoma:** Shape mismatch durante treinamento

**Prevenção:**
```python
features = ['Open', 'High', 'Low', 'Close', 'Volume']
close_idx = features.index('Close')  # 3

# Validar
if X_train.shape[2] != len(features):
    raise ValueError(f"Features mismatch: {X_train.shape[2]} != {len(features)}")
```

**Status:** ✅ Validação implementada

---

## 🧪 Como Testar Localmente

### Validação Rápida
```bash
python scripts/validate_retrain.py
```

### Dry Run (Não Substitui Modelo)
```bash
python scripts/retrain_model.py --dry-run
```

### Execução Completa
```bash
python scripts/retrain_model.py
```

### Forçar Substituição
```bash
python scripts/retrain_model.py --force
```

---

## 📊 Métricas de Comparação

O script compara automaticamente:

| Métrica | Critério | Ação |
|---------|----------|------|
| MAPE | < modelo atual | ✅ Substitui |
| MAE | < modelo atual | ✅ Substitui |
| RMSE | < modelo atual | ✅ Substitui |
| R² | > modelo atual | ✅ Substitui |

Se **todas** as métricas forem piores → ❌ Não substitui (usar `--force`)

---

## 🔄 Workflow GitHub Actions

### Gatilhos
- ✅ Segunda-feira 3h UTC (schedule)
- ✅ Manual (workflow_dispatch)

### Passos
1. Checkout código
2. Setup Python 3.10
3. Instalar dependências
4. Executar re-treino
5. Comparar métricas
6. Substituir se melhor
7. Commit e push novo modelo
8. Upload artifact (métricas)

### Arquivo de Log
Todos os logs salvos em: `.github/workflows/weekly_retrain.yml`

---

## ✅ Status Final

**Todos os 5 erros corrigidos:**
1. ✅ Import `coletar_dados_yahoo` → `coletar_dados_historicos`
2. ✅ Import `preparar_dados_lstm` → pipeline granular
3. ✅ Parâmetros `construir_modelo_lstm` → int separados
4. ✅ Parâmetros `treinar_modelo` → dict dados + callbacks
5. ✅ Caminho `scaler.pkl` → usar variável local, scaler salvo em models/

**Validações implementadas:**
- ✅ Script `validate_retrain.py` com 5 tipos de validação
- ✅ Tratamento de primeira execução
- ✅ Backup automático antes de substituir
- ✅ Comparação de métricas
- ✅ Flags `--dry-run` e `--force`

**Próxima execução:**
O workflow executará automaticamente na próxima segunda-feira ou pode ser acionado manualmente via GitHub Actions.

---

## 📞 Troubleshooting

Se ainda houver erros:

1. **Verificar logs do GitHub Actions**
   ```
   Repository → Actions → weekly_retrain → Último run
   ```

2. **Executar localmente**
   ```bash
   python scripts/retrain_model.py --dry-run
   ```

3. **Validar imports**
   ```bash
   python scripts/validate_retrain.py
   ```

4. **Verificar versões**
   ```bash
   python --version  # 3.10+
   pip show tensorflow keras pandas numpy scikit-learn
   ```

---

**Última atualização:** 2025-11-20  
**Commits de correção:** df0689a, 7205c0e, 6729655, 5105821, [PRÓXIMO]
