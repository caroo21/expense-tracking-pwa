// ========================================
// Automatische Synchronisation
// ========================================

console.log('🔄 Sync Script geladen');

// ========================================
// Alle pending Expenses synchronisieren
// ========================================

async function syncPendingExpenses() {
  // Prüfe ob online
  if (!navigator.onLine) {
    console.log('⏸️ Offline - Sync übersprungen');
    return;
  }

  const token = localStorage.getItem('auth_token');
  if (!token) {
    console.error('❌ Kein Token vorhanden - Sync abgebrochen');
    // Optional: Redirect zu Login
    window.location.href = '/login.html';
    return;
  }
  try {
    console.log('🔄 Starte Synchronisation...');
    
    // Hole alle pending Expenses
    const pendingExpenses = await getPendingExpenses();
    
    if (pendingExpenses.length === 0) {
      console.log('✅ Keine pending Expenses zum synchronisieren');
      return;
    }
    
    console.log(`📤 Synchronisiere ${pendingExpenses.length} Expense(s)...`);
    
    let successCount = 0;
    let failCount = 0;
    
    // Sende jede Expense einzeln
    for (const expense of pendingExpenses) {
      try {
        console.log(`📤 Sende Expense ID ${expense.id}:`, expense);
        
        // Entferne Metadaten (id, timestamp, synced)
        const { id, timestamp, synced, ...cleanExpense } = expense;
        
        // Sende an Server
        const response = await fetch('/api', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify(cleanExpense)
        });
        
        if (response.status === 401) {
          console.error('❌ Token ungültig - Sync abgebrochen');
          // Lösche ungültigen Token
          localStorage.removeItem('auth_token');
          localStorage.removeItem('user');
          // Redirect zu Login
          window.location.href = '/login.html';
          return;
        }
        if (response.ok) {
          const data = await response.json();
          console.log(`✅ Expense ${id} erfolgreich synchronisiert:`, data);
          
          // Lösche aus IndexedDB
          await deleteExpense(id);
          successCount++;
          
        } else {
          console.error(`❌ Server-Fehler für Expense ${id}:`, response.status);
          failCount++;
        }
        
      } catch (error) {
        console.error(`❌ Sync fehlgeschlagen für Expense ${expense.id}:`, error);
        failCount++;
      }
    }
    
    // Zusammenfassung
    console.log(`✅ Synchronisation abgeschlossen: ${successCount} erfolgreich, ${failCount} fehlgeschlagen`);
    
    // Zeige Notification
    if (successCount > 0) {
      showNotification(`✅ ${successCount} Expense(s) synchronisiert`, 'success');
    }
    
    if (failCount > 0) {
      showNotification(`⚠️ ${failCount} Expense(s) konnten nicht synchronisiert werden`, 'warning');
    }
    
    // Dashboard neu laden (falls vorhanden)
    if (typeof loadDashboard === 'function') {
      console.log('🔄 Lade Dashboard neu...');
      loadDashboard();
    }
    
  } catch (error) {
    console.error('❌ Fehler bei der Synchronisation:', error);
  }
}

// ========================================
// Online Event - Automatische Sync
// ========================================

window.addEventListener('online', async () => {
  console.log('🟢 Online - starte automatische Synchronisation');
  
  // Warte kurz (damit Verbindung stabil ist)
  setTimeout(async () => {
    await syncPendingExpenses();
  }, 1000);
});

// ========================================
// Beim Laden - Sync wenn online
// ========================================

window.addEventListener('load', async () => {
  // Warte bis IndexedDB initialisiert ist
  await new Promise(resolve => setTimeout(resolve, 500));
  
  if (navigator.onLine) {
    console.log('🟢 Seite geladen (online) - prüfe pending Expenses');
    
    const pending = await getPendingExpenses();
    
    if (pending.length > 0) {
      console.log(`⚠️ ${pending.length} pending Expense(s) gefunden - starte Sync`);
      await syncPendingExpenses();
    }
  }
});

// ========================================
// Manueller Sync-Button (optional)
// ========================================

function createSyncButton() {
  const button = document.createElement('button');
  button.id = 'manual-sync-btn';
  button.textContent = '🔄 Jetzt synchronisieren';
  button.style.cssText = `
    position: fixed;
    bottom: 20px;
    left: 20px;
    padding: 12px 20px;
    background: #2196F3;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-weight: bold;
    box-shadow: 0 2px 5px rgba(0,0,0,0.3);
    z-index: 10000;
    display: none;
  `;
  
  button.onclick = async () => {
    console.log('🔘 Manueller Sync-Button geklickt');
    button.disabled = true;
    button.textContent = '⏳ Synchronisiere...';
    
    await syncPendingExpenses();
    
    button.disabled = false;
    button.textContent = '🔄 Jetzt synchronisieren';
    
    // Verstecke Button wenn keine pending Expenses mehr
    const pending = await getPendingExpenses();
    if (pending.length === 0) {
      button.style.display = 'none';
    }
  };
  
  document.body.appendChild(button);
  return button;
}

// Zeige Sync-Button wenn pending Expenses vorhanden
window.addEventListener('load', async () => {
  await new Promise(resolve => setTimeout(resolve, 600));
  
  const pending = await getPendingExpenses();
  
  if (pending.length > 0) {
    const syncBtn = document.getElementById('manual-sync-btn') || createSyncButton();
    syncBtn.style.display = 'block';
    
    // Update Button-Text mit Anzahl
    syncBtn.textContent = `🔄 ${pending.length} Expense(s) synchronisieren`;
  }
});

console.log('✅ Sync Script komplett geladen');
