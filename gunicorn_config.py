# Gunicorn configuration file
# Uso: gunicorn -c gunicorn_config.py pro_igreja.wsgi:application

import multiprocessing
import os

# Diretório do projeto (igual ao REMOTE_DIR do local_subir_para_do.sh)
PROJECT_DIR = "/home/oncristo"
bind = f"unix:{PROJECT_DIR}/gunicorn.sock"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = "info"

# Process naming
proc_name = "oncristo_gunicorn"

# Server mechanics
daemon = False
pidfile = f"{PROJECT_DIR}/gunicorn.pid"
umask = 0
tmp_upload_dir = None

# SSL (se necessário)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

