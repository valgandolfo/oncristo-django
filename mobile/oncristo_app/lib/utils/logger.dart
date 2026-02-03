/// Sistema de logging em arquivo
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:intl/intl.dart';

class AppLogger {
  static File? _logFile;
  static const int _maxLogSize = 1024 * 1024; // 1MB
  static const int _maxLogFiles = 5;

  /// Inicializar o logger (silencioso - não mostra erros)
  static Future<void> init() async {
    try {
      final directory = await getApplicationDocumentsDirectory();
      final logDir = Directory('${directory.path}/logs');
      if (!await logDir.exists()) {
        await logDir.create(recursive: true);
      }
      _logFile = File('${logDir.path}/app_errors.log');
      
      // Rotacionar logs se necessário (com tratamento de erro silencioso)
      try {
        await _rotateLogs(logDir);
      } catch (e) {
        // Silenciar erro de rotação
      }
      
      // Escrever cabeçalho (com tratamento de erro silencioso)
      try {
        await _writeToFile('═══════════════════════════════════════');
        await _writeToFile('🚀 App iniciado em ${DateFormat('yyyy-MM-dd HH:mm:ss').format(DateTime.now())}');
        await _writeToFile('═══════════════════════════════════════');
      } catch (e) {
        // Silenciar erro de escrita
      }
    } catch (e) {
      // Se falhar completamente, apenas tenta criar arquivo básico (silencioso)
      try {
        final directory = await getApplicationDocumentsDirectory();
        _logFile = File('${directory.path}/app_errors.log');
      } catch (_) {
        // Se tudo falhar, continua sem logger (silencioso)
      }
    }
  }

  /// Rotacionar logs antigos
  static Future<void> _rotateLogs(Directory logDir) async {
    try {
      // Verificar se o diretório existe e tem permissão
      if (!await logDir.exists()) {
        return;
      }

      final logFiles = logDir
          .listSync()
          .whereType<File>()
          .where((f) => f.path.endsWith('.log'))
          .toList();
      
      if (logFiles.isEmpty) {
        return;
      }

      logFiles.sort((a, b) => b.lastModifiedSync().compareTo(a.lastModifiedSync()));

      // Manter apenas os últimos N arquivos
      if (logFiles.length >= _maxLogFiles) {
        for (var i = _maxLogFiles - 1; i < logFiles.length; i++) {
          try {
            await logFiles[i].delete();
          } catch (e) {
            // Ignorar erros ao deletar arquivos antigos
            print('⚠️ Erro ao deletar log antigo: $e');
          }
        }
      }

      // Se o arquivo atual for muito grande, rotacionar
      if (_logFile != null && await _logFile!.exists()) {
        try {
          final size = await _logFile!.length();
          if (size > _maxLogSize) {
            final timestamp = DateFormat('yyyyMMdd_HHmmss').format(DateTime.now());
            final oldFile = File('${logDir.path}/app_errors_$timestamp.log');
            await _logFile!.copy(oldFile.path);
            await _logFile!.delete();
            _logFile = File('${logDir.path}/app_errors.log');
          }
        } catch (e) {
          // Se falhar a rotação, continua mesmo assim
          print('⚠️ Erro ao rotacionar arquivo de log: $e');
        }
      }
    } catch (e) {
      // Se falhar completamente, apenas loga e continua
      print('⚠️ Erro ao rotacionar logs: $e');
    }
  }

  /// Escrever no arquivo de log
  static Future<void> _writeToFile(String message) async {
    // Sempre imprimir no console primeiro
    print(message);
    
    // Tentar escrever no arquivo (não bloquear se falhar)
    if (_logFile == null) {
      // Se o arquivo não foi inicializado, tentar inicializar agora
      try {
        final directory = await getApplicationDocumentsDirectory();
        final logDir = Directory('${directory.path}/logs');
        if (!await logDir.exists()) {
          await logDir.create(recursive: true);
        }
        _logFile = File('${logDir.path}/app_errors.log');
      } catch (e) {
        print('⚠️ Erro ao criar arquivo de log: $e');
        return;
      }
    }
    
    try {
      final timestamp = DateFormat('yyyy-MM-dd HH:mm:ss').format(DateTime.now());
      await _logFile!.writeAsString(
        '[$timestamp] $message\n',
        mode: FileMode.append,
      );
    } catch (e) {
      // Se falhar, apenas loga no console
      print('⚠️ Erro ao escrever no arquivo de log: $e');
      print('   Tentando recriar arquivo...');
      // Tentar recriar o arquivo
      try {
        final directory = await getApplicationDocumentsDirectory();
        final logDir = Directory('${directory.path}/logs');
        if (!await logDir.exists()) {
          await logDir.create(recursive: true);
        }
        _logFile = File('${logDir.path}/app_errors.log');
        final timestamp = DateFormat('yyyy-MM-dd HH:mm:ss').format(DateTime.now());
        await _logFile!.writeAsString(
          '[$timestamp] $message\n',
          mode: FileMode.append,
        );
      } catch (e2) {
        print('❌ Erro crítico ao recriar arquivo de log: $e2');
      }
    }
  }

  /// Log de erro
  static Future<void> error(String message, {Object? error, StackTrace? stackTrace, String? location}) async {
    try {
      final buffer = StringBuffer();
      buffer.writeln('═══════════════════════════════════════');
      buffer.writeln('❌ ERRO${location != null ? ' EM $location' : ''}');
      buffer.writeln('═══════════════════════════════════════');
      buffer.writeln('Mensagem: $message');
      if (error != null) {
        buffer.writeln('Erro: $error');
        buffer.writeln('Tipo: ${error.runtimeType}');
      }
      if (stackTrace != null) {
        buffer.writeln('Stack: $stackTrace');
      }
      buffer.writeln('═══════════════════════════════════════');
      await _writeToFile(buffer.toString());
    } catch (e) {
      // Se falhar ao logar, pelo menos imprime no console
      print('❌ ERRO${location != null ? ' EM $location' : ''}: $message');
      if (error != null) print('   Erro: $error');
      if (stackTrace != null) print('   Stack: $stackTrace');
      print('⚠️ Erro ao escrever no arquivo de log: $e');
    }
  }

  /// Log de informação
  static Future<void> info(String message) async {
    await _writeToFile('ℹ️ INFO: $message');
  }

  /// Log de aviso
  static Future<void> warning(String message) async {
    await _writeToFile('⚠️ AVISO: $message');
  }

  /// Obter caminho do arquivo de log
  static Future<String?> getLogFilePath() async {
    try {
      if (_logFile != null) {
        return _logFile!.path;
      }
      final directory = await getApplicationDocumentsDirectory();
      return '${directory.path}/logs/app_errors.log';
    } catch (e) {
      return null;
    }
  }

  /// Ler logs do arquivo
  static Future<String> readLogs() async {
    try {
      if (_logFile != null && await _logFile!.exists()) {
        return await _logFile!.readAsString();
      }
      // Tentar recriar o caminho
      final directory = await getApplicationDocumentsDirectory();
      final logFile = File('${directory.path}/logs/app_errors.log');
      if (await logFile.exists()) {
        return await logFile.readAsString();
      }
      return 'Nenhum log encontrado.';
    } catch (e) {
      return 'Erro ao ler logs: $e';
    }
  }

  /// Limpar logs - zera completamente o arquivo
  static Future<bool> clearLogs() async {
    try {
      // Deletar arquivo atual
      if (_logFile != null && await _logFile!.exists()) {
        await _logFile!.delete();
      }
      
      // Limpar arquivos de log rotacionados também
      try {
        final directory = await getApplicationDocumentsDirectory();
        final logDir = Directory('${directory.path}/logs');
        if (await logDir.exists()) {
          final logFiles = logDir
              .listSync()
              .whereType<File>()
              .where((f) => f.path.endsWith('.log'))
              .toList();
          
          for (var file in logFiles) {
            try {
              await file.delete();
            } catch (e) {
              // Ignorar erros ao deletar
            }
          }
        }
      } catch (e) {
        // Ignorar erros ao limpar arquivos antigos
      }
      
      // Recriar arquivo vazio com cabeçalho
      final directory = await getApplicationDocumentsDirectory();
      final logDir = Directory('${directory.path}/logs');
      if (!await logDir.exists()) {
        await logDir.create(recursive: true);
      }
      _logFile = File('${logDir.path}/app_errors.log');
      
      // Escrever apenas cabeçalho
      await _writeToFile('═══════════════════════════════════════');
      await _writeToFile('🚀 Logs limpos em ${DateFormat('yyyy-MM-dd HH:mm:ss').format(DateTime.now())}');
      await _writeToFile('═══════════════════════════════════════');
      
      return true;
    } catch (e) {
      print('❌ Erro ao limpar logs: $e');
      return false;
    }
  }
}
