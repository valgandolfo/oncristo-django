#!/bin/bash
# ============================================================
# RODAR NO SERVIDOR (em /home/oncristo)
# Ajuda a descobrir a causa do Server Error (500).
# ============================================================

set -e

PROJECT_DIR="/home/oncristo"
cd "$PROJECT_DIR"

echo "=== 1. Arquivo .env_production existe? ==="
if [ -f ".env_production" ]; then
    echo "Sim. Tamanho: $(stat -c%s .env_production) bytes"
else
    echo "NAO. Crie ou copie .env_production para /home/oncristo (rsync nao envia .env)."
fi

echo ""
echo "=== 2. Variaveis necessarias no .env_production (apenas nomes) ==="
[ -f ".env_production" ] && grep -E '^[A-Z_]+=' .env_production | cut -d= -f1 | sort || true

echo ""
echo "=== 3. Django check (DJANGO_ENV=production) ==="
set +e
source venv/bin/activate 2>/dev/null
export DJANGO_ENV=production
python manage.py check 2>&1
CHECK_EXIT=$?
set -e
if [ $CHECK_EXIT -ne 0 ]; then
    echo "Django check FALHOU - corrija os erros acima."
fi

echo ""
echo "=== 4. Ultimas linhas do Gunicorn (erro 500 costuma aparecer aqui) ==="
journalctl -u gunicorn_oncristo -n 30 --no-pager 2>/dev/null || echo "Rode como root ou com sudo."

echo ""
echo "=== Dica: se .env_production nao existir, copie da sua maquina: ==="
echo "  scp .env_production root@SEU_SERVIDOR:/home/oncristo/"
echo "  (depois: systemctl restart gunicorn_oncristo)"
