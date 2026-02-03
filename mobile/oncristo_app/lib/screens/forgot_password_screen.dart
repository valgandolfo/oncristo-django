/// Tela de Recuperação de Senha via WebView
import 'package:flutter/material.dart';
import 'webview_screen.dart';

class ForgotPasswordScreen extends StatelessWidget {
  const ForgotPasswordScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // Redireciona imediatamente para o WebView
    // Usamos o WidgetsBinding para fazer isso após o build inicial
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (context) => const WebViewScreen(
            route: '/accounts/password_reset/?modo=app',
            hideAppBar: false, // Vamos deixar o AppBar do WebView para poder voltar
          ),
        ),
      );
    });

    // Enquanto redireciona, mostra um loading bonito
    return Scaffold(
      backgroundColor: Colors.white,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF8B0000)),
            ),
            const SizedBox(height: 20),
            Text(
              'Carregando recuperação de senha...',
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 16,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
