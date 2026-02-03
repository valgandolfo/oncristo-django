class AppConfig {
  // IP/Domínio padrão do servidor - On Cristo
  // Para desenvolvimento local: 
  //   - IP local: 192.168.0.13 (sua máquina na rede)
  //   - Ngrok: 07a6d636a9d9.ngrok-free.app (SEM https://)
  //   - Produção: oncristo.com.br
  //   - Emulador Android: 10.0.2.2
  
  // ATUALIZADO: Use IP local quando celular estiver na mesma rede Wi-Fi
  static const String defaultServerIp = '192.168.0.13';
  
  // Porta padrão: DEIXE VAZIO para Ngrok/Produção (pois usam 80/443 padrão)
  // Use '8000' apenas para IP local (192.168.x.x)
  static const String defaultPort = '8000'; 
  
  // Prefixo da API
  static const String apiPrefix = '/app_igreja/api';
}
