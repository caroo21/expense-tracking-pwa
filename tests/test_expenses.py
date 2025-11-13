import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import user_model

from models import user_model, expense_model
from datetime import date

# Erstelle zuerst einen User (oder nutze eine existierende ID)
print("📝 Erstelle Test-User...")
user_id = user_model.add_user("expenseuser", "expense@example.com", "password123")

if user_id:
    print(f"✅ User erstellt: {user_id}")
    
    # Test: Expense hinzufügen
    print("\n💰 Füge Ausgabe hinzu...")
    expense_data = {
        'user_id': user_id,
        'amount': 25.50,
        'category': 'Food',
        'info': 'Lunch',
        'date': str(date.today())
    }
    
    expense_id = expense_model.add_expense(expense_data)
    print(f"✅ Ausgabe erstellt mit ID: {expense_id}")
else:
    print("❌ Konnte keinen User erstellen")
