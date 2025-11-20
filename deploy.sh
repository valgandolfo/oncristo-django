#!/bin/bash
# Script de deploy para o servidor Digital Ocean
# Uso: ./deploy.sh

set -e  # Parar em caso de erro

echo "🚀 Iniciando deploy do OnCristo..."

# Diretório do projeto
PROJECT_DIR="/home/oncristo"
cd "$PROJECT_DIR"

# Ativar ambiente virtual
if [ -d "venv" ]; then
    echo "📦 Ativando ambiente virtual..."
    source venv/bin/activate
else
    echo "⚠️ Ambiente virtual não encontrado. Criando..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Atualizar código do Git
echo "📥 Atualizando código do Git..."
if [ -d ".git" ]; then
    git fetch origin
    git reset --hard origin/main || git reset --hard origin/master
    echo "✅ Código atualizado"
else
    echo "⚠️ Repositório Git não encontrado. Pulando atualização do Git."
fi

# Instalar/atualizar dependências
echo "📦 Instalando/atualizando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# Aplicar migrações
echo "🗄️ Aplicando migrações do banco de dados..."
export DJANGO_ENV=production
python manage.py migrate --noinput

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Reiniciar Gunicorn
echo "🔄 Reiniciando serviço Gunicorn..."
if systemctl is-active --quiet gunicorn_oncristo; then
    systemctl restart gunicorn_oncristo
    echo "✅ Gunicorn reiniciado"
else
    echo "⚠️ Serviço Gunicorn não está ativo. Iniciando..."
    systemctl start gunicorn_oncristo
fi

# Verificar status
echo "✅ Verificando status do serviço..."
sleep 2
if systemctl is-active --quiet gunicorn_oncristo; then
    echo "✅ Serviço Gunicorn está rodando corretamente"
    systemctl status gunicorn_oncristo --no-pager -l
else
    echo "❌ Erro: Serviço Gunicorn não está rodando!"
    systemctl status gunicorn_oncristo --no-pager -l
    exit 1
fi

echo ""
echo "✅ Deploy concluído com sucesso!"
echo "🌐 Acesse: https://oncristo.com.br"

