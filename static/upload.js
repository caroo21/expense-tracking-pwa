// JavaScript zum Umschalten des mobilen Menüs
        const menuBtn = document.getElementById('menu-btn');
        const mobileMenu = document.getElementById('mobile-menu');

        menuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });

        document.addEventListener('DOMContentLoaded', (event) => {
            const now = new Date();
            // Zeitverschiebung der Zeitzone berücksichtigen
            now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
            // In das richtige Format für datetime-local konvertieren (YYYY-MM-DDTHH:mm)
            const formattedDateTime = now.toISOString().slice(0, 16);
            document.getElementById('date').value = formattedDateTime;
        });

        const form = document.getElementById('expense-form');
        const formMessage = document.getElementById('form-message');

        form.addEventListener('submit', async function(event){
            event.preventDefault()
            const amount = document.getElementById("amount").value
            const category = document.getElementById("category").value
            const info = document.getElementById("info").value
            const date = document.getElementById("date").value
            const token = getToken();

            if (!amount || !category ) {
                formMessage.textContent = `Please complete all fields!`
                return
            }

            const formData = {
                amount: amount,
                category: category,
                info: info,
                date: date,
            }
            try{
                formMessage.textContent = ""
                const response = await fetch("/api", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`
                    },
                    body: JSON.stringify(formData),
                })
                if (response.status === 401) { // ← NEU: Token ungültig
                    logout();
                    console.log("token ungültig")
                    return;
                }
                if (response.ok) {
                    form.reset()
                    formMessage.textContent = `your expense was saved successfully`;
                    const now = new Date();
                    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
                    document.getElementById('date').value = now.toISOString().slice(0, 16);
                } else {
                    formMessage.textContent = `Fehler vom Server. Bitte erneut versuchen.`
                    console.error("Server Error:", response.statusText)
                }
            }catch (error) {
                    console.log('⚠️ Konnte nicht online speichern:', error.message);
                formMessage.textContent = `Netzwerkfehler! Konnte den Server nicht erreichen.`
                console.error("Error:", error)
                try {
      const id = await saveExpenseLocally(expenseData);
      console.log('✅ Expense offline gespeichert, ID:', id);
      
      showNotification('💾 Offline gespeichert - wird später synchronisiert', 'warning');
      
      // Optional: Formular trotzdem zurücksetzen
      return { status: 'pending', id: id };
      
    } catch (dbError) {
      console.error('❌ Fehler beim lokalen Speichern:', dbError);
      showNotification('❌ Fehler beim Speichern', 'error');
      throw dbError;
    }
            }
        })