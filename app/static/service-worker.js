importScripts("https://js.pusher.com/beams/service-worker.js");

// For PWA: Handling fetch requests to serve assets (without caching interference)
self.addEventListener('fetch', (event) => {
    event.respondWith(
      // Just pass through the request; no caching of dynamic assets needed
      fetch(event.request).catch((err) => {
        console.log("Fetch failed; returning offline page", err);
        // Optionally, serve a fallback page if offline
        return caches.match('/offline.html');
      })
    );
  });
  
  // Optional: Handle other events as needed, e.g., notification click events
  self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    
    event.waitUntil(
      clients.openWindow('/').then(() => {
        // You can redirect to a specific page after clicking the notification
      })
    );
  });