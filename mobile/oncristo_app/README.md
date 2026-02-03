# 📱 On Cristo App - Flutter

Aplicativo oficial do Projeto On Cristo, integrando tecnologia e fé.

Aplicativo mobile para gerenciamento de mídias desenvolvido em Flutter.

## 🚀 Setup Inicial

### 1. Instalar Flutter

```bash
# Verificar se Flutter está instalado
flutter --version

# Se não estiver, seguir instruções em:
# https://docs.flutter.dev/get-started/install/linux
```

### 2. Instalar Dependências

```bash
cd /home/joaonote/allmedias/mobile/allmedias_app
flutter pub get
```

### 3. Configurar IP da API

Editar `lib/services/api_service.dart` e alterar:

```dart
const String API_BASE_URL = 'http://SEU_IP:8000/api';
```

Para descobrir seu IP:
```bash
hostname -I | awk '{print $1}'
```

### 4. Executar App

```bash
# Verificar dispositivos conectados
flutter devices

# Executar no dispositivo/emulador
flutter run
```

## 📋 Estrutura do Projeto

```
lib/
├── main.dart                 # Ponto de entrada
├── screens/
│   ├── login_screen.dart    # Tela de login com biometria
│   └── home_screen.dart     # Tela home (placeholder)
├── services/
│   ├── api_service.dart     # Comunicação com API Django
│   └── biometric_service.dart # Autenticação biométrica
└── utils/
    └── storage.dart         # Armazenamento local
```

## 🔐 Funcionalidades Implementadas

- ✅ Login com email e senha
- ✅ Login com biometria (Touch ID / Face ID / Fingerprint)
- ✅ Armazenamento de tokens JWT
- ✅ Verificação automática de autenticação
- ✅ Logout

## 📱 Permissões Necessárias

### Android
- Internet
- Biometria
- Fingerprint

### iOS
- Biometria (configurado automaticamente)

## 🔗 API Endpoints

- `POST /api/auth/login/` - Login (email/senha ou biometria)
- `POST /api/auth/refresh/` - Renovar token

## 📝 Próximos Passos

1. Implementar tela Home completa
2. Listar mídias
3. Upload de mídias
4. Favoritos
5. Conversão de mídias
