# backend/routes/utils.py
from flask import Blueprint, render_template, request, jsonify
import os
import importlib.util
import sys

bp = Blueprint('utils', __name__)

# Ruta base de scripts
UTILS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'utils')
os.makedirs(UTILS_DIR, exist_ok=True)

# Definición de herramientas por categoría
HERRAMIENTAS = {
    "conversores": [
        {"id": "convertir_swagger_postman", "nombre": "Swagger → Postman conversor", "script": "convertir_swagger_to_postman.py"},
    ],
    "formateadores": [
        {"id": "formatear_json", "nombre": "Formatear JSON", "script": "formatear_json.py"},
    ],
    "validadores": [
        {"id": "validar_openapi", "nombre": "Validar OpenAPI", "script": "validar_openapi.py"},
    ],
    "generadores": [
        {"id": "generar_id", "nombre": "Generar ID Único", "script": "generar_id_unico.py"},
        {"id": "calcular_hash", "nombre": "Calcular Hash SHA256", "script": "calcular_hash.py"},
    ]
}

@bp.route('/')
def utils_home():
    return render_template('utils/index.html', herramientas=HERRAMIENTAS)

@bp.route('/ejecutar/<herramienta_id>', methods=['GET', 'POST'])
def ejecutar_herramienta(herramienta_id):
    # Buscar herramienta
    herramienta = None
    for categoria, lista in HERRAMIENTAS.items():
        for h in lista:
            if h['id'] == herramienta_id:
                herramienta = h
                break
        if herramienta:
            break

    if not herramienta:
        return "Herramienta no encontrada", 404

    script_path = os.path.join(UTILS_DIR, herramienta['script'])
    if not os.path.exists(script_path):
        return f"Script no encontrado: {script_path}", 404

    if request.method == 'POST':
        # Leer datos del formulario
        input_data = request.form.get('input_data', '')
        extra = request.form.get('extra', '')

        # Ejecutar script dinámicamente
        try:
            spec = importlib.util.spec_from_file_location("module.name", script_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules["module.name"] = module
            spec.loader.exec_module(module)

            # Asumimos que cada script tiene una función: ejecutar(input_data, extra=None)
            if hasattr(module, 'ejecutar'):
                resultado = module.ejecutar(input_data, extra)
            else:
                resultado = f"El script no tiene función 'ejecutar()': {herramienta['script']}"

            return render_template('utils/ejecutar_herramienta.html',
                                   herramienta=herramienta,
                                   entrada=input_data,
                                   resultado=resultado,
                                   volver_url=url_for('utils.utils_home'))
        except Exception as e:
            return f"Error al ejecutar {herramienta['script']}: {str(e)}", 500

    # Método GET: mostrar formulario
    return render_template('utils/ejecutar_herramienta.html',
                           herramienta=herramienta,
                           modo='form',
                           volver_url=url_for('utils.utils_home'))