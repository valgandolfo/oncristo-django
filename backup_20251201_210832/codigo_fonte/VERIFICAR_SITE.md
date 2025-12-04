# 🔍 Verificar Site OnCristo

## ⚠️ IMPORTANTE: Execute no servidor Digital Ocean!

Você precisa estar **conectado via SSH** ao servidor para executar estes comandos.

---

## 📋 PASSO 1: Conectar ao servidor

```bash
ssh root@137.184.116.197
```

---

## 📋 PASSO 2: Testar Django diretamente

```bash
cd /home/oncristo
curl http://127.0.0.1:8000
```

**Resultado esperado:** HTML do Django (não erro 400)

---

## 📋 PASSO 3: Testar via Nginx

```bash
curl http://localhost
```

**Resultado esperado:** HTML do Django

---

## 📋 PASSO 4: Verificar status dos serviços

```bash
sudo systemctl status gunicorn_oncristo
sudo systemctl status nginx
```

---

## 🌐 TESTAR NO NAVEGADOR (do seu computador):

Acesse:
- **http://oncristo.com.br**
- **http://www.oncristo.com.br**
- **http://137.184.116.197**

---

## ❓ O que você está vendo?

1. **Erro 400?** → Problema com ALLOWED_HOSTS
2. **Erro 502?** → Gunicorn não está rodando
3. **Erro 404?** → Nginx não está configurado corretamente
4. **Site funcionando?** → ✅ Sucesso!

**Me diga o que aparece quando você acessa o site no navegador!**

