# Test 1: User erstellen
from user_model import create_table, add_user, verify_user

create_table()
user_id = add_user("testuser", "test@example.com", "meinpasswort123")
print(f"User ID: {user_id}")

# Test 2: Login testen
user = verify_user("testuser", "meinpasswort123")
print(f"Login erfolgreich: {user}")

# Test 3: Falsches Passwort
user = verify_user("testuser", "falschespasswort")
print(f"Login fehlgeschlagen: {user}")  # Sollte None sein

# Test 4: Expense mit user_id hinzufügen
from expense_model import add_expense, create_table
create_table()
expense_data = {
    'user_id': "481037f8-ec51-4ded-b7e8-1c94aecd5fdf",
    'amount': 50.0,
    'category': 'Essen',
    'info': 'Pizza',
    'date': '2025-01-15'
}
add_expense(expense_data)
