// ========================================
// Offline-Indikator
// ========================================

// Banner erstellen
function createOfflineBanner() {
  const banner = document.createElement('div');
  banner.id = 'offline-banner';
  banner.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    padding: 10px;
    text-align: center;
    font-weight: bold;
    z-index: 9999;
    transition: all 0.3s ease;
    display: none;
  `;
  document.body.appendChild(banner);
  return banner;
}

// Funktion um Navigation zu verschieben
function adjustNavigation(show) {
  const header = document.querySelector('header');
  
  if (!header) {
    console.warn('Header nicht gefunden!');
    return;
  }
  
  if (show) {
    const banner = document.getElementById('offline-banner');
    if (banner) {
      const bannerHeight = banner.offsetHeight;
      console.log('📏 Banner Höhe:', bannerHeight);
      header.style.top = `${bannerHeight}px`;
      header.style.transition = 'margin-top 0.3s ease';
    }
  } else {
    header.style.top = '0';
  }
}


// Banner anzeigen
function showBanner(message, type) {
  const banner = document.getElementById('offline-banner') || createOfflineBanner();
  
  // Farben je nach Typ
  const colors = {
    offline: { bg: '#f44336', text: '#fff' },  // Rot
    online: { bg: '#4CAF50', text: '#fff' },   // Grün
    syncing: { bg: '#FF9800', text: '#fff' }   // Orange
  };
  
  const color = colors[type] || colors.offline;
  
  banner.textContent = message;
  banner.style.backgroundColor = color.bg;
  banner.style.color = color.text;
  banner.style.display = 'block';
  banner.style.margin = 28;

  setTimeout(() => {
    adjustNavigation(true);
  }, 10);
}

// Banner verstecken
function hideBanner() {
  const banner = document.getElementById('offline-banner');
  if (banner) {
    banner.style.display = 'none';
  }
  adjustNavigation(false);
}

// ========================================
// Online/Offline Events
// ========================================

window.addEventListener('online', () => {
  console.log('🟢 Online');
  showBanner('✅ Wieder online!', 'online');
  
  // Banner nach 3 Sekunden ausblenden
  setTimeout(() => {
    hideBanner();
  }, 2000);
});

window.addEventListener('offline', () => {
  console.log('🔴 Offline');
  showBanner('⚠️ Offline-Modus - Daten werden lokal gespeichert', 'offline');
});

// ========================================
// Beim Laden prüfen
// ========================================

window.addEventListener('load', () => {
  if (!navigator.onLine) {
    console.log('🔴 Seite geladen im Offline-Modus');
    showBanner('⚠️ Offline-Modus!!', 'offline');
  }
});
