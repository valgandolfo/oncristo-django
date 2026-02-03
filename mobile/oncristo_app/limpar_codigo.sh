#!/bin/bash
# Script para limpar código Flutter - Remover telas nativas complexas

echo "🧹 Limpando código Flutter - Removendo telas nativas complexas..."

cd "$(dirname "$0")"

# Remover telas que serão substituídas por Django HTML
echo "❌ Removendo telas nativas..."
rm -f lib/screens/home_screen.dart
rm -f lib/screens/media_lista_screen.dart
rm -f lib/screens/media_detalhes_screen.dart
rm -f lib/screens/media_inclusao_screen.dart
rm -f lib/screens/conversor_media_screen.dart
rm -f lib/screens/anota_ai_screen.dart
rm -f lib/screens/anota_ai_detail_screen.dart
rm -f lib/screens/profile_edit_screen.dart

# Remover service de mídias (não precisa mais, Django faz tudo)
echo "❌ Removendo services desnecessários..."
rm -f lib/services/media_api_service.dart

# Remover telas de login antigas (manter apenas login_screen_new.dart)
echo "❌ Removendo telas de login antigas..."
rm -f lib/screens/login_screen.dart  # Manter apenas login_screen_new.dart

echo "✅ Limpeza concluída!"
echo ""
echo "📋 Arquivos mantidos:"
echo "  ✅ lib/screens/login_screen_new.dart"
echo "  ✅ lib/screens/biometric_screen.dart"
echo "  ✅ lib/screens/webview_screen.dart"
echo "  ✅ lib/screens/home_screen_simple.dart (NOVO)"
echo "  ✅ lib/screens/register_screen.dart"
echo "  ✅ lib/screens/forgot_password_screen.dart"
echo "  ✅ lib/services/api_service.dart"
echo "  ✅ lib/services/biometric_service.dart"
echo ""
echo "🚀 Próximo passo: flutter pub get"
