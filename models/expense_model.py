import uuid
from database import get_db_connection, get_db_type, release_db_connection

def create_table():
    """Erstellt expense tabelle mit Verknüpfung zu users"""
    conn = get_db_connection()
    cursor = conn.cursor()
    print("erstelle tablle expenses")

    if get_db_type() == 'postgresql':
        cursor.execute('''
                        CREATE TABLE IF NOT EXISTS expenses(
                        expense_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        amount DECIMAL(10, 2) NOT NULL,
                        category TEXT NOT NULL,
                        info TEXT,
                        date DATE NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
                       )
                       ''')
    else:
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
    release_db_connection(conn)

def add_expense(expense_data):
    """fügt ausgabe für bestimmten user hinzu"""
    conn = get_db_connection()
    cursor = conn.cursor()
    new_expense_id = str(uuid.uuid4())

    placeholder = '%s' if get_db_type() == 'postgresql' else '?'

    sql = f'''
            INSERT INTO expenses(expense_id, user_id, amount, category, info, date)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        '''
    values = (new_expense_id,
        expense_data['user_id'],
        expense_data['amount'],
        expense_data['category'],
        expense_data['info'],
        expense_data['date']
    )

    cursor.execute(sql, values)
    conn.commit()
    release_db_connection(conn)

    print(F"neue Ausgabe mit ID {new_expense_id} gespeichert")

    return new_expense_id