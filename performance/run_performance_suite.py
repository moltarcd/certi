# performance/run_performance_suite.py
import subprocess
import os
import sys
import argparse
from datetime import datetime

# Perfiles de pruebas parametrizados
PROFILES = {
    "load": {
        "users": "50",
        "spawn_rate": "5",
        "run_time": "10m"
    },
    "stress": {
        "users": "250",
        "spawn_rate": "25",
        "run_time": "5m"
    },
    "spike": {
        "users": "500",
        "spawn_rate": "100",  # Subida ultra rápida
        "run_time": "2m"
    },
    "soak": {
        "users": "30",
        "spawn_rate": "2",
        "run_time": "2h"      # Resistencia en el tiempo
    }
}

def execute_locust_test(test_type: str):
    profile = PROFILES.get(test_type)
    if not profile:
        print(f"Tipo de prueba no válido: {test_type}")
        sys.exit(1)
        
    print(f"[{datetime.now()}] Iniciando Prueba de Rendimiento Tipo: {test_type.upper()}")
    
    csv_prefix = f"reports/raw_perf_{test_type}"
    os.makedirs("reports", exist_ok=True)
    
    # Comando CLI para ejecutar Locust de manera "headless" (sin UI) y exportar los CSVs nativos
    cmd = [
        "locust",
        "-f", "performance/locustfile.py",
        "--host", os.getenv("TARGET_HOST", "https://api-staging.yourbank.com"),
        "--headless",
        "-u", profile["users"],
        "-r", profile["spawn_rate"],
        "--run-time", profile["run_time"],
        "--csv", csv_prefix,
        "--only-summary"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"[{datetime.now()}] Prueba finalizada con éxito. Procesando resultados...")
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando Locust: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Runner de Performance Testing Bank APIs")
    parser.add_argument("--type", choices=["load", "stress", "spike", "soak"], required=True)
    args = parser.parse_args()
    
    execute_locust_test(args.type)