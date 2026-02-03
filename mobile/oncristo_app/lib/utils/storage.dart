/// Utilitário para armazenamento local (SharedPreferences)
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'logger.dart';

class Storage {
  static const String _accessTokenKey = '@OnCristo:access_token';
  static const String _refreshTokenKey = '@OnCristo:refresh_token';
  static const String _userEmailKey = '@OnCristo:user_email';
  static const String _biometricEnabledKey = '@OnCristo:biometric_enabled';
  static const String _profileNameKey = '@OnCristo:profile_name';
  static const String _profileWhatsKey = '@OnCristo:profile_whats';
  static const String _profileEmailKey = '@OnCristo:profile_email';
  static const String _profilePix1Key = '@OnCristo:profile_pix1';
  static const String _profilePix2Key = '@OnCristo:profile_pix2';
  static const String _profilePix3Key = '@OnCristo:profile_pix3';
  static const String _profileFavorecidoKey = '@OnCristo:profile_favorecido';
  static const String _profilePhotoPathKey = '@OnCristo:profile_photo_path';
  static const String _profileAdminKey = '@OnCristo:profile_admin';
  static const String _notesKey = '@OnCristo:notes_local';
  static const String _serverIpKey = '@OnCristo:server_ip';
  static const String _printerColumnsKey = '@OnCristo:printer_columns';

  /// Salvar token de acesso
  static Future<void> saveAccessToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_accessTokenKey, token);
  }

  /// Obter token de acesso
  static Future<String?> getAccessToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_accessTokenKey);
  }

  /// Salvar token de refresh
  static Future<void> saveRefreshToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_refreshTokenKey, token);
  }

  /// Obter token de refresh
  static Future<String?> getRefreshToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_refreshTokenKey);
  }

  /// Salvar email do usuário
  static Future<void> saveUserEmail(String email) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final saved = await prefs.setString(_userEmailKey, email);
      if (saved) {
        print('✅ Storage: Email salvo com sucesso: $email');
        // Verificar se foi salvo corretamente
        final verify = await prefs.getString(_userEmailKey);
        print('✅ Storage: Verificação - email recuperado: $verify');
      } else {
        print('❌ Storage: Falha ao salvar email');
      }
    } catch (e) {
      print('❌ Storage: Erro ao salvar email: $e');
    }
  }

  /// Obter email do usuário
  static Future<String?> getUserEmail() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final email = prefs.getString(_userEmailKey);
      if (email != null) {
        print('✅ Storage: Email recuperado: $email');
      } else {
        print('⚠️ Storage: Nenhum email encontrado');
      }
      return email;
    } catch (e) {
      print('❌ Storage: Erro ao recuperar email: $e');
      return null;
    }
  }

  /// Verificar se biometria está habilitada
  static Future<bool> isBiometricEnabled() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(_biometricEnabledKey) ?? false;
  }

  /// Habilitar/desabilitar biometria
  static Future<void> setBiometricEnabled(bool enabled) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_biometricEnabledKey, enabled);
  }

  /// === Perfil local (somente dispositivo) ===
  static Future<void> saveProfileLocal({
    String? name,
    String? whatsapp,
    String? email,
    String? pix1,
    String? pix2,
    String? pix3,
    String? favorecido,
    String? photoPath,
    bool? isAdmin,
  }) async {
    try {
      print('💾 Storage.saveProfileLocal chamado');
      print('   name: $name');
      print('   whatsapp: $whatsapp');
      print('   email: $email');
      print('   pix1: $pix1');
      print('   pix2: $pix2');
      print('   pix3: $pix3');
      print('   favorecido: $favorecido');
      print('   isAdmin: $isAdmin');
      print('   photoPath: ${photoPath != null && photoPath.isNotEmpty ? '${photoPath.length > 50 ? photoPath.substring(0, 50) + '...' : photoPath}' : '(vazio)'}');
      
      final prefs = await SharedPreferences.getInstance();
      
      // Sempre salvar todos os campos (mesmo que vazios, para limpar valores antigos)
      if (isAdmin != null) {
        await prefs.setBool(_profileAdminKey, isAdmin);
        print('✅ Admin status salvo: $isAdmin');
      }
      if (name != null) {
        if (name.isEmpty) {
          await prefs.remove(_profileNameKey);
          print('🗑️ Nome removido (campo vazio)');
        } else {
          await prefs.setString(_profileNameKey, name);
          print('✅ Nome salvo: $name');
        }
      }
      
      if (whatsapp != null) {
        if (whatsapp.isEmpty) {
          await prefs.remove(_profileWhatsKey);
          print('🗑️ WhatsApp removido (campo vazio)');
        } else {
          await prefs.setString(_profileWhatsKey, whatsapp);
          print('✅ WhatsApp salvo: $whatsapp');
        }
      }
      
      if (email != null) {
        if (email.isEmpty) {
          await prefs.remove(_profileEmailKey);
          print('🗑️ Email removido (campo vazio)');
        } else {
          await prefs.setString(_profileEmailKey, email);
          print('✅ Email salvo: $email');
        }
      }
      
      if (pix1 != null) {
        if (pix1.isEmpty) {
          await prefs.remove(_profilePix1Key);
          print('🗑️ Pix1 removido (campo vazio)');
        } else {
          await prefs.setString(_profilePix1Key, pix1);
          print('✅ Pix1 salvo: $pix1');
        }
      }
      
      if (pix2 != null) {
        if (pix2.isEmpty) {
          await prefs.remove(_profilePix2Key);
          print('🗑️ Pix2 removido (campo vazio)');
        } else {
          await prefs.setString(_profilePix2Key, pix2);
          print('✅ Pix2 salvo: $pix2');
        }
      }
      
      if (pix3 != null) {
        if (pix3.isEmpty) {
          await prefs.remove(_profilePix3Key);
          print('🗑️ Pix3 removido (campo vazio)');
        } else {
          await prefs.setString(_profilePix3Key, pix3);
          print('✅ Pix3 salvo: $pix3');
        }
      }
      
      if (favorecido != null) {
        if (favorecido.isEmpty) {
          await prefs.remove(_profileFavorecidoKey);
          print('🗑️ Favorecido removido (campo vazio)');
        } else {
          await prefs.setString(_profileFavorecidoKey, favorecido);
          print('✅ Favorecido salvo: $favorecido');
        }
      }
      
      if (photoPath != null) {
        if (photoPath.isEmpty || !photoPath.startsWith('data:image/')) {
          await prefs.remove(_profilePhotoPathKey);
          print('🗑️ PhotoPath removido (campo vazio ou inválido)');
        } else {
          await prefs.setString(_profilePhotoPathKey, photoPath);
          print('✅ PhotoPath salvo (tamanho: ${photoPath.length})');
        }
      }
      
      print('✅ Storage.saveProfileLocal concluído com sucesso');
    } catch (e, stackTrace) {
      print('❌ Erro em Storage.saveProfileLocal: $e');
      print('❌ StackTrace: $stackTrace');
      rethrow;
    }
  }

  static Future<Map<String, dynamic>> getProfileLocal() async {
    final prefs = await SharedPreferences.getInstance();
    return {
      'name': prefs.getString(_profileNameKey),
      'whatsapp': prefs.getString(_profileWhatsKey),
      'email': prefs.getString(_profileEmailKey),
      'pix1': prefs.getString(_profilePix1Key),
      'pix2': prefs.getString(_profilePix2Key),
      'pix3': prefs.getString(_profilePix3Key),
      'favorecido': prefs.getString(_profileFavorecidoKey),
      'photoPath': prefs.getString(_profilePhotoPathKey),
      'isAdmin': prefs.getBool(_profileAdminKey) ?? false,
    };
  }

  /// === Anotações locais (somente dispositivo) ===
  /// Estrutura: lista de maps {id, titulo, tipo, texto, itens: [{texto, checked}], data}
  static Future<void> saveNotesLocal(List<Map<String, dynamic>> notes) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_notesKey, jsonEncode(notes));
  }

  static Future<List<Map<String, dynamic>>> getNotesLocal() async {
    final prefs = await SharedPreferences.getInstance();
    final data = prefs.getString(_notesKey);
    if (data == null) return [];
    try {
      final decoded = jsonDecode(data);
      if (decoded is List) {
        return decoded.cast<Map<String, dynamic>>();
      }
    } catch (_) {}
    return [];
  }

  /// Limpar todos os dados (logout)
  static Future<void> clearAll() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_accessTokenKey);
      await prefs.remove(_refreshTokenKey);
      // NÃO remover email e biometria no logout (para manter preferências)
      // await prefs.remove(_userEmailKey);
      // await prefs.remove(_biometricEnabledKey);
      print('✅ Storage: Tokens removidos (email e biometria mantidos)');
    } catch (e) {
      print('❌ Storage: Erro ao limpar dados: $e');
    }
  }
  
  /// Limpar tudo incluindo email e biometria (reset completo)
  static Future<void> clearAllIncludingPreferences() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_accessTokenKey);
      await prefs.remove(_refreshTokenKey);
      await prefs.remove(_userEmailKey);
      await prefs.remove(_biometricEnabledKey);
      print('✅ Storage: Todos os dados removidos (reset completo)');
    } catch (e) {
      print('❌ Storage: Erro ao limpar todos os dados: $e');
    }
  }

  /// Verificar se usuário está autenticado
  static Future<bool> isAuthenticated() async {
    try {
      final token = await getAccessToken();
      return token != null && token.isNotEmpty;
    } catch (e, stackTrace) {
      await AppLogger.error(
        'Erro ao verificar autenticação no storage',
        error: e,
        stackTrace: stackTrace,
        location: 'Storage.isAuthenticated',
      );
      return false;
    }
  }

  /// === Configuração do Servidor ===
  /// Salvar IP do servidor
  static Future<void> saveServerIp(String ip) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_serverIpKey, ip);
  }

  /// Obter IP do servidor (retorna null se não configurado)
  static Future<String?> getServerIp() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_serverIpKey);
  }

  /// === Configurações da Impressora ===
  /// Salvar número de colunas da impressora
  static Future<void> savePrinterColumns(int columns) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt(_printerColumnsKey, columns);
  }

  /// Obter número de colunas da impressora (retorna 40 se não configurado)
  static Future<int> getPrinterColumns() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getInt(_printerColumnsKey) ?? 40;
  }
}
