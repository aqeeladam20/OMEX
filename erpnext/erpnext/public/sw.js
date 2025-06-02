// OMEX ERP Service Worker - Simple PWA Setup
console.log('OMEX ERP Service Worker loading...');

// Install event - just activate immediately
self.addEventListener('install', (event) => {
    console.log('OMEX ERP Service Worker installing...');
    self.skipWaiting();
});

// Activate event - take control immediately
self.addEventListener('activate', (event) => {
    console.log('OMEX ERP Service Worker activated');
    event.waitUntil(self.clients.claim());
});

// Push notification event
self.addEventListener('push', (event) => {
    console.log('Push notification received:', event);
    
    const options = {
        body: event.data ? event.data.text() : 'New notification from OMEX ERP',
        icon: '/assets/erpnext/images/omex-icon-192.png',
        badge: '/assets/erpnext/images/omex-icon-96.png',
        vibrate: [200, 100, 200],
        data: {
            url: '/app'
        },
        actions: [
            {
                action: 'open',
                title: 'Open OMEX ERP',
                icon: '/assets/erpnext/images/omex-icon-96.png'
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification('OMEX ERP', options)
    );
});

// Notification click event
self.addEventListener('notificationclick', (event) => {
    console.log('Notification clicked:', event);
    
    event.notification.close();

    if (event.action === 'open' || !event.action) {
        event.waitUntil(
            clients.openWindow(event.notification.data.url || '/app')
        );
    }
});

// Handle app shortcuts from manifest
self.addEventListener('notificationclick', (event) => {
    if (event.action === 'scan-barcode') {
        event.waitUntil(
            clients.openWindow('/app/item?scan=true')
        );
    } else if (event.action === 'ai-assistant') {
        event.waitUntil(
            clients.openWindow('/app?ai=true')
        );
    } else if (event.action === 'sales') {
        event.waitUntil(
            clients.openWindow('/app/selling')
        );
    } else if (event.action === 'inventory') {
        event.waitUntil(
            clients.openWindow('/app/stock')
        );
    }
});

console.log('OMEX ERP Service Worker loaded successfully'); 