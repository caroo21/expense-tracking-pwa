import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import user_model

from models import user_model, expense_model, analytics_model
from datetime import date, timedelta

# Erstelle User und Expenses
user_id = user_model.add_user("analyticsuser", "analytics@example.com", "password123")

if user_id:
    # Füge mehrere Ausgaben hinzu
    expenses = [
        {'user_id': user_id, 'amount': 50.00, 'category': 'Food', 'info': 'Groceries', 'date': str(date.today())},
        {'user_id': user_id, 'amount': 30.00, 'category': 'Transport', 'info': 'Bus', 'date': str(date.today())},
        {'user_id': user_id, 'amount': 20.00, 'category': 'Food', 'info': 'Restaurant', 'date': str(date.today())},
    ]
    
    for exp in expenses:
        expense_model.add_expense(exp)
    
    print("✅ Test-Daten erstellt\n")
    
    # Test Summary
    start = str(date.today() - timedelta(days=7))
    end = str(date.today())
    summary = analytics_model.get_summary_for_period(user_id, start, end)
    print(f"📊 Summary: {summary}\n")
    
    # Test Categories
    categories = analytics_model.get_expenses_by_category(user_id)
    print(f"📈 By Category: {categories}")
