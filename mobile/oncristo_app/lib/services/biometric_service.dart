/// Serviço para autenticação biométrica
import 'package:local_auth/local_auth.dart';

class BiometricService {
  static final LocalAuthentication _auth = LocalAuthentication();

  /// Verificar se biometria está disponível
  static Future<bool> isAvailable() async {
    try {
      final bool canAuthenticate = await _auth.canCheckBiometrics ||
          await _auth.isDeviceSupported();
      return canAuthenticate;
    } catch (e) {
      return false;
    }
  }

  /// Obter tipos de biometria disponíveis
  static Future<List<BiometricType>> getAvailableBiometrics() async {
    try {
      return await _auth.getAvailableBiometrics();
    } catch (e) {
      return [];
    }
  }

  /// Autenticar com biometria
  static Future<Map<String, dynamic>> authenticate({
    String localizedReason = 'Por favor, autentique-se para continuar',
    bool useErrorDialogs = true,
    bool stickyAuth = true,
  }) async {
    try {
      // Verificar se biometria está disponível
      final bool isAvailable = await BiometricService.isAvailable();
      if (!isAvailable) {
        return {
          'success': false,
          'error': 'Biometria não disponível neste dispositivo',
        };
      }

      // Tentar autenticar
      final bool didAuthenticate = await _auth.authenticate(
        localizedReason: localizedReason,
        options: AuthenticationOptions(
          useErrorDialogs: useErrorDialogs,
          stickyAuth: stickyAuth,
          biometricOnly: false, // Permite usar PIN/senha como fallback
        ),
      );

      if (didAuthenticate) {
        // Gerar token biométrico simples (em produção, use algo mais seguro)
        final biometricToken = _generateBiometricToken();
        
        return {
          'success': true,
          'biometric_token': biometricToken,
        };
      } else {
        return {
          'success': false,
          'error': 'Autenticação cancelada ou falhou',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Erro ao autenticar: ${e.toString()}',
      };
    }
  }

  /// Gerar token biométrico simples
  /// Em produção, isso deve ser mais seguro (usar device ID, etc.)
  static String _generateBiometricToken() {
    // Por enquanto, retorna um token simples
    // Em produção, você pode:
    // - Usar device ID
    // - Gerar hash baseado em dados do dispositivo
    // - Usar chave criptográfica armazenada no dispositivo
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    return 'biometric_${timestamp}';
  }

  /// Verificar se biometria está habilitada nas configurações
  static Future<bool> isBiometricEnabled() async {
    try {
      final availableBiometrics = await getAvailableBiometrics();
      return availableBiometrics.isNotEmpty;
    } catch (e) {
      return false;
    }
  }
}
