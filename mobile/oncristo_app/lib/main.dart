import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kDebugMode;
import 'screens/login_screen_new.dart';
import 'screens/home_menu.dart';
import 'screens/register_screen.dart';
import 'screens/forgot_password_screen.dart';
import 'screens/main_tabs_screen.dart';
import 'services/api_service.dart';
import 'services/upload_service.dart';
import 'utils/storage.dart';
import 'utils/logger.dart';
// import 'workers/upload_worker.dart';  // Comentado temporariamente

void main() async {
  // Inicializar bindings PRIMEIRO
  WidgetsFlutterBinding.ensureInitialized();
  
  // Inicializações em background (não bloqueia o início do app)
  AppLogger.init().then((_) {
    return UploadService().initialize();
  }).catchError((e) {
    // Silenciar erros de inicialização para não poluir a tela
    if (kDebugMode) {
      print('⚠️ Erro nas inicializações de background: $e');
    }
  });
  
  // Configurar tratamento de erros global (apenas em debug)
  if (kDebugMode) {
    FlutterError.onError = (FlutterErrorDetails details) {
      // Em debug, apenas logar, não mostrar diálogo
      AppLogger.error(
        'ERRO FLUTTER CAPTURADO',
        error: details.exception,
        stackTrace: details.stack,
        location: 'FlutterError.onError',
      ).catchError((e) {
        print('❌ ERRO FLUTTER: ${details.exception}');
      });
    };
  } else {
    // Em produção, apenas logar silenciosamente
    FlutterError.onError = (FlutterErrorDetails details) {
      AppLogger.error(
        'ERRO FLUTTER CAPTURADO',
        error: details.exception,
        stackTrace: details.stack,
        location: 'FlutterError.onError',
      ).catchError((_) {
        // Ignorar erros de log em produção
      });
    };
  }
  
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'On Cristo',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF8B0000)),
        useMaterial3: true,
      ),
      debugShowCheckedModeBanner: false,
      home: const AuthWrapper(),
      routes: {
        '/login': (context) => const LoginScreenNew(),
        '/home': (context) => const MainTabsScreen(), // Agora usa as abas do On Cristo
        '/home-menu': (context) => const HomeMenu(), // Mantém o menu antigo como opção
        '/register': (context) => const RegisterScreen(),
        '/forgot-password': (context) => const ForgotPasswordScreen(),
        // Todas as outras rotas são carregadas via WebView (Django HTML)
      },
    );
  }
}

/// Widget inicial que verifica autenticação e redireciona
class AuthWrapper extends StatefulWidget {
  const AuthWrapper({super.key});

  @override
  State<AuthWrapper> createState() => _AuthWrapperState();
}

class _AuthWrapperState extends State<AuthWrapper> {
  @override
  void initState() {
    super.initState();
    _checkAuthentication();
  }

  Future<void> _checkAuthentication() async {
    try {
      final isAuthenticated = await ApiService.isAuthenticated();
      final biometricEnabled = await Storage.isBiometricEnabled();

      if (mounted) {
        // Se autenticado e biometria habilitada, força tela de login com biometria
        if (isAuthenticated && biometricEnabled) {
          Navigator.of(context).pushReplacement(
            MaterialPageRoute(
              builder: (_) => const LoginScreenNew(forceBiometric: true),
            ),
          );
        } else if (isAuthenticated) {
          Navigator.of(context).pushReplacementNamed('/home');
        } else {
          Navigator.of(context).pushReplacementNamed('/login');
        }
      }
    } catch (e, stackTrace) {
      // Logar erro silenciosamente (não bloquear se logger falhar)
      AppLogger.error(
        'Erro ao verificar autenticação',
        error: e,
        stackTrace: stackTrace,
        location: 'AuthWrapper._checkAuthentication',
      ).catchError((_) {
        // Ignorar se logger falhar
        if (kDebugMode) {
          print('⚠️ Erro ao verificar autenticação: $e');
        }
      });
      
      // Em caso de erro, sempre redirecionar para login (sem mostrar erro)
      if (mounted) {
        Navigator.of(context).pushReplacementNamed('/login');
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(
        child: CircularProgressIndicator(),
      ),
    );
  }
}
