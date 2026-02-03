# 🔧 Configuração do Servidor no App Flutter

## 📱 Como Configurar o IP/Porta do Servidor

### Opção 1: Configuração Automática (Recomendado)

O app detecta automaticamente se você está usando:
- **IP local** (ex: `192.168.0.13`) → usa HTTP
- **Domínio** (ex: `oncristo.com.br`) → usa HTTPS
- **Ngrok** (ex: `4401b3d3d3e5.ngrok-free.app`) → usa HTTPS

### Opção 2: Configuração Manual no Login

1. Abra o app
2. Na tela de login, **pressione e segure** o ícone da igreja (canto superior)
3. O campo de IP do servidor aparecerá
4. Digite o IP ou domínio desejado:
   - **IP Local:** `192.168.0.13:8000`
   - **Ngrok:** `4401b3d3d3e5.ngrok-free.app` (sem porta, sem http://)
   - **Produção:** `oncristo.com.br` (sem porta, sem https://)

---

## 🔄 Configurações por Ambiente

### Desenvolvimento Local (Rede WiFi)

**Configuração:**
```
IP: 192.168.0.13
Porta: 8000
```

**Como descobrir seu IP:**
```bash
# Linux/Mac
hostname -I | awk '{print $1}'
# ou
ip addr show | grep "inet " | grep -v 127.0.0.1

# Windows
ipconfig
# Procure por "IPv4 Address"
```

### Desenvolvimento com Ngrok

**Configuração:**
```
URL: 4401b3d3d3e5.ngrok-free.app
(Sem http://, sem porta)
```

**Importante:** Quando o ngrok mudar (a cada reinício), atualize no app:
1. Pressione e segure o ícone da igreja no login
2. Digite a nova URL do ngrok
3. Salve

### Produção

**Configuração:**
```
Domínio: oncristo.com.br
(Sem https://, sem porta)
```

---

## 📝 Arquivo de Configuração

O arquivo `lib/config/app_config.dart` define os padrões:

```dart
class AppConfig {
  // IP/Domínio padrão
  static const String defaultServerIp = '192.168.0.13';
  
  // Porta padrão (só usada se for IP)
  static const String defaultPort = '8000';
  
  // Prefixo da API
  static const String apiPrefix = '/app_igreja/api';
}
```

**Para mudar o padrão:**
1. Edite `lib/config/app_config.dart`
2. Altere `defaultServerIp` para seu IP/domínio
3. Recompile o app: `flutter run`

---

## 🔐 APIs de Autenticação

### Login
- **URL:** `/app_igreja/api/auth/login/`
- **Método:** POST
- **Body:**
  ```json
  {
    "email": "usuario@exemplo.com",
    "password": "Senha123"
  }
  ```

### Registro
- **URL:** `/app_igreja/api/auth/register/`
- **Método:** POST
- **Body:**
  ```json
  {
    "email": "usuario@exemplo.com",
    "password": "Senha123",
    "password2": "Senha123"  // Opcional
  }
  ```

### Reset de Senha
- **URL:** `/app_igreja/api/auth/password-reset/`
- **Método:** POST
- **Body:**
  ```json
  {
    "email": "usuario@exemplo.com"
  }
  ```

---

## 🐛 Solução de Problemas

### Erro: "Connection timed out"

**Causa:** IP incorreto ou servidor não está rodando

**Solução:**
1. Verifique se o servidor Django está rodando: `python manage.py runserver 0.0.0.0:8000`
2. Verifique o IP correto: `hostname -I`
3. Certifique-se de que o celular está na mesma rede WiFi
4. Teste no navegador: `http://SEU_IP:8000`

### Erro: "CSRF verification failed"

**Causa:** Ngrok não está no CSRF_TRUSTED_ORIGINS

**Solução:**
1. Adicione o ngrok ao `pro_igreja/settings.py`:
   ```python
   CSRF_TRUSTED_ORIGINS = [
       # ...
       'https://4401b3d3d3e5.ngrok-free.app',
   ]
   ```
2. Reinicie o servidor Django

### Erro: "You have multiple authentication backends"

**Causa:** Backend não especificado no login

**Solução:** ✅ **Já corrigido!** O código agora especifica o backend automaticamente.

### App não conecta ao servidor

**Checklist:**
- [ ] Servidor Django está rodando?
- [ ] IP/domínio está correto?
- [ ] Celular está na mesma rede WiFi (se IP local)?
- [ ] Firewall não está bloqueando a porta 8000?
- [ ] Ngrok está ativo (se usando ngrok)?

---

## 📝 Exemplo de URLs Geradas

### IP Local:
```
http://192.168.0.13:8000/app_igreja/api/auth/login/
```

### Ngrok:
```
https://4401b3d3d3e5.ngrok-free.app/app_igreja/api/auth/login/
```

### Produção:
```
https://oncristo.com.br/app_igreja/api/auth/login/
```

---

## 🔄 Atualizar Configuração no App

O app salva a configuração do servidor localmente. Para mudar:

1. **Via Interface:**
   - Tela de login → Pressione e segure o ícone da igreja
   - Digite novo IP/domínio
   - Faça login (salva automaticamente)

2. **Via Código:**
   - Edite `lib/config/app_config.dart`
   - Recompile: `flutter run`

3. **Limpar Configuração:**
   - Desinstale e reinstale o app
   - Ou limpe os dados do app nas configurações do Android/iOS

---

**Última atualização:** 23 de Janeiro de 2026  
**IP Padrão Atual:** `192.168.0.13`  
**Ngrok Atual:** `4401b3d3d3e5.ngrok-free.app`
