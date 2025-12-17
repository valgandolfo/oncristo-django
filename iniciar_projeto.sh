#!/bin/bash

# 🚀 SCRIPT PARA INICIAR O PROJETO ON CRISTO
# Autor: Assistente IA
# Data: Setembro 2025

echo "🎯 INICIANDO PROJETO ON CRISTO"
echo "=================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Função para imprimir com cores
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${PURPLE}🎉 $1${NC}"
}

# Verifica se está no diretório correto
if [ ! -f "manage.py" ]; then
    print_error "Você não está no diretório do projeto Django!"
    print_info "Navegue para o diretório do projeto e execute novamente."
    exit 1
fi

print_status "Verificando diretório do projeto..."

# 1. CRIAR AMBIENTE VIRTUAL
print_info "1. Criando ambiente virtual..."
if [ -d "venv" ]; then
    print_warning "Ambiente virtual já existe. Removendo..."
    rm -rf venv
fi

python3 -m venv venv
if [ $? -eq 0 ]; then
    print_status "Ambiente virtual criado com sucesso!"
else
    print_error "Erro ao criar ambiente virtual!"
    exit 1
fi

# 2. ATIVAR AMBIENTE VIRTUAL
print_info "2. Ativando ambiente virtual..."
source venv/bin/activate
if [ $? -eq 0 ]; then
    print_status "Ambiente virtual ativado!"
    print_info "Python: $(which python)"
    print_info "Pip: $(which pip)"
else
    print_error "Erro ao ativar ambiente virtual!"
    exit 1
fi

# 3. ATUALIZAR PIP
print_info "3. Atualizando pip..."
pip install --upgrade pip
print_status "Pip atualizado!"

# 4. INSTALAR DEPENDÊNCIAS
print_info "4. Instalando dependências..."

# Lista de dependências principais
dependencies=(
    "Django==5.0.3"
    "python-dotenv==1.0.1"
    "django-storages==1.14.2"
    "boto3==1.34.0"
    "Pillow==10.4.0"
    "qrcode==8.2"
    "gunicorn==21.2.0"
    "whitenoise==6.6.0"
    "mysqlclient==2.2.0"
    "PyMySQL==1.1.1"
    "requests==2.31.0"
    "beautifulsoup4==4.12.3"
    "lxml==5.1.0"
    "django-widget-tweaks==1.5.0"
)

# Instalar cada dependência
for dep in "${dependencies[@]}"; do
    print_info "Instalando $dep..."
    pip install "$dep"
    if [ $? -eq 0 ]; then
        print_status "$dep instalado!"
    else
        print_error "Erro ao instalar $dep!"
        exit 1
    fi
done

print_success "Todas as dependências instaladas!"

# 5. VERIFICAR ARQUIVO .env_local
print_info "5. Verificando arquivo .env_local..."
if [ ! -f ".env_local" ]; then
    print_warning "Arquivo .env_local não encontrado!"
    print_info "Criando arquivo .env_local básico..."
    
    cat > .env_local << EOF
# Configurações do Banco de Dados
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

# Configurações do Django
DEBUG=True
SECRET_KEY=django-insecure-p^jvx3o%fns*))l(5bmtn^3+=_w5iz!dd^-6+pdhog__p23+d9
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Configurações de Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app

# Configurações AWS S3
AWS_ACCESS_KEY_ID=sua-access-key
AWS_SECRET_ACCESS_KEY=sua-secret-key
AWS_STORAGE_BUCKET_NAME=seu-bucket
AWS_S3_REGION_NAME=us-east-1

# Configurações WhatsApp API (Whapi Cloud)
WHAPI_KEY=sua-chave-api-whapi
CHANNEL_ID=seu-channel-id
# OU (alternativa)
WHATSAPP_API_KEY=sua-chave-api
WHATSAPP_CHANNEL_ID=seu-channel-id
WHATSAPP_BASE_URL=https://gate.whapi.cloud
EOF
    
    print_status "Arquivo .env_local criado!"
    print_warning "⚠️  IMPORTANTE: Configure as variáveis no arquivo .env_local!"
else
    print_status "Arquivo .env_local encontrado!"
fi

# 6. EXECUTAR MIGRAÇÕES
print_info "6. Executando migrações..."

# Verificar se há problemas com migrações antigas
python manage.py makemigrations
MAKEMIGRATIONS_STATUS=$?

if [ $MAKEMIGRATIONS_STATUS -eq 0 ]; then
    print_status "Migrações criadas!"
else
    print_warning "Nenhuma migração nova encontrada."
fi

# Tentar aplicar migrações
python manage.py migrate 2>&1 | tee /tmp/migrate_output.log
MIGRATE_STATUS=$?

if [ $MIGRATE_STATUS -ne 0 ]; then
    # Verificar se o erro é relacionado a tabelas não existentes ou migrações conflitantes
    if grep -q "no such table" /tmp/migrate_output.log || grep -q "OperationalError" /tmp/migrate_output.log; then
        print_error "Erro ao aplicar migrações!"
        print_warning "Detectado problema com migrações antigas/conflitantes."
        echo ""
        print_info "Opções disponíveis:"
        echo "   1. Resetar todas as migrações e começar do zero (RECOMENDADO se não há dados importantes)"
        echo "   2. Tentar corrigir manualmente"
        echo "   3. Sair e corrigir depois"
        echo ""
        read -p "Deseja resetar as migrações agora? (s/n): " resposta_reset
        
        if [ "$resposta_reset" = "s" ] || [ "$resposta_reset" = "S" ]; then
            print_info "Resetando migrações..."
            
            # Fazer backup do banco se existir
            if [ -f "db.sqlite3" ]; then
                BACKUP_NAME="db_backup_$(date +%Y%m%d_%H%M%S).sqlite3"
                cp db.sqlite3 "$BACKUP_NAME"
                print_status "Backup criado: $BACKUP_NAME"
            fi
            
            # Remover banco de dados
            rm -f db.sqlite3
            print_status "Banco de dados removido"
            
            # Remover todas as migrações (exceto __init__.py)
            find app_igreja/migrations -type f -name "*.py" ! -name "__init__.py" -delete
            find app_igreja/migrations -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
            print_status "Migrações antigas removidas"
            
            # Criar nova migração inicial
            print_info "Criando nova migração inicial..."
            python manage.py makemigrations app_igreja
            
            if [ $? -eq 0 ]; then
                print_status "Migração inicial criada!"
                
                # Aplicar migração
                print_info "Aplicando migração inicial..."
                python manage.py migrate
                
                if [ $? -eq 0 ]; then
                    print_success "Migrações resetadas e aplicadas com sucesso!"
                else
                    print_error "Erro ao aplicar migração inicial!"
                    exit 1
                fi
            else
                print_error "Erro ao criar migração inicial!"
                exit 1
            fi
        else
            print_warning "Migrações não foram resetadas. Corrija manualmente antes de continuar."
            print_info "Para resetar depois, execute: ./resetar_migracoes.sh"
            exit 1
        fi
    else
        print_error "Erro ao aplicar migrações!"
        print_info "Verifique o log acima para mais detalhes."
        exit 1
    fi
else
    print_status "Migrações aplicadas!"
fi

# Limpar arquivo temporário
rm -f /tmp/migrate_output.log

# 7. COLETAR ARQUIVOS ESTÁTICOS
print_info "7. Coletando arquivos estáticos..."
python manage.py collectstatic --noinput
if [ $? -eq 0 ]; then
    print_status "Arquivos estáticos coletados!"
else
    print_warning "Nenhum arquivo estático encontrado."
fi

# 8. VERIFICAR SE SUPERUSUÁRIO EXISTE
print_info "8. Verificando superusuário..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if User.objects.filter(is_superuser=True).exists():
    print('Superusuário encontrado!')
else:
    print('Nenhum superusuário encontrado.')
    print('Execute: python create_superuser.py')
"

# 9. INICIAR SERVIDOR DJANGO
print_info "9. Iniciando servidor Django..."
echo ""
print_success "🎉 PROJETO ON CRISTO INICIADO COM SUCESSO!"
echo ""
# Detectar IP local da rede
IP_LOCAL=$(hostname -I | awk '{print $1}')
print_info "📋 INFORMAÇÕES DO SERVIDOR:"
echo "   🌐 Local (PC): http://127.0.0.1:8002"
echo "   📱 Rede (Celular): http://${IP_LOCAL}:8002"
echo "   🔧 Debug: HABILITADO"
echo "   📊 Logs: VISÍVEIS NO TERMINAL"
echo "   🛑 Para parar: Ctrl+C"
echo ""
print_info "🔗 URLs disponíveis:"
echo "   🏠 Home Local: http://127.0.0.1:8002/"
echo "   🏠 Home Celular: http://${IP_LOCAL}:8002/"
echo "   🔐 Login: http://${IP_LOCAL}:8002/login/"
echo "   📝 Registro: http://${IP_LOCAL}:8002/register/"
echo "   ⚙️  Admin: http://${IP_LOCAL}:8002/app_igreja/admin-area/"
echo "   🗄️  Django Admin: http://${IP_LOCAL}:8002/admin/"
echo "   📱 WhatsApp Webhook: http://${IP_LOCAL}:8002/app_igreja/api/whatsapp/webhook/"
echo "   🧪 Teste Webhook: http://${IP_LOCAL}:8002/app_igreja/api/whatsapp/test/"
echo ""
print_warning "⚠️  LEMBRETES:"
echo "   - Configure o arquivo .env_local com suas credenciais"
echo "   - Configure WHAPI_KEY e CHANNEL_ID para o webhook do WhatsApp"
echo "   - Execute 'python create_superuser.py' se necessário"
echo "   - Verifique se a pasta 'static/' existe"
echo ""

# Iniciar servidor com debug habilitado (0.0.0.0 permite acesso de outras máquinas na rede)
python manage.py runserver 0.0.0.0:8002 --verbosity=2

# Se o servidor parar, mostrar mensagem
echo ""
print_info "Servidor parado. Para reiniciar, execute: ./iniciar_projeto.sh"

print_info "Servidor parado. Para reiniciar, execute: ./iniciar_projeto.sh"
