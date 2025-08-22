# utils/comprimir_proyecto.py
import os
import shutil
from datetime import datetime

def encontrar_raiz():
    """Encuentra la raíz del proyecto buscando archivos clave"""
    current = os.path.abspath(os.path.dirname(__file__))
    while current != os.path.dirname(current):
        # Busca indicios de que estamos en la raíz
        if os.path.exists(os.path.join(current, 'web_launcher.py')):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    # Si no encuentra, usa el directorio del script
    return os.path.abspath(os.path.dirname(__file__))

def comprimir_proyecto():
    # === 🔥 Detectar raíz del proyecto ===
    root_dir = encontrar_raiz()
    print(f"📁 Raíz del proyecto detectada: {root_dir}")

    project_name = "qa-agent"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_name = f"{project_name}_{timestamp}"

    # === 🚫 Elementos a excluir ===
    EXCLUDE_PATTERNS = {
        '__pycache__',
        '.git',
        '.pytest_cache',
        'venv',
        'env',
        '.vscode',
        '.idea',
        '*.pyc',
        'desktop.ini',
        '.DS_Store',
        '*.log',
        'tmp',
        'temp',
        '_build'
    }

    def should_exclude(name):
        return (
            name in EXCLUDE_PATTERNS or
            any(ex in name for ex in EXCLUDE_PATTERNS) or
            name.startswith('.') or
            name.endswith('.pyc') or
            any(name.endswith(ext) for ext in ['.log', '.tmp'])
        )

    def ignore_filter(directory, contents):
        # Ignorar elementos según nombre
        return [item for item in contents if should_exclude(item)]

    # === 📦 Carpeta temporal ===
    temp_dir = os.path.join(root_dir, '_build')
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

    try:
        # === 🔗 Copiar TODO el proyecto (raíz completa) ===
        shutil.copytree(root_dir, temp_dir, ignore=ignore_filter, dirs_exist_ok=False)

        # === 📦 Comprimir ===
        output_path = os.path.join(root_dir, output_name)
        shutil.make_archive(output_path, 'zip', temp_dir)

        print(f"✅ Proyecto comprimido: {output_name}.zip")
        print(f"💾 Guardado en: {root_dir}")

    except Exception as e:
        print(f"❌ Error al comprimir: {str(e)}")
    finally:
        # === 🧹 Limpiar temporal ===
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == '__main__':
    comprimir_proyecto()