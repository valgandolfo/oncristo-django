const CACHE_NAME = 'on-cristo-v1.0.1';
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/js/app.js',
  '/static/img/catedral.jpg',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png',
  '/avisos-publico/',
  '/horarios-missas/',
  '/eventos-publico/',
  '/paroquia-info/',
  '/liturgia-diaria/',
  '/aniversariantes/'
];

// Instalação do Service Worker
self.addEventListener('install', (event) => {
  console.log('Service Worker instalando...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Cache aberto');
        // Adicionar URLs ao cache uma por vez para melhor tratamento de erros
        return Promise.allSettled(
          urlsToCache.map(url => 
            cache.add(url).catch(error => {
              console.warn(`Falha ao cachear ${url}:`, error);
              return null;
            })
          )
        );
      })
      .then(() => {
        console.log('Service Worker instalado com sucesso');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('Erro na instalação do Service Worker:', error);
      })
  );
});

// Ativação do Service Worker
self.addEventListener('activate', (event) => {
  console.log('Service Worker ativando...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Removendo cache antigo:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('Service Worker ativado');
      return self.clients.claim();
    })
  );
});

// Interceptação de requisições
self.addEventListener('fetch', (event) => {
  // Ignorar requisições não-GET
  if (event.request.method !== 'GET') {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Retorna do cache se disponível
        if (response) {
          return response;
        }

        // Se não estiver no cache, busca da rede
        return fetch(event.request)
          .then((response) => {
            // Verifica se a resposta é válida
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // Clona a resposta para armazenar no cache
            const responseToCache = response.clone();

            caches.open(CACHE_NAME)
              .then((cache) => {
                cache.put(event.request, responseToCache);
              })
              .catch(error => {
                console.warn('Erro ao salvar no cache:', error);
              });

            return response;
          })
          .catch((error) => {
            console.warn('Erro na requisição:', error);
            // Se offline e não estiver no cache, retorna página offline
            if (event.request.destination === 'document') {
              return caches.match('/offline.html');
            }
            // Para outros recursos, retorna uma resposta vazia
            return new Response('', { status: 404 });
          });
      })
  );
});

// Sincronização em background
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    console.log('Sincronização em background iniciada');
    event.waitUntil(doBackgroundSync());
  }
});

// Notificações push
self.addEventListener('push', (event) => {
  console.log('Push notification recebida');
  
  const options = {
    body: event.data ? event.data.text() : 'Nova notificação da paróquia',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/icon-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'Ver mais',
        icon: '/static/icons/icon-96x96.png'
      },
      {
        action: 'close',
        title: 'Fechar',
        icon: '/static/icons/icon-96x96.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('On Cristo - Paróquia', options)
  );
});

// Clique em notificação
self.addEventListener('notificationclick', (event) => {
  console.log('Notificação clicada');
  
  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    );
  } else if (event.action === 'close') {
    // Apenas fecha a notificação
  } else {
    // Clique padrão
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Função de sincronização em background
async function doBackgroundSync() {
  try {
    console.log('Executando sincronização em background...');
    // Aqui você pode adicionar lógica de sincronização
  } catch (error) {
    console.error('Erro na sincronização:', error);
  }
} 