document.addEventListener('DOMContentLoaded', function() {
    // Simulate loading delay (or wait for your actual data to load)
    setTimeout(() => {
        document.getElementById('loading-spinner').classList.add('hidden');
        document.getElementById('dashboard-content').classList.remove('hidden');
    }, 1200); // Shows spinner for 1.5 seconds
}); 
 
 // JavaScript für das mobile Menü
        const menuBtn = document.getElementById('menu-btn');
        const mobileMenu = document.getElementById('mobile-menu');
        menuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });

    // WICHTIG: Füge hier die User-ID ein, die du beim Erstellen des Test-Users kopiert hast.
    const USER_ID = '321fd1f2-0a9c-476a-93ba-c6f16fa56354';

    // Diese Funktion wird ausgeführt, sobald die HTML-Seite komplett geladen ist.
    document.addEventListener('DOMContentLoaded', () => {
        fetchDashboardData();
    });

    // Funktion, um die Daten vom Backend zu holen
    async function fetchDashboardData() {
        const token = getToken();
        // Baue die URL mit dem Query-Parameter zusammen
        const url = `/api/dashboard`;

        try {
            const response = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${token}` // ← NEU
                }
            });
            if (response.status === 401) { // ← NEU
                logout();
                console.log("toekn nicht gut")
                return;
            }
            if (!response.ok) {
                console.error("Fehler beim Abrufen der Dashboard-Daten:", response.statusText);
                return;
            }
            const data = await response.json();
            console.log("Daten vom Backend erhalten:", data); // Zum Testen

            // Rufe die Funktion auf, um das HTML zu aktualisieren
            renderDashboard(data);

        } catch (error) {
            console.error("Netzwerkfehler:", error);
        }
    }

    // Funktion, um die HTML-Elemente mit den neuen Daten zu füllen
    function renderDashboard(data) {
        // Aktualisiere "Dieser Monat"
        updateSummaryBlock('current-month', data.this_month);
        
        // Aktualisiere die Detail-Karten
        updateSummaryBlock('last-month', data.last_month);

        updateSummaryBlock('before-last-month', data.month_before_last);

        updateSummaryBlock('this-year', data.this_year)

        updateSummaryBlock('same-month-last-year', data.same_month_last_year)
        // FÜGE HIER DIE AUFRUFE FÜR 'month_before_last' UND 'same_month_last_year' HINZU
        // updateSummaryBlock('month-before-last', data.month_before_last);
        // updateSummaryBlock('same-month-last-year', data.same_month_last_year);
    }

    // Eine Hilfsfunktion, um Codedoppelung zu vermeiden
    function updateSummaryBlock(prefix, summaryData) {
        const incomeEl = document.getElementById(`${prefix}-income`);
        const expensesEl = document.getElementById(`${prefix}-expenses`);
        const differenceEl = document.getElementById(`${prefix}-difference`);

        if (incomeEl) incomeEl.textContent = `€ ${summaryData.income.toFixed(2)}`;
        if (expensesEl) expensesEl.textContent = `€ ${summaryData.expenses.toFixed(2)}`;
        
        if (differenceEl) {
            // Formatierung der Differenz mit Vorzeichen
            const formattedDiff = `${summaryData.difference > 0 ? '+' : ''} € ${summaryData.difference.toFixed(2)}`;
            differenceEl.textContent = formattedDiff;

            // Klassen für die Farbe setzen/entfernen
            differenceEl.classList.remove('text-green-600', 'text-red-600');
            if (summaryData.difference >= 0) {
                differenceEl.classList.add('text-green-600');
            } else {
                differenceEl.classList.add('text-red-600');
            }
        }
    }
