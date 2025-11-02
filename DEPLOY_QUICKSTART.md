# 🚀 Guia de Deploy - Render.com

## ✅ Status Atual

Os seguintes arquivos foram criados e estão prontos para deploy:

### Arquivos de Configuração

- ✅ `requirements-render.txt` - Dependências otimizadas para produção
- ✅ `render.yaml` - Configuração do serviço Render
- ✅ `Procfile` - Comando de inicialização (backup)
- ✅ `.gitignore` - Atualizado para incluir modelos

### Arquivos Necessários

- ✅ `api/main.py` - Aplicação FastAPI
- ✅ `api/schemas.py` - Modelos Pydantic
- ✅ `api/__init__.py` - Inicialização
- ✅ `models/lstm_model_best.h5` - Modelo LSTM (0.39 MB)
- ✅ `models/scaler.pkl` - Scaler (0.86 KB)

---

## 📋 Checklist Pré-Deploy

Execute os seguintes comandos para verificar:

```bash
# 1. Verificar arquivos de configuração
ls -la requirements-render.txt render.yaml Procfile

# 2. Verificar modelos
ls -lh models/

# 3. Verificar API
ls -la api/

# 4. Verificar se está no Git
git status
```

---

## 🚀 Passos para Deploy

### 1. Commit e Push para GitHub

```bash
# Adicionar todos os arquivos necessários
git add requirements-render.txt
git add render.yaml
git add Procfile
git add .gitignore
git add api/
git add models/
git add test_production.py
git add docs/DEPLOY_RENDER.md

# Commit
git commit -m "feat: Adicionar configuração para deploy no Render (Fase 7)

- Adicionar requirements-render.txt otimizado
- Configurar render.yaml para deploy automático
- Incluir modelos no repositório
- Criar script de teste de produção
- Documentação completa de deploy"

# Push
git push origin main
```

### 2. Acessar Render.com

1. Acesse: https://render.com/
2. Faça login com GitHub
3. Clique em **"New +"** → **"Web Service"**

### 3. Conectar Repositório

1. Selecione **"PredictFinance"** da lista
2. Ou clique em **"Configure account"** se não aparecer

### 4. Configurar Service

| Campo | Valor |
|-------|-------|
| Name | `b3sa3-api` |
| Region | `Oregon (US West)` |
| Branch | `main` |
| Build Command | `pip install -r requirements-render.txt` |
| Start Command | `uvicorn api.main:app --host 0.0.0.0 --port $PORT` |
| Plan | **Free** |

### 5. Deploy

1. Clique em **"Create Web Service"**
2. Aguarde build (~5 minutos)
3. Copie a URL gerada

---

## 🧪 Testar API em Produção

### Opção 1: Script Automático

```bash
# Substituir URL pela real
python test_production.py https://b3sa3-api.onrender.com
```

### Opção 2: cURL Manual

```bash
# Health check
curl https://b3sa3-api.onrender.com/

# Info do modelo
curl https://b3sa3-api.onrender.com/info

# Fazer previsão (exemplo simplificado)
curl -X POST https://b3sa3-api.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{"prices": [12.5,12.6,12.7,12.8,12.9,13.0,13.1,13.2,13.3,13.4,13.5,13.6,13.7,13.8,13.9,14.0,14.1,14.2,14.3,14.4,14.5,14.6,14.7,14.8,14.9,15.0,14.9,14.8,14.7,14.6,14.5,14.4,14.3,14.2,14.1,14.0,13.9,13.8,13.7,13.6,13.5,13.4,13.3,13.2,13.1,13.0,12.9,12.8,12.7,12.6,12.5,12.4,12.3,12.2,12.1,12.0,11.9,11.8,11.7,11.6]}'
```

### Opção 3: Navegador

Acesse a documentação interativa:

```
https://b3sa3-api.onrender.com/docs
```

---

## ⚠️ Importante - Free Tier

### Sleep Mode

- API entra em "sleep" após **15 minutos** de inatividade
- Primeira requisição após sleep: **~30 segundos** de delay
- Requisições seguintes: rápidas

### Solução

Isso é normal no free tier. Para produção contínua:
- Upgrade para plano pago ($7/mês)
- Ou aceitar o delay inicial

---

## 📊 Monitoramento

No Dashboard do Render:

- **Logs**: Ver logs em tempo real
- **Metrics**: CPU, memória, tráfego
- **Events**: Histórico de deploys

---

## 🔗 Links Úteis

- **Documentação Render**: https://render.com/docs/deploy-fastapi
- **Dashboard**: https://dashboard.render.com/
- **Documentação completa**: [DEPLOY_RENDER.md](docs/DEPLOY_RENDER.md)

---

## ✅ Próximos Passos

Após deploy bem-sucedido:

1. ✅ Anotar URL pública
2. ✅ Executar `test_production.py`
3. ✅ Atualizar README com URL
4. ➡️ Prosseguir para Fase 8

---

**Pronto para deploy!** 🚀
