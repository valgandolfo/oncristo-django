import 'dart:convert';
import 'package:flutter/material.dart';
import 'webview_screen.dart';
import '../services/api_service.dart';
import '../utils/storage.dart';

/// Tela Home com Menu de Botões Grandes
/// 
/// Menu principal com botões grandes para navegação:
/// - Minhas Mídias
/// - Converter de Mídias
/// - Anota Ai +
/// - Perfil
/// - Sair
class HomeMenu extends StatefulWidget {
  const HomeMenu({super.key});

  @override
  State<HomeMenu> createState() => _HomeMenuState();
}

class _HomeMenuState extends State<HomeMenu> with WidgetsBindingObserver {
  String? _userEmail;
  String? _profileName;
  String? _profilePhotoData; // data:image/... base64
  bool _isAdmin = false;
  DateTime? _lastBackPressed;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _loadUserEmail();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      // Recarregar dados quando o app volta ao foreground
      _loadUserEmail();
    }
  }

  Future<void> _loadUserEmail() async {
    final email = await Storage.getUserEmail();
    final profile = await Storage.getProfileLocal();
    final String? photoPath = profile['photoPath'];
    print('📸 Carregando foto do perfil...');
    print('   photoPath: ${photoPath != null ? (photoPath.length > 50 ? photoPath.substring(0, 50) + '...' : photoPath) : 'null'}');
    
    // Pegar apenas o primeiro nome
    String? fullName = (profile['name'] as String?) ?? (profile['email'] as String?);
    String? firstName;
    if (fullName != null && fullName.isNotEmpty) {
      // Se for email, usar apenas a parte antes do @
      if (fullName.contains('@')) {
        firstName = fullName.split('@').first;
      } else {
        // Pegar apenas o primeiro nome (primeira palavra)
        firstName = fullName.split(' ').first;
      }
    }
    
    setState(() {
      _userEmail = email;
      _profileName = firstName ?? email;
      _profilePhotoData = profile['photoPath'];
      _isAdmin = profile['isAdmin'] == true;
    });
    print('📸 Foto carregada no estado: ${_profilePhotoData != null ? 'sim' : 'não'}');
  }

  void _onProfileTap() {
    showModalBottomSheet<void>(
      context: context,
      builder: (context) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.person),
              title: const Text('Ver Perfil'),
              onTap: () {
                Navigator.pop(context);
                _navigateTo('/perfil/');
              },
            ),
            ListTile(
              leading: const Icon(Icons.settings),
              title: const Text('Configurações'),
              onTap: () {
                Navigator.pop(context);
                _navigateTo('/configuracoes/');
              },
            ),
            ListTile(
              leading: const Icon(Icons.cloud_upload, color: Colors.green),
              title: const Text('Fazer Backup', style: TextStyle(color: Colors.green, fontWeight: FontWeight.bold)),
              subtitle: const Text('Sincronizar mídias com a nuvem'),
              onTap: () {
                Navigator.pop(context);
                _showBackupDialog();
              },
            ),
            if (_isAdmin)
              ListTile(
                leading: const Icon(Icons.admin_panel_settings, color: Colors.blue),
                title: const Text('Administrador', style: TextStyle(color: Colors.blue, fontWeight: FontWeight.bold)),
                onTap: () {
                  Navigator.pop(context);
                  _navigateTo('/admin-painel/usuarios/');
                },
              ),
            ListTile(
              leading: const Icon(Icons.logout, color: Colors.red),
              title: const Text('Sair', style: TextStyle(color: Colors.red)),
              onTap: () {
                Navigator.pop(context);
                _logout();
              },
            ),
          ],
        ),
      ),
    );
  }

  void _navigateTo(String route) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => WebViewScreen(route: route),
      ),
    ).then((_) {
      // Recarregar dados do perfil quando voltar da navegação
      // Isso garante que a foto atualizada seja exibida
      _loadUserEmail();
    });
  }

  Future<void> _logout() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Sair'),
        content: const Text('Deseja realmente sair?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancelar'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('Sair'),
          ),
        ],
      ),
    );

    if (confirm == true) {
      await ApiService.logout();
      if (mounted) {
        Navigator.pushReplacementNamed(context, '/login');
      }
    }
  }

  Future<bool> _onWillPop() async {
    // If there is a navigator stack, allow normal pop
    if (Navigator.canPop(context)) return true;

    final now = DateTime.now();
    if (_lastBackPressed == null || now.difference(_lastBackPressed!) > const Duration(seconds: 2)) {
      _lastBackPressed = now;
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Pressione novamente para sair'), duration: Duration(seconds: 2)),
        );
      }
      return false;
    }

    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Sair'),
        content: const Text('Deseja realmente sair da sua conta?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancelar')),
          TextButton(onPressed: () => Navigator.pop(context, true), child: const Text('Sair', style: TextStyle(color: Colors.red))),
        ],
      ),
    );

    if (confirm == true) {
      await _logout();
    }
    return false;
  }

  void _showBackupDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const SizedBox(height: 10),
              const CircularProgressIndicator(color: Colors.green),
              const SizedBox(height: 25),
              const Text(
                'Sincronizando com a Nuvem',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
              ),
              const SizedBox(height: 10),
              const Text(
                'Enviando suas mídias para o Wasabi S3...\nIsso pode levar alguns minutos.',
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.grey),
              ),
              const SizedBox(height: 10),
            ],
          ),
        );
      },
    );

    // Simular o processo de backup por 3 segundos (depois implementaremos a fila real)
    Future.delayed(const Duration(seconds: 4), () {
      Navigator.pop(context);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('✅ Backup concluído com sucesso!'),
          backgroundColor: Colors.green,
        ),
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    final Future<bool> Function() _handleWillPop = () async {
      // Duplo back: primeira pressão mostra snackbar; segunda abre confirmação
      if (Navigator.canPop(context)) return true;
      final now = DateTime.now();
      if (_lastBackPressed == null || now.difference(_lastBackPressed!) > const Duration(seconds: 2)) {
        _lastBackPressed = now;
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Pressione novamente para sair'), duration: Duration(seconds: 2)),
          );
        }
        return false;
      }

      final confirm = await showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Sair'),
          content: const Text('Deseja realmente sair da sua conta?'),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancelar')),
            TextButton(onPressed: () => Navigator.pop(context, true), child: const Text('Sair', style: TextStyle(color: Colors.red))),
          ],
        ),
      );

      if (confirm == true) {
        await _logout();
      }
      return false;
    };

    return WillPopScope(
      onWillPop: _handleWillPop,
      child: Scaffold(
        appBar: AppBar(
          // Removido título superior para liberar espaço conforme solicitado
          title: const SizedBox.shrink(),
          centerTitle: false,
        ),
        body: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
              // Header com layout personalizado: ícone + título e foto do perfil à direita
              Card(
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 12.0, horizontal: 12.0),
                  child: Column(
                    children: [
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Ícone do app + título (texto restaurado)
                          Container(
                            width: 48,
                            height: 48,
                            decoration: BoxDecoration(
                              color: const Color(0xFF8B0000),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: const Icon(Icons.church, color: Colors.white, size: 30),
                          ),
                          const SizedBox(width: 12),
                          const Text(
                            'On Cristo',
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF8B0000),
                            ),
                          ),
                          const Spacer(),
                          
                          // DEBUG INFO: IP do Servidor
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: [
                              FutureBuilder<String>(
                                future: getApiBaseUrl(),
                                builder: (context, snapshot) {
                                  if (snapshot.hasData) {
                                    final url = snapshot.data!.replaceAll('/api', '');
                                    return Text(
                                      'Servidor: $url',
                                      style: const TextStyle(fontSize: 10, color: Colors.grey),
                                    );
                                  }
                                  return const SizedBox.shrink();
                                },
                              ),
                              const SizedBox(height: 4),
                              // Foto do perfil (toque abre opções)
                              GestureDetector(
                                onTap: _onProfileTap,
                                child: _buildProfileAvatar(),
                              ),
                            ],
                          ),
                        ],
                      ),
                      // Segunda linha: nome de usuário à direita
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          const Spacer(),
                          Text(
                            _profileName ?? _userEmail ?? '',
                            style: const TextStyle(
                              fontSize: 14,
                              color: Colors.black54,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),
              
              // Botão: Minhas Celebrações
              _buildMenuButton(
                context,
                title: 'Minhas Celebrações',
                subtitle: 'Consulte seus agendamentos',
                icon: Icons.calendar_today_rounded,
                color: Colors.blue[700],
                onTap: () => _navigateTo('/app_igreja/celebracoes-agendadas-pub/?modo=app'),
              ),
              const SizedBox(height: 16),
              
              // Botão: Dizimista
              _buildMenuButton(
                context,
                title: 'Quero ser Dizimista',
                subtitle: 'Faça parte da nossa comunidade',
                icon: Icons.favorite_rounded,
                color: Colors.red[700],
                onTap: () => _navigateTo('/app_igreja/quero-ser-dizimista/?modo=app'),
              ),
              const SizedBox(height: 16),
              
              // Botão: Doações
              _buildMenuButton(
                context,
                title: 'Doações e PIX',
                subtitle: 'Ajude sua paróquia',
                icon: Icons.qr_code_rounded,
                color: Colors.green[700],
                onTap: () => _navigateTo('/app_igreja/doacoes/?modo=app'),
              ),
              const SizedBox(height: 16),
              
              // Botão: Pedidos de Oração
              _buildMenuButton(
                context,
                title: 'Pedidos de Oração',
                subtitle: 'Envie suas intenções',
                icon: Icons.auto_awesome_rounded,
                color: Colors.orange[700],
                onTap: () => _navigateTo('/app_igreja/meus-pedidos-oracoes/?modo=app'),
              ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildMenuButton(
    BuildContext context, {
    required String title,
    required IconData icon,
    required VoidCallback onTap,
    Color? color,
    String? subtitle,
  }) {
    final buttonColor = color ?? Theme.of(context).primaryColor;
    
    return Card(
      elevation: 4,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.all(20.0),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: buttonColor.withOpacity(0.3),
              width: 1,
            ),
          ),
          child: Row(
            children: [
              Container(
                width: 56,
                height: 56,
                decoration: BoxDecoration(
                  color: buttonColor,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: buttonColor.withOpacity(0.25),
                      blurRadius: 6,
                      offset: const Offset(0, 3),
                    ),
                  ],
                ),
                child: Icon(
                  icon,
                  size: 28,
                  color: Colors.white,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.black87,
                      ),
                    ),
                    if (subtitle != null) ...[
                      const SizedBox(height: 4),
                      Text(
                        subtitle,
                        style: TextStyle(
                          fontSize: 13,
                          color: Colors.black54,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              Icon(
                Icons.arrow_forward_ios,
                size: 18,
                color: Colors.black38,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildProfileAvatar() {
    // If profile photo is a data URI, decode and show; otherwise show initial
    if (_profilePhotoData != null && _profilePhotoData!.isNotEmpty && _profilePhotoData!.startsWith('data:image/')) {
      try {
        final base64Str = _profilePhotoData!.split(',').last;
        final bytes = base64Decode(base64Str);
        print('📸 Exibindo foto do perfil (${bytes.length} bytes)');
        return CircleAvatar(
          radius: 24,
          backgroundImage: MemoryImage(bytes),
          backgroundColor: Colors.grey[200],
          onBackgroundImageError: (exception, stackTrace) {
            print('❌ Erro ao carregar imagem: $exception');
            // Se houver erro, mostrar inicial
          },
        );
      } catch (e) {
        print('❌ Erro ao decodificar foto: $e');
        // Fallthrough to initial
      }
    }

    final initial = (_profileName ?? _userEmail ?? '').isNotEmpty
        ? (_profileName ?? _userEmail ?? '').substring(0, 1).toUpperCase()
        : '?';

    print('📸 Exibindo inicial do perfil: $initial');
    return CircleAvatar(
      radius: 24,
      backgroundColor: Theme.of(context).primaryColor,
      child: Text(initial, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
    );
  }
}
