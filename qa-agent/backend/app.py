# backend/app.py
from flask import Flask, render_template, redirect, url_for
import os

# === 1. Definir rutas absolutas ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "..", "frontend", "templates")
ASSETS_DIR = os.path.join(BASE_DIR, "..", "frontend", "assets")

# Validación temprana
if not os.path.exists(TEMPLATES_DIR):
    raise FileNotFoundError(f"❌ No se encontró 'templates': {TEMPLATES_DIR}")
if not os.path.exists(ASSETS_DIR):
    raise FileNotFoundError(f"❌ No se encontró 'assets': {ASSETS_DIR}")

# === 2. Crear la app ===
app = Flask(__name__,
            template_folder=TEMPLATES_DIR,
            static_folder=ASSETS_DIR,
            static_url_path='/static')

# === 3. Registrar blueprints (DESPUÉS de crear app) ===
from backend.routes import analysis, execution, utils

app.register_blueprint(analysis.bp, url_prefix='/analysis')
app.register_blueprint(execution.bp, url_prefix='/execution')
app.register_blueprint(utils.bp, url_prefix='/utils')

# === 4. Definir rutas directas (como /) ===
@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(404)
def not_found(e):
    # Solo maneja 404 si no coincide con ninguna ruta
    return render_template('index.html'), 404

# === 5. Iniciar (opcional: solo si ejecutas app.py directamente) ===
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)