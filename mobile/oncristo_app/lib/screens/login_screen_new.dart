/// Tela de Login com opções: Acessar com Senha ou Acessar com Biometria
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/api_service.dart';
import '../services/biometric_service.dart';
import '../utils/storage.dart';
import '../utils/logger.dart';
import 'main_tabs_screen.dart';
import 'home_menu.dart';
import 'register_screen.dart';
import 'forgot_password_screen.dart';
import '../config/app_config.dart';

class LoginScreenNew extends StatefulWidget {
  final bool forceBiometric;
  const LoginScreenNew({super.key, this.forceBiometric = false});

  @override
  State<LoginScreenNew> createState() => _LoginScreenNewState();
}

class _LoginScreenNewState extends State<LoginScreenNew> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _serverController = TextEditingController();
  
  bool _isLoading = false;
  bool _obscurePassword = true;
  bool _canUseBiometrics = false;
  bool _autoBiometricTried = false;
  bool _showServerConfig = false; // Controle para mostrar campo de IP (secreto)
  String? _lastError; // Último erro capturado

  @override
  void initState() {
    super.initState();
    _checkBiometricSupport();
    // Carregar email e servidor após um pequeno delay para garantir que o widget está montado
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadSavedEmail();
      _loadSavedServer();
    });
  }

  /// Verificar se biometria está disponível
  Future<void> _checkBiometricSupport() async {
    final isAvailable = await BiometricService.isAvailable();
    setState(() {
      _canUseBiometrics = isAvailable;
    });
  }

  /// Carregar email salvo
  Future<void> _loadSavedEmail() async {
    final email = await Storage.getUserEmail();
    if (email != null && email.isNotEmpty) {
      setState(() {
        _emailController.text = email;
      });
      print('✅ Email carregado automaticamente: $email');
      _maybeAutoBiometric();
    }
  }

  /// Carregar IP do servidor salvo ou usar padrão local
  Future<void> _loadSavedServer() async {
    final serverIp = await Storage.getServerIp();
    final defaultIp = AppConfig.defaultServerIp;
    
    // Se o IP salvo for o antigo padrão do emulador (10.0.2.2) ou domínio de produção,
    // forçar a atualização para o novo defaultIp (192.168.0.13)
    if (serverIp != null && 
        serverIp.isNotEmpty && 
        serverIp != '10.0.2.2' && 
        !serverIp.contains('oncristo.com.br') &&
        !serverIp.contains('ngrok')) {
      setState(() {
        _serverController.text = serverIp;
      });
      print('✅ IP do servidor carregado: $serverIp');
    } else {
      // Se não tiver salvo OU se for IP/domínio antigo, 
      // usar padrão local e salvar automaticamente
      setState(() {
        _serverController.text = defaultIp;
      });
      await Storage.saveServerIp(defaultIp);
      print('✅ IP padrão local configurado automaticamente: $defaultIp');
    }
  }

  /// Tentar login automático com biometria se houver email+token salvos
  Future<void> _maybeAutoBiometric() async {
    if (_autoBiometricTried) return;
    if (!widget.forceBiometric) return;
    if (!_canUseBiometrics) return;
    final savedEmail = await Storage.getUserEmail();
    final token = await Storage.getAccessToken();
    final biometricEnabled = await Storage.isBiometricEnabled();
    if (savedEmail == null || savedEmail.isEmpty) return;
    if (token == null || token.isEmpty) return;
    if (!biometricEnabled) return;
    _autoBiometricTried = true;
    await _loginWithBiometric(silent: true);
  }

  /// Login com email e senha
  Future<void> _loginWithPassword() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    // Salvar IP do servidor antes de fazer login
    final serverIp = _serverController.text.trim();
    if (serverIp.isNotEmpty) {
      await Storage.saveServerIp(serverIp);
      print('✅ IP do servidor salvo: $serverIp');
    }

    setState(() {
      _isLoading = true;
    });

    final result = await ApiService.login(
      email: _emailController.text.trim(),
      password: _passwordController.text,
    );

    setState(() {
      _isLoading = false;
    });

    if (result['success'] == true) {
      // Aguardar um pouco para garantir que tokens foram salvos
      await Future.delayed(const Duration(milliseconds: 200));
      
      // Verificar se tokens foram realmente salvos
      final token = await Storage.getAccessToken();
      if (token == null || token.isEmpty) {
        _showSnackBar('Erro ao salvar tokens. Tente novamente.');
        return;
      }
      
      // Salvar email ANTES de perguntar sobre biometria
      final emailToSave = _emailController.text.trim();
      await Storage.saveUserEmail(emailToSave);
      print('✅ Email salvo: $emailToSave');
      
      // Perguntar se quer habilitar biometria (se disponível e ainda não habilitada)
      final biometricEnabled = await Storage.isBiometricEnabled();
      if (_canUseBiometrics && !biometricEnabled) {
        _showBiometricDialog();
      } else {
        _navigateToHome();
      }
    } else {
      // Erro no login - MOSTRAR EM DIÁLOGO GRANDE
      final error = result['error'] ?? 'Erro desconhecido ao fazer login';
      final serverIp = _serverController.text.trim();
      final serverDisplay = serverIp.isEmpty ? AppConfig.defaultServerIp : serverIp;
      
      // Obter URL base para debug
      final baseUrl = 'http://$serverDisplay:${AppConfig.defaultPort}${AppConfig.apiPrefix}';
      
      _showErrorDialog(
        'Erro ao Fazer Login',
        error,
        details: 'Servidor: $serverDisplay\nURL: $baseUrl/auth/login/\n\nTente:\n1. Verificar se o servidor está rodando\n2. Verificar se o IP está correto\n3. Verificar se está na mesma rede WiFi\n4. Pressione e segure o ícone da igreja para configurar o IP',
      );
      
      // Registrar no log de erros
      await AppLogger.error(
        'Falha na tentativa de login',
        error: error,
        location: 'LoginScreen._loginWithPassword',
      );
    }
  }

  /// Login com biometria
  Future<void> _loginWithBiometric({bool silent = false}) async {
    // Carregar email salvo se não tiver no campo
    var email = _emailController.text.trim();
    if (email.isEmpty) {
      final savedEmail = await Storage.getUserEmail();
      if (savedEmail != null && savedEmail.isNotEmpty) {
        email = savedEmail;
        setState(() {
          _emailController.text = email;
        });
        print('✅ Email carregado do storage: $email');
      } else {
        _showSnackBar('Por favor, digite seu email ou faça login com senha primeiro');
        return;
      }
    }

    if (!_isEmailValid(email)) {
      _showSnackBar('Email inválido');
      return;
    }

    if (!_canUseBiometrics) {
      _showSnackBar('Biometria não disponível no dispositivo');
      return;
    }

    setState(() {
      _isLoading = true;
    });

    // Autenticar com biometria
    final biometricResult = await BiometricService.authenticate(
      localizedReason: 'Autentique-se com sua biometria para fazer login',
    );

    if (biometricResult['success'] == true) {
      // Verificar se tem token salvo válido
      final token = await Storage.getAccessToken();
      final savedEmail = await Storage.getUserEmail();
      
      // Se tem token válido e email corresponde, ir direto para home
      if (token != null && token.isNotEmpty && savedEmail != null && savedEmail == email) {
        setState(() {
          _isLoading = false;
        });
        print('✅ Login com biometria: token válido encontrado');
        _navigateToHome();
        return;
      }
      
      // Se não tem token ou email diferente, precisa fazer login normal
      setState(() {
        _isLoading = false;
      });
      if (!silent) {
        _showSnackBar('Sessão expirada. Por favor, faça login com senha novamente.');
      }
    } else {
      setState(() {
        _isLoading = false;
      });
      if (biometricResult['error'] != 'Autenticação cancelada ou falhou' && !silent) {
        _showSnackBar(biometricResult['error'] ?? 'Erro na autenticação biométrica');
      }
    }
  }

  /// Mostrar diálogo para habilitar biometria
  void _showBiometricDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Text('Habilitar Biometria'),
        content: const Text(
          'Deseja usar biometria para fazer login mais rápido nas próximas vezes?',
        ),
        actions: [
          TextButton(
            onPressed: () async {
              if (context.mounted) {
                Navigator.pop(context);
              }
              await Storage.setBiometricEnabled(false);
              await Future.delayed(const Duration(milliseconds: 200));
              if (mounted) {
                _navigateToHome();
              }
            },
            child: const Text('Não'),
          ),
          TextButton(
            onPressed: () async {
              if (context.mounted) {
                Navigator.pop(context);
              }
              await Storage.saveUserEmail(_emailController.text.trim());
              await Storage.setBiometricEnabled(true);
              print('✅ Biometria habilitada e email salvo: ${_emailController.text.trim()}');
              await Future.delayed(const Duration(milliseconds: 200));
              if (mounted) {
                _navigateToHome();
              }
            },
            child: const Text('Sim'),
          ),
        ],
      ),
    );
  }

  /// Validar email
  bool _isEmailValid(String email) {
    final RegExp emailRegex = RegExp(
      r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    );
    return emailRegex.hasMatch(email);
  }

  /// Mostrar mensagem
  void _showSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        duration: const Duration(seconds: 5),
      ),
    );
  }

  /// Mostrar erro completo em diálogo
  void _showErrorDialog(String title, String error, {String? details}) {
    setState(() {
      _lastError = error;
    });
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            const Icon(Icons.error, color: Colors.red, size: 28),
            const SizedBox(width: 8),
            Expanded(child: Text(title, style: const TextStyle(fontSize: 18))),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                error,
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              if (details != null) ...[
                const SizedBox(height: 12),
                const Divider(),
                const SizedBox(height: 8),
                const Text(
                  'Detalhes técnicos:',
                  style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.grey),
                ),
                const SizedBox(height: 4),
                Text(
                  details,
                  style: const TextStyle(fontSize: 11, fontFamily: 'monospace'),
                ),
              ],
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () async {
              // Copiar erro para área de transferência
              await Clipboard.setData(ClipboardData(text: '$title\n\n$error${details != null ? '\n\n$details' : ''}'));
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Erro copiado para área de transferência')),
                );
              }
            },
            child: const Text('Copiar'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Fechar'),
          ),
        ],
      ),
    );
  }

  /// Testar conexão com o servidor
  Future<void> _testConnection() async {
    final serverIp = _serverController.text.trim();
    if (serverIp.isEmpty) {
      _showSnackBar('Digite o IP ou domínio do servidor primeiro');
      return;
    }

    // Salvar IP temporariamente para teste
    await Storage.saveServerIp(serverIp);
    
    setState(() {
      _isLoading = true;
    });

    final result = await ApiService.testConnection();
    
    setState(() {
      _isLoading = false;
    });

    if (result['success'] == true) {
      _showSnackBar('✅ Conexão OK! Servidor acessível em ${result['url']}');
    } else {
      _showSnackBar('❌ ${result['message']}\n\nErro: ${result['error']}\n\nURL: ${result['url']}');
    }
  }

  /// Navegar para tela home
  void _navigateToHome() {
    Navigator.of(context, rootNavigator: true).pushAndRemoveUntil(
      MaterialPageRoute(builder: (context) => const MainTabsScreen()),
      (route) => false,
    );
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text('Login'),
        actions: [
          // Botão de refresh - limpar cache e recarregar
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Recarregar',
            onPressed: () async {
              // Limpar tokens e forçar novo login
              await Storage.clearAll();
              setState(() {
                _emailController.clear();
                _passwordController.clear();
              });
              _showSnackBar('Cache limpo. Faça login novamente.');
            },
          ),
          // Botão de debug - ver último erro ou logs
          IconButton(
            icon: const Icon(Icons.bug_report),
            tooltip: 'Ver último erro / logs',
            onPressed: () async {
              try {
                // Se tem último erro, mostrar ele primeiro
                if (_lastError != null) {
                  _showErrorDialog(
                    'Último Erro Capturado',
                    _lastError!,
                  );
                  return;
                }
                
                // Senão, mostrar logs
                final logs = await AppLogger.readLogs();
                if (mounted) {
                  showDialog(
                    context: context,
                    builder: (context) => AlertDialog(
                      title: const Text('Logs de Erro'),
                      content: SingleChildScrollView(
                        child: Text(
                          logs.isEmpty ? 'Nenhum erro registrado.' : logs,
                          style: const TextStyle(fontSize: 12, fontFamily: 'monospace'),
                        ),
                      ),
                      actions: [
                        TextButton(
                          onPressed: () async {
                            await AppLogger.clearLogs();
                            if (mounted) {
                              Navigator.of(context).pop();
                              _showSnackBar('Logs limpos!');
                            }
                          },
                          child: const Text('Limpar Logs'),
                        ),
                        TextButton(
                          onPressed: () => Navigator.of(context).pop(),
                          child: const Text('Fechar'),
                        ),
                      ],
                    ),
                  );
                }
              } catch (e) {
                _showErrorDialog('Erro ao Ler Logs', e.toString());
              }
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Form(
            key: _formKey,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                SizedBox(height: MediaQuery.of(context).size.height * 0.08),
                // Header - Ícone da Igreja com gesto longo para mostrar config de servidor
                GestureDetector(
                  onLongPress: () {
                    setState(() {
                      _showServerConfig = !_showServerConfig;
                    });
                    _showSnackBar(_showServerConfig 
                      ? 'Configurações de servidor ativadas' 
                      : 'Configurações de servidor ocultas');
                  },
                  child: Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: const Color(0xFF8B0000).withOpacity(0.1),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(
                      Icons.church,
                      size: 80,
                      color: Color(0xFF8B0000),
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                const Text(
                  'On Cristo',
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF8B0000),
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  'Acesse sua conta com email e senha ou biometria',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[600],
                  ),
                ),
                const SizedBox(height: 48),
                // Server IP Field - Oculto por padrão, ativado pelo long press no ícone acima
                if (_showServerConfig) ...[
                  TextFormField(
                    controller: _serverController,
                    keyboardType: TextInputType.url,
                    decoration: InputDecoration(
                      labelText: 'Servidor (IP/Domínio)',
                      hintText: '192.168.0.13 ou 4401b3d3d3e5.ngrok-free.app',
                      prefixIcon: const Icon(Icons.dns_outlined),
                      suffixIcon: IconButton(
                        icon: _isLoading 
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.network_check),
                        onPressed: _isLoading ? null : _testConnection,
                        tooltip: 'Testar conexão',
                      ),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide(color: Colors.grey[300]!),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: const BorderSide(
                          color: Color(0xFF8B0000),
                          width: 2,
                        ),
                      ),
                    ),
                    validator: (value) {
                      if (_showServerConfig && (value == null || value.isEmpty)) {
                        return 'Digite o IP ou domínio do servidor';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Dica: Digite apenas o IP ou domínio (sem http:// ou porta). Clique no ícone de rede para testar.',
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                  const SizedBox(height: 20),
                ],
                // Email Field
                TextFormField(
                  controller: _emailController,
                  keyboardType: TextInputType.emailAddress,
                  decoration: InputDecoration(
                    labelText: 'Email',
                    hintText: 'seu@email.com',
                    prefixIcon: const Icon(Icons.email_outlined),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: Colors.grey[300]!),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: const BorderSide(
                        color: Color(0xFF8B0000),
                        width: 2,
                      ),
                    ),
                  ),
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Digite seu email';
                    }
                    if (!_isEmailValid(value)) {
                      return 'Email inválido';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 20),
                // Password Field
                TextFormField(
                  controller: _passwordController,
                  obscureText: _obscurePassword,
                  decoration: InputDecoration(
                    labelText: 'Senha',
                    hintText: '••••••••',
                    prefixIcon: const Icon(Icons.lock_outline),
                    suffixIcon: IconButton(
                      icon: Icon(
                        _obscurePassword
                            ? Icons.visibility_off_outlined
                            : Icons.visibility_outlined,
                      ),
                      onPressed: () {
                        setState(() => _obscurePassword = !_obscurePassword);
                      },
                    ),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: Colors.grey[300]!),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: const BorderSide(
                        color: Color(0xFF8B0000),
                        width: 2,
                      ),
                    ),
                  ),
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Digite sua senha';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 32),
                // Buttons
                Column(
                  children: [
                    // Acessar com Senha
                    SizedBox(
                      width: double.infinity,
                      height: 56,
                      child: ElevatedButton(
                        onPressed: _isLoading ? null : _loginWithPassword,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF8B0000),
                          disabledBackgroundColor: Colors.grey[400],
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        child: _isLoading
                            ? const SizedBox(
                                height: 24,
                                width: 24,
                                child: CircularProgressIndicator(
                                  valueColor:
                                      AlwaysStoppedAnimation<Color>(Colors.white),
                                  strokeWidth: 2,
                                ),
                              )
                            : const Text(
                                'Acessar com Senha',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w600,
                                  color: Colors.white,
                                ),
                              ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    // Acessar com Biometria (condicional)
                    if (_canUseBiometrics)
                      SizedBox(
                        width: double.infinity,
                        height: 56,
                        child: OutlinedButton(
                          onPressed: _isLoading ? null : _loginWithBiometric,
                          style: OutlinedButton.styleFrom(
                            side: const BorderSide(
                              color: const Color(0xFF8B0000),
                              width: 2,
                            ),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              const Icon(
                                Icons.fingerprint,
                                color: const Color(0xFF8B0000),
                                size: 24,
                              ),
                              const SizedBox(width: 12),
                              const Text(
                                'Acessar com Biometria',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w600,
                                  color: const Color(0xFF8B0000),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 32),
                // Links adicionais
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    TextButton(
                      onPressed: () {
                        Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (context) => const ForgotPasswordScreen(),
                          ),
                        );
                      },
                      child: const Text('Esqueci minha senha'),
                    ),
                    const SizedBox(width: 8),
                    const Text('|', style: TextStyle(color: Colors.grey)),
                    const SizedBox(width: 8),
                    TextButton(
                      onPressed: () {
                        Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (context) => const RegisterScreen(),
                          ),
                        );
                      },
                      child: const Text('Criar conta'),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

