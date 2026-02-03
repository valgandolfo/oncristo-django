import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';
import 'dart:io';
import '../utils/storage.dart';
import '../utils/logger.dart';
import '../services/upload_service.dart';
import 'package:path/path.dart' as p;
import 'edit_profile_screen.dart';

import '../config/app_config.dart';

/// Tela WebView que carrega páginas Django responsivas
/// 
/// Esta tela substitui todas as telas Flutter nativas, permitindo
/// que o Django renderize HTML/CSS/JS responsivo diretamente no app.
class WebViewScreen extends StatefulWidget {
  final String route; // Ex: '/medias/lista/', '/medias/criar/'
  final bool hideAppBar;
  
  const WebViewScreen({
    Key? key,
    this.route = '/',
    this.hideAppBar = false,
  }) : super(key: key);

  @override
  State<WebViewScreen> createState() => _WebViewScreenState();
}

class _WebViewScreenState extends State<WebViewScreen> {
  WebViewController? _controller;
  bool _isLoading = true;
  String? _error;
  String _currentRoute = '/dashboard/';

  @override
  void initState() {
    super.initState();
    _currentRoute = widget.route;
    _initWebView();
  }

  Future<void> _initWebView() async {
    try {
      // Obter token JWT antes de criar o WebView
      final token = await Storage.getAccessToken();
      
      // Obter URL base do servidor
      String server = await Storage.getServerIp() ?? AppConfig.defaultServerIp;
      server = server.trim().replaceAll('http://', '').replaceAll('https://', '');
      
      // Lógica idêntica ao api_service.dart para consistência
      final isIp = RegExp(r'^(\d{1,3}\.){3}\d{1,3}').hasMatch(server);
      String baseUrl;
      if (isIp) {
        if (server.contains(':')) {
          baseUrl = 'http://$server';
        } else {
          baseUrl = 'http://$server:${AppConfig.defaultPort}';
        }
      } else {
        baseUrl = 'https://$server';
      }
      
      // Adicionar token + timestamp para furar cache
      final timestamp = DateTime.now().millisecondsSinceEpoch;
      final route = _currentRoute.isNotEmpty ? _currentRoute : widget.route;
      final hasQuery = route.contains('?');
      final sep = hasQuery ? '&' : '?';
      final url = token != null 
          ? '$baseUrl$route${sep}token=$token&_t=$timestamp'
          : '$baseUrl$route${sep}_t=$timestamp';
      print('🔄 URL carregada no WebView: $url');

      // Criar controller do WebView
      final controller = WebViewController()
        ..setJavaScriptMode(JavaScriptMode.unrestricted)
        ..enableZoom(true)
        ..setBackgroundColor(Colors.white)
        ..addJavaScriptChannel(
          'ProfileGetChannel',
          onMessageReceived: (JavaScriptMessage message) async {
            try {
              print('📤 ProfileGetChannel: Solicitando dados do perfil');
              final profile = await Storage.getProfileLocal();
              
              // Enviar dados de volta para JavaScript
              final profileJson = jsonEncode(profile);
              if (_controller != null) {
                await _controller!.runJavaScript('''
                  if (window.onProfileDataReceived) {
                    window.onProfileDataReceived($profileJson);
                  }
                ''');
              }
              
              print('✅ Dados do perfil enviados para JavaScript');
            } catch (e, stackTrace) {
              print('❌ Erro ao obter perfil: $e');
              print('❌ StackTrace: $stackTrace');
            }
          },
        )
        ..addJavaScriptChannel(
          'ProfileChannel',
          onMessageReceived: (JavaScriptMessage message) async {
            try {
              print('═══════════════════════════════════════');
              print('📥 ProfileChannel RECEBEU MENSAGEM');
              print('═══════════════════════════════════════');
              print('Mensagem completa: ${message.message}');
              print('Tamanho da mensagem: ${message.message.length} caracteres');
              
              final data = jsonDecode(message.message);
              print('📥 Dados decodificados: $data');
              print('Tipo de dados: ${data.runtimeType}');
              
              // Tratar valores - sempre enviar, mesmo que vazios (para limpar campos antigos)
              final name = data['name']?.toString().trim() ?? '';
              final whatsapp = data['whatsapp']?.toString().trim() ?? '';
              final email = data['email']?.toString().trim() ?? '';
              final photoPathRaw = data['photoPath']?.toString().trim() ?? '';
              final isAdmin = data['isAdmin'] == true;
              
              // Filtrar photoPath - só aceitar se for data URI válida
              final photoPath = (photoPathRaw.isNotEmpty && photoPathRaw.startsWith('data:image/')) 
                  ? photoPathRaw 
                  : '';
              
              print('📝 Valores processados:');
              print('   name: "$name" (${name.length} chars)');
              print('   whatsapp: "$whatsapp" (${whatsapp.length} chars)');
              print('   email: "$email" (${email.length} chars)');
              print('   isAdmin: $isAdmin');
              print('   photoPath: ${photoPath.isNotEmpty ? (photoPath.length > 50 ? '${photoPath.substring(0, 50)}...' : photoPath) : '(vazio)'} (${photoPath.length} chars)');           
              print('💾 Chamando Storage.saveProfileLocal...');
              // Sempre enviar todos os campos (mesmo vazios) para garantir que sejam salvos/limpos
              await Storage.saveProfileLocal(
                name: name,
                whatsapp: whatsapp,
                email: email,
                photoPath: photoPath,
                isAdmin: isAdmin,
              );
              
              print('✅ Storage.saveProfileLocal concluído');
              
              // Verificar se foi salvo
              print('🔍 Verificando dados salvos...');
              final verificado = await Storage.getProfileLocal();
              print('✅ Verificação - Dados recuperados:');
              print('   Nome: ${verificado['name'] ?? 'null'}');
              print('   WhatsApp: ${verificado['whatsapp'] ?? 'null'}');
              print('   Email: ${verificado['email'] ?? 'null'}');
              final photoPathVerificado = verificado['photoPath'];
              print('   PhotoPath: ${photoPathVerificado != null && photoPathVerificado.isNotEmpty ? (photoPathVerificado.length > 50 ? '${photoPathVerificado.substring(0, 50)}...' : photoPathVerificado) : '(vazio)'}');
              print('═══════════════════════════════════════');
            } catch (e, stackTrace) {
              print('═══════════════════════════════════════');
              print('❌ ERRO AO SALVAR PERFIL');
              print('═══════════════════════════════════════');
              print('Erro: $e');
              print('Tipo do erro: ${e.runtimeType}');
              print('StackTrace:');
              print(stackTrace);
              print('Mensagem recebida: ${message.message}');
              print('═══════════════════════════════════════');
            }
          },
        )
        ..addJavaScriptChannel(
          'SaveMediaChannel',
          onMessageReceived: (JavaScriptMessage message) async {
            try {
              final data = jsonDecode(message.message);
              final url = data['url']?.toString() ?? '';
              final filename = data['filename']?.toString() ?? 'midia';
              
              print('💾 SaveMediaChannel: Salvando mídia');
              print('   URL: $url');
              print('   Filename: $filename');
              
              // Obter token JWT para autenticação
              final token = await Storage.getAccessToken();
              final headers = <String, String>{};
              if (token != null) {
                headers['Authorization'] = 'Bearer $token';
              }
              
              // Baixar arquivo da URL
              final response = await http.get(Uri.parse(url), headers: headers);
              
              if (response.statusCode == 200) {
                // Salvar no diretório de documentos do celular
                final directory = await getApplicationDocumentsDirectory();
                // Criar pasta OnCristo se não existir
                final oncristoDir = Directory('${directory.path}/OnCristo');
                if (!await oncristoDir.exists()) {
                  await oncristoDir.create(recursive: true);
                }
                
                // Determinar extensão do arquivo
                final uri = Uri.parse(url);
                final pathSegments = uri.pathSegments;
                final lastSegment = pathSegments.isNotEmpty ? pathSegments.last : '';
                final ext = lastSegment.contains('.') 
                    ? '.${lastSegment.split('.').last}' 
                    : '';
                
                final file = File('${oncristoDir.path}/${filename}$ext');
                await file.writeAsBytes(response.bodyBytes);
                
                print('✅ Mídia salva em: ${file.path}');
                
                if (_controller != null) {
                  await _controller!.runJavaScript('''
                    alert('✅ Mídia salva com sucesso!\\n\\nLocal: OnCristo/${filename}$ext');
                  ''');
                }
              } else {
                throw Exception('Erro ao baixar arquivo: ${response.statusCode}');
              }
            } catch (e, stackTrace) {
              print('❌ Erro ao salvar mídia: $e');
              print('❌ StackTrace: $stackTrace');
              
              if (_controller != null) {
                await _controller!.runJavaScript('''
                  alert('❌ Erro ao salvar mídia. Tente novamente.');
                ''');
              }
            }
          },
        )
        ..addJavaScriptChannel(
          'ConfigGetChannel',
          onMessageReceived: (JavaScriptMessage message) async {
            try {
              final data = jsonDecode(message.message);
              final type = data['type']?.toString();
              
              if (type == 'serverIp') {
                final serverIp = await Storage.getServerIp() ?? '192.168.0.13';
                if (_controller != null) {
                  await _controller!.runJavaScript('''
                    if (window.onServerIpReceived) {
                      window.onServerIpReceived('$serverIp');
                    }
                  ''');
                }
              } else if (type == 'printerColumns') {
                final columns = await Storage.getPrinterColumns();
                if (_controller != null) {
                  await _controller!.runJavaScript('''
                    if (window.onPrinterColumnsReceived) {
                      window.onPrinterColumnsReceived($columns);
                    }
                  ''');
                }
              }
            } catch (e) {
              print('❌ Erro ao obter configuração: $e');
            }
          },
        )
        ..addJavaScriptChannel(
          'ConfigChannel',
          onMessageReceived: (JavaScriptMessage message) async {
            try {
              final data = jsonDecode(message.message);
              final type = data['type']?.toString();
              
              if (type == 'serverIp') {
                final ip = data['value']?.toString().trim() ?? '';
                if (ip.isNotEmpty) {
                  await Storage.saveServerIp(ip);
                  print('✅ IP do servidor salvo: $ip');
                }
              } else if (type == 'printerColumns') {
                final columns = int.tryParse(data['value']?.toString() ?? '40') ?? 40;
                await Storage.savePrinterColumns(columns);
                print('✅ Colunas impressora salvas: $columns');
              }
            } catch (e) {
              print('❌ Erro ao salvar configuração: $e');
            }
          },
        )
        ..addJavaScriptChannel(
          'PrintChannel',
          onMessageReceived: (JavaScriptMessage message) async {
            try {
              final data = jsonDecode(message.message);
              final text = data['text']?.toString() ?? '';
              final title = data['title']?.toString() ?? 'Impressão On Cristo';
              
              print('🖨️ PrintChannel: Solicitando impressão/compartilhamento');
              
              // No Android, o Share.share permite enviar o texto para a fila de impressão
              // ou salvar como PDF/Drive através do menu de compartilhamento.
              await Share.share(text, subject: title);
            } catch (e) {
              print('❌ Erro ao processar impressão: $e');
            }
          },
        )
        ..addJavaScriptChannel(
          'ImagePickerChannel',
          onMessageReceived: (JavaScriptMessage message) async {
            try {
              final data = jsonDecode(message.message);
              final source = data['source']; // 'gallery' ou 'camera'
              final callbackId = data['callbackId'] ?? 'default';
              
              print('📷 ImagePickerChannel: $source');
              
              final ImagePicker picker = ImagePicker();
              XFile? image;
              
              if (source == 'camera') {
                image = await picker.pickImage(source: ImageSource.camera);
              } else {
                image = await picker.pickImage(source: ImageSource.gallery);
              }
              
              if (image != null) {
                // Ler a imagem como base64
                final bytes = await image.readAsBytes();
                final base64Image = base64Encode(bytes);
                final dataUri = 'data:image/jpeg;base64,$base64Image';
                
                // Enviar de volta para o JavaScript
                if (_controller != null) {
                  await _controller!.runJavaScript('''
                    if (window.onImagePicked_$callbackId) {
                      window.onImagePicked_$callbackId('$dataUri');
                    } else if (window.onImagePicked) {
                      window.onImagePicked('$dataUri', '$callbackId');
                    }
                  ''');
                }
                
                print('✅ Imagem selecionada e enviada para JavaScript');
              } else {
                // Usuário cancelou
                if (_controller != null) {
                  await _controller!.runJavaScript('''
                    if (window.onImagePicked_$callbackId) {
                      window.onImagePicked_$callbackId(null);
                    } else if (window.onImagePicked) {
                      window.onImagePicked(null, '$callbackId');
                    }
                  ''');
                }
                print('⚠️ Seleção de imagem cancelada');
              }
            } catch (e, stackTrace) {
              print('❌ Erro ao selecionar imagem: $e');
              print('❌ StackTrace: $stackTrace');
              
              // Enviar erro para JavaScript
              try {
                final errorData = jsonDecode(message.message);
                final callbackId = errorData['callbackId'] ?? 'default';
                if (_controller != null) {
                  await _controller!.runJavaScript('''
                    if (window.onImagePicked_$callbackId) {
                      window.onImagePicked_$callbackId(null);
                    }
                  ''');
                }
              } catch (_) {
                // Ignorar erro de parse
              }
            }
          },
        )
        ..addJavaScriptChannel(
          'UploadChannel',
          onMessageReceived: (JavaScriptMessage message) async {
            try {
              final data = jsonDecode(message.message);
              final String dataUri = data['dataUri'] ?? '';
              final String description = data['description'] ?? 'Sem descrição';
              final String type = data['type'] ?? 'outro';
              final String? tags = data['tags'];
              final bool isEdit = data['is_edit'] == true;
              final String? mediaId = data['media_id']?.toString();

              print('🚀 UploadChannel: Recebido pedido de upload em background');
              
              if (dataUri.isEmpty) {
                throw Exception('Arquivo vazio ou não selecionado');
              }

              // Converter Data URI para arquivo temporário
              final bytes = base64Decode(dataUri.split(',').last);
              final tempDir = await getTemporaryDirectory();
              
              // Determinar extensão
              String ext = '.jpg';
              if (dataUri.contains('image/png')) ext = '.png';
              if (dataUri.contains('application/pdf')) ext = '.pdf';
              
              final tempFile = File(p.join(tempDir.path, 'upload_${DateTime.now().millisecondsSinceEpoch}$ext'));
              await tempFile.writeAsBytes(bytes);

              // Enfileirar no serviço de background
              await UploadService().enqueueUpload(
                file: tempFile,
                descricao: description,
                tipo: type,
                tags: tags,
                isEdit: isEdit,
                mediaId: mediaId,
              );

              // Avisar o JavaScript que o processo começou
              if (_controller != null) {
                await _controller!.runJavaScript('''
                  if (window.onUploadStarted) {
                    window.onUploadStarted();
                  } else {
                    alert('✅ Upload iniciado em background! Você pode continuar usando o app.');
                  }
                ''');
              }
            } catch (e, stackTrace) {
              print('❌ Erro no UploadChannel: $e');
              AppLogger.error('Erro no UploadChannel', error: e, stackTrace: stackTrace);
              
              if (_controller != null) {
                await _controller!.runJavaScript('''
                  alert('❌ Erro ao iniciar upload: $e');
                ''');
              }
            }
          },
        )
        ..addJavaScriptChannel(
          'NavigationChannel',
          onMessageReceived: (JavaScriptMessage message) async {
            if (message.message == 'open_profile_edit') {
              print('🚀 NavigationChannel: Abrindo editor de perfil local');
              final result = await Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const EditProfileScreen(),
                ),
              );
              if (result == true && _controller != null) {
                // Após editar, recarregar os dados no HTML
                await _controller!.runJavaScript('loadLocalProfile();');
              }
            }
          },
        )
        ..setNavigationDelegate(
          NavigationDelegate(
            onPageStarted: (String url) {
              setState(() {
                _isLoading = true;
                _error = null;
              });
            },
            onPageFinished: (String url) async {
              setState(() {
                _isLoading = false;
              });
              
              // Injetar token JWT como cookie (importante para Django)
              if (token != null) {
                await _injectAuthToken();
              }
              
              // Injetar função para salvar IP (para página de perfil)
              await _injectSaveIpFunction();
              
              // Injetar funções de perfil (sempre, para estar disponível)
              await _injectProfileFunctions();
              
              // Injetar funções de configurações
              await _injectConfigFunctions();
              
              // Aguardar um pouco e verificar se ProfileChannel está disponível
              await Future.delayed(Duration(milliseconds: 500));
              if (_controller != null) {
                await _controller!.runJavaScript('''
                  console.log('=== VERIFICAÇÃO ProfileChannel ===');
                  console.log('ProfileChannel type:', typeof ProfileChannel);
                  if (typeof ProfileChannel !== 'undefined') {
                    console.log('✅ ProfileChannel está disponível');
                    console.log('ProfileChannel keys:', Object.keys(ProfileChannel));
                  } else {
                    console.log('❌ ProfileChannel NÃO está disponível');
                  }
                ''');
              }
              
              // Verificar se a página retornou erro 401 (token expirado)
              try {
                if (_controller != null) {
                  final bodyText = await _controller!.runJavaScriptReturningResult('''
                    document.body.innerText
                  ''');
                  final bodyStr = bodyText.toString().toLowerCase();
                if (bodyStr.contains('sessão expirada') || 
                    bodyStr.contains('login necessário') ||
                    bodyStr.contains('sessao expirada')) {
                  // Token expirado, redirecionar para login após 1 segundo
                  await Future.delayed(const Duration(seconds: 1));
                  if (mounted) {
                    Navigator.pushReplacementNamed(context, '/login');
                  }
                }
                }
              } catch (e) {
                // Ignorar erro de JavaScript
              }
            },
            onWebResourceError: (WebResourceError error) {
              String errorMsg = error.description;
              
              // Log detalhado do erro para o ícone de bug
              AppLogger.error(
                'Erro de rede no WebView',
                error: 'Código: ${error.errorCode}\nDescrição: $errorMsg\nURL: ${error.url}\nTipo: ${error.errorType}',
                location: 'WebViewScreen.onWebResourceError',
              ).catchError((e) => print('⚠️ Erro ao registrar log: $e'));
              
              // Determinar mensagem de erro amigável
              String errorMessage = 'Erro ao carregar página';
              bool canChangeIp = false;

              if (errorMsg.contains('ERR_CONNECTION_REFUSED') || errorMsg.contains('ERR_CONNECTION_TIMED_OUT')) {
                errorMessage = '❌ Não foi possível conectar ao servidor Django!\n\n'
                    'IP atual: $server\n\n'
                    'Soluções:\n'
                    '1. Inicie o servidor: ./iniciar_projeto.sh\n'
                    '2. Verifique se o notebook e o celular estão no mesmo Wi-Fi\n'
                    '3. Verifique se o IP do notebook mudou';
                canChangeIp = true;
              } else if (errorMsg.contains('ERR_NAME_NOT_RESOLVED')) {
                errorMessage = '❌ IP do servidor inválido ou não encontrado!\n\n'
                    'IP atual: $server';
                canChangeIp = true;
              } else if (error.errorCode == -6 || errorMsg.contains('BLOCKED_BY_ORB')) {
                errorMessage = '❌ Bloqueio de Segurança (ORB)\n\nO servidor Django recusou a conexão do app.';
              } else {
                errorMessage = 'Erro: $errorMsg (Cód: ${error.errorCode})';
              }
              
              // Atualizar estado com botão de mudar IP se necessário
              if (mounted) {
                setState(() {
                  _isLoading = false;
                  _error = errorMessage;
                });

                if (canChangeIp) {
                  // Mostrar diálogo para mudar IP imediatamente
                  WidgetsBinding.instance.addPostFrameCallback((_) {
                    _showChangeIpDialog(server);
                  });
                }
              }
            },
          ),
        )
        ..loadRequest(Uri.parse(url));

      // Assign and rebuild so UI can use the controller
      setState(() {
        _controller = controller;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _error = 'Erro ao inicializar: $e';
      });
    }
  }

  Future<void> _injectAuthToken() async {
    try {
      final token = await Storage.getAccessToken();
      if (token != null && _controller != null) {
        // Injetar token como cookie (Django vai ler isso)
        // IMPORTANTE: Cookie precisa ser definido no domínio correto
        await _controller!.runJavaScript('''
          // Definir cookie para o domínio atual
          document.cookie = 'auth_token=$token; path=/; SameSite=None; Secure=false';
          // Também salvar no localStorage (backup)
          localStorage.setItem('auth_token', '$token');
          console.log('Token JWT injetado no cookie e localStorage');
        ''');
      }
      
      // Injetar função para obter logs do app
      await _injectLogsFunction();
      
      // Injetar função para salvar IP do servidor
      await _injectSaveIpFunction();
      
      // Injetar funções de perfil (PIX)
      await _injectProfileFunctions();
      
      // Injetar funções de configurações
      await _injectConfigFunctions();
    } catch (e) {
      print('Erro ao injetar token: $e');
    }
  }

  Future<void> _injectLogsFunction() async {
    try {
      final logsPath = await AppLogger.getLogFilePath();
      final logsContent = await AppLogger.readLogs();
      final logsEscaped = logsContent.replaceAll("'", "\\'").replaceAll("\n", "\\n");
      
      if (_controller != null) {
        await _controller!.runJavaScript('''
        window.getAppLogs = async function() {
          return '$logsEscaped';
        };
      ''');
      }
    } catch (e) {
      print('Erro ao injetar função de logs: $e');
      // Fallback: função que retorna mensagem de erro
      if (_controller != null) {
        await _controller!.runJavaScript('''
          window.getAppLogs = async function() {
            return 'Erro ao carregar logs: $e';
          };
        ''');
      }
    }
  }

  Future<void> _injectSaveIpFunction() async {
    try {
      // Injetar IP atual no localStorage da página
      final currentIp = await Storage.getServerIp() ?? '192.168.0.13';
      if (_controller != null) {
        await _controller!.runJavaScript('''
        localStorage.setItem('server_ip', '$currentIp');
        
        // Função para salvar IP (mostra mensagem para usuário)
        window.saveServerIp = async function(ip) {
          localStorage.setItem('server_ip', ip);
          alert('IP salvo: ' + ip + '\\n\\nReinicie o app para aplicar a mudança.');
          return true;
        };
      ''');
      }
    } catch (e) {
      print('Erro ao injetar função de salvar IP: $e');
    }
  }

  Future<void> _injectProfileFunctions() async {
    try {
      if (_controller != null) {
        // Injetar função para obter dados do perfil
        await _controller!.runJavaScript('''
          window.getProfileData = async function() {
            return new Promise((resolve) => {
              // Configurar callback para receber dados
              window.onProfileDataReceived = function(profile) {
                resolve(profile);
                delete window.onProfileDataReceived;
              };
              
              // Solicitar dados via ProfileGetChannel
              if (typeof ProfileGetChannel !== 'undefined') {
                ProfileGetChannel.postMessage('get');
              } else {
                // Fallback: retornar null se channel não estiver disponível
                setTimeout(() => resolve(null), 100);
              }
            });
          };
          
          console.log("✅ Funções de perfil injetadas");
        ''');
      }
    } catch (e) {
      print('Erro ao injetar funções de perfil: $e');
    }
  }

  Future<void> _injectConfigFunctions() async {
    try {
      if (_controller != null) {
        final serverIp = await Storage.getServerIp() ?? '192.168.0.13';
        final printerColumns = await Storage.getPrinterColumns();
        
        await _controller!.runJavaScript('''
          // Função para obter IP do servidor
          window.getServerIp = async function() {
            return new Promise((resolve) => {
              if (typeof ConfigGetChannel !== 'undefined') {
                window.onServerIpReceived = function(ip) {
                  resolve(ip);
                  delete window.onServerIpReceived;
                };
                ConfigGetChannel.postMessage(JSON.stringify({type: 'serverIp'}));
              } else {
                // Fallback: retornar do localStorage
                const saved = localStorage.getItem('server_ip');
                resolve(saved || '$serverIp');
              }
            });
          };
          
          // Função para salvar IP do servidor
          window.saveServerIp = async function(ip) {
            if (typeof ConfigChannel !== 'undefined') {
              ConfigChannel.postMessage(JSON.stringify({type: 'serverIp', value: ip}));
              return true;
            } else {
              // Fallback: salvar no localStorage
              localStorage.setItem('server_ip', ip);
              return true;
            }
          };
          
          // Função para obter colunas da impressora
          window.getPrinterColumns = async function() {
            return new Promise((resolve) => {
              if (typeof ConfigGetChannel !== 'undefined') {
                window.onPrinterColumnsReceived = function(columns) {
                  resolve(columns);
                  delete window.onPrinterColumnsReceived;
                };
                ConfigGetChannel.postMessage(JSON.stringify({type: 'printerColumns'}));
              } else {
                // Fallback: retornar do localStorage ou padrão
                const saved = localStorage.getItem('printer_columns');
                resolve(saved ? parseInt(saved) : $printerColumns);
              }
            });
          };
          
          // Função para salvar colunas da impressora
          window.savePrinterColumns = async function(columns) {
            if (typeof ConfigChannel !== 'undefined') {
              ConfigChannel.postMessage(JSON.stringify({type: 'printerColumns', value: columns}));
              return true;
            } else {
              // Fallback: salvar no localStorage
              localStorage.setItem('printer_columns', columns.toString());
              return true;
            }
          };
          
          console.log("✅ Funções de configurações injetadas");
        ''');
      }
    } catch (e) {
      print('Erro ao injetar funções de configurações: $e');
    }
  }

  void _showChangeIpDialog(String currentIp) {
    final controller = TextEditingController(text: currentIp);
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Text('Configurar Servidor'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Não foi possível conectar. O IP do servidor mudou?'),
            const SizedBox(height: 16),
            TextField(
              controller: controller,
              decoration: const InputDecoration(
                labelText: 'IP ou Domínio',
                hintText: 'Ex: 192.168.0.13 ou igeracao.com.br',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            onPressed: () async {
              final newIp = controller.text.trim();
              if (newIp.isNotEmpty) {
                await Storage.saveServerIp(newIp);
                if (mounted) {
                  Navigator.pop(context);
                  _initWebView(); // Tentar novamente com o novo IP
                }
              }
            },
            child: const Text('Salvar e Conectar'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: widget.hideAppBar ? null : AppBar(
        title: const Text('On Cristo'),
        leading: IconButton(
          icon: const Icon(Icons.home),
          onPressed: () {
            Navigator.pushReplacementNamed(context, '/home');
          },
          tooltip: 'Menu Principal',
        ),
        actions: [
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.all(16.0),
              child: SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(strokeWidth: 2),
              ),
            )
          else
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: _controller == null ? null : () => _controller!.reload(),
              tooltip: 'Recarregar',
            ),
          IconButton(
            icon: const Icon(Icons.arrow_back),
            onPressed: () async {
              if (_controller != null && await _controller!.canGoBack()) {
                await _controller!.goBack();
              } else {
                Navigator.pop(context);
              }
            },
            tooltip: 'Voltar',
          ),
        ],
      ),
      body: _error != null
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error_outline, size: 64, color: Colors.red),
                  const SizedBox(height: 16),
                  Text(
                    _error!,
                    textAlign: TextAlign.center,
                    style: const TextStyle(color: Colors.red),
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () {
                      _initWebView();
                    },
                    child: const Text('Tentar Novamente'),
                  ),
                ],
              ),
            )
          : (_controller == null
              ? const Center(child: CircularProgressIndicator())
              : WebViewWidget(controller: _controller!)),
    );
  }
}
