import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import uuid
from database import get_db_connection
import bcrypt
from datetime import datetime 

def create_table():
    """Erstellt die 'users' Tabelle."""
    conn = get_db_connection()
    cursor = conn.cursor()
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
    conn.close()

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8') 

def verify_password(password, password_hash):
    """Verifiziert ein Passwort gegen einen Hash."""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def add_user(username, email, password):
    """Fügt einen neuen User hinzu und gibt seine ID zurück."""
    conn = get_db_connection()
    cursor = conn.cursor()
    new_user_id = str(uuid.uuid4())
    password_hash = hash_password(password)
    created_at = datetime.now().isoformat()
    try:
        cursor.execute(
            "INSERT INTO users (user_id, username, email, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
            (new_user_id, username, email, password_hash, created_at)
        )
        conn.commit()
        print(f"User '{username}' mit ID {new_user_id} erstellt.")
        return new_user_id
    except sqlite3.IntegrityError:
        print(f"Fehler: User '{username}' oder Email '{email}' existiert bereits.")
        return None
    finally:
        conn.close()

def verify_user(username, password):
    """
    Prüft ob Username und Passwort korrekt sind
    
    Gibt User-Daten zurück wenn korrekt, sonst None
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Suche User mit diesem Username
        cursor.execute('''
            SELECT user_id, username, email, password_hash
            FROM users
            WHERE username = ?
        ''', (username,))
        
        user = cursor.fetchone()
        
        # 2. Wenn User existiert, prüfe Passwort
        if user and verify_password(password, user['password_hash']):
            return {
                'user_id': user['user_id'],
                'username': user['username'],
                'email': user['email']
            }
        else:
            return None
            
    finally:
        conn.close()

def get_user_by_id(user_id):
    """Holt User-Daten anhand der ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT user_id, username, email, created_at
            FROM users
            WHERE user_id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        
        if user:
            return {
                'user_id': user['user_id'],
                'username': user['username'],
                'email': user['email'],
                'created_at': user['created_at']
            }
        return None
            
    finally:
        conn.close()