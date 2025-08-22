# web_launcher.py
import os
import sys

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import app

if __name__ == '__main__':
    print("🚀 QA Agent iniciado en http://127.0.0.1:5000")
    print("🔧 Modo offline activado. No se requiere conexión externa.")
    app.run(host='127.0.0.1', port=5000, debug=True)