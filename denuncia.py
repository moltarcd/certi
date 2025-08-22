# === Configuración general === #
BASE_URL = "https://api-qa.prismamediosdepago.com/v1/debit_lost_stolen_card_reporting/"
BANK_CODE = "007"
AUTHORIZATION_TOKEN = "Bearer f90e61e4c75dda0bae6a48a380ef"  # ⚠️ Usa variable de entorno

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": AUTHORIZATION_TOKEN
}

# === Archivo de entrada y configuración === #
CSV_FILE = "datos_tarjetas.csv"
LOG_FILE = "logs/reportes.log"  # Ruta de reporte 
DELAY_BETWEEN_REQUESTS = 1.5
EXECUTION_MODE = "filtrar"  # "filtrar" o "todo" los caoss a ejecutar del csv

# === Crear directorio del log si no existe === #
import os
log_dir = os.path.dirname(LOG_FILE)
if log_dir and not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configurar logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()  # También muestra en consola
    ]
)

# === Plantilla del body === #
def create_request_body(row):
    return {
        "client": {
            "document_type": "DNI",
            "document_number": int(row["document_number"]),
            "gender": "M"
        },
        "afip": {
            "cuit": "DNI"
        },
        "card_details": {
            "bin": str(row["bin"]),
            "last_four_digits": str(row["last_four_digits"])
        },
        "ip": "198.51.100.42",
        "reason": int(row["reason"])
    }

# === Función para enviar la solicitud y loguear === #
import requests
import csv
import time
import json

def send_card_report(data, case_num, total_cases):
    url = f"{BASE_URL}?bank_code={BANK_CODE}"
    body = create_request_body(data)

    # 🔹 Log del Request
    logging.info(f"🔁 [{case_num}/{total_cases}] PROCESANDO CASO")
    logging.info(f"📤 REQUEST - DNI: {data['document_number']}, BIN: {data['bin']}, Últimos 4: {data['last_four_digits']}")
    logging.info(f"   URL: {url}")
    logging.info(f"   HEADERS: {{'Content-Type': 'application/json', 'Authorization': 'Bearer ***'}}")
    logging.info(f"   BODY: {json.dumps(body, indent=2, ensure_ascii=False)}")

    try:
        response = requests.post(url, json=body, headers=HEADERS, timeout=10)

        # 🔹 Log de la Respuesta
        try:
            resp_json = response.json()
            response_body = json.dumps(resp_json, indent=2, ensure_ascii=False)
        except requests.exceptions.JSONDecodeError:
            response_body = response.text

        logging.info(f"📥 RESPONSE - Status: {response.status_code}")
        logging.info(f"   RESPONSE BODY: {response_body}")

        return response

    except Exception as e:
        logging.error(f"❌ ERROR en solicitud para DNI {data['document_number']}: {e}")
        return None

# === Lectura del CSV y ejecución === #
def run_tests():
    if not os.path.exists(CSV_FILE):
        logging.critical(f"❌ Archivo {CSV_FILE} no encontrado.")
        return

    results = []
    logging.info(f"🚀 Iniciando suite de pruebas")
    logging.info(f"📁 Archivo de datos: {CSV_FILE}")
    logging.info(f"📄 Archivo de log: {os.path.abspath(LOG_FILE)}")
    logging.info(f"🔧 Modo de ejecución: {EXECUTION_MODE}")

    try:
        with open(CSV_FILE, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            required_columns = {"document_number", "bin", "last_four_digits", "reason"}
            if not required_columns.issubset(reader.fieldnames):
                logging.critical(f"❌ Faltan columnas requeridas: {required_columns}")
                return

            use_filter = "ejecutar" in reader.fieldnames and EXECUTION_MODE == "filtrar"

            # Contar filas para mostrar progreso
            rows = list(reader)
            total_cases = len(rows)
            executed_cases = 0

            for idx, row in enumerate(rows, start=1):
                # Filtro
                if use_filter and row.get("ejecutar", "").strip().lower() != "si":
                    logging.info(f"⏭️  [Salteado] Caso {idx}: DNI {row['document_number']}")
                    results.append({
                        "case": idx,
                        "document_number": row["document_number"],
                        "status": "SKIPPED",
                        "success": False
                    })
                    continue

                executed_cases += 1
                response = send_card_report(row, executed_cases, total_cases)
                success = response is not None and response.status_code in [200, 201]

                results.append({
                    "case": idx,
                    "document_number": row["document_number"],
                    "status": response.status_code if response else "ERROR",
                    "success": success
                })

                # ⏱️ Espera entre solicitudes
                if DELAY_BETWEEN_REQUESTS > 0 and executed_cases < total_cases:
                    time.sleep(DELAY_BETWEEN_REQUESTS)

    except Exception as e:
        logging.critical(f"❌ Error al procesar el archivo CSV: {e}")
        return

    # === Resumen final (también en log) === #
    total_executed = len([r for r in results if r["status"] != "SKIPPED"])
    successful = len([r for r in results if r["success"]])

    logging.info("="*60)
    logging.info("📋 RESUMEN FINAL DE EJECUCIÓN")
    logging.info("="*60)
    for r in results:
        if r["status"] == "SKIPPED":
            logging.info(f"⏭️  Caso {r['case']} - DNI {r['document_number']} → Saltado")
        else:
            emoji = "✅" if r["success"] else "❌"
            logging.info(f"{emoji} Caso {r['case']} - DNI {r['document_number']} → Status {r['status']}")

    logging.info(f"\n🎯 Ejecutados: {total_executed}")
    logging.info(f"✅ Exitosos: {successful}")
    logging.info(f"❌ Fallidos: {total_executed - successful}")
    logging.info("🏁 Suite de pruebas finalizada.")

# === Ejecutar === #
if __name__ == "__main__":
    run_tests()