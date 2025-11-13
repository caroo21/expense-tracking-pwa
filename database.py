import os 
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictConnection
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URI = os.getenv('SUPABASE_URI', 'sqlite:///app_data.db')

# Bestimme den Datenbanktyp
if SUPABASE_URI.startswith('postgresql://') or SUPABASE_URI.startswith('postgres://'):
    DB_TYPE = 'postgresql'
    # Supabase verwendet manchmal 'postgres://' - konvertiere zu 'postgresql://'
    if SUPABASE_URI.startswith('postgres://'):
        SUPABASE_URI = SUPABASE_URI.replace('postgres://', 'postgresql://', 1)
    connection_pool = psycopg2.pool.SimpleConnectionPool(
            1,  # minimum connections
            10, # maximum connections
            SUPABASE_URI
    )
elif SUPABASE_URI.startswith('sqlite:///'):
    DB_TYPE = 'sqlite'
    DATABASE_FILE = SUPABASE_URI.replace('sqlite:///', '')
else:
    # Fallback zu SQLite
    DB_TYPE = 'sqlite'
    DATABASE_FILE = 'app_data.db'

def get_db_connection():
    """Erstellt eine Verbindung zur Datenbank (PostgreSQL oder SQLite)."""
    if DB_TYPE == 'postgresql':
        # Get connection from pool instead of creating new one
        conn = connection_pool.getconn()
        conn.cursor_factory = psycopg2.extras.RealDictCursor
        return conn
    else:
        import sqlite3
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row
        return conn

def release_db_connection(conn):
    """Gibt die Verbindung zurück an den Pool."""
    if DB_TYPE == 'postgresql':
        connection_pool.putconn(conn)
    else:
        conn.close()

def get_db_type():
    """Gibt den aktuellen Datenbanktyp zurück."""
    return DB_TYPE
