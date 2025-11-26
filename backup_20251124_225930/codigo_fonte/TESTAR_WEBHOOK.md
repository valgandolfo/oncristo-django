# 🧪 Guia Prático para Testar Webhook e Chatbot

## 🎯 Opções para Testar

### ✅ **OPÇÃO 1: Usar ngrok (MAIS PRÁTICO) ⭐ RECOMENDADO**

O **ngrok** cria um túnel público para seu servidor local, permitindo que a API do WhatsApp acesse seu webhook localmente.

#### Passo 1: Instalar ngrok
```bash
# No seu computador
# Ubuntu/Debian
sudo apt install ngrok

# Ou baixar de: https://ngrok.com/download
```

#### Passo 2: Iniciar servidor Django local
```bash
cd /home/joaonote/oncristo.local
./iniciar_servidor.sh
# Ou: python manage.py runserver 0.0.0.0:8000
```

#### Passo 3: Criar túnel ngrok
```bash
# Em outro terminal
ngrok http 8000
```

#### Passo 4: Configurar webhook na Whapi Cloud
- Use a URL do ngrok: `https://xxxx-xxxx-xxxx.ngrok-free.app/app_igreja/api/whatsapp/webhook/`
- A URL do ngrok será algo como: `https://abc123.ngrok-free.app`

**Vantagens:**
- ✅ Testa localmente sem fazer deploy
- ✅ Ver logs em tempo real
- ✅ Fácil de debugar
- ✅ Gratuito (com algumas limitações)

---

### ✅ **OPÇÃO 2: Testar Localmente com Postman/curl**

Testar o webhook diretamente sem precisar da API do WhatsApp:

```bash
# Testar endpoint de teste
curl http://localhost:8000/app_igreja/api/whatsapp/test/

# Simular webhook POST
curl -X POST http://localhost:8000/app_igreja/api/whatsapp/webhook/ \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{
      "id": "test123",
      "from": "5511999999999",
      "type": "text",
      "text": {"body": "teste"}
    }]
  }'
```

**Vantagens:**
- ✅ Testa a lógica sem precisar da API externa
- ✅ Rápido e direto
- ✅ Não precisa de ngrok

---

### ✅ **OPÇÃO 3: Deploy Seletivo (Só se realmente precisar)**

Se você **realmente** precisar testar na nuvem, use o script de deploy seletivo:

```bash
./deploy_webhook_chatbot.sh
```

**Quando usar:**
- ⚠️ Só se o ngrok não funcionar
- ⚠️ Se precisar testar com a URL de produção
- ⚠️ Se quiser validar no ambiente real

---

## 🎯 **RECOMENDAÇÃO**

**Use a OPÇÃO 1 (ngrok)** porque:
1. ✅ Mais rápido - não precisa fazer deploy
2. ✅ Testa localmente com logs em tempo real
3. ✅ Fácil de debugar e corrigir
4. ✅ Não mexe no servidor de produção
5. ✅ Pode testar quantas vezes quiser

---

## 📋 Passo a Passo com ngrok

### 1. Instalar ngrok
```bash
# Ubuntu
sudo snap install ngrok
# Ou
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/
```

### 2. Iniciar servidor Django
```bash
cd /home/joaonote/oncristo.local
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

### 3. Em outro terminal, iniciar ngrok
```bash
ngrok http 8000
```

### 4. Copiar a URL do ngrok
Você verá algo como:
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:8000
```

### 5. Configurar webhook na Whapi Cloud
- URL: `https://abc123.ngrok-free.app/app_igreja/api/whatsapp/webhook/`
- Método: POST
- Headers: Content-Type: application/json

### 6. Testar
- Envie uma mensagem para o número do WhatsApp
- Veja os logs no terminal do Django
- Veja as requisições no dashboard do ngrok

---

## 🔍 Verificar se está funcionando

### Testar endpoint de teste:
```bash
curl https://SUA_URL_NGROK/app_igreja/api/whatsapp/test/
```

### Ver logs do Django:
No terminal onde o servidor está rodando, você verá:
```
[INFO] Webhook recebido - Método: POST
[INFO] Dados recebidos: {...}
```

---

## ⚠️ Importante

1. **Variáveis de ambiente**: Certifique-se de ter no `.env`:
   ```
   WHAPI_KEY=sua_chave_aqui
   CHANNEL_ID=seu_channel_id
   WHATSAPP_BASE_URL=https://gate.whapi.cloud
   ```

2. **URL do ngrok muda**: A URL gratuita do ngrok muda a cada reinicialização. Use ngrok com conta para URL fixa.

3. **Teste local primeiro**: Sempre teste localmente antes de fazer deploy!

---

## 🆘 Problemas Comuns

### ngrok não conecta
- Verifique se o servidor Django está rodando na porta 8000
- Verifique firewall: `sudo ufw allow 8000`

### Webhook não recebe mensagens
- Verifique se a URL está correta na Whapi Cloud
- Verifique os logs do Django
- Teste o endpoint `/test/` primeiro

### Erro 404
- Certifique-se de incluir o `/app_igreja/api/whatsapp/webhook/` completo
- Verifique se as URLs estão configuradas no `urls.py`

