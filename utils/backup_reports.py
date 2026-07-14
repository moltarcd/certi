import os
import shutil
from pathlib import Path

# Ruta raíz del proyecto
PROJECT_ROOT = Path("C:\Proyectos\certificacion-nds-emision")

# Carpeta que contiene los reportes actuales
REPORTS_DIR = PROJECT_ROOT / "reportes"

# Carpeta destino para reportes antiguos
OLD_REPORTS_DIR = PROJECT_ROOT / "old_reports"

# Cachés a eliminar
CACHE_DIRS = [
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox"
]


def clean_cache(root_path):
    """Elimina directorios de caché."""
    for path in root_path.rglob("*"):
        if path.is_dir() and path.name in CACHE_DIRS:
            print(f"Eliminando caché: {path}")
            shutil.rmtree(path, ignore_errors=True)


def move_reports(src_dir, dst_dir):
    """Mueve todos los archivos al directorio old_reports."""
    dst_dir.mkdir(exist_ok=True)

    for file in src_dir.iterdir():
        if file.is_file():
            destination = dst_dir / file.name

            # Si ya existe, renombrar
            if destination.exists():
                stem = file.stem
                suffix = file.suffix
                counter = 1

                while destination.exists():
                    destination = dst_dir / f"{stem}_{counter}{suffix}"
                    counter += 1

            print(f"Moviendo {file} -> {destination}")
            shutil.move(str(file), str(destination))


if __name__ == "__main__":
    print("Limpiando caché...")
    clean_cache(PROJECT_ROOT)

    print("Moviendo reportes antiguos...")
    move_reports(REPORTS_DIR, OLD_REPORTS_DIR)

    print("Proceso finalizado.")