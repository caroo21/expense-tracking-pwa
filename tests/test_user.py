import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import user_model

from models import user_model

# Test: User erstellen
print("📝 Erstelle Test-User...")
user_id ="ca1de205-83a8-4f92-9e05-558c025d6ecc"
if user_id:
    print(f"✅ User erstellt mit ID: {user_id}")
    
    # Test: User Login
    print("\n🔐 Teste Login...")
    user = user_model.verify_user("testuser", "password123")
    if user:
        print(f"✅ Login erfolgreich: {user}")
    else:
        print("❌ Login fehlgeschlagen")
    
    # Test: User abrufen
    print("\n📖 Hole User-Daten...")
    user_data = user_model.get_user_by_id(user_id)
    if user_data:
        print(f"✅ User gefunden: {user_data}")
    else:
        print("❌ User nicht gefunden")
else:
    print("❌ User konnte nicht erstellt werden")
