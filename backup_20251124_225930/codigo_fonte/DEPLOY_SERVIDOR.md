# 🚀 Guia de Deploy no Servidor Digital Ocean

## 📋 Pré-requisitos
- Acesso SSH ao servidor: `root@137.184.116.197`
- Repositório no GitHub: `https://github.com/valgandolfo/oncristo-django.git`
- Token do GitHub configurado

---

## 🔧 PASSO 1: Conectar ao Servidor

```bash
ssh root@137.184.116.197
```

---

## 🔧 PASSO 2: Instalar Git (se não estiver instalado)

```bash
apt update
apt install -y git
git --version
```

---

## 🔧 PASSO 3: Fazer Backup do Projeto Atual (Importante!)

```bash
cd /home/oncristo

# Criar backup do projeto atual
BACKUP_DIR="backup_antes_git_$(date +%Y%m%d_%H%M%S)"
mkdir -p "/root/$BACKUP_DIR"

# Copiar arquivos importantes
cp -r app_igreja "/root/$BACKUP_DIR/" 2>/dev/null || true
cp -r pro_igreja "/root/$BACKUP_DIR/" 2>/dev/null || true
cp -r templates "/root/$BACKUP_DIR/" 2>/dev/null || true
cp -r static "/root/$BACKUP_DIR/" 2>/dev/null || true
cp manage.py "/root/$BACKUP_DIR/" 2>/dev/null || true
cp requirements.txt "/root/$BACKUP_DIR/" 2>/dev/null || true
cp .env_production "/root/$BACKUP_DIR/" 2>/dev/null || true

echo "✅ Backup criado em: /root/$BACKUP_DIR"
```

---

## 🔧 PASSO 4: Clonar Repositório do GitHub

```bash
cd /home/oncristo

# Clonar repositório (usando token na URL)
# IMPORTANTE: Substitua SEU_TOKEN pelo seu token do GitHub
git clone https://SEU_TOKEN@github.com/valgandolfo/oncristo-django.git temp_repo

# Mover arquivos para o diretório principal
mv temp_repo/* .
mv temp_repo/.* . 2>/dev/null || true
rmdir temp_repo

echo "✅ Repositório clonado com sucesso"
```

---

## 🔧 PASSO 5: Configurar Ambiente Virtual

```bash
cd /home/oncristo

# Criar ambiente virtual (se não existir)
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Ambiente virtual criado"
fi

# Ativar ambiente virtual
source venv/bin/activate

# Atualizar pip
pip install --upgrade pip
```

---

## 🔧 PASSO 6: Instalar Dependências do Sistema

**⚠️ IMPORTANTE:** Antes de instalar os pacotes Python, instale as dependências do sistema necessárias:

```bash
# Atualizar lista de pacotes
apt update

# Instalar dependências do sistema para compilar pacotes Python
apt install -y \
    python3-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    zlib1g-dev \
    libmysqlclient-dev \
    build-essential \
    pkg-config

echo "✅ Dependências do sistema instaladas"
```

---

## 🔧 PASSO 7: Instalar Dependências Python

```bash
cd /home/oncristo
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

echo "✅ Dependências Python instaladas"
```

---

## 🔧 PASSO 8: Configurar Variáveis de Ambiente

```bash
cd /home/oncristo

# Verificar se .env_production existe
if [ ! -f ".env_production" ]; then
    echo "⚠️  .env_production não encontrado!"
    echo "Copiando do backup ou criando novo..."
    
    # Tentar copiar do backup
    if [ -f "/root/$BACKUP_DIR/.env_production" ]; then
        cp "/root/$BACKUP_DIR/.env_production" .env_production
        echo "✅ .env_production restaurado do backup"
    else
        # Criar a partir do exemplo
        cp .env_production.example .env_production
        echo "⚠️  Criado .env_production a partir do exemplo"
        echo "⚠️  IMPORTANTE: Configure as variáveis de ambiente!"
        nano .env_production
    fi
else
    echo "✅ .env_production já existe"
fi
```

---

## 🔧 PASSO 9: Aplicar Migrações

```bash
cd /home/oncristo
source venv/bin/activate

export DJANGO_ENV=production
python manage.py migrate --noinput

echo "✅ Migrações aplicadas"
```

---

## 🔧 PASSO 10: Coletar Arquivos Estáticos

```bash
cd /home/oncristo
source venv/bin/activate

export DJANGO_ENV=production
python manage.py collectstatic --noinput

echo "✅ Arquivos estáticos coletados"
```

---

## 🔧 PASSO 11: Tornar Script de Deploy Executável

```bash
cd /home/oncristo
chmod +x deploy.sh
echo "✅ Script de deploy configurado"
```

---

## 🔧 PASSO 12: Reiniciar Gunicorn

```bash
# Reiniciar serviço
systemctl restart gunicorn_oncristo

# Verificar status
systemctl status gunicorn_oncristo --no-pager

echo "✅ Gunicorn reiniciado"
```

---

## 🔧 PASSO 13: Verificar se Está Funcionando

```bash
# Verificar se o serviço está rodando
systemctl is-active gunicorn_oncristo

# Verificar logs
journalctl -u gunicorn_oncristo -n 20 --no-pager

# Testar acesso local
curl -I http://127.0.0.1:8000
```

---

## ✅ DEPLOY CONCLUÍDO!

Acesse: **https://oncristo.com.br**

---

## 🔄 Para Futuros Deploys (Mais Rápido)

Depois da primeira configuração, para atualizar o código:

```bash
cd /home/oncristo
./deploy.sh
```

Ou manualmente:

```bash
cd /home/oncristo
source venv/bin/activate
git pull origin main
pip install -r requirements.txt
export DJANGO_ENV=production
python manage.py migrate --noinput
python manage.py collectstatic --noinput
systemctl restart gunicorn_oncristo
```

---

## 🆘 Solução de Problemas

### Erro: "Git não encontrado"
```bash
apt install -y git
```

### Erro: "Permission denied"
```bash
chmod +x deploy.sh
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

### Ver logs de erro
```bash
journalctl -u gunicorn_oncristo -f
```

### Reiniciar serviço
```bash
systemctl restart gunicorn_oncristo
```

---

## 📝 Notas Importantes

1. **Token do GitHub**: O token está na URL do remote. Se expirar, será necessário atualizar.
2. **Backup**: Sempre faça backup antes de grandes mudanças.
3. **.env_production**: Nunca commite este arquivo no Git (já está no .gitignore).
4. **Banco de Dados**: As migrações são aplicadas automaticamente, mas faça backup do banco antes.

