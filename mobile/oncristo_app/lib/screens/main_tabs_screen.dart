import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../services/api_service.dart';
import '../utils/storage.dart';
import 'webview_screen.dart';
import 'edit_profile_screen.dart';

class MainTabsScreen extends StatefulWidget {
  const MainTabsScreen({super.key});

  @override
  State<MainTabsScreen> createState() => _MainTabsScreenState();
}

class _MainTabsScreenState extends State<MainTabsScreen> {
  int _currentIndex = 0;
  List<dynamic> _tabs = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadAppConfig();
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

  Future<void> _loadAppConfig() async {
    try {
      final baseUrl = await getApiBaseUrl();
      final configUrl = '$baseUrl/app_igreja/api/app-config/';
      
      print('🌐 Buscando configuração do app: $configUrl');
      
      final response = await http.get(Uri.parse(configUrl));
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _tabs = data['tabs'];
          _isLoading = false;
        });
      } else {
        setState(() {
          _error = 'Erro ao carregar configuração: ${response.statusCode}';
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Falha na conexão: $e';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    if (_error != null || _tabs.isEmpty) {
      return Scaffold(
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(20.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.error_outline, size: 64, color: Colors.red),
                const SizedBox(height: 16),
                const Text(
                  'Não foi possível conectar ao servidor.',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                Text(
                  _error ?? 'Nenhuma aba configurada no servidor.',
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.red),
                ),
                const SizedBox(height: 24),
                ElevatedButton(
                  onPressed: () {
                    setState(() {
                      _isLoading = true;
                      _error = null;
                    });
                    _loadAppConfig();
                  },
                  child: const Text('Tentar Novamente'),
                ),
              ],
            ),
          ),
        ),
      );
    }

    // A URL da aba atual
    final String currentUrl = _tabs[_currentIndex]['url'];
    // Extrair apenas a rota (path) da URL absoluta
    final uri = Uri.parse(currentUrl);
    final String route = uri.path + (uri.query.isNotEmpty ? '?${uri.query}' : '');
    
    // Garantir que passamos o parâmetro modo=app apenas se não estiver lá
    String finalRoute = route;
    if (!finalRoute.contains('modo=app')) {
      finalRoute = route.contains('?') 
          ? '$route&modo=app' 
          : '$route?modo=app';
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('On Cristo', style: TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF8B0000))),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout, color: Colors.grey),
            onPressed: _logout,
          ),
        ],
      ),
      body: SafeArea(
        child: IndexedStack(
          index: _currentIndex,
          children: _tabs.map((tab) {
            final tabUri = Uri.parse(tab['url']);
            final tabRoute = tabUri.path + (tabUri.query.isNotEmpty ? '?${tabUri.query}' : '');
            
            String tabFinalRoute = tabRoute;
            if (!tabFinalRoute.contains('modo=app')) {
              tabFinalRoute = tabRoute.contains('?') 
                  ? '$tabRoute&modo=app' 
                  : '$tabRoute?modo=app';
            }
            
            return WebViewScreen(route: tabFinalRoute, hideAppBar: true);
          }).toList(),
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        type: BottomNavigationBarType.fixed,
        selectedItemColor: const Color(0xFF8B0000), // Vinho On Cristo
        unselectedItemColor: Colors.grey,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        items: _tabs.map((tab) {
          return BottomNavigationBarItem(
            icon: Icon(_getIconData(tab['icon'])),
            label: tab['label'],
          );
        }).toList(),
      ),
    );
  }

  IconData _getIconData(String iconName) {
    switch (iconName) {
      case 'home':
        return Icons.home_rounded;
      case 'info_outline':
        return Icons.info_rounded;
      case 'list_alt':
        return Icons.auto_awesome_motion_rounded;
      case 'share':
        return Icons.share_rounded;
      default:
        return Icons.help_outline_rounded;
    }
  }
}
