import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import uuid
from database import get_db_connection, get_db_type, release_db_connection
import bcrypt
from datetime import datetime 

def create_table():
    """Erstellt die 'users' Tabelle."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if get_db_type() == 'postgresql':
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE, 
                password_hash TEXT NOT NULL,        
                created_at TIMESTAMP NOT NULL
            )
        ''')
    else:
        # SQLite Version
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE, 
                password_hash TEXT NOT NULL,        
                created_at TEXT NOT NULL
            )
        ''')
    
    conn.commit()
    release_db_connection(conn)

def hash_password(password):
    salt = bcrypt.gensalt()
    # Don't encode - bcrypt wants string in this version
    return bcrypt.hashpw(password, salt).decode('utf-8')

def verify_password(password, password_hash):
    """Verifiziert ein Passwort gegen einen Hash."""
    # Don't encode - bcrypt wants string in this version
    return bcrypt.checkpw(password, password_hash)

def add_user(username, email, password):
    """Fügt einen neuen User hinzu und gibt seine ID zurück."""
    conn = get_db_connection()
    cursor = conn.cursor()
    new_user_id = str(uuid.uuid4())
    password_hash = hash_password(password)
    created_at = datetime.now().isoformat()

    db_type = get_db_type()
    try:
        if db_type == 'postgresql':
            sql = "INSERT INTO users (user_id, username, email, password_hash, created_at) VALUES (%s, %s, %s, %s, %s)"
        else:
            sql = "INSERT INTO users (user_id, username, email, password_hash, created_at) VALUES (?, ?, ?, ?, ?)"

        cursor.execute(sql, (new_user_id, username, email, password_hash, created_at))

        conn.commit()
        print(f"User '{username}' mit ID {new_user_id} erstellt.")
        return new_user_id
    except Exception as e:
         if 'unique' in str(e).lower() or 'integrity' in str(e).lower():
            print(f"Fehler: User '{username}' oder Email '{email}' existiert bereits.")
         else:
            print(f"Fehler beim Erstellen des Users: {e}")
            
    finally:
        release_db_connection(conn)

def verify_user(username, password):
    """
    Prüft ob Username und Passwort korrekt sind
    
    Gibt User-Daten zurück wenn korrekt, sonst None
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    db_type = get_db_type()
    
    try:
        # 1. Suche User mit diesem Username
        if db_type == 'postgresql':
            cursor.execute('''
                SELECT user_id, username, email, password_hash
                FROM users
                WHERE username = %s
            ''', (username,))
        else:
            cursor.execute('''
                SELECT user_id, username, email, password_hash
                FROM users
                WHERE username = ?
            ''', (username,))
        
        user = cursor.fetchone()
        
        # 2. Wenn User existiert, prüfe Passwort
        if user :
            user_dict = dict(user) if db_type == 'postgresql' else user
            if verify_password(password, user_dict['password_hash']):
                return {
                    'user_id': user_dict['user_id'],
                    'username': user_dict['username'],
                    'email': user_dict['email']
                }
        else:
            return None
            
    finally:
        release_db_connection(conn)

def get_user_by_id(user_id):
    """Holt User-Daten anhand der ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if get_db_type() == 'postgresql':
            sql = '''
                SELECT user_id, username, email, created_at
                FROM users
                WHERE user_id = %s
            '''
        else:
            sql = '''
                SELECT user_id, username, email, created_at
                FROM users
                WHERE user_id = ?
            '''

        cursor.execute(sql, (user_id,))
        
        user = cursor.fetchone()
        
        if user:
            user_dict = dict(user) if get_db_type() == 'postgresql' else user
            return {
                'user_id': user_dict['user_id'],
                'username': user_dict['username'],
                'email': user_dict['email'],
                'created_at': str(user_dict['created_at'])
            }
        return None
            
    finally:
        release_db_connection(conn)