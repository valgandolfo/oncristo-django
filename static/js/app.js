// PWA - Projeto On Cristo
class OnCristoPWA {
  constructor() {
    this.deferredPrompt = null;
    this.installButton = null;
    this.init();
  }

  init() {
    this.registerServiceWorker();
    this.setupInstallPrompt();
    this.setupNotifications();
    this.setupOfflineDetection();
    this.setupAppUpdate();
  }

  // Registrar Service Worker
  async registerServiceWorker() {
    if ('serviceWorker' in navigator) {
      try {
        // Verificar se estamos em produção (PythonAnywhere) ou desenvolvimento
        const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
        
        // Desabilitar Service Worker no PythonAnywhere se houver problemas
        if (isProduction && window.location.hostname.includes('pythonanywhere')) {
          console.log('Service Worker desabilitado no PythonAnywhere para evitar problemas');
          return;
        }
        
        // Caminho do Service Worker baseado no ambiente
        const swPath = '/static/js/sw.js';
        
        const registration = await navigator.serviceWorker.register(swPath);
        console.log('Service Worker registrado:', registration);
        
        // Verificar atualizações
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              this.showUpdateNotification();
            }
          });
        });
      } catch (error) {
        console.error('Erro ao registrar Service Worker:', error);
        // Fallback: tentar registrar sem Service Worker
        console.log('PWA funcionará sem cache offline');
      }
    }
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
  async setupNotifications() {
    if ('Notification' in window) {
      // DESABILITADO TEMPORARIAMENTE - Popup de notificações
      // if (Notification.permission === 'default') {
      //   this.showNotificationPermission();
      // }
    }
  }

  // Função de notificações removida temporariamente

  // Solicitar permissão para notificações
  async requestNotificationPermission() {
    try {
      const permission = await Notification.requestPermission();
      if (permission === 'granted') {
        console.log('Permissão para notificações concedida');
        this.subscribeToPushNotifications();
      }
    } catch (error) {
      console.error('Erro ao solicitar permissão:', error);
    }
  }

  // Inscrever para notificações push
  async subscribeToPushNotifications() {
    if ('serviceWorker' in navigator && 'PushManager' in window) {
      try {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: this.urlBase64ToUint8Array('YOUR_VAPID_PUBLIC_KEY')
        });
        
        console.log('Inscrito para notificações push:', subscription);
        // Aqui você enviaria a subscription para o servidor
      } catch (error) {
        console.error('Erro ao inscrever para notificações:', error);
      }
    }
  }

  // Detectar status offline/online
  setupOfflineDetection() {
    window.addEventListener('online', () => {
      this.showOnlineStatus();
    });

    window.addEventListener('offline', () => {
      this.showOfflineStatus();
    });
  }

  // Mostrar status online
  showOnlineStatus() {
    this.showToast('Conectado à internet', 'success');
  }

  // Mostrar status offline
  showOfflineStatus() {
    this.showToast('Modo offline ativo', 'warning');
  }

  // Configurar atualização do app
  setupAppUpdate() {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.addEventListener('controllerchange', () => {
        this.showToast('App atualizado! Recarregue para aplicar as mudanças.', 'info');
      });
    }
  }

  // Mostrar notificação de atualização
  showUpdateNotification() {
    const updateCard = document.createElement('div');
    updateCard.className = 'alert alert-warning alert-dismissible fade show position-fixed';
    updateCard.style.cssText = `
      top: 20px;
      left: 20px;
      z-index: 1000;
      max-width: 300px;
    `;
    updateCard.innerHTML = `
      <strong>Atualização Disponível</strong>
      <p class="mb-2">Uma nova versão do app está disponível!</p>
      <button type="button" class="btn btn-sm btn-warning" onclick="location.reload()">
        Atualizar Agora
      </button>
    `;
    
    document.body.appendChild(updateCard);
  }

  // Mostrar toast
  showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0 position-fixed`;
    toast.style.cssText = `
      top: 20px;
      right: 20px;
      z-index: 1000;
    `;
    toast.innerHTML = `
      <div class="d-flex">
        <div class="toast-body">
          ${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    `;
    
    document.body.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
      toast.remove();
    });
  }

  // Converter VAPID key
  urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/-/g, '+')
      .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }

  // Verificar se é PWA instalado
  isPWAInstalled() {
    return window.matchMedia('(display-mode: standalone)').matches ||
           window.navigator.standalone === true;
  }

  // Adicionar CSS para animações
  addStyles() {
    const style = document.createElement('style');
    style.textContent = `
      @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
      }
      
      .pwa-installed {
        padding-top: env(safe-area-inset-top);
        padding-bottom: env(safe-area-inset-bottom);
      }
    `;
    document.head.appendChild(style);
  }
}

// Inicializar PWA quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
  window.onCristoPWA = new OnCristoPWA();
  
  // Adicionar classe se for PWA instalado
  if (window.onCristoPWA.isPWAInstalled()) {
    document.body.classList.add('pwa-installed');
  }
});

// Detectar mudanças de conectividade
window.addEventListener('load', () => {
  if ('connection' in navigator) {
    navigator.connection.addEventListener('change', () => {
      const connection = navigator.connection;
      console.log('Tipo de conexão:', connection.effectiveType);
      console.log('Velocidade:', connection.downlink, 'Mbps');
    });
  }
}); 