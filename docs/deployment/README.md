# Deployment do Modelo LSTM - B3SA3 Predictor

## 📦 Artefatos de Produção

### Modelo Treinado
- **Arquivo**: `lstm_model_best.h5`
- **Formato**: HDF5 (Keras/TensorFlow)
- **Tamanho**: 0.39 MB
- **Parâmetros**: 30,369

### Scaler de Normalização
- **Arquivo**: `scaler.pkl`
- **Formato**: PKL (joblib)
- **Tipo**: MinMaxScaler
- **Range**: [0, 1]

## 🔧 Especificações Técnicas

### Input do Modelo
- **Shape**: [None, 60, 5]
- **Timesteps**: 60 dias
- **Features**: 5 por dia
- **Ordem**: Open, High, Low, Close, Volume

### Output do Modelo
- **Shape**: [None, 1]
- **Tipo**: Preço de fechamento normalizado
- **Range**: [0, 1]

## 📝 Como Usar

### 1. Carregar Artefatos

```python
import joblib
from tensorflow import keras

# Carregar modelo
model = keras.models.load_model('models/lstm_model_best.h5')

# Carregar scaler
scaler = joblib.load('models/scaler.pkl')
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

print(f"Preço previsto: R$ {preco_previsto:.2f}")
```

## ✅ Validação

### Testes Realizados
- ✅ Carregamento do modelo: **Sucesso**
- ✅ Carregamento do scaler: **Sucesso**
- ✅ Predição de exemplo: **SUCESSO**

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

- **Versão**: 1.0.0
- **Data**: 2025-11-02
- **Status**: Produção

---

Gerado automaticamente em 2025-11-02 16:31:21
