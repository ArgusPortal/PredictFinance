# 📘 Guia de Execução - Fase 7: Deploy da API no Render

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Pré-requisitos](#pré-requisitos)
3. [Objetivos da Fase](#objetivos-da-fase)
4. [Preparação dos Arquivos](#preparação-dos-arquivos)
5. [Deploy Passo a Passo](#deploy-passo-a-passo)
6. [Testes em Produção](#testes-em-produção)
7. [Monitoramento e Logs](#monitoramento-e-logs)
8. [Troubleshooting](#troubleshooting)
9. [Checklist de Conclusão](#checklist-de-conclusão)
10. [Referências](#referências)

---

## 🎯 Visão Geral

A **Fase 7** realiza o deploy da API FastAPI no **Render.com**, tornando-a acessível publicamente via HTTPS. Esta fase transforma o serviço local em uma API de produção na nuvem.

**Duração Estimada**: 30-60 minutos  
**Complexidade**: Intermediária  
**Plataforma**: Render.com (Free Tier)

---

## ✅ Pré-requisitos

### Fases Anteriores

- ✅ Fase 1-5: Modelo treinado e validado
- ✅ Fase 6: API FastAPI funcionando localmente

### Contas Necessárias

- ✅ **GitHub**: Repositório com código
- ✅ **Render.com**: Conta gratuita (criar em https://render.com)

### Artefatos Necessários

```
PredictFinance/
├── api/
│   ├── __init__.py
│   ├── main.py
│   └── schemas.py
├── models/
│   ├── lstm_model_best.h5  (0.39 MB)
│   └── scaler.pkl           (0.86 KB)
├── requirements-render.txt
├── render.yaml
└── Procfile
```

---

## 🎯 Objetivos da Fase

1. ✅ Preparar dependências otimizadas para produção
2. ✅ Configurar arquivos de deploy (render.yaml, Procfile)
3. ✅ Incluir modelos no repositório Git
4. ✅ Fazer deploy no Render.com
5. ✅ Obter URL pública da API
6. ✅ Testar todos os endpoints em produção
7. ✅ Validar funcionalidade completa

---

## 📦 Preparação dos Arquivos

### 1. Requirements Otimizado

**Arquivo**: `requirements-render.txt`

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

**Por que tensorflow-cpu?**
- Reduz tamanho do build de ~2GB para ~500MB
- Free tier do Render tem limite de recursos
- Suficiente para inferência (não precisa GPU)

### 2. Configuração Render

**Arquivo**: `render.yaml`

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

### 3. Procfile (Backup)

**Arquivo**: `Procfile`

```
web: uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

### 4. Atualizar .gitignore

O `.gitignore` foi atualizado para **incluir** os modelos no Git:

```gitignore
# Modelos (comentado para permitir deploy)
# models/*.h5
# models/*.pkl

# Por enquanto, os modelos são versionados para o deploy
```

---

## 🚀 Deploy Passo a Passo

### Passo 1: Commit e Push para GitHub

```bash
# 1. Verificar arquivos modificados
git status

# 2. Adicionar arquivos de configuração
git add requirements-render.txt
git add render.yaml
git add Procfile
git add .gitignore

# 3. Adicionar código da API
git add api/
git add run_api.py

# 4. Adicionar modelos (IMPORTANTE!)
git add models/lstm_model_best.h5
git add models/scaler.pkl
git add models/model_architecture.json

# 5. Adicionar documentação
git add docs/DEPLOY_RENDER.md
git add docs/FASE_7_GUIA.md
git add DEPLOY_QUICKSTART.md
git add test_production.py

# 6. Commit
git commit -m "feat: Deploy no Render.com (Fase 7)

- Adicionar requirements-render.txt otimizado
- Configurar render.yaml para deploy automático
- Incluir modelos no repositório para deploy
- Criar script de teste de produção
- Documentação completa de deploy"

# 7. Push
git push origin main
```

**Verificar Push**:
```bash
# Acessar GitHub e verificar se arquivos foram enviados
# https://github.com/ArgusPortal/PredictFinance
```

### Passo 2: Criar Conta no Render

1. Acesse: https://render.com/
2. Clique em **"Get Started for Free"**
3. Selecione **"Sign up with GitHub"**
4. Autorize o Render a acessar sua conta GitHub

### Passo 3: Criar Web Service

1. No Dashboard do Render, clique em **"New +"**
2. Selecione **"Web Service"**
3. Na lista de repositórios:
   - Procure por **"PredictFinance"**
   - Clique em **"Connect"**
   
**Se o repositório não aparecer**:
- Clique em **"Configure account"**
- Autorize acesso ao repositório específico

### Passo 4: Configurar o Service

Preencha os campos conforme abaixo:

#### Settings Básicos

| Campo | Valor |
|-------|-------|
| **Name** | `b3sa3-api` (ou nome de sua preferência) |
| **Region** | `Oregon (US West)` |
| **Branch** | `main` |
| **Root Directory** | (deixar em branco) |

#### Build & Deploy

| Campo | Valor |
|-------|-------|
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements-render.txt` |
| **Start Command** | `uvicorn api.main:app --host 0.0.0.0 --port $PORT` |

#### Instance Type

| Campo | Valor |
|-------|-------|
| **Plan** | **Free** |

### Passo 5: Environment Variables (Opcional)

Não são necessárias variáveis de ambiente obrigatórias, mas você pode adicionar:

| Key | Value | Descrição |
|-----|-------|-----------|
| `PYTHON_VERSION` | `3.10.11` | Versão do Python (já definido no render.yaml) |

### Passo 6: Criar e Deploy

1. Clique em **"Create Web Service"**
2. O Render iniciará o build automaticamente
3. Acompanhe o progresso na aba **"Logs"**

---

## 📊 Monitoramento do Build

### Logs Esperados

Durante o build, você verá (pode levar ~5 minutos):

```
==> Cloning from https://github.com/ArgusPortal/PredictFinance...
==> Checked out commit abc123

==> Installing dependencies
==> Running 'pip install -r requirements-render.txt'
    Collecting fastapi==0.109.2
    Downloading fastapi-0.109.2-py3-none-any.whl (92 kB)
    Collecting uvicorn[standard]==0.27.1
    Downloading uvicorn-0.27.1-py3-none-any.whl (60 kB)
    Collecting tensorflow-cpu==2.15.1
    Downloading tensorflow_cpu-2.15.1-cp310-cp310-manylinux2014_x86_64.whl (211.7 MB)
    ...
    Successfully installed fastapi-0.109.2 uvicorn-0.27.1 tensorflow-cpu-2.15.1 ...

==> Build successful ✓

==> Starting service
==> Running 'uvicorn api.main:app --host 0.0.0.0 --port $PORT'

🚀 Iniciando API...
📂 Carregando artefatos do modelo...
   └─ Carregando modelo: /opt/render/project/src/models/lstm_model_best.h5
   ✅ Modelo carregado com sucesso!
   └─ Carregando scaler: /opt/render/project/src/models/scaler.pkl
   ✅ Scaler carregado com sucesso!
✅ API pronta para receber requisições!

INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:10000

==> Your service is live 🎉
```

### Tempo de Build

- **Instalar dependências**: 3-5 minutos
- **Iniciar service**: 10-15 segundos
- **Total**: ~5 minutos

### Obter URL da API

Após deploy bem-sucedido, a URL aparecerá no topo:

```
https://b3sa3-api.onrender.com
```

**Copie esta URL** - você usará nos testes!

---

## 🧪 Testes em Produção

### Teste 1: Health Check (cURL)

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
  },
  "window_size": 60,
  "features": ["Open", "High", "Low", "Close", "Volume"]
}
```

### Teste 3: Script Automatizado

```bash
# Substituir pela URL real do Render
python test_production.py https://b3sa3-api.onrender.com
```

**Saída esperada**:

```
================================================================================
                        🧪 TESTE DA API EM PRODUÇÃO
================================================================================

📍 URL da API: https://b3sa3-api.onrender.com
📅 Data: 02/11/2025

================================================================================

1️⃣  Health Check (GET /)
--------------------------------------------------------------------------------
Status Code: 200
Resposta:
{
  "status": "ativo",
  "mensagem": "API de previsão B3SA3.SA operacional",
  "versao": "1.0.0",
  "modelo_carregado": true
}
✅ Health check passou! Modelo está carregado.

[... demais testes ...]

================================================================================
                        ✅ TODOS OS TESTES PASSARAM!
================================================================================

🌐 API em Produção: https://b3sa3-api.onrender.com
📖 Documentação: https://b3sa3-api.onrender.com/docs
```

### Teste 4: Documentação Swagger

Abra no navegador:

```
https://b3sa3-api.onrender.com/docs
```

Você verá a interface interativa do Swagger UI.

### Teste 5: Fazer Previsão

```bash
curl -X POST https://b3sa3-api.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{
    "prices": [12.5, 12.6, 12.7, 12.8, 12.9, 13.0, 13.1, 13.2, 13.3, 13.4,
               13.5, 13.6, 13.7, 13.8, 13.9, 14.0, 14.1, 14.2, 14.3, 14.4,
               14.5, 14.6, 14.7, 14.8, 14.9, 15.0, 14.9, 14.8, 14.7, 14.6,
               14.5, 14.4, 14.3, 14.2, 14.1, 14.0, 13.9, 13.8, 13.7, 13.6,
               13.5, 13.4, 13.3, 13.2, 13.1, 13.0, 12.9, 12.8, 12.7, 12.6,
               12.5, 12.4, 12.3, 12.2, 12.1, 12.0, 11.9, 11.8, 11.7, 11.6]
  }'
```

**Resposta esperada**:
```json
{
  "preco_previsto": 11.52,
  "confianca": "alta",
  "mensagem": "Previsão gerada com sucesso. Modelo com MAPE de 1.53% no teste."
}
```

---

## 📈 Monitoramento e Logs

### Acessar Logs em Tempo Real

1. No Dashboard do Render, selecione seu serviço
2. Clique na aba **"Logs"**
3. Veja requisições em tempo real:

```
INFO:     127.0.0.1:57361 - "GET / HTTP/1.1" 200 OK
INFO:     127.0.0.1:52582 - "GET /info HTTP/1.1" 200 OK
INFO:     127.0.0.1:65262 - "POST /predict HTTP/1.1" 200 OK
```

### Métricas

Na aba **"Metrics"**, veja:
- **CPU Usage**: Uso de processador
- **Memory**: Uso de memória
- **Bandwidth**: Tráfego de rede

### Events

Na aba **"Events"**, veja:
- Histórico de deploys
- Builds bem-sucedidos/falhados
- Reinicializações do serviço

---

## ⚠️ Comportamento do Free Tier

### Sleep Mode

O free tier do Render tem uma característica importante:

- ⏱️ **Sleep após 15 minutos** de inatividade
- 🐌 **Primeira requisição após sleep**: ~30 segundos
- ⚡ **Requisições subsequentes**: rápidas (<100ms)

### Como Funciona

```
[API Ativa] → 15 min inatividade → [Sleep Mode]
                ↓
    Primeira requisição (30s delay)
                ↓
          [API Acordada]
                ↓
    Requisições rápidas (<100ms)
```

### Isso é Normal?

✅ **SIM!** É comportamento esperado do free tier.

### Soluções

1. **Aceitar o delay** (recomendado para desenvolvimento/demonstração)
2. **Upgrade para plano pago** ($7/mês) - serviço sempre ativo
3. **NÃO fazer ping periódico** - viola Terms of Service do Render

---

## 🔧 Troubleshooting

### Problema 1: Build Falha - Memory Error

**Sintoma**:
```
MemoryError: Unable to allocate array
```

**Causa**: Free tier tem limite de 512MB RAM

**Solução**:
✅ Já implementado: `tensorflow-cpu` em vez de `tensorflow`
✅ Dependências otimizadas em `requirements-render.txt`

Se ainda ocorrer:
- Verificar se não tem dependências extras no requirements
- Usar versões exatas (sem `>=`)

### Problema 2: Modelo Não Encontrado

**Sintoma**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'models/lstm_model_best.h5'
```

**Solução**:
```bash
# Verificar se modelos estão no Git
git ls-files | grep models/

# Se não aparecer, adicionar forçadamente
git add -f models/lstm_model_best.h5
git add -f models/scaler.pkl
git commit -m "fix: Adicionar modelos para deploy"
git push
```

### Problema 3: Port Binding Error

**Sintoma**:
```
OSError: [Errno 98] Address already in use
```

**Causa**: Start command não está usando `$PORT`

**Solução**: Sempre usar `$PORT`:
```bash
uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

### Problema 4: Import Error

**Sintoma**:
```
ModuleNotFoundError: No module named 'api'
```

**Soluções**:
```bash
# 1. Verificar se api/__init__.py existe
ls api/__init__.py

# 2. Se não existir, criar
touch api/__init__.py
git add api/__init__.py
git commit -m "fix: Adicionar __init__.py"
git push
```

### Problema 5: Timeout na Primeira Requisição

**Sintoma**: Requisição demora >30 segundos

**Causa**: API estava em sleep mode (free tier)

**Solução**: 
- Aguardar ~30 segundos
- API "acordará" e ficará rápida
- Comportamento normal do free tier

---

## 📊 Limitações do Free Tier

| Recurso | Free Tier | Plano Pago |
|---------|-----------|------------|
| **RAM** | 512 MB | 2+ GB |
| **CPU** | Shared | Dedicated |
| **Bandwidth** | 100 GB/mês | Ilimitado |
| **Build Time** | 500 horas/mês | Ilimitado |
| **Sleep** | Sim (15 min) | Não |
| **Custom Domain** | ✅ Sim | ✅ Sim |
| **HTTPS** | ✅ Automático | ✅ Automático |
| **Custo** | **Grátis** | $7+/mês |

---

## ✅ Checklist de Conclusão

### Preparação

- [ ] `requirements-render.txt` criado
- [ ] `render.yaml` criado
- [ ] `Procfile` criado
- [ ] `.gitignore` atualizado para incluir modelos
- [ ] Modelos adicionados ao Git
- [ ] Código commitado e pushado para GitHub

### Deploy

- [ ] Conta criada no Render.com
- [ ] Repositório conectado
- [ ] Web Service configurado
- [ ] Build concluído com sucesso
- [ ] URL pública obtida

### Testes

- [ ] Health check funcionando (GET /)
- [ ] Info do modelo respondendo (GET /info)
- [ ] Métricas acessíveis (GET /metrics)
- [ ] Previsão funcionando (POST /predict)
- [ ] Documentação Swagger acessível (/docs)
- [ ] Script `test_production.py` executado com sucesso

### Verificação Final

Executar:

```bash
# 1. Testar API
python test_production.py https://SUA-URL.onrender.com

# 2. Verificar documentação
# Abrir no navegador: https://SUA-URL.onrender.com/docs

# 3. Anotar URL para documentação
echo "API URL: https://SUA-URL.onrender.com" >> .env
```

**Critérios de Sucesso**:
- ✅ API acessível publicamente
- ✅ Todos os endpoints funcionando
- ✅ Previsões retornando valores razoáveis
- ✅ Documentação Swagger operacional
- ✅ Logs mostrando requisições

---

## 📚 Referências

### Documentação Oficial

- **Render FastAPI Guide**: https://render.com/docs/deploy-fastapi
- **Render Free Tier**: https://render.com/docs/free
- **Render Dashboard**: https://dashboard.render.com/

### Documentação do Projeto

- [DEPLOY_RENDER.md](DEPLOY_RENDER.md) - Documentação detalhada
- [DEPLOY_QUICKSTART.md](../DEPLOY_QUICKSTART.md) - Guia rápido
- [test_production.py](../test_production.py) - Script de teste

### Alternativas de Deploy

Se preferir outras plataformas:
- **Railway**: https://railway.app/
- **Fly.io**: https://fly.io/
- **PythonAnywhere**: https://www.pythonanywhere.com/

Processo similar ao Render.

---

## 🎯 Próximos Passos

Após concluir a Fase 7:

### Fase 8: Monitoramento e Finalização (última fase!)

**Objetivos**:
- Implementar logging estruturado (Loguru)
- Dashboard de monitoramento (Streamlit - opcional)
- Vídeo explicativo (10 minutos)
- Documentação final completa
- README aprimorado

**Estimativa**: 2-3 horas

---

**Elaborado por**: Sistema PredictFinance  
**Data**: 02/11/2025  
**Versão**: 1.0.0  
**Status**: ✅ Fase 7 - Instruções Completas
