// ========================================
// IndexedDB für Offline-Expenses
// ========================================

console.log('🗄️ IndexedDB Script geladen');

let db;
const DB_NAME = 'ExpenseTrackerDB';
const DB_VERSION = 1;
const STORE_NAME = 'pendingExpenses';

// ========================================
// Datenbank initialisieren
// ========================================

function initDB() {
  return new Promise((resolve, reject) => {
    console.log('🔄 Öffne IndexedDB...');
    
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    
    // Fehler beim Öffnen
    request.onerror = () => {
      console.error('❌ IndexedDB Fehler:', request.error);
      reject(request.error);
    };
    
    // Erfolgreich geöffnet
    request.onsuccess = () => {
      db = request.result;
      console.log('✅ IndexedDB geöffnet');
      resolve(db);
    };
    
    // Erste Installation oder Version-Update
    request.onupgradeneeded = (event) => {
      console.log('🔧 IndexedDB wird eingerichtet...');
      const db = event.target.result;
      
      // Erstelle Object Store (wie eine Tabelle)
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        const objectStore = db.createObjectStore(STORE_NAME, { 
          keyPath: 'id',
          autoIncrement: true 
        });
        
        // Index für Timestamp (zum Sortieren)
        objectStore.createIndex('timestamp', 'timestamp', { unique: false });
        
        console.log('✅ Object Store erstellt:', STORE_NAME);
      }
    };
  });
}

// ========================================
// Expense lokal speichern
// ========================================

function saveExpenseLocally(expenseData) {
  return new Promise((resolve, reject) => {
    console.log('💾 Speichere Expense lokal:', expenseData);
    
    // Füge Metadaten hinzu
    const expense = {
      ...expenseData,
      timestamp: Date.now(),
      synced: false
    };
    
    const transaction = db.transaction([STORE_NAME], 'readwrite');
    const store = transaction.objectStore(STORE_NAME);
    const request = store.add(expense);
    
    request.onsuccess = () => {
      console.log('✅ Expense lokal gespeichert, ID:', request.result);
      resolve(request.result);
    };
    
    request.onerror = () => {
      console.error('❌ Fehler beim Speichern:', request.error);
      reject(request.error);
    };
  });
}

// ========================================
// Alle pending Expenses holen
// ========================================

function getPendingExpenses() {
  return new Promise((resolve, reject) => {
    console.log('📋 Hole pending Expenses...');
    
    const transaction = db.transaction([STORE_NAME], 'readonly');
    const store = transaction.objectStore(STORE_NAME);
    const request = store.getAll();
    
    request.onsuccess = () => {
      const expenses = request.result.filter(exp => !exp.synced);
      console.log(`✅ ${expenses.length} pending Expense(s) gefunden`);
      resolve(expenses);
    };
    
    request.onerror = () => {
      console.error('❌ Fehler beim Laden:', request.error);
      reject(request.error);
    };
  });
}

// ========================================
// Expense als synchronisiert markieren
// ========================================

function markAsSynced(id) {
  return new Promise((resolve, reject) => {
    console.log('✓ Markiere Expense als synced:', id);
    
    const transaction = db.transaction([STORE_NAME], 'readwrite');
    const store = transaction.objectStore(STORE_NAME);
    const request = store.get(id);
    
    request.onsuccess = () => {
      const expense = request.result;
      expense.synced = true;
      
      const updateRequest = store.put(expense);
      updateRequest.onsuccess = () => {
        console.log('✅ Expense markiert als synced');
        resolve();
      };
    };
    
    request.onerror = () => {
      console.error('❌ Fehler beim Markieren:', request.error);
      reject(request.error);
    };
  });
}

// ========================================
// Expense löschen
// ========================================

function deleteExpense(id) {
  return new Promise((resolve, reject) => {
    console.log('🗑️ Lösche Expense:', id);
    
    const transaction = db.transaction([STORE_NAME], 'readwrite');
    const store = transaction.objectStore(STORE_NAME);
    const request = store.delete(id);
    
    request.onsuccess = () => {
      console.log('✅ Expense gelöscht');
      resolve();
    };
    
    request.onerror = () => {
      console.error('❌ Fehler beim Löschen:', request.error);
      reject(request.error);
    };
  });
}

// ========================================
// Beim Laden initialisieren
// ========================================
 
window.addEventListener('load', async () => {
  try {
    await initDB();
    
    // Zeige Anzahl pending Expenses
    const pending = await getPendingExpenses();
    if (pending.length > 0) {
      console.log(`⚠️ ${pending.length} Expense(s) warten auf Synchronisation`);
    }
  } catch (error) {
    console.error('❌ IndexedDB Initialisierung fehlgeschlagen:', error);
  }
});

console.log('✅ IndexedDB Script komplett geladen');


// ========================================
// Message Listener für Service Worker
// ========================================
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.addEventListener('message', (event) => {
    console.log('📨 Message vom Service Worker erhalten:', event.data);
    
    if (event.data.type === 'SAVE_OFFLINE_EXPENSE') {
      // Speichere in IndexedDB
      const expenseData = event.data.data;
      
      saveExpenseLocally(expenseData)
        .then(() => {
          console.log('✅ Offline-Expense in IndexedDB gespeichert');
          
          // Optional: Zeige Benachrichtigung
          showNotification('Offline gespeichert', 'Wird synchronisiert sobald du online bist.');
        })
        .catch(err => {
          console.error('❌ Fehler beim Speichern in IndexedDB:', err);
        });
    }
  });
}

// Hilfsfunktion für Benachrichtigungen (optional)
function showNotification(title, message) {
  // Nutze dein bestehendes Notification-System
  // Oder einfach console.log
  console.log(`🔔 ${title}: ${message}`);
}