import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

# Hole DATABASE_URL aus Environment Variable
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app_data.db')

# Extrahiere den Dateipfad
if DATABASE_URL.startswith('sqlite:///'):
    DATABASE_FILE = DATABASE_URL.replace('sqlite:///', '')
else:
    # Fallback
    DATABASE_FILE = 'app_data.db'

def get_db_connection():
    """Erstellt eine Verbindung zur SQLite-Datenbank."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # Ermöglicht Zugriff auf Spalten per Name
    return conn