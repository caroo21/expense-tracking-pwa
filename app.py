from flask import Flask, request,send_from_directory, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from models import expense_model, analytics_model, user_model
from auth import create_token, require_auth

app = Flask(__name__, static_folder='static', static_url_path='')
# cross origin resource sharing
CORS(app)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/manifest.json')
def manifest():
    response = send_from_directory('static', 'manifest.json')
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/service-worker.js')
def service_worker():
    response = send_from_directory('static', 'service-worker.js')
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Service-Worker-Allowed'] = '/'
    return response

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

@app.route("/api", methods=["POST"])
@require_auth
def handle_expense():
    # empfängt daten
    data = request.get_json()
    if not data:
        print("keine Daten")
        return jsonify({"status": "error", "message": "Keine Daten erhalten"}), 400
    print("Daten vom Frontend erhalten: ")
    print(data)

    # User-ID aus Token holen (nicht mehr vom Frontend!)
    data['user_id'] = request.current_user['user_id']
    try:
        # GEÄNDERT: Wir übergeben das gesamte Datenobjekt an die Model-Funktion
        expense_id = expense_model.add_expense(data)
        return jsonify({"status": "success", "expense_id": expense_id}), 201
    except Exception as e:
        print(f"Fehler: {e}")
        return jsonify({"status": "error", "message": "Interner Serverfehler"}), 500

@app.route("/api/dashboard", methods=["GET"])
@require_auth
def get_dashboard_data():
    # User-ID aus Token holen (nicht mehr als Query-Parameter!)
    user_id = request.current_user['user_id']  # ← GEÄNDERT
    try:
        # 2. Heutiges Datum als Basis für alle Berechnungen
        today = datetime.today()
        today_end = today +timedelta(days=1)

        # --- Zeitraum-Berechnungen ---

        # Dieser Monat (z.B. 01.09.2025 - 30.09.2025)
        start_this_month = today.replace(day=1)
        # Für das End-Datum gehen wir zum Anfang des nächsten Monats und einen Tag zurück
        next_month_start = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
        end_this_month = (next_month_start - timedelta(days=1))

        # Letzter Monat (August)
        end_last_month = today.replace(day=1) #- timedelta(days=1)
        start_last_month = end_last_month.replace(day=1)

        # Vorletzter Monat (Juli)
        end_month_before_last = start_last_month #- timedelta(days=1)
        start_month_before_last = end_month_before_last.replace(day=1)

        # Gleicher Monat letztes Jahr (September 2024)
        start_same_month_last_year = today.replace(year=today.year - 1, day=1)
        end_same_month_last_year = (start_same_month_last_year.replace(day=28) + timedelta(days=4)).replace(day=1) #- timedelta(days=1)

        # gesamtes Jahr
        start_this_year = today.replace(month=1, day = 1)

        # 3. Den Analyse-Spezialisten für jeden Zeitraum aufrufen
        summary_this_month = analytics_model.get_summary_for_period(user_id, start_this_month.strftime('%Y-%m-%d'), today_end.strftime('%Y-%m-%d'))
        summary_last_month = analytics_model.get_summary_for_period(user_id, start_last_month.strftime('%Y-%m-%d'), end_last_month.strftime('%Y-%m-%d'))
        summary_month_before_last = analytics_model.get_summary_for_period(user_id, start_month_before_last.strftime('%Y-%m-%d'), end_month_before_last.strftime('%Y-%m-%d'))
        summary_same_month_last_year = analytics_model.get_summary_for_period(user_id, start_same_month_last_year.strftime('%Y-%m-%d'), end_same_month_last_year.strftime('%Y-%m-%d'))
        summary_this_year = analytics_model.get_summary_for_period(user_id, start_this_year.strftime('%Y-%m-%d'), today_end.strftime('%Y-%m-%d'))

        print(summary_this_month)
        print(summary_last_month)
        print(summary_month_before_last)
        print(summary_same_month_last_year)
        print(summary_this_year)

        # 4. Alle Ergebnisse in einem großen JSON-Objekt zusammenfassen
        dashboard_data = {
            "this_month": summary_this_month,
            "last_month": summary_last_month,
            "month_before_last": summary_month_before_last,
            "same_month_last_year": summary_same_month_last_year,
            "this_year": summary_this_year
        }

        # 5. Das fertige "Tablett" an das Frontend senden
        return jsonify(dashboard_data), 200

    except Exception as e:
        print(f"Fehler bei der Dashboard-Daten-Erstellung: {e}")
        return jsonify({"status": "error", "message": "Interner Serverfehler"}), 500

# ==================== AUTH ROUTES ====================

@app.route("/api/auth/register", methods=["POST"])
def register():
    """Registriert einen neuen User."""
    data = request.get_json()
    
    # Validierung
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"status": "error", "message": "Username, Email und Passwort erforderlich"}), 400
    
    # User erstellen
    user_id = user_model.add_user(
        username=data['username'],
        email=data['email'],
        password=data['password']
    )
    
    if not user_id:
        return jsonify({"status": "error", "message": "User existiert bereits"}), 409
    
    # Token erstellen
    token = create_token(user_id, data['username'])
    
    return jsonify({
        "status": "success",
        "token": token,
        "user": {
            "user_id": user_id,
            "username": data['username'],
            "email": data['email']
        }
    }), 201

@app.route("/api/auth/login", methods=["POST"])
def login():
    """Loggt einen User ein."""
    data = request.get_json()
    
    # Validierung
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"status": "error", "message": "Username und Passwort erforderlich"}), 400
    
    # User verifizieren
    user = user_model.verify_user(data['username'], data['password'])
    
    if not user:
        return jsonify({"status": "error", "message": "Ungültige Anmeldedaten"}), 401
    
    # Token erstellen
    token = create_token(user['user_id'], user['username'])
    
    return jsonify({
        "status": "success",
        "token": token,
        "user": user
    }), 200

@app.route("/api/auth/me", methods=["GET"])
@require_auth
def get_current_user():
    """Gibt den aktuell eingeloggten User zurück."""
    user_id = request.current_user['user_id']
    
    # Optional: Hole vollständige User-Daten aus DB
    return jsonify({
        "status": "success",
        "user": {
            "user_id": user_id,
            "username": request.current_user['username']
        }
    }), 200


import os
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
