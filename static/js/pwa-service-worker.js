/**
 * Progressive Web App Service Worker
 * Handles caching, offline functionality, and background sync
 */

const CACHE_NAME = 'target-capital-v1.2.0';
const OFFLINE_URL = '/offline.html';

// Files to cache for offline functionality
const CACHE_FILES = [
    '/',
    '/static/css/style.css',
    '/static/css/mobile-first.css',
    '/static/js/react-components.js',
    '/static/js/react-dashboard.js',
    '/static/js/mobile-performance.js',
    '/static/js/websocket-client.js',
    '/static/js/main.js',
    '/static/images/logo-192.png',
    '/static/images/logo-512.png',
    OFFLINE_URL
];

// API routes to cache
const API_CACHE_PATTERNS = [
    /\/api\/portfolio/,
    /\/api\/user\/profile/,
    /\/api\/market-data/
];

// Install event - cache core files
self.addEventListener('install', (event) => {
    console.log('🔧 SW: Installing service worker');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('📦 SW: Caching core files');
                return cache.addAll(CACHE_FILES);
            })
            .then(() => {
                console.log('✅ SW: Installation complete');
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('❌ SW: Installation failed', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('🚀 SW: Activating service worker');
    
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (cacheName !== CACHE_NAME) {
                            console.log('🗑️ SW: Deleting old cache', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('✅ SW: Activation complete');
                return self.clients.claim();
            })
    );
});

// Fetch event - handle network requests with caching strategies
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Skip chrome-extension and similar schemes
    if (!url.protocol.startsWith('http')) {
        return;
    }
    
    // Different strategies for different types of requests
    if (url.pathname === '/' || url.pathname.startsWith('/dashboard')) {
        event.respondWith(networkFirstStrategy(request));
    } else if (url.pathname.startsWith('/static/')) {
        event.respondWith(cacheFirstStrategy(request));
    } else if (isAPIRequest(url.pathname)) {
        event.respondWith(networkFirstWithFallbackStrategy(request));
    } else if (url.pathname.startsWith('/api/')) {
        event.respondWith(networkOnlyStrategy(request));
    } else {
        event.respondWith(networkFirstStrategy(request));
    }
});

// Network-first strategy (for HTML pages)
async function networkFirstStrategy(request) {
    try {
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.log('🌐 SW: Network failed, trying cache', request.url);
        const cachedResponse = await caches.match(request);
        
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline page for navigation requests
        if (request.mode === 'navigate') {
            return caches.match(OFFLINE_URL);
        }
        
        throw error;
    }
}

// Cache-first strategy (for static assets)
async function cacheFirstStrategy(request) {
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
        return cachedResponse;
    }
    
    try {
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.log('❌ SW: Failed to fetch asset', request.url);
        throw error;
    }
}

// Network-first with fallback strategy (for API data)
async function networkFirstWithFallbackStrategy(request) {
    try {
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.log('🔄 SW: API network failed, trying cache', request.url);
        const cachedResponse = await caches.match(request);
        
        if (cachedResponse) {
            // Add offline indicator to cached API responses
            const response = cachedResponse.clone();
            const data = await response.json();
            data._offline = true;
            data._cachedAt = new Date().toISOString();
            
            return new Response(JSON.stringify(data), {
                headers: {
                    'Content-Type': 'application/json',
                    'X-Served-By': 'ServiceWorker'
                }
            });
        }
        
        // Return fallback data for critical API endpoints
        return getFallbackAPIResponse(request);
    }
}

// Network-only strategy (for real-time data)
async function networkOnlyStrategy(request) {
    try {
        return await fetch(request);
    } catch (error) {
        console.log('❌ SW: Real-time API failed', request.url);
        throw error;
    }
}

// Check if request is for cached API data
function isAPIRequest(pathname) {
    return API_CACHE_PATTERNS.some(pattern => pattern.test(pathname));
}

// Provide fallback data for critical API endpoints when offline
function getFallbackAPIResponse(request) {
    const url = new URL(request.url);
    
    // Portfolio fallback data
    if (url.pathname.includes('/api/portfolio')) {
        return new Response(JSON.stringify({
            portfolio: {
                totalValue: 0,
                todayChange: 0,
                holdings: []
            },
            _offline: true,
            _fallback: true,
            message: 'Offline - showing cached data'
        }), {
            headers: { 'Content-Type': 'application/json' }
        });
    }
    
    // User profile fallback
    if (url.pathname.includes('/api/user/profile')) {
        return new Response(JSON.stringify({
            user: {
                name: 'User',
                email: 'user@example.com'
            },
            _offline: true,
            _fallback: true
        }), {
            headers: { 'Content-Type': 'application/json' }
        });
    }
    
    // Generic fallback
    return new Response(JSON.stringify({
        error: 'Service unavailable offline',
        _offline: true,
        _fallback: true
    }), {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
    });
}

// Background sync for form submissions
self.addEventListener('sync', (event) => {
    console.log('🔄 SW: Background sync triggered', event.tag);
    
    if (event.tag === 'portfolio-sync') {
        event.waitUntil(syncPortfolioData());
    } else if (event.tag === 'user-actions') {
        event.waitUntil(syncUserActions());
    }
});

// Sync portfolio data when back online
async function syncPortfolioData() {
    try {
        console.log('📊 SW: Syncing portfolio data');
        
        // Get pending portfolio updates from IndexedDB
        const pendingUpdates = await getPendingPortfolioUpdates();
        
        // OAUTH DEBUG: Skip portfolio sync API calls temporarily
        console.log('🔄 SW: Skipping portfolio sync during OAuth debug');
        return;
    } catch (error) {
        console.error('❌ SW: Portfolio sync failed', error);
        throw error;
    }
}

// Sync user actions when back online
async function syncUserActions() {
    try {
        console.log('👤 SW: Syncing user actions');
        
        const pendingActions = await getPendingUserActions();
        
        for (const action of pendingActions) {
            try {
                await fetch('/api/user/actions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(action)
                });
                
                await removePendingAction(action.id);
                console.log('✅ SW: User action synced', action.id);
            } catch (error) {
                console.log('❌ SW: Failed to sync action', action.id, error);
            }
        }
    } catch (error) {
        console.error('❌ SW: User actions sync failed', error);
        throw error;
    }
}

// IndexedDB helpers for offline storage
async function getPendingPortfolioUpdates() {
    // Simplified - in production, use proper IndexedDB implementation
    return [];
}

async function removePendingUpdate(id) {
    // Simplified - in production, use proper IndexedDB implementation
    console.log('Removing pending update:', id);
}

async function getPendingUserActions() {
    // Simplified - in production, use proper IndexedDB implementation
    return [];
}

async function removePendingAction(id) {
    // Simplified - in production, use proper IndexedDB implementation
    console.log('Removing pending action:', id);
}

// Push notification handling
self.addEventListener('push', (event) => {
    console.log('🔔 SW: Push notification received');
    
    let options = {
        body: 'You have new market updates',
        icon: '/static/images/logo-192.png',
        badge: '/static/images/logo-96.png',
        tag: 'market-update',
        renotify: true,
        requireInteraction: false,
        actions: [
            { action: 'view', title: 'View Dashboard' },
            { action: 'dismiss', title: 'Dismiss' }
        ]
    };
    
    if (event.data) {
        try {
            const data = event.data.json();
            options.body = data.message || options.body;
            options.tag = data.tag || options.tag;
            options.data = data;
        } catch (error) {
            console.log('Failed to parse push data');
        }
    }
    
    event.waitUntil(
        self.registration.showNotification('Target Capital', options)
    );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
    console.log('🔔 SW: Notification clicked', event.action);
    
    event.notification.close();
    
    if (event.action === 'view') {
        event.waitUntil(
            clients.openWindow('/dashboard')
        );
    } else if (event.action === 'dismiss') {
        // Just close the notification
        return;
    } else {
        // Default action - open app
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Periodic background sync (if supported)
self.addEventListener('periodicsync', (event) => {
    console.log('⏰ SW: Periodic sync triggered', event.tag);
    
    if (event.tag === 'portfolio-refresh') {
        event.waitUntil(refreshPortfolioCache());
    }
});

// Refresh portfolio cache in background
async function refreshPortfolioCache() {
    try {
        // OAUTH DEBUG: Skip portfolio API call temporarily
        console.log('🔄 SW: Skipping portfolio cache refresh during OAuth debug');
        return;
    } catch (error) {
        console.log('❌ SW: Failed to refresh portfolio cache', error);
    }
}

console.log('🚀 SW: Service worker script loaded');