import 'dart:io';
import 'package:background_downloader/background_downloader.dart';
import 'package:path/path.dart' as p;
import 'package:uuid/uuid.dart';
import 'api_service.dart';
import '../utils/logger.dart';

/// Serviço responsável por gerenciar uploads em background (estilo Google Fotos)
class UploadService {
  static final UploadService _instance = UploadService._internal();
  factory UploadService() => _instance;
  UploadService._internal();

  bool _isInitialized = false;

  /// Inicializa o serviço de upload
  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      // Configurar o downloader/uploader
      FileDownloader().configureNotification(
        running: const TaskNotification('Fazendo Upload', 'Enviando sua mídia... {progress}'),
        complete: const TaskNotification('Upload Concluído', 'Sua mídia já está segura na nuvem!'),
        error: const TaskNotification('Erro no Upload', 'Ocorreu um problema ao enviar sua mídia.'),
        paused: const TaskNotification('Upload Pausado', 'O upload continuará quando houver conexão.'),
        progressBar: true,
      );

      // Escutar atualizações de status (com tratamento de erro)
      FileDownloader().updates.listen(
        (update) {
          try {
            if (update is TaskStatusUpdate) {
              _handleStatusUpdate(update);
            } else if (update is TaskProgressUpdate) {
              // Aqui poderíamos atualizar uma barra de progresso na UI
              print('Progresso do Upload: ${(update.progress * 100).toStringAsFixed(1)}%');
            }
          } catch (e) {
            // Ignorar erros no handler para não quebrar o app
            print('⚠️ Erro ao processar update do upload: $e');
          }
        },
        onError: (error) {
          // Ignorar erros no stream
          print('⚠️ Erro no stream de uploads: $error');
        },
      );

      _isInitialized = true;
      print('🚀 UploadService: Inicializado com sucesso');
    } catch (e) {
      // Se falhar, apenas logar e continuar (não quebrar o app)
      print('⚠️ Erro ao inicializar UploadService: $e');
      _isInitialized = true; // Marcar como inicializado mesmo com erro para não tentar de novo
    }
  }

  /// Trata atualizações de status do upload
  void _handleStatusUpdate(TaskStatusUpdate update) {
    switch (update.status) {
      case TaskStatus.complete:
        print('✅ Upload finalizado com sucesso: ${update.task.taskId}');
        break;
      case TaskStatus.failed:
        AppLogger.error('Falha no upload em background', 
          location: 'UploadService', 
          error: 'ID: ${update.task.taskId}');
        break;
      case TaskStatus.canceled:
        print('⚠️ Upload cancelado: ${update.task.taskId}');
        break;
      default:
        break;
    }
  }

  /// Enfileira um novo upload para ser processado em background
  Future<String> enqueueUpload({
    required File file,
    required String descricao,
    required String tipo,
    String? tags,
    bool isEdit = false,
    String? mediaId,
  }) async {
    if (!_isInitialized) await initialize();

    final baseUrl = await getApiBaseUrl();
    final token = await ApiService.getAccessToken();

    if (token == null) {
      throw Exception('Usuário não autenticado para fazer upload');
    }

    // Determinar a URL correta (Criar ou Editar)
    final url = isEdit && mediaId != null
        ? '$baseUrl/medias/$mediaId/editar/'
        : '$baseUrl/medias/criar/';

    // Criar um ID único para a tarefa
    final taskId = const Uuid().v4();
    final fileName = p.basename(file.path);

    // Configurar a requisição Multipart
    final task = UploadTask(
      taskId: taskId,
      url: url,
      filename: fileName,
      headers: {
        'Authorization': 'Bearer $token',
      },
      fields: {
        'MID_descricao': descricao,
        'MID_tipo_midia': tipo,
        'MID_tags': tags ?? '',
      },
      fileField: 'MID_arquivo',
      mimeType: _getMimeType(fileName),
      updates: Updates.statusAndProgress,
      requiresWiFi: false, // Permitir dados móveis por padrão (estilo WhatsApp)
      retries: 3,         // Tentar 3 vezes em caso de falha de conexão
    );

    // Iniciar o upload
    final enqueued = await FileDownloader().enqueue(task);
    
    if (enqueued) {
      print('📤 Upload enfileirado: $taskId ($descricao)');
      return taskId;
    } else {
      throw Exception('Falha ao enfileirar upload');
    }
  }

  /// Helper para pegar o MimeType básico baseado na extensão
  String _getMimeType(String fileName) {
    final ext = p.extension(fileName).toLowerCase();
    switch (ext) {
      case '.jpg':
      case '.jpeg':
        return 'image/jpeg';
      case '.png':
        return 'image/png';
      case '.pdf':
        return 'application/pdf';
      case '.mp4':
        return 'video/mp4';
      case '.mp3':
        return 'audio/mpeg';
      default:
        return 'application/octet-stream';
    }
  }
}
