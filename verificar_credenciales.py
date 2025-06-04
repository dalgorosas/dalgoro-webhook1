import os
import json

cred_path = os.environ.get("GOOGLE_CREDENTIALS_JSON")
print(f"🟢 Archivo a cargar: {cred_path}")

try:
    with open(cred_path, "r") as f:
        cred_data = json.load(f)
        print("✅ JSON cargado correctamente")
        print(json.dumps(cred_data, indent=2))
except Exception as e:
    print(f"❌ Error: {e}")
