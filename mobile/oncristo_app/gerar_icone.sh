#!/bin/bash
# Script para copiar imagem de static para assets e gerar ícones

echo "🖼️  Copiando imagem de static para assets..."

# Copiar imagem da pasta static para assets
cp ../../static/img/oncristo2.png assets/allmedias_icon.png

echo "✅ Imagem copiada!"

echo "📦 Gerando ícones nativos..."
flutter pub get
flutter pub run flutter_launcher_icons:main

echo "✅ Ícones gerados!"
echo ""
echo "📱 Agora compile o app novamente para ver o novo ícone:"
echo "   flutter run"
echo "   ou"
echo "   flutter build apk"
