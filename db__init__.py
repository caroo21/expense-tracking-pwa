from models import user_model, expense_model 

def initialize_database():
    """
    Initialisiert die gesamte Datenbank.
    Diese Funktion ruft die Setup-Funktionen für alle Tabellen auf.
    """
    print("Initialisiere Datenbank...")

    # Erstellt die 'users'-Tabelle, indem sie die Funktion aus dem user_model aufruft
    user_model.create_table()
    print(" - 'users' Tabelle erfolgreich geprüft/erstellt.")

    # Erstellt die 'expenses'-Tabelle, indem sie die Funktion aus dem expense_model aufruft
    expense_model.create_table()
    print(" - 'expenses' Tabelle erfolgreich geprüft/erstellt.")

    print("Datenbank-Initialisierung abgeschlossen.")


# Dieser Block macht die Datei als Skript ausführbar.
# Wenn du "python database.py" im Terminal eingibst, wird diese Funktion gestartet.
if __name__ == '__main__':
    initialize_database()