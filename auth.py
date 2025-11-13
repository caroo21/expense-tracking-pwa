import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv('JWT_SECRET')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24 * 7  # 7 Tage

def create_token(user_id, username):
    """Erstellt einen JWT-Token für einen User."""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def verify_token(token):
    """Verifiziert einen JWT-Token und gibt die Payload zurück."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token abgelaufen
    except jwt.InvalidTokenError:
        return None  # Token ungültig

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        print(f"🔍 Authorization Header: {auth_header}")  # ← DEBUG
        
        if not auth_header:
            print("❌ Kein Authorization Header!")  # ← DEBUG
            return jsonify({
                'status': 'error',
                'message': 'Kein Token vorhanden'
            }), 401
        
        try:
            token = auth_header.split(' ')[1]
            print(f"🔑 Token: {token[:30]}...")  # ← DEBUG (erste 30 Zeichen)
        except IndexError:
            print("❌ Token Format falsch!")  # ← DEBUG
            return jsonify({
                'status': 'error',
                'message': 'Ungültiges Token-Format'
            }), 401
        
        payload = verify_token(token)
        print(f"📦 Payload: {payload}")  # ← DEBUG
        
        if not payload:
            print("❌ Token Verifikation fehlgeschlagen!")  # ← DEBUG
            return jsonify({
                'status': 'error',
                'message': 'Ungültiger oder abgelaufener Token'
            }), 401
        
        request.current_user = payload
        print(f"✅ User authentifiziert: {payload['username']}")  # ← DEBUG
        
        return f(*args, **kwargs)
    
    return decorated_function

