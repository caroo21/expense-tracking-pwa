from database import get_db_connection, get_db_type, release_db_connection

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
    placeholder = '%s' if get_db_type() == 'postgresql' else '?'

    # --- Ausgaben berechnen ---
    # COALESCE(SUM(amount), 0) sorgt dafür, dass wir 0 bekommen,
    # wenn es keine Ausgaben gibt, anstatt eines Fehlers.
    sql_expenses = f"""
        SELECT COALESCE(SUM(amount), 0) as total
        FROM expenses 
        WHERE user_id = {placeholder} AND date BETWEEN {placeholder} AND {placeholder}
    """
    cursor.execute(sql_expenses, (user_id, start_date, end_date))
    result = cursor.fetchone()
    
    # Handle both PostgreSQL (dict) and SQLite (tuple) results
    if get_db_type() == 'postgresql':
        total_expenses = float(result['total'])
    else:
        total_expenses = result[0]

    # --- Einnahmen berechnen (PLATZHALTER) ---
    # HINWEIS: Da wir noch keine "incomes"-Tabelle haben, geben wir hier
    # vorerst immer 0 zurück. Dies wäre der Ort, um sie zu berechnen.
    total_income = 1697.0

    release_db_connection(conn)

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
    placeholder = '%s' if get_db_type() == 'postgresql' else '?'
    
    if start_date and end_date:
        sql = f'''
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE user_id = {placeholder} AND date BETWEEN {placeholder} AND {placeholder}
            GROUP BY category
            ORDER BY total DESC
        '''
        cursor.execute(sql, (user_id, start_date, end_date))
    else:
        sql = f'''
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE user_id = {placeholder}
            GROUP BY category
            ORDER BY total DESC
        '''
        cursor.execute(sql, (user_id,))
    
    rows = cursor.fetchall()
    release_db_connection(conn)
    
    categories = []
    for row in rows:
        # Handle both PostgreSQL (dict) and SQLite (Row) results
        row_dict = dict(row) if get_db_type() == 'postgresql' else row
        categories.append({
            'category': row_dict['category'],
            'total': float(row_dict['total'])
        })
    
    return categories
