# 🚀 Deploy da API B3SA3.SA no Render

## 📋 Pré-requisitos Completos

Antes de iniciar o deploy, certifique-se de que todos os artefatos estão prontos:

### ✅ Checklist de Arquivos

- [x] `api/main.py` - Aplicação FastAPI
- [x] `api/schemas.py` - Modelos Pydantic
- [x] `api/__init__.py` - Inicialização do módulo
- [x] `models/lstm_model_best.h5` - Modelo treinado (0.39 MB)
- [x] `models/scaler.pkl` - Scaler MinMax (0.86 KB)
- [x] `requirements-render.txt` - Dependências otimizadas
- [x] `render.yaml` - Configuração do Render
- [x] `Procfile` - Comando de inicialização (backup)
- [x] `.gitignore` - Configurado para incluir modelos

---

## 📦 Preparação dos Arquivos

### 1. Verificar Artefatos do Modelo

```bash
# Verificar existência e tamanho dos arquivos
ls -lh models/

# Saída esperada:
# lstm_model_best.h5     (0.39 MB)
# scaler.pkl             (0.86 KB)
# model_architecture.json
```

### 2. Dependências Otimizadas

O arquivo `requirements-render.txt` foi criado com dependências otimizadas:

```txt
# Core Framework
fastapi==0.109.2
uvicorn[standard]==0.27.1
pydantic==2.5.3

# Machine Learning (CPU only)
tensorflow-cpu==2.15.1
scikit-learn==1.3.2
numpy==1.24.4

# Data Processing
pandas==2.0.3

# Model Persistence
joblib==1.5.2
```

**Motivo do tensorflow-cpu**: Reduz significativamente o tamanho do build (~500MB vs ~2GB).

### 3. Configuração do Render

Arquivo `render.yaml` criado:

```yaml
services:
  - type: web
    name: b3sa3-api
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r requirements-render.txt
    startCommand: uvicorn api.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.10.11
```

---

## 🔧 Configuração do Repositório GitHub

### Passo 1: Commitar Arquivos

```bash
# Verificar status
git status

# Adicionar novos arquivos de deploy
git add requirements-render.txt
git add render.yaml
git add Procfile
git add .gitignore

# Adicionar modelos (necessários para deploy)
git add models/lstm_model_best.h5
git add models/scaler.pkl
git add models/model_architecture.json

# Adicionar código da API
git add api/
git add run_api.py

# Commit
git commit -m "feat: Adicionar configuração para deploy no Render (Fase 7)"

# Push para GitHub
git push origin main
```

**⚠️ IMPORTANTE**: Certifique-se de que o repositório está configurado:

```bash
# Verificar remote
git remote -v

# Se necessário, adicionar remote
git remote add origin https://github.com/ArgusPortal/PredictFinance.git
```

---

## 🌐 Deploy no Render

### Passo 1: Criar Conta no Render

1. Acesse: https://render.com/
2. Clique em **"Get Started for Free"**
3. Faça login com sua conta GitHub
4. Autorize o Render a acessar seus repositórios

### Passo 2: Criar Novo Web Service

1. No Dashboard do Render, clique em **"New +"**
2. Selecione **"Web Service"**
3. Conecte seu repositório:
   - Se aparecer a lista, selecione **"PredictFinance"**
   - Se não aparecer, clique em **"Configure account"** e autorize acesso

### Passo 3: Configurar o Service

Preencha os campos:

| Campo | Valor |
|-------|-------|
| **Name** | `b3sa3-api` (ou nome de sua preferência) |
| **Region** | `Oregon (US West)` (free tier) |
| **Branch** | `main` |
| **Root Directory** | (deixar em branco) |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements-render.txt` |
| **Start Command** | `uvicorn api.main:app --host 0.0.0.0 --port $PORT` |
| **Plan** | `Free` |

### Passo 4: Variáveis de Ambiente (Opcional)

Não são necessárias variáveis de ambiente adicionais, pois:
- ✅ Modelo e scaler estão no repositório
- ✅ Não há credenciais externas
- ✅ PORT é definido automaticamente pelo Render

Se quiser adicionar (opcional):

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.10.11` |

### Passo 5: Iniciar Deploy

1. Clique em **"Create Web Service"**
2. O Render iniciará o build automaticamente
3. Acompanhe os logs em tempo real

---

## 📊 Monitoramento do Build

### Logs Esperados

Durante o build, você verá:

```
==> Cloning from https://github.com/ArgusPortal/PredictFinance...
==> Checking out commit abc123...
==> Installing dependencies from requirements-render.txt
    Collecting fastapi==0.109.2
    Collecting uvicorn[standard]==0.27.1
    Collecting tensorflow-cpu==2.15.1
    ...
==> Build successful
==> Starting service with: uvicorn api.main:app --host 0.0.0.0 --port $PORT
🚀 Iniciando API...
📂 Carregando artefatos do modelo...
   └─ Carregando modelo: models/lstm_model_best.h5
   ✅ Modelo carregado com sucesso!
   └─ Carregando scaler: models/scaler.pkl
   ✅ Scaler carregado com sucesso!
✅ API pronta para receber requisições!
INFO:     Uvicorn running on http://0.0.0.0:10000
```

### Tempo de Build Estimado

- **Install dependencies**: 3-5 minutos
- **Start service**: 10-15 segundos
- **Total**: ~5 minutos

---

## 🧪 Testes da API em Produção

### Obter URL da API

Após deploy bem-sucedido:

1. No Dashboard do Render, copie a URL do serviço
2. Formato: `https://b3sa3-api.onrender.com`

### Teste 1: Health Check

```bash
curl https://b3sa3-api.onrender.com/
```

**Resposta esperada**:
```json
{
  "status": "ativo",
  "mensagem": "API de previsão B3SA3.SA operacional",
  "versao": "1.0.0",
  "modelo_carregado": true
}
```

### Teste 2: Informações do Modelo

```bash
curl https://b3sa3-api.onrender.com/info
```

**Resposta esperada**:
```json
{
  "nome": "LSTM_B3SA3_Predictor",
  "arquitetura": "LSTM - 2 camadas (64 → 32 unidades) + Dropout (0.2)",
  "parametros": 30369,
  "metricas": {
    "RMSE": "R$ 0.26",
    "MAE": "R$ 0.20",
    "MAPE": "1.53%",
    "R2": "0.9351"
  }
}
```

### Teste 3: Fazer Previsão

```bash
# Opção 1: Previsão AUTOMÁTICA (recomendado)
curl -X POST https://b3sa3-api.onrender.com/predict/auto \
  -H "Content-Type: application/json" \
  -d '{"ticker": "B3SA3.SA"}'

# Opção 2: Previsão com dados manuais (60 dias × 5 features)
# Veja docs/FASE_7_GUIA.md para exemplo completo
```

**Resposta esperada**:
```json
{
  "preco_previsto": 11.52,
  "confianca": "alta",
  "mensagem": "Previsão para B3SA3.SA gerada com sucesso. Modelo MAPE 1.53%..."
}
```

### Teste 4: Documentação Swagger

Acesse no navegador:

```
https://b3sa3-api.onrender.com/docs
```

Você verá a interface interativa do Swagger UI.

---

## 🐍 Script de Teste Python

Criar arquivo `test_production.py`:

```python
"""
Script de Teste da API em Produção (Render)
"""

import requests
import json

# Substituir pela sua URL do Render
API_URL = "https://b3sa3-api.onrender.com"

def testar_api_producao():
    """Testa todos os endpoints da API em produção."""
    
    print("=" * 70)
    print(" " * 15 + "🧪 TESTE DA API EM PRODUÇÃO")
    print("=" * 70)
    print(f"\n📍 URL: {API_URL}\n")
    
    # Teste 1: Health Check
    print("1️⃣  Health Check")
    print("-" * 70)
    try:
        response = requests.get(f"{API_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        print("✅ Passou!\n")
    except Exception as e:
        print(f"❌ Erro: {e}\n")
        return False
    
    # Teste 2: Info do Modelo
    print("2️⃣  Informações do Modelo")
    print("-" * 70)
    try:
        response = requests.get(f"{API_URL}/info")
        data = response.json()
        print(f"Nome: {data['nome']}")
        print(f"MAPE: {data['metricas']['MAPE']}")
        print("✅ Passou!\n")
    except Exception as e:
        print(f"❌ Erro: {e}\n")
        return False
    
    # Teste 3: Previsão
    print("3️⃣  Fazer Previsão")
    print("-" * 70)
    try:
        import numpy as np
        np.random.seed(42)
        prices = [12.5 + np.random.randn() * 0.3 for _ in range(60)]
        
        response = requests.post(
            f"{API_URL}/predict",
            json={"prices": prices}
        )
        
        data = response.json()
        print(f"Preço Previsto: R$ {data['preco_previsto']:.2f}")
        print(f"Confiança: {data['confianca']}")
        print("✅ Passou!\n")
    except Exception as e:
        print(f"❌ Erro: {e}\n")
        return False
    
    print("=" * 70)
    print(" " * 20 + "✅ TODOS OS TESTES PASSARAM!")
    print("=" * 70)
    print(f"\n📖 Documentação: {API_URL}/docs")
    return True

if __name__ == "__main__":
    testar_api_producao()
```

**Executar**:
```bash
python test_production.py
```

---

## ⚙️ Configurações Adicionais (Opcional)

### Auto-Deploy

O Render automaticamente faz redeploy quando você:
- Faz push para a branch `main`
- Atualiza o código no GitHub

### Monitoramento

No Dashboard do Render:
- **Logs**: Ver logs em tempo real
- **Metrics**: CPU, memória, requisições
- **Events**: Histórico de deploys

### Domínio Customizado (Opcional)

1. No Render Dashboard, vá em **Settings**
2. Em **Custom Domain**, adicione seu domínio
3. Configure DNS conforme instruções

---

## 🚨 Troubleshooting

### Problema 1: Build Falha por Falta de Memória

**Sintoma**: `MemoryError during pip install`

**Solução**:
- O `tensorflow-cpu` já está otimizado
- Considere usar `tensorflow-cpu==2.15.1` (versão atual)
- Free tier do Render tem limite de 512MB RAM

### Problema 2: Modelo Não Carrega

**Sintoma**: `FileNotFoundError: modelo não encontrado`

**Solução**:
```bash
# Verificar se modelos estão no Git
git ls-files | grep models/

# Adicionar se necessário
git add -f models/lstm_model_best.h5
git add -f models/scaler.pkl
git commit -m "fix: Adicionar modelos para deploy"
git push
```

### Problema 3: Porta Incorreta

**Sintoma**: Service não inicia

**Solução**: Sempre use `$PORT` no comando:
```bash
uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

### Problema 4: Import Error

**Sintoma**: `ModuleNotFoundError: No module named 'api'`

**Solução**: Certifique-se de que `api/__init__.py` existe no repositório.

### Problema 5: Service em Sleep (Free Tier)

**Sintoma**: API demora para responder após inatividade

**Explicação**: 
- Free tier do Render coloca serviços inativos em "sleep" após 15 minutos
- Primeira requisição após sleep leva ~30 segundos
- Requisições subsequentes são rápidas

**Soluções**:
1. Aceitar o delay (comportamento normal do free tier)
2. Fazer ping periódico (não recomendado, viola ToS)
3. Upgrade para plano pago ($7/mês)

---

## 📊 Limitações do Free Tier

| Recurso | Free Tier |
|---------|-----------|
| **RAM** | 512 MB |
| **CPU** | Shared |
| **Bandwidth** | 100 GB/mês |
| **Build Time** | 500 horas/mês |
| **Sleep após inatividade** | 15 minutos |
| **Custom Domain** | ✅ Sim |
| **HTTPS** | ✅ Sim (automático) |

---

## 🎯 Checklist de Deploy

- [ ] Código commitado no GitHub
- [ ] Modelos (`lstm_model_best.h5`, `scaler.pkl`) no repositório
- [ ] `requirements-render.txt` configurado
- [ ] `render.yaml` criado
- [ ] Conta criada no Render.com
- [ ] Web Service criado
- [ ] Build concluído com sucesso
- [ ] API respondendo na URL pública
- [ ] Health check funcionando
- [ ] Endpoint `/predict` testado
- [ ] Documentação Swagger acessível

---

## 🔗 URLs de Referência

- **Render Docs**: https://render.com/docs/deploy-fastapi
- **Render Dashboard**: https://dashboard.render.com/
- **GitHub Repo**: https://github.com/ArgusPortal/PredictFinance

---

## 📝 Próximos Passos

Após deploy bem-sucedido:

1. ✅ Anotar URL pública da API
2. ✅ Testar todos os endpoints
3. ✅ Atualizar documentação com URL de produção
4. ➡️ Prosseguir para Fase 8 (Monitoramento e Finalização)

---

**Elaborado por**: Sistema PredictFinance  
**Data**: 02/11/2025  
**Versão**: 1.0.0
