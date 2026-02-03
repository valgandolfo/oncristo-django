# OnCristo - Instruções para Agentes de IA

## Visão Geral do Projeto

**OnCristo** é uma plataforma Django integrada com aplicativo Flutter para gerenciamento de paróquias católicas. O sistema funciona em dois modos:
- **Modo Web** (Desktop/Responsivo): Interface web tradicional
- **Modo App** (Flutter WebView): Aplicativo híbrido para dispositivos móveis

O projeto está hospedado no DigitalOcean com Gunicorn/Nginx e usa S3-compatible storage (DigitalOcean Spaces) para mídia.

## Arquitetura Geral

### Estrutura de Código
```
pro_igreja/             # Projeto Django (settings, urls, wsgi)
  settings.py          # Configuração multiambiente (local/produção)
  urls.py              # Roteamento principal
  
app_igreja/            # App principal
  models/
    area_admin/        # Modelos administrativos (paróquias, liturgias, escala, etc.)
    area_publica/      # Modelos públicos
  views/
    admin_area/        # Vistas administrativas (CRUD, relatórios)
    area_publica/      # Vistas públicas (API, formulários públicos)
  forms/               # Formulários Django
  middleware.py        # AppModeMiddleware (preserva modo=app no Flutter)
  backends.py          # EmailBackend (login por email ou username)
```

### Domínios de Negócio
1. **Administrativo**: Gerenciamento de dioceses, paróquias, celebrantes, colaboradores, liturgias
2. **Finanças**: Controle de dízimos (TBDIZIMISTAS, TBGERDIZIMO), doacoes, escala de cobrança
3. **Eventos**: Celebrações, escala mensal de missas, eventos e itens (Eventos substituem Planos antigos)
4. **Comunicação**: Murais, avisos, WhatsApp API, YouTube integrado
5. **Público**: Horários de missas, liturgias, pedidos de oração, cadastros

## Padrões Críticos

### 1. Ambientes e Configuração
```python
# settings.py detecta automaticamente o ambiente
DJANGO_ENV = os.getenv('DJANGO_ENV', 'development')  # 'development' ou 'production'
# Carrega .env_local (dev) ou .env_production (prod)
```
**Importante**: SEMPRE testar mudanças em desenvolvimento com `DJANGO_ENV=development`.

### 2. Sistema de Storage Multiprovededor
```python
STORAGE_PROVIDER = os.getenv('STORAGE_PROVIDER', 'local')  # ou 'aws', 'digitalocean', 'wasabi', 'backblaze', 'cloudflare'
```
- **Local (dev)**: Usa `media/` do disco
- **Produção**: DigitalOcean Spaces (S3-compatible)
- Modelos com imagem usam `ImageField` que automaticamente delegam ao storage configurado

### 3. Autenticação Customizada
```python
# backends.py: EmailBackend permite login por EMAIL ou USERNAME
# Em views: usar @login_required e garantir verificação de permissões
```

### 4. Modo App (Flutter Integration)
```python
# middleware.py: AppModeMiddleware preserva ?modo=app em redirecionamentos
# Necessário porque Flutter WebView tem restrições ORB (Cross-Origin Embedder Policy)
# Detecção automática via: GET ?modo=app, sessão, ou HTTP_REFERER
```
**Regra**: Quando redirecionar dentro do app, SEMPRE incluir `?modo=app` nas URLs.

### 5. Database Multiambiente
- **Desenvolvimento**: SQLite (`db.sqlite3`)
- **Produção**: MySQL com SSL (DigitalOcean)
```python
# settings.py configura automaticamente baseado em DB_ENGINE/.env
# MySQL requer 'ssl': {'ca': None} para DigitalOcean
```

## Workflows Críticos

### Setup Inicial
```bash
cd /home/joaonote/oncristo.local
bash iniciar_projeto.sh  # Cria venv, instala dependências, executa migrações
```

### Desenvolvimento Diário
```bash
source venv/bin/activate  # Ativar ambiente virtual
export DJANGO_ENV=development
python manage.py runserver 0.0.0.0:8000
```

### Teste de Funcionalidade
```bash
python manage.py test                    # Rodar testes
python manage.py shell                   # Shell interativo para testar queries
python manage.py migrate --no-input      # Aplicar migrações
```

### Deploy Automático (Recomendado)
```bash
./deploy_completo.sh  # Faz commit, push, conecta SSH ao DigitalOcean e deploy automático
```

### Deploy Manual
1. **Local**: `git add . && git commit && git push origin main`
2. **Servidor**: `ssh root@137.184.116.197 && cd /home/oncristo && ./deploy.sh`

### Gerenciar Serviços (Produção)
```bash
systemctl status gunicorn_oncristo   # Status do Gunicorn
systemctl restart gunicorn_oncristo  # Reiniciar após mudanças
systemctl status nginx               # Status do Nginx
systemctl reload nginx               # Recarregar config Nginx
```

## Convenções de Código

### Nomes de Modelos
- Prefixo `TB` + nome em maiúsculas (ex: `TBPAROQUIA`, `TBDIZIMISTAS`, `TBCELEBRANTES`)
- Campos seguem padrão: Prefixo 3-4 letras + sufixo (ex: `PAR_id`, `DIS_nome`, `MUR_data_mural`)

### Views CRUD
- Função-based views são preferidas (mais comuns no projeto)
- Nomenclatura: `listar_*`, `criar_*`, `editar_*`, `excluir_*`, `detalhar_*`
- Exemplo: `listar_dizimistas`, `criar_celebrante`, `editar_colaborador`

### Relatórios e PDFs
- Usar `weasyprint` para gerar PDFs (já instalado)
- Exemplo: [app_igreja/views/admin_area/views_relatorios.py](app_igreja/views/admin_area/views_relatorios.py)

### APIs/Webhooks
- WhatsApp: Webhook em [views_whatsapp_api.py](app_igreja/views/area_publica/views_whatsapp_api.py)
- YouTube: Verificar livestream em [views_youtube.py](app_igreja/views/area_publica/views_youtube.py)
- Endpoints JSON: Usar `application/json` e retornar `JsonResponse()`

### Segurança
- **Session timeout**: 30 min (área administrativa)
- **CSRF**: Middleware ativo; usar `@csrf_protect` em views sensíveis
- **HTTPS em produção**: Nginx redireciona HTTP → HTTPS automaticamente
- **Authentication**: Verificar `@login_required` em todas as views admin

## Integração com S3 / DigitalOcean Spaces

### Upload de Arquivos
```python
# Models com imagens delegam automaticamente ao storage configurado
class TBPAROQUIA(models.Model):
    PAR_imagem = models.ImageField(upload_to='paroquias/', null=True, blank=True)
    # Em produção: salva em DigitalOcean Spaces automaticamente
```

### Debug de Uploads
- Script de teste: [debug_s3_upload.py](debug_s3_upload.py)
- Verificar credenciais: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`

## Estrutura de Banco de Dados

### Tabelas Principais
- **TBPAROQUIA**: Dados da paróquia (contato, coordenadas, imagens)
- **TBDIZIMISTAS**: Dizimistas cadastrados com status, data de pagamento
- **TBGERDIZIMO**: Geração mensal automática de mensalidades
- **TBCELEBRANTES**: Sacerdotes e diáconos
- **TBCOLABORADORES**: Voluntários com funções e grupos litúrgicos
- **TBCELEBRACOES**: Batizados, casamentos, funerais com escala
- **TBMODELO + TBITEM_MODELO**: Escalas de base (reutilizáveis)
- **TBITEM_ESCALA**: Escala gerada do modelo aplicada a celebrantes/colaboradores

### Migrations
- Localização: [app_igreja/migrations/](app_igreja/migrations/)
- Criar nova: `python manage.py makemigrations app_igreja`
- Aplicar: `python manage.py migrate`
- Em produção: `migrate --no-input` durante deploy

## Troubleshooting Comum

| Problema | Solução |
|----------|---------|
| "Modo app" quebrado (ORB error em Flutter) | Verificar middleware.py; garantir `?modo=app` em redirects |
| Imagens não aparecem em produção | Verificar: `STORAGE_PROVIDER`, credenciais S3, `collectstatic` executado |
| Login falha | Backend EmailBackend suporta email E username; verificar User.objects.filter() |
| Migrações atrasadas em produção | Rodar `./deploy_completo.sh`; inclui `migrate --no-input` automático |
| Timeout de sessão muito curto | Editar `SESSION_COOKIE_AGE` em settings.py (segundos) |

## Recursos Importantes

- **Deploy Info**: [INFORMACOES_DEPLOY.md](INFORMACOES_DEPLOY.md)
- **Requirements**: [requirements.txt](requirements.txt) (Django 5.0.3, Gunicorn, WeasyPrint, boto3)
- **GitHub Repo**: `https://github.com/valgandolfo/oncristo-django.git`
- **Servidor**: IP `137.184.116.197`, domínio `oncristo.com.br`
