# Gunicorn configuration file
# Uso: gunicorn -c gunicorn_config.py pro_igreja.wsgi:application

import multiprocessing
import os

# Diretório do projeto
bind = "unix:/home/django/oncristo/gunicorn.sock"
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
pidfile = "/home/django/oncristo/gunicorn.pid"
umask = 0
user = "django"
group = "www-data"
tmp_upload_dir = None

# SSL (se necessário)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

