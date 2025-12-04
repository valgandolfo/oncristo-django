# 📋 Informações Completas de Deploy - OnCristo

## 🌐 Servidor Digital Ocean

### Dados de Acesso
- **IP:** `137.184.116.197`
- **Usuário:** `root`
- **Diretório do Projeto:** `/home/oncristo`
- **Domínio:** `oncristo.com.br`
- **URL:** `https://oncristo.com.br`

### Repositório Git
- **URL:** `https://github.com/valgandolfo/oncristo-django.git`
- **Token:** Já configurado no remote (não precisa informar)
- **Branch:** `main`

---

## 🚀 Como Fazer Deploy

### Opção 1: Deploy Automático Completo (RECOMENDADO)

Execute localmente:

```bash
cd /home/joaonote/oncristo.local
./deploy_completo.sh
```

Este script faz TUDO automaticamente:
1. ✅ Commit das mudanças locais
2. ✅ Push para GitHub
3. ✅ Conexão ao servidor
4. ✅ Backup automático
5. ✅ Atualização do código
6. ✅ Instalação de dependências
7. ✅ Migrações do banco
8. ✅ Coleta de arquivos estáticos
9. ✅ Reinício dos serviços

### Opção 2: Deploy Manual

#### Passo 1: Local (preparar código)
```bash
cd /home/joaonote/oncristo.local
git add .
git commit -m "Deploy: $(date +'%Y-%m-%d %H:%M:%S')"
git push origin main
```

#### Passo 2: Servidor (executar deploy)
```bash
ssh root@137.184.116.197
cd /home/oncristo
./deploy.sh
```

---

## ⚙️ Configurações do Servidor

### Serviços Systemd

#### Gunicorn
- **Serviço:** `gunicorn_oncristo`
- **Comandos:**
  ```bash
  systemctl status gunicorn_oncristo
  systemctl restart gunicorn_oncristo
  systemctl start gunicorn_oncristo
  systemctl stop gunicorn_oncristo
  ```

#### Nginx
- **Serviço:** `nginx`
- **Configuração:** `/etc/nginx/sites-available/oncristo`
- **Comandos:**
  ```bash
  systemctl status nginx
  systemctl reload nginx
  nginx -t  # Testar configuração
  ```

### Arquivos Importantes

#### Configuração do Projeto
- **Diretório:** `/home/oncristo`
- **Ambiente Virtual:** `/home/oncristo/venv`
- **Arquivo de Configuração:** `/home/oncristo/.env_production`
- **Arquivos Estáticos:** `/home/oncristo/staticfiles/`

#### Configuração do Gunicorn
- **Arquivo:** `/home/oncristo/gunicorn_config.py`
- **Socket:** `unix:/home/django/oncristo/gunicorn.sock` (⚠️ verificar se está correto)
- **PID:** `/home/django/oncristo/gunicorn.pid` (⚠️ verificar se está correto)

#### Configuração do Nginx
- **Arquivo:** `/etc/nginx/sites-available/oncristo`
- **Link Simbólico:** `/etc/nginx/sites-enabled/oncristo`

---

## ⚠️ IMPORTANTE: Inconsistências Detectadas

### Diretórios
Há uma inconsistência nos arquivos de configuração:

- **Scripts de deploy** usam: `/home/oncristo`
- **gunicorn_config.py** usa: `/home/django/oncristo`
- **gunicorn.service** usa: `/home/django/oncristo`
- **nginx_oncristo.conf** usa: `/home/django/oncristo`

### Ação Necessária

**Verificar no servidor qual é o diretório correto:**

```bash
ssh root@137.184.116.197
ls -la /home/
```

Se o diretório for `/home/oncristo`, será necessário atualizar:
- `gunicorn_config.py` (linha 8 e 25)
- `gunicorn.service` (linha 16, 18, 19, 23)
- `nginx_oncristo.conf` (linha 31, 38, 46)

---

## 🔍 Verificar Deploy

### Verificar Serviços
```bash
# Status do Gunicorn
systemctl status gunicorn_oncristo

# Status do Nginx
systemctl status nginx

# Logs do Gunicorn
journalctl -u gunicorn_oncristo -n 50 --no-pager

# Logs do Nginx
tail -f /var/log/nginx/error.log
```

### Testar Site
```bash
# Via curl
curl -I https://oncristo.com.br

# Via navegador
# Acesse: https://oncristo.com.br
```

---

## 🆘 Solução de Problemas

### Erro: "Permission denied"
```bash
chmod +x deploy.sh
chmod +x deploy_completo.sh
```

### Erro: "Git não encontrado"
```bash
apt update
apt install -y git
```

### Erro: "Gunicorn não está rodando"
```bash
systemctl start gunicorn_oncristo
systemctl status gunicorn_oncristo
journalctl -u gunicorn_oncristo -n 50
```

### Erro: "Migrations pending"
```bash
cd /home/oncristo
source venv/bin/activate
export DJANGO_ENV=production
python manage.py migrate
```

### Erro: "Static files not found"
```bash
cd /home/oncristo
source venv/bin/activate
export DJANGO_ENV=production
python manage.py collectstatic --noinput
```

### Erro: "Nginx configuration test failed"
```bash
nginx -t
# Verificar erros e corrigir
nano /etc/nginx/sites-available/oncristo
nginx -t
systemctl reload nginx
```

---

## 📝 Checklist Antes do Deploy

- [ ] Código testado localmente
- [ ] Mudanças commitadas no Git
- [ ] `.env_production` configurado no servidor
- [ ] Backup do banco de dados (se necessário)
- [ ] Migrações testadas localmente
- [ ] Arquivos estáticos coletados localmente (teste)
- [ ] Verificar diretório correto no servidor (`/home/oncristo` ou `/home/django/oncristo`)

---

## 🔄 Deploy Rápido (Após primeira configuração)

Depois da primeira configuração, para atualizar o código:

```bash
# Local
cd /home/joaonote/oncristo.local
./deploy_completo.sh
```

Ou manualmente:

```bash
# Local
cd /home/joaonote/oncristo.local
git add .
git commit -m "Atualização"
git push origin main

# Servidor
ssh root@137.184.116.197
cd /home/oncristo
./deploy.sh
```

---

## 📞 Informações Importantes

1. **Token do GitHub:** Já configurado no remote do Git
2. **Backup:** Sempre feito automaticamente antes do deploy
3. **.env_production:** Nunca é commitado (está no .gitignore)
4. **Banco de Dados:** Migrações aplicadas automaticamente
5. **Arquivos Estáticos:** Coletados automaticamente
6. **Diretório:** Verificar se é `/home/oncristo` ou `/home/django/oncristo`

---

## ✅ Após o Deploy

Verificar:
- ✅ Home page carrega: `https://oncristo.com.br`
- ✅ Login funciona: `https://oncristo.com.br/app_igreja/login/`
- ✅ Área administrativa acessível
- ✅ Banners rotativos funcionando
- ✅ WhatsApp chatbot funcionando
- ✅ Módulo de divulgação acessível

---

## 📚 Arquivos de Referência

- `deploy_completo.sh` - Script de deploy completo (local → servidor)
- `deploy.sh` - Script de deploy no servidor
- `GUIA_DEPLOY_RAPIDO.md` - Guia rápido de deploy
- `DEPLOY_SERVIDOR.md` - Guia detalhado de deploy
- `gunicorn_config.py` - Configuração do Gunicorn
- `nginx_oncristo.conf` - Configuração do Nginx
- `gunicorn.service` - Serviço systemd do Gunicorn

