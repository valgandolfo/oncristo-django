#!/bin/bash

# 🚀 SCRIPT PARA INICIAR SERVIDOR DJANGO + NGROK AUTOMATICAMENTE
# Autor: Assistente IA
# Uso: ./iniciar_tudo.sh

echo "🎯 INICIANDO SERVIDOR DJANGO + NGROK"
echo "======================================"
echo ""

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

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    print_error "Ambiente virtual não encontrado!"
    print_info "Execute primeiro: ./iniciar_projeto.sh"
    exit 1
fi

# Ativar ambiente virtual
print_info "Ativando ambiente virtual..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    print_error "Erro ao ativar ambiente virtual!"
    exit 1
fi

print_status "Ambiente virtual ativado!"

# Verificar e instalar dependências essenciais
print_info "Verificando dependências..."

# Lista de dependências essenciais
dependencies=(
    "Django==5.0.3"
    "python-dotenv==1.0.1"
    "django-storages==1.14.2"
    "boto3==1.34.0"
    "Pillow==10.4.0"
    "requests==2.31.0"
    "django-widget-tweaks==1.5.0"
)

for dep in "${dependencies[@]}"; do
    package_name=$(echo "$dep" | cut -d'=' -f1)
    if ! pip show "$package_name" &> /dev/null; then
        print_warning "$package_name não encontrado. Instalando..."
        pip install "$dep" --quiet
        if [ $? -eq 0 ]; then
            print_status "$package_name instalado!"
        else
            print_error "Erro ao instalar $package_name!"
        fi
    fi
done

print_success "Dependências verificadas!"

# Parar processos existentes
print_info "Verificando processos existentes..."

# Parar servidor Django se estiver rodando
if pgrep -f "manage.py runserver.*8000" > /dev/null; then
    print_warning "Servidor Django já está rodando. Parando..."
    pkill -f "manage.py runserver.*8000"
    sleep 2
fi

# Parar ngrok se estiver rodando
if pgrep -f "ngrok" > /dev/null; then
    print_warning "ngrok já está rodando. Parando..."
    pkill -f ngrok
    sleep 2
fi

# Verificar se ngrok está instalado
if ! command -v ngrok &> /dev/null; then
    print_error "ngrok não está instalado!"
    print_info "Para instalar: sudo snap install ngrok"
    print_info "Ou baixar de: https://ngrok.com/download"
    exit 1
fi

print_status "ngrok está instalado"

# Criar diretório para logs se não existir
mkdir -p logs

# Função para limpar processos ao sair
cleanup() {
    echo ""
    print_warning "Parando processos..."
    
    # Parar servidor Django
    if pgrep -f "manage.py runserver.*8000" > /dev/null; then
        pkill -f "manage.py runserver.*8000"
        print_status "Servidor Django parado"
    fi
    
    # Parar ngrok
    if pgrep -f "ngrok" > /dev/null; then
        pkill -f ngrok
        print_status "ngrok parado"
    fi
    
    print_info "Todos os processos foram parados. Até logo!"
    exit 0
}

# Capturar Ctrl+C
trap cleanup SIGINT SIGTERM

# Detectar IP local da rede
IP_LOCAL=$(hostname -I | awk '{print $1}')

# Iniciar servidor Django em background
print_info "Iniciando servidor Django na porta 8000..."
python manage.py runserver 0.0.0.0:8000 > logs/django.log 2>&1 &
DJANGO_PID=$!

# Aguardar servidor iniciar
sleep 3

# Verificar se o servidor iniciou corretamente
if ! pgrep -f "manage.py runserver.*8000" > /dev/null; then
    print_error "Erro ao iniciar servidor Django!"
    print_info "Verifique o log: logs/django.log"
    exit 1
fi

print_status "Servidor Django iniciado! (PID: $DJANGO_PID)"

# Iniciar ngrok em background
print_info "Iniciando ngrok na porta 8000..."
ngrok http 8000 > logs/ngrok.log 2>&1 &
NGROK_PID=$!

# Aguardar ngrok iniciar
sleep 5

# Verificar se ngrok iniciou
if ! pgrep -f "ngrok" > /dev/null; then
    print_error "Erro ao iniciar ngrok!"
    print_info "Verifique o log: logs/ngrok.log"
    # Parar Django se ngrok falhou
    pkill -f "manage.py runserver.*8000"
    exit 1
fi

print_status "ngrok iniciado! (PID: $NGROK_PID)"

# Tentar obter URL do ngrok da API
sleep 3
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"https://[^"]*"' | head -1 | cut -d'"' -f4)

echo ""
print_success "🎉 SERVIDOR DJANGO + NGROK INICIADOS COM SUCESSO!"
echo ""
print_info "📋 INFORMAÇÕES DO SERVIDOR:"
echo "   🌐 Local (PC): http://127.0.0.1:8000"
echo "   📱 Rede (Celular): http://${IP_LOCAL}:8000"
echo "   🔧 Debug: HABILITADO"
echo ""
print_info "🔗 URLs DISPONÍVEIS:"
echo "   🏠 Home Local: http://127.0.0.1:8000/"
echo "   🏠 Home Rede: http://${IP_LOCAL}:8000/"
echo "   ⚙️  Admin: http://${IP_LOCAL}:8000/app_igreja/admin-area/"
echo "   🗄️  Django Admin: http://${IP_LOCAL}:8000/admin/"
echo ""

if [ -n "$NGROK_URL" ]; then
    print_info "🌐 NGROK URL:"
    echo "   🔗 Pública: ${NGROK_URL}"
    echo "   📱 WhatsApp Webhook: ${NGROK_URL}/app_igreja/api/whatsapp/webhook/"
    echo "   🧪 Teste Webhook: ${NGROK_URL}/app_igreja/api/whatsapp/test/"
    echo ""
    print_warning "⚠️  Configure esta URL no painel da Whapi Cloud:"
    echo "   ${NGROK_URL}/app_igreja/api/whatsapp/webhook/"
    echo ""
else
    print_warning "⚠️  Não foi possível obter a URL do ngrok automaticamente."
    print_info "   Acesse: http://localhost:4040 para ver a URL do ngrok"
    echo ""
fi

print_info "📊 LOGS:"
echo "   Django: logs/django.log"
echo "   ngrok: logs/ngrok.log"
echo "   ngrok UI: http://localhost:4040"
echo ""
print_warning "⚠️  Para parar tudo, pressione Ctrl+C"
echo ""

# Manter script rodando e monitorar processos
while true; do
    # Verificar se Django ainda está rodando
    if ! pgrep -f "manage.py runserver.*8000" > /dev/null; then
        print_error "Servidor Django parou inesperadamente!"
        cleanup
    fi
    
    # Verificar se ngrok ainda está rodando
    if ! pgrep -f "ngrok" > /dev/null; then
        print_error "ngrok parou inesperadamente!"
        cleanup
    fi
    
    sleep 5
done

