const CACHE_NAME = 'eazyebooks-cache-v1';
const urlsToCache = [
    '/',
    '/offline',
    '/static/css/home.css',
    '/static/css/responsive.css',
    '/static/css/added-to-app.css',
    '/static/css/get-started.css',
    '/static/css/profile-settings.css',
    '/static/css/purchase_history.css',
    '/static/js/service-worker.js',
    '/static/images/general/preloader.mp4',
    '/static/images/general/1277.jpg',
    '/static/icons/EEappicon192.png',
    '/static/icons/EEappicon512.png'
];

self.addEventListener("install", event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log("Opened cache");
                return cache.addAll(urlsToCache);
            })
    );
});

// Fetch event - Serves files from cache when offline
self.addEventListener("fetch", event => {
    event.respondWith(
        fetch(event.request).catch(() => 
            caches.match(event.request).then(response => response || caches.match("/offline"))
        )
    );
});

// Activate event - Clears old caches when updating
self.addEventListener("activate", event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cache => {
                    if (cache !== CACHE_NAME) {
                        console.log("Deleting old cache:", cache);
                        return caches.delete(cache);
                    }
                })
            );
        })
    );
});
