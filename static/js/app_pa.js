// PWA - Projeto On Cristo (Versão PythonAnywhere)
class OnCristoPWA {
  constructor() {
    this.deferredPrompt = null;
    this.installButton = null;
    this.init();
  }

  init() {
    // Não registrar Service Worker no PythonAnywhere
    // this.registerServiceWorker();
    this.setupInstallPrompt();
    this.setupNotifications();
    this.setupOfflineDetection();
    this.setupAppUpdate();
  }

  // Registrar Service Worker (DESABILITADO para PythonAnywhere)
  async registerServiceWorker() {
    console.log('Service Worker desabilitado no PythonAnywhere');
    return;
  }

  // Configurar prompt de instalação
  setupInstallPrompt() {
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      this.deferredPrompt = e;
      this.showInstallButton();
    });

    window.addEventListener('appinstalled', () => {
      console.log('PWA instalado com sucesso!');
      this.hideInstallButton();
      this.deferredPrompt = null;
    });
  }

  // Mostrar botão de instalação
  showInstallButton() {
    // Criar botão de instalação se não existir
    if (!this.installButton) {
      this.installButton = document.createElement('button');
      this.installButton.id = 'install-button';
      this.installButton.className = 'btn btn-success btn-lg position-fixed';
      this.installButton.style.cssText = `
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        border-radius: 50px;
        padding: 15px 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        animation: pulse 2s infinite;
      `;
      this.installButton.innerHTML = `
        <i class="fas fa-download me-2"></i>
        Instalar App
      `;
      
      this.installButton.addEventListener('click', () => {
        this.installPWA();
      });

      document.body.appendChild(this.installButton);
    }
  }

  // Esconder botão de instalação
  hideInstallButton() {
    if (this.installButton) {
      this.installButton.remove();
      this.installButton = null;
    }
  }

  // Instalar PWA
  async installPWA() {
    if (this.deferredPrompt) {
      this.deferredPrompt.prompt();
      const { outcome } = await this.deferredPrompt.userChoice;
      console.log('Resultado da instalação:', outcome);
      this.deferredPrompt = null;
    }
  }

  // Configurar notificações
  setupNotifications() {
    // Notification API só funciona em HTTPS (origens seguras)
    if ('Notification' in window && (location.protocol === 'https:' || location.hostname === 'localhost' || location.hostname === '127.0.0.1')) {
      Notification.requestPermission().then(permission => {
        console.log('Permissão de notificação:', permission);
      }).catch(error => {
        console.log('Erro ao solicitar permissão de notificação:', error);
      });
    }
  }

  // Detectar status offline
  setupOfflineDetection() {
    window.addEventListener('online', () => {
      console.log('Aplicação online');
      this.hideOfflineMessage();
    });

    window.addEventListener('offline', () => {
      console.log('Aplicação offline');
      this.showOfflineMessage();
    });
  }

  // Mostrar mensagem offline
  showOfflineMessage() {
    if (!document.getElementById('offline-message')) {
      const message = document.createElement('div');
      message.id = 'offline-message';
      message.className = 'alert alert-warning alert-dismissible fade show position-fixed';
      message.style.cssText = `
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 1000;
        min-width: 300px;
      `;
      message.innerHTML = `
        <i class="fas fa-wifi-slash me-2"></i>
        <strong>Modo Offline:</strong> Algumas funcionalidades podem não estar disponíveis.
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
      `;
      document.body.appendChild(message);
    }
  }

  // Esconder mensagem offline
  hideOfflineMessage() {
    const message = document.getElementById('offline-message');
    if (message) {
      message.remove();
    }
  }

  // Configurar atualizações do app
  setupAppUpdate() {
    // Verificar atualizações periodicamente
    setInterval(() => {
      this.checkForUpdates();
    }, 300000); // Verificar a cada 5 minutos
  }

  // Verificar atualizações
  async checkForUpdates() {
    try {
      const response = await fetch('/static/js/app.js', { cache: 'no-cache' });
      if (response.ok) {
        console.log('Verificação de atualizações concluída');
      }
    } catch (error) {
      console.warn('Erro ao verificar atualizações:', error);
    }
  }

  // Mostrar notificação de atualização
  showUpdateNotification() {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('On Cristo', {
        body: 'Uma nova versão está disponível! Recarregue a página para atualizar.',
        icon: '/static/icons/icon-192x192.png'
      });
    }
  }
}

// Inicializar PWA quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
  new OnCristoPWA();
});
