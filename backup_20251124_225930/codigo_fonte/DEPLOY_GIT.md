# 🚀 Guia de Deploy usando Git

Este guia explica como fazer deploy do projeto OnCristo no servidor Digital Ocean usando Git.

## 📋 Pré-requisitos

1. Conta no GitHub/GitLab/Bitbucket
2. Acesso SSH ao servidor Digital Ocean
3. Git instalado localmente e no servidor

## 🔧 Passo 1: Configurar Repositório Git Local

### 1.1 Inicializar Git (se ainda não foi feito)

```bash
cd /home/joaonote/oncristo.local
git init
git add .
git commit -m "Initial commit - Projeto OnCristo"
```

### 1.2 Criar Repositório no GitHub

1. Acesse https://github.com
2. Crie um novo repositório (ex: `oncristo-django`)
3. **NÃO** inicialize com README, .gitignore ou licença

### 1.3 Conectar Repositório Local ao Remoto

```bash
# Substitua SEU_USUARIO e SEU_REPOSITORIO pelos seus dados
git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
git branch -M main
git push -u origin main
```

## 🔧 Passo 2: Configurar Servidor Digital Ocean

### 2.1 Conectar ao Servidor

```bash
ssh root@137.184.116.197
```

### 2.2 Instalar Git (se não estiver instalado)

```bash
apt update
apt install -y git
```

### 2.3 Clonar Repositório no Servidor

```bash
cd /home/oncristo
# Fazer backup do projeto atual (se necessário)
mv app_igreja app_igreja_backup_$(date +%Y%m%d_%H%M%S) 2>/dev/null || true

# Clonar repositório
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git /home/oncristo/temp_repo

# Mover arquivos para o diretório principal
mv /home/oncristo/temp_repo/* /home/oncristo/
mv /home/oncristo/temp_repo/.* /home/oncristo/ 2>/dev/null || true
rmdir /home/oncristo/temp_repo
```

### 2.4 Configurar Ambiente no Servidor

```bash
cd /home/oncristo

# Criar ambiente virtual (se não existir)
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
# Copiar .env_production.example para .env_production e preencher
cp .env_production.example .env_production
nano .env_production  # Preencher com dados corretos

# Aplicar migrações
export DJANGO_ENV=production
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic --noinput
```

## 🔄 Passo 3: Script de Deploy Automatizado

### 3.1 Criar Script de Deploy no Servidor

Crie o arquivo `/home/oncristo/deploy.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Iniciando deploy..."

cd /home/oncristo

# Ativar ambiente virtual
source venv/bin/activate

# Atualizar código do Git
echo "📥 Atualizando código do Git..."
git fetch origin
git reset --hard origin/main

# Instalar/atualizar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Aplicar migrações
echo "🗄️ Aplicando migrações..."
export DJANGO_ENV=production
python manage.py migrate --noinput

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Reiniciar Gunicorn
echo "🔄 Reiniciando Gunicorn..."
systemctl restart gunicorn_oncristo

# Verificar status
echo "✅ Verificando status do serviço..."
systemctl status gunicorn_oncristo --no-pager

echo "✅ Deploy concluído com sucesso!"
```

### 3.2 Tornar Script Executável

```bash
chmod +x /home/oncristo/deploy.sh
```

## 🔄 Passo 4: Processo de Deploy

### 4.1 No Seu Computador Local

```bash
cd /home/joaonote/oncristo.local

# Fazer alterações no código...

# Adicionar e commitar alterações
git add .
git commit -m "Descrição das alterações"

# Enviar para o repositório remoto
git push origin main
```

### 4.2 No Servidor

```bash
ssh root@137.184.116.197
cd /home/oncristo
./deploy.sh
```

## 🔐 Passo 5: Configurar Deploy Automático (Opcional)

### 5.1 Usando Webhook do GitHub

1. No GitHub, vá em Settings > Webhooks
2. Adicione um webhook apontando para: `http://oncristo.com.br/api/webhook/deploy`
3. Configure para enviar apenas eventos de `push`

### 5.2 Criar View de Webhook no Django

Crie `app_igreja/views/admin_area/views_deploy.py`:

```python
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import subprocess
import os

@csrf_exempt
@require_POST
def webhook_deploy(request):
    """
    Webhook para deploy automático via GitHub
    """
    # Verificar se é uma requisição do GitHub (opcional: validar assinatura)
    
    try:
        # Executar script de deploy
        result = subprocess.run(
            ['/home/oncristo/deploy.sh'],
            cwd='/home/oncristo',
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            return JsonResponse({
                'status': 'success',
                'message': 'Deploy realizado com sucesso',
                'output': result.stdout
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Erro no deploy',
                'error': result.stderr
            }, status=500)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
```

## 📝 Checklist de Deploy

Antes de cada deploy, verifique:

- [ ] Código testado localmente
- [ ] Migrações criadas (se houver mudanças no modelo)
- [ ] `.env_production` configurado corretamente no servidor
- [ ] Backup do banco de dados (opcional, mas recomendado)
- [ ] Arquivos sensíveis não estão no repositório (`.env`, etc.)

## 🆘 Solução de Problemas

### Erro: "Permission denied"
```bash
chmod +x deploy.sh
```

### Erro: "Git não encontrado"
```bash
apt install -y git
```

### Erro: "Migrations pending"
```bash
export DJANGO_ENV=production
python manage.py migrate
```

### Erro: "Static files not found"
```bash
python manage.py collectstatic --noinput
```

### Rollback (voltar versão anterior)
```bash
cd /home/oncristo
git log  # Ver commits anteriores
git reset --hard <commit-hash>  # Voltar para commit específico
./deploy.sh
```

## 🔒 Segurança

1. **Nunca** commite arquivos `.env` ou `.env_production`
2. Use variáveis de ambiente no servidor
3. Mantenha o `.gitignore` atualizado
4. Use SSH keys para autenticação Git (mais seguro que HTTPS)

## 📚 Comandos Úteis

```bash
# Ver histórico de commits
git log --oneline

# Ver diferenças antes de commitar
git diff

# Ver status do repositório
git status

# Desfazer alterações não commitadas
git checkout -- .

# Verificar remotes
git remote -v
```

