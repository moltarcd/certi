# backend/routes/analysis.py
from flask import Blueprint, render_template, request, redirect, url_for  
import os
import json

bp = Blueprint('analysis', __name__)

@bp.route('/')
def analysis_home():
    return render_template('analysis/upload.html')

@bp.route('/upload', methods=['POST'])
def upload_spec():
    if 'file' not in request.files:
        return redirect(url_for('analysis.analysis_home'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('analysis.analysis_home'))

    # Guardar archivo
    upload_dir = 'backend/data/specs'
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, file.filename)
    file.save(filepath)

    # Parsear
    try:
        from backend.agents.spec_parser import parse_spec
        api_data = parse_spec(filepath)
    except Exception as e:
        return f"Error al parsear: {str(e)}", 400

    # Generar casos de prueba
    from backend.agents.case_generator import generate_test_cases
    test_cases = generate_test_cases(api_data['endpoints'])

    return render_template('analysis/impact_report.html',
                           api=api_data,
                           test_cases=test_cases)