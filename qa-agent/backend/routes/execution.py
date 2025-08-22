# backend/routes/execution.py
from flask import Blueprint, render_template

bp = Blueprint('execution', __name__)

@bp.route('/')
def execution_home():
    return render_template('execution/select.html')