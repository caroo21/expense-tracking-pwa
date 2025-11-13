import uuid
from database import get_db_connection

def create_table():
    """Erstellt die 'expenses' Tabelle mit einer Verknüpfung zu 'users'."""
    conn = get_db_connection()
    cursor = conn.cursor()
    print("erstelle tabelle expenses")
        # NEU: Spalte "user_id", um die Ausgabe einem User zuzuordnen
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                expense_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                info TEXT,
                date TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
    ''')
    conn.commit()
    conn.close()

def add_expense(expense_data):
    """Fügt eine neue Ausgabe für einen bestimmten User hinzu."""
    conn = get_db_connection()
    cursor = conn.cursor()
    new_expense_id = str(uuid.uuid4())
        
    sql = '''
            INSERT INTO expenses (expense_id, user_id, amount, category, info, date)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
    values = (
            new_expense_id,
            expense_data['user_id'], # NEU: Die ID des Users wird mitgespeichert
            expense_data['amount'],
            expense_data['category'],
            expense_data['info'],
            expense_data['date']
    )
        
    cursor.execute(sql, values)
    conn.commit()
    conn.close()
        
    print(f"Neue Ausgabe mit ID {new_expense_id} für User gespeichert.")
    return new_expense_id
