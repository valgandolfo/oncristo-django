#!/bin/bash
# ============================================================
# RODAR NO SERVIDOR (como root)
# Garante que o Gunicorn use DJANGO_ENV=production para carregar production.py
# e assim ALLOWED_HOSTS inclua oncristo.com.br.
# ============================================================

SERVICE_NAME="gunicorn_oncristo"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

if [ ! -f "$SERVICE_FILE" ]; then
    echo "Arquivo não encontrado: $SERVICE_FILE"
    echo "Ajuste SERVICE_NAME no script se o serviço tiver outro nome."
    exit 1
fi

if grep -q 'Environment="DJANGO_ENV=production"' "$SERVICE_FILE" || grep -q "Environment=DJANGO_ENV=production" "$SERVICE_FILE"; then
    echo "DJANGO_ENV=production já está configurado em $SERVICE_FILE"
else
    echo "Adicionando Environment=DJANGO_ENV=production em [Service]..."
    sed -i '/^\[Service\]/a Environment=DJANGO_ENV=production' "$SERVICE_FILE"
    echo "Feito."
fi

echo "Recarregando systemd, reiniciando Gunicorn e recarregando Nginx..."
systemctl daemon-reload
systemctl restart "$SERVICE_NAME"
systemctl reload nginx
echo ""
systemctl status "$SERVICE_NAME" --no-pager -l
echo ""
echo "Nginx: $(systemctl is-active nginx 2>/dev/null || echo '?')"

echo ""
echo "Pronto. O Django deve carregar pro_igreja.settings.production e aceitar oncristo.com.br"
