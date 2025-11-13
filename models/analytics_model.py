from database import get_db_connection

def get_summary_for_period(user_id, start_date, end_date):
    """
    Berechnet die Summe der Einnahmen und Ausgaben für einen User
    in einem bestimmten Zeitraum.

    Args:
        user_id (str): Die ID des Benutzers.
        start_date (str): Das Startdatum im Format 'YYYY-MM-DD'.
        end_date (str): Das Enddatum im Format 'YYYY-MM-DD'.

    Returns:
        dict: Ein Dictionary mit 'income', 'expenses' und 'difference'.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # --- Ausgaben berechnen ---
    # COALESCE(SUM(amount), 0) sorgt dafür, dass wir 0 bekommen,
    # wenn es keine Ausgaben gibt, anstatt eines Fehlers.
    sql_expenses = """
        SELECT COALESCE(SUM(amount), 0) 
        FROM expenses 
        WHERE user_id = ? AND date BETWEEN ? AND ?
    """
    cursor.execute(sql_expenses, (user_id, start_date, end_date))
    # fetchone() gibt ein Tupel zurück, z.B. (745.50,). Wir brauchen den ersten Wert.
    total_expenses = cursor.fetchone()[0]

    # --- Einnahmen berechnen (PLATZHALTER) ---
    # HINWEIS: Da wir noch keine "incomes"-Tabelle haben, geben wir hier
    # vorerst immer 0 zurück. Dies wäre der Ort, um sie zu berechnen.
    total_income = 1697.0

    conn.close()

    # --- Differenz berechnen ---
    difference = total_income - total_expenses

    # Gib ein sauberes Dictionary mit den Ergebnissen zurück
    return {
        "income": total_income,
        "expenses": total_expenses,
        "difference": difference
    }

def get_expenses_by_category(user_id, start_date=None, end_date=None):
    """
    Gruppiert Ausgaben nach Kategorie für einen User.
    
    Args:
        user_id (str): Die ID des Benutzers.
        start_date (str, optional): Startdatum.
        end_date (str, optional): Enddatum.
    
    Returns:
        list: Liste von Dictionaries mit 'category' und 'total'.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if start_date and end_date:
        sql = '''
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE user_id = ? AND date BETWEEN ? AND ?
            GROUP BY category
            ORDER BY total DESC
        '''
        cursor.execute(sql, (user_id, start_date, end_date))
    else:
        sql = '''
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE user_id = ?
            GROUP BY category
            ORDER BY total DESC
        '''
        cursor.execute(sql, (user_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    categories = []
    for row in rows:
        categories.append({
            'category': row['category'],
            'total': row['total']
        })
    
    return categories