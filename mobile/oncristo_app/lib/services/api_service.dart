/// Serviço de API para comunicação com o backend Django
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart' show kIsWeb;
import '../utils/storage.dart';
import '../utils/logger.dart';
import '../config/app_config.dart';

// URL base da API (ajustada para web e mobile)
// No navegador, usar localhost; no mobile, usar IP da rede local por padrão
Future<String> getApiBaseUrl() async {
  if (kIsWeb) {
    return 'http://localhost:8000${AppConfig.apiPrefix}';
  } else {
    // Tenta obter IP/domínio do storage, se não houver usa o IP local padrão
    final savedIp = await Storage.getServerIp();
    String server = savedIp ?? AppConfig.defaultServerIp;
    
    // Limpar espaços e protocolos acidentais
    server = server.trim().replaceAll('http://', '').replaceAll('https://', '');
    
    // Remover porta se estiver no final (vamos adicionar depois se necessário)
    if (server.contains(':')) {
      final parts = server.split(':');
      server = parts[0];
    }
    
    // Se o servidor for um IP (mesmo com porta), usar HTTP. Se for domínio, usar HTTPS.
    final isIp = RegExp(r'^(\d{1,3}\.){3}\d{1,3}').hasMatch(server);
    final isNgrok = server.contains('ngrok');
    final isLocalhost = server.contains('localhost') || server == '127.0.0.1';
    
    String baseUrl;
    if (isIp || isLocalhost) {
      // IP local ou localhost: usar HTTP com porta
      baseUrl = 'http://$server:${AppConfig.defaultPort}${AppConfig.apiPrefix}';
    } else if (isNgrok) {
      // Ngrok: usar HTTPS sem porta
      baseUrl = 'https://$server${AppConfig.apiPrefix}';
    } else {
      // Domínio de produção: usar HTTPS sem porta
      baseUrl = 'https://$server${AppConfig.apiPrefix}';
    }
    return baseUrl;
  }
}

// Mantém compatibilidade com código existente (usa IP local padrão)
String get API_BASE_URL {
  if (kIsWeb) {
    return 'http://localhost:8000/api';
  } else {
    return 'http://${AppConfig.defaultServerIp}:${AppConfig.defaultPort}/api';
  }
}

class ApiService {
  /// Fazer login com email e senha
  static Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    try {
      final baseUrl = await getApiBaseUrl();
      final loginUrl = '$baseUrl/auth/login/';
      
      final response = await http.post(
        Uri.parse(loginUrl),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'email': email, // Sistema usa APENAS email (não username)
          'password': password,
        }),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final accessToken = data['access'] as String;
        final refreshToken = data['refresh'] as String;
        final isAdmin = data['isAdmin'] as bool? ?? false;

        // Salvar tokens, email e status admin (aguardar conclusão)
        await Storage.saveAccessToken(accessToken);
        await Storage.saveRefreshToken(refreshToken);
        await Storage.saveUserEmail(email);
        
        // Também salvar status admin no perfil local
        final currentProfile = await Storage.getProfileLocal();
        await Storage.saveProfileLocal(
          name: currentProfile['name'],
          whatsapp: currentProfile['whatsapp'],
          email: email,
          photoPath: currentProfile['photoPath'],
          isAdmin: isAdmin,
        );
        
        // Verificar se tokens foram salvos corretamente
        final savedToken = await Storage.getAccessToken();
        final savedEmail = await Storage.getUserEmail();
        
        if (savedToken == null || savedToken.isEmpty) {
          return {
            'success': false,
            'error': 'Erro ao salvar tokens. Tente novamente.',
          };
        }
        
        if (savedEmail == null || savedEmail.isEmpty) {
          await Storage.saveUserEmail(email);
        }

        return {
          'success': true,
          'access': accessToken,
          'refresh': refreshToken,
        };
      } else {
        try {
          final error = jsonDecode(response.body);
          String errorMessage = error['detail'] ?? error['error'] ?? 'Erro ao fazer login';
          
          // Se for erro de conexão, dar mensagem mais clara
          if (response.statusCode == 0 || response.statusCode >= 500) {
            errorMessage = 'Servidor não está respondendo. Verifique se está rodando e acessível.';
          }
          
          return {
            'success': false,
            'error': errorMessage,
          };
        } catch (parseError) {
          return {
            'success': false,
            'error': 'Erro ao processar resposta do servidor (Status: ${response.statusCode})',
          };
        }
      }
    } catch (e, stackTrace) {
      final baseUrl = await getApiBaseUrl();
      String errorMsg = 'Erro de conexão: ${e.toString()}';
      
      // Melhorar mensagens de erro comuns
      if (e.toString().contains('Failed host lookup') || 
          e.toString().contains('Connection refused') ||
          e.toString().contains('Network is unreachable')) {
        errorMsg = 'Não foi possível conectar ao servidor. Verifique:\n'
                   '1. Se o servidor está rodando\n'
                   '2. Se o IP/domínio está correto\n'
                   '3. Se o celular está na mesma rede WiFi\n'
                   '4. Se o firewall não está bloqueando\n\n'
                   'URL tentada: $baseUrl/auth/login/';
      }
      
      await AppLogger.error(
        'Falha no login (Senha)',
        error: e,
        stackTrace: stackTrace,
        location: 'ApiService.login',
      );

      return {
        'success': false,
        'error': errorMsg,
      };
    }
  }

  /// Fazer login com biometria (token biométrico)
  static Future<Map<String, dynamic>> loginWithBiometric({
    required String biometricToken,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('${await getApiBaseUrl()}/auth/login/'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'biometric_token': biometricToken,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final accessToken = data['access'];
        final refreshToken = data['refresh'];

        // Salvar tokens
        await Storage.saveAccessToken(accessToken);
        await Storage.saveRefreshToken(refreshToken);

        return {
          'success': true,
          'access': accessToken,
          'refresh': refreshToken,
        };
      } else {
        final error = jsonDecode(response.body);
        return {
          'success': false,
          'error': error['detail'] ?? 'Erro ao fazer login com biometria',
        };
      }
    } catch (e, stackTrace) {
      final baseUrl = await getApiBaseUrl();
      final errorMsg = 'Erro de conexão: ${e.toString()}';
      
      await AppLogger.error(
        'Falha no login (Biometria)',
        error: e,
        stackTrace: stackTrace,
        location: 'ApiService.loginWithBiometric',
      );
      await AppLogger.warning('URL Base: $baseUrl');

      return {
        'success': false,
        'error': errorMsg,
      };
    }
  }

  /// Renovar token de acesso
  static Future<Map<String, dynamic>> refreshToken() async {
    try {
      final refreshToken = await Storage.getRefreshToken();
      if (refreshToken == null) {
        return {
          'success': false,
          'error': 'Token de refresh não encontrado',
        };
      }

      final response = await http.post(
        Uri.parse('${await getApiBaseUrl()}/auth/refresh/'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'refresh': refreshToken,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final accessToken = data['access'];

        // Salvar novo token de acesso
        await Storage.saveAccessToken(accessToken);

        return {
          'success': true,
          'access': accessToken,
        };
      } else {
        // Se falhar, fazer logout
        await Storage.clearAll();
        return {
          'success': false,
          'error': 'Token expirado. Faça login novamente.',
        };
      }
    } catch (e, stackTrace) {
      final baseUrl = await getApiBaseUrl();
      final errorMsg = 'Erro de conexão: ${e.toString()}';
      
      await AppLogger.error(
        'Falha no refresh token',
        error: e,
        stackTrace: stackTrace,
        location: 'ApiService.refreshToken',
      );
      await AppLogger.warning('URL Base: $baseUrl');

      return {
        'success': false,
        'error': errorMsg,
      };
    }
  }

  /// Fazer logout
  static Future<void> logout() async {
    await Storage.clearAll();
  }

  /// Obter token de acesso para usar em requisições
  static Future<String?> getAccessToken() async {
    return await Storage.getAccessToken();
  }

  /// Verificar se está autenticado
  static Future<bool> isAuthenticated() async {
    try {
      return await Storage.isAuthenticated();
    } catch (e, stackTrace) {
      await AppLogger.error(
        'Erro ao verificar autenticação',
        error: e,
        stackTrace: stackTrace,
        location: 'ApiService.isAuthenticated',
      );
      // Em caso de erro, retornar false (não autenticado)
      return false;
    }
  }

  /// Registrar novo usuário
  static Future<Map<String, dynamic>> register({
    required String email,
    required String password,
    required String password2,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('${await getApiBaseUrl()}/auth/register/'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'email': email,
          'password': password,
          'password2': password2,
        }),
      );

      if (response.statusCode == 201) {
        final data = jsonDecode(response.body);
        return {
          'success': true,
          'message': data['message'] ?? 'Conta criada com sucesso!',
        };
      } else {
        final error = jsonDecode(response.body);
        // Extrair primeira mensagem de erro
        String errorMessage = 'Erro ao criar conta';
        if (error is Map) {
          final firstError = error.values.first;
          if (firstError is List && firstError.isNotEmpty) {
            errorMessage = firstError.first;
          } else if (firstError is String) {
            errorMessage = firstError;
          }
        }
        return {
          'success': false,
          'error': errorMessage,
        };
      }
    } catch (e, stackTrace) {
      final baseUrl = await getApiBaseUrl();
      final errorMsg = 'Erro de conexão: ${e.toString()}';
      
      await AppLogger.error(
        'Falha no registro',
        error: e,
        stackTrace: stackTrace,
        location: 'ApiService.register',
      );
      await AppLogger.warning('URL Base: $baseUrl');

      return {
        'success': false,
        'error': errorMsg,
      };
    }
  }

  /// Solicitar reset de senha
  static Future<Map<String, dynamic>> requestPasswordReset({
    required String email,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('${await getApiBaseUrl()}/auth/password-reset/'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'email': email,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return {
          'success': true,
          'message': data['message'] ?? 'E-mail enviado com sucesso!',
        };
      } else {
        final errorData = jsonDecode(response.body);
        return {
          'success': false,
          'error': errorData['error'] ?? errorData['detail'] ?? 'Erro ao enviar e-mail',
        };
      }
    } catch (e, stackTrace) {
      final baseUrl = await getApiBaseUrl();
      final errorMsg = 'Erro de conexão: ${e.toString()}';
      
      await AppLogger.error(
        'Falha no reset de senha',
        error: e,
        stackTrace: stackTrace,
        location: 'ApiService.requestPasswordReset',
      );
      await AppLogger.warning('URL Base: $baseUrl');

      return {
        'success': false,
        'error': errorMsg,
      };
    }
  }

  /// Salvar email do usuário (helper)
  static Future<void> saveUserEmail(String email) async {
    await Storage.saveUserEmail(email);
  }

  /// Testar conexão com o servidor
  static Future<Map<String, dynamic>> testConnection() async {
    try {
      final baseUrl = await getApiBaseUrl();
      
      // Tentar fazer uma requisição simples (GET na raiz)
      final testUrl = baseUrl.replaceAll('/app_igreja/api', '');
      
      final response = await http.get(
        Uri.parse(testUrl),
      ).timeout(const Duration(seconds: 5));
      
      // Se retornar qualquer status (mesmo 404), significa que o servidor está acessível
      return {
        'success': true,
        'statusCode': response.statusCode,
        'url': testUrl,
        'message': 'Conexão OK! Servidor está acessível.',
      };
    } catch (e) {
      final baseUrl = await getApiBaseUrl();
      
      String errorMsg = e.toString();
      String suggestion = '';
      
      if (errorMsg.contains('Failed host lookup') || errorMsg.contains('getaddrinfo failed')) {
        suggestion = '\n\nSugestão: Verifique se o IP/domínio está correto e se o servidor está rodando.';
      } else if (errorMsg.contains('Connection refused') || errorMsg.contains('Connection timed out')) {
        suggestion = '\n\nSugestão: Verifique se o servidor está rodando com: python manage.py runserver 0.0.0.0:8000';
      } else if (errorMsg.contains('Network is unreachable')) {
        suggestion = '\n\nSugestão: Certifique-se de que o celular está na mesma rede WiFi.';
      }
      
      return {
        'success': false,
        'error': errorMsg,
        'url': baseUrl,
        'message': 'Não foi possível conectar ao servidor$suggestion',
      };
    }
  }
}
