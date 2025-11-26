# 📱 Documentação do Chatbot WhatsApp

Este documento lista todos os arquivos Python (.py) e HTML relacionados ao chatbot WhatsApp do sistema.

---

## 🔗 **1. WEBHOOK E API DO CHATBOT**

### **Arquivo Principal do Webhook**
- **Arquivo**: `app_igreja/views/area_publica/views_whatsapp_api.py`
- **Descrição**: Arquivo principal que processa todas as mensagens recebidas do WhatsApp via webhook. Contém:
  - Função `whatsapp_webhook()` - endpoint principal do webhook
  - Função `send_whatsapp_menu()` - envia menu principal interativo
  - Função `processar_item_menu()` - processa seleção de itens do menu
  - Função `processar_botao_menu()` - processa cliques em botões
  - Funções de envio de menus específicos:
    - `send_whatsapp_menu_liturgias()`
    - `send_whatsapp_menu_dizimista()`
    - `send_whatsapp_menu_colaborador()`
    - `send_whatsapp_menu_escalas()`
    - `send_whatsapp_menu_agendar_celebracao()`
    - `send_whatsapp_menu_oracoes()`
  - Função `get_site_url()` - determina URL local/ngrok/produção
  - Função `limpar_telefone()` - limpa e formata números de telefone

---

## 📖 **2. LITURGIAS**

### **View (Backend)**
- **Arquivo**: `app_igreja/views/area_publica/views_liturgias_publico.py`
- **Função Principal**: `liturgias_publico(request)`
- **Descrição**: Exibe liturgias do dia atual (filtra automaticamente por data atual se não houver parâmetro)

### **Template (Frontend)**
- **Arquivo**: `templates/area_publica/tpl_liturgias_publico.html`
- **Descrição**: Template que exibe as liturgias do dia em formato público

### **URL**
- **Rota**: `/app_igreja/liturgias/`
- **Configuração**: `app_igreja/urls.py`

---

## 💰 **3. DIZIMISTAS**

### **View (Backend)**
- **Arquivo**: `app_igreja/views/area_publica/views_dizimistas.py`
- **Função Principal**: `quero_ser_dizimista(request)`
- **Descrição**: 
  - Aceita parâmetro `telefone` via GET
  - Pré-preenche campo de telefone (readonly)
  - Remove código do país (55) antes de salvar
  - Redireciona para home após sucesso

### **Template (Frontend)**
- **Arquivo**: `templates/area_publica/tpl_dizimistas_publico.html`
- **Descrição**: Formulário público de cadastro de dizimista com telefone pré-preenchido

### **URL**
- **Rota**: `/app_igreja/quero-ser-dizimista/`
- **Configuração**: `app_igreja/urls.py`

---

## 👥 **4. COLABORADORES**

### **View (Backend)**
- **Arquivo**: `app_igreja/views/area_publica/views_colaboradores_publico.py`
- **Função Principal**: `quero_ser_colaborador(request)`
- **Descrição**: 
  - Aceita parâmetro `telefone` via GET
  - Pré-preenche campo de telefone (readonly)
  - Remove código do país (55) antes de salvar
  - Define status como 'PENDENTE' automaticamente
  - Oculta campos de status e membro ativo
  - Redireciona para home após sucesso
  - Valida telefone duplicado antes de salvar

### **Form (Validação)**
- **Arquivo**: `app_igreja/forms/area_publica/forms_colaboradores_publico.py`
- **Classe**: `ColaboradorPublicoForm`
- **Descrição**: 
  - Formulário simplificado para cadastro público
  - Validação de telefone duplicado no método `clean_COL_telefone()`
  - Remove código do país (55) automaticamente
  - Define status como 'PENDENTE' no método `save()`

### **Template (Frontend)**
- **Arquivo**: `templates/area_publica/tpl_colaboradores_publico_whatsapp.html`
- **Descrição**: 
  - Formulário público de cadastro de colaborador
  - Telefone readonly quando vem do WhatsApp
  - Loading overlay durante submissão
  - Modal de sucesso com redirecionamento

### **URL**
- **Rota**: `/app_igreja/quero-ser-colaborador/`
- **Configuração**: `app_igreja/urls.py`

---

## ⏰ **5. ESCALAS DE MISSAS**

### **View (Backend)**
- **Arquivo**: `app_igreja/views/area_publica/views_escala_publico.py`
- **Funções Principais**: 
  - `escala_publico(request)` - exibe grid de escalas
  - `atribuir_colaborador_escala(request)` - API para atribuir colaborador (AJAX)
- **Descrição**: 
  - Busca colaborador por telefone (flexível: com/sem 55, parcial)
  - Filtra escalas por mês/ano
  - Permite atribuição de colaborador a item de escala

### **Template (Frontend)**
- **Arquivo**: `templates/area_publica/tpl_escala_publico.html`
- **Descrição**: 
  - Grid com colunas: ATR | DIA | DIA SEMANA | HORA | ENCARGO | COLABORADOR
  - Ícone de pessoa para atribuir, X para bloqueado
  - Modal de confirmação para atribuição
  - Botão flutuante "Home"
  - Responsivo para mobile

### **URL**
- **Rotas**: 
  - `/app_igreja/escala-missas/` - visualização
  - `/app_igreja/escala-missas/atribuir/` - API de atribuição
- **Configuração**: `app_igreja/urls.py`

---

## 🕯️ **6. AGENDAR CELEBRAÇÕES**

### **View (Backend)**
- **Arquivo**: `app_igreja/views/area_publica/views_celebracoes_publico.py`
- **Funções Principais**: 
  - `agendar_celebracao_publico(request)` - formulário de agendamento
  - `minhas_celebracaoes_publico_detalhe(request, telefone)` - lista de celebrações
- **Descrição**: 
  - Aceita parâmetro `telefone` via GET
  - Pré-preenche campo de telefone (readonly)
  - Remove código do país (55) antes de salvar
  - Permite múltiplos agendamentos (não redireciona após salvar)
  - Mostra histórico das últimas 10 celebrações

### **Form (Validação)**
- **Arquivo**: `app_igreja/forms/area_publica/forms_celebracoes_publico.py`
- **Classe**: `CelebracaoPublicoForm`
- **Descrição**: 
  - Formulário simplificado para agendamento público
  - Remove campo de status (sempre 'pendente')
  - Telefone readonly quando vem do WhatsApp

### **Template (Frontend)**
- **Arquivo**: `templates/area_publica/tpl_agendar_celebracao_publico.html`
- **Descrição**: 
  - Formulário de agendamento de celebrações
  - Telefone readonly quando vem do WhatsApp
  - Loading overlay durante submissão
  - Limpa formulário após sucesso (permite novo agendamento)
  - Mostra histórico de celebrações agendadas

### **URL**
- **Rotas**: 
  - `/app_igreja/agendar-celebracao/` - agendar nova celebração
  - `/app_igreja/minhas-celebracoes/<telefone>/` - consultar celebrações
- **Configuração**: `app_igreja/urls.py`

---

## 🙏 **7. PEDIDOS DE ORAÇÃO**

### **View (Backend)**
- **Arquivo**: `app_igreja/views/area_publica/views_oracoes.py`
- **Função Principal**: `criar_pedido_oracao_publico(request)`
- **Descrição**: 
  - **NÃO requer login** (removido `@login_required`)
  - Permite criar pedido de oração sem autenticação
  - Redireciona para home após sucesso (se não estiver logado)

### **Form (Validação)**
- **Arquivo**: `app_igreja/forms/area_admin/forms_oracoes.py`
- **Classe**: `OracaoPublicoForm`
- **Descrição**: 
  - Formulário público simplificado (sem campos administrativos)
  - Validação de descrição (mínimo 10 caracteres)
  - Máscara de telefone no widget

### **Template (Frontend)**
- **Arquivo**: `templates/area_publica/tpl_oracoes_publico.html`
- **Descrição**: 
  - Formulário de pedido de oração
  - Máscara JavaScript para telefone
  - Suporta três ações: criar, consultar, listar

### **URL**
- **Rota**: `/app_igreja/meus-pedidos-oracoes/novo/`
- **Configuração**: `app_igreja/urls.py`

---

## 🎨 **8. TEMPLATES BASE**

### **Template Base para Formulários Públicos**
- **Arquivo**: `templates/area_publica/base_form_publico.html`
- **Descrição**: 
  - Template base para todos os formulários públicos
  - **NÃO requer login** (verificação removida)
  - Estrutura comum: hero section, form container, footer com botões
  - Estilos padronizados

---

## ⚙️ **9. CONFIGURAÇÃO DE URLs**

### **Arquivo de Rotas**
- **Arquivo**: `app_igreja/urls.py`
- **Rotas do Chatbot**:
  ```python
  # Webhook
  path('api/whatsapp/webhook/', whatsapp_webhook, name='whatsapp_webhook'),
  
  # Liturgias
  path('liturgias/', liturgias_publico, name='liturgias_publico'),
  
  # Dizimistas
  path('quero-ser-dizimista/', quero_ser_dizimista, name='quero_ser_dizimista'),
  
  # Colaboradores
  path('quero-ser-colaborador/', quero_ser_colaborador, name='quero_ser_colaborador'),
  
  # Escalas
  path('escala-missas/', escala_publico, name='escala_publico'),
  path('escala-missas/atribuir/', atribuir_colaborador_escala, name='atribuir_colaborador_escala'),
  
  # Celebrações
  path('agendar-celebracao/', agendar_celebracao_publico, name='agendar_celebracao_publico'),
  path('minhas-celebracoes/<str:telefone>/', minhas_celebracaoes_publico_detalhe, name='minhas_celebracaoes_publico_detalhe'),
  
  # Orações
  path('meus-pedidos-oracoes/novo/', criar_pedido_oracao_publico, name='criar_pedido_oracao_publico'),
  ```

---

## 🔑 **10. VARIÁVEIS DE AMBIENTE**

### **Arquivo de Configuração**
- **Arquivo**: `.env_local` (ou `.env`, `.env_production`)
- **Variáveis Necessárias**:
  ```
  WHAPI_KEY=seu_token_aqui
  WHAPI_CHANNEL_ID=seu_channel_id
  # OU
  WHATSAPP_API_KEY=seu_token_aqui
  WHATSAPP_CHANNEL_ID=seu_channel_id
  
  SITE_URL=https://seu-site.com.br
  SITE_URL_LOCAL=http://192.168.0.12:8000
  NGROK_URL=https://seu-ngrok.ngrok.io  # (opcional, auto-detectado)
  ```

---

## 📋 **11. FLUXO DO CHATBOT**

### **Fluxo Principal**
1. **Usuário envia mensagem** → Webhook recebe em `views_whatsapp_api.py`
2. **Sistema envia menu principal** → `send_whatsapp_menu()`
3. **Usuário seleciona opção** → `processar_item_menu()`
4. **Sistema envia menu interativo** → Funções específicas (ex: `send_whatsapp_menu_liturgias()`)
5. **Usuário clica "Sim"** → Redirecionado para URL pública
6. **Usuário preenche formulário** → View pública processa
7. **Sistema salva dados** → Redireciona ou mantém na página

### **Estrutura de Menus**
- **Menu Principal**: Lista com 6 opções
  1. 📖 Liturgias
  2. 👥 Quero ser Colaborador
  3. ⏰ Escalas de Missas
  4. 💰 Dízimo, ofertas e donativos
  5. 🕯️ Agendar Celebrações
  6. 🙏 Pedido de Oração

- **Menus Interativos**: Botões "Sim" / "Não" para cada opção

---

## 🐛 **12. PONTOS DE ATENÇÃO PARA DEBUG**

### **Problemas Comuns**

1. **Webhook não recebe mensagens**
   - Verificar: `views_whatsapp_api.py` → função `whatsapp_webhook()`
   - Verificar: URL do webhook configurada na Whapi Cloud
   - Verificar: Variáveis de ambiente (WHAPI_KEY, WHAPI_CHANNEL_ID)

2. **Menu não aparece**
   - Verificar: `send_whatsapp_menu()` em `views_whatsapp_api.py`
   - Verificar: Formato do payload (deve ser `type: "list"`)

3. **Botões não funcionam**
   - Verificar: `processar_botao_menu()` em `views_whatsapp_api.py`
   - Verificar: IDs dos botões correspondem aos enviados

4. **URLs erradas (produção vs local)**
   - Verificar: `get_site_url()` em `views_whatsapp_api.py`
   - Verificar: Variáveis SITE_URL_LOCAL, NGROK_URL, SITE_URL

5. **Telefone não pré-preenche**
   - Verificar: View pública recebe parâmetro `telefone` via GET
   - Verificar: Template renderiza campo como readonly
   - Verificar: Função `limpar_telefone()` remove código do país

6. **Formulário não salva**
   - Verificar: View pública não tem `@login_required`
   - Verificar: Template base não bloqueia acesso (`base_form_publico.html`)
   - Verificar: Form valida corretamente

7. **Telefone duplicado**
   - Verificar: `forms_colaboradores_publico.py` → `clean_COL_telefone()`
   - Verificar: Busca flexível (com/sem formatação, com/sem 55)

---

## 📝 **13. RESUMO DE ARQUIVOS**

### **Python (.py)**
1. `app_igreja/views/area_publica/views_whatsapp_api.py` - **PRINCIPAL** (webhook)
2. `app_igreja/views/area_publica/views_liturgias_publico.py` - Liturgias
3. `app_igreja/views/area_publica/views_dizimistas.py` - Dizimistas
4. `app_igreja/views/area_publica/views_colaboradores_publico.py` - Colaboradores
5. `app_igreja/views/area_publica/views_escala_publico.py` - Escalas
6. `app_igreja/views/area_publica/views_celebracoes_publico.py` - Celebrações
7. `app_igreja/views/area_publica/views_oracoes.py` - Orações
8. `app_igreja/forms/area_publica/forms_colaboradores_publico.py` - Form Colaboradores
9. `app_igreja/forms/area_publica/forms_celebracoes_publico.py` - Form Celebrações
10. `app_igreja/forms/area_admin/forms_oracoes.py` - Form Orações
11. `app_igreja/urls.py` - Rotas

### **HTML (.html)**
1. `templates/area_publica/tpl_liturgias_publico.html` - Liturgias
2. `templates/area_publica/tpl_dizimistas_publico.html` - Dizimistas
3. `templates/area_publica/tpl_colaboradores_publico_whatsapp.html` - Colaboradores
4. `templates/area_publica/tpl_escala_publico.html` - Escalas
5. `templates/area_publica/tpl_agendar_celebracao_publico.html` - Celebrações
6. `templates/area_publica/tpl_oracoes_publico.html` - Orações
7. `templates/area_publica/base_form_publico.html` - Template Base

---

## ✅ **14. CHECKLIST DE TESTES**

- [ ] Webhook recebe mensagens
- [ ] Menu principal aparece
- [ ] Cada opção do menu funciona
- [ ] Botões "Sim"/"Não" funcionam
- [ ] URLs redirecionam corretamente (local/ngrok/produção)
- [ ] Telefone pré-preenche nos formulários
- [ ] Formulários salvam sem login
- [ ] Validação de telefone duplicado funciona
- [ ] Máscara de telefone funciona
- [ ] Redirecionamentos após salvar funcionam
- [ ] Loading overlay aparece durante submissão
- [ ] Modal de sucesso aparece

---

**Última atualização**: 23/11/2025
**Versão do Django**: 5.0.3

