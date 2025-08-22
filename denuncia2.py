# === Configuración general === #
BASE_URL = "https://api-qa.prismamediosdepago.com/v1/debit_lost_stolen_card_reporting/"
BANK_CODE = "007"
AUTHORIZATION_TOKEN = "Bearer f90e61e4c75dda0bae6a48a380ef"  # ⚠️ Reemplazar o usar variable de entorno

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": AUTHORIZATION_TOKEN
}

# === Archivo de entrada y configuración === #
CSV_FILE = "datos_tarjetas.csv"
LOG_FILE = "logs/reportes.log"  # 🔧 Puedes cambiar la ruta: "./resultados/log.txt", etc.
DELAY_BETWEEN_REQUESTS = 1.5  # segundos
EXECUTION_MODE = "filtrar"  # "filtrar" o "todo"

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
        logging.StreamHandler()  # Muestra en consola
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
            response_body = resp_json
        except requests.exceptions.JSONDecodeError:
            response_body = {"raw_response": response.text}

        logging.info(f"📥 RESPONSE - Status: {response.status_code}")
        logging.info(f"   RESPONSE BODY: {json.dumps(response_body, indent=2, ensure_ascii=False)}")

        return response, response_body

    except Exception as e:
        logging.error(f"❌ ERROR en solicitud para DNI {data['document_number']}: {e}")
        return None, {"error": str(e)}

# === Generar reporte HTML === #
from datetime import datetime

def generate_html_report(results, case_details_list):
    log_dir = os.path.dirname(LOG_FILE)
    html_path = os.path.join(log_dir, "reporte_ejecucion.html")

    total_count = len(case_details_list)
    success_count = len([c for c in case_details_list if c["success"]])
    fail_count = len([c for c in case_details_list if not c["success"] and c["status"] != "SKIPPED"])
    skip_count = len([c for c in case_details_list if c["status"] == "SKIPPED"])

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Reporte de Ejecución - Reporte de Tarjetas</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #2c3e50; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #bdc3c7; padding: 10px; text-align: left; vertical-align: top; }}
            th {{ background-color: #3498db; color: white; }}
            .success {{ background-color: #d5f4e6; }}
            .error {{ background-color: #fadbd8; }}
            .skipped {{ background-color: #f0f0f0; }}
            .code {{ font-family: 'Courier New', monospace; background: #ecf0f1; padding: 5px; border-radius: 3px; }}
            .summary {{ margin: 30px 0; padding: 15px; background: #f8f9fa; border: 1px solid #ddd; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>📋 Reporte de Ejecución - Reporte de Tarjetas Perdidas/Robadas</h1>
        <p><strong>Fecha:</strong> {current_time}</p>

        <div class="summary">
            <h2>📊 Resumen de Ejecución</h2>
            <ul>
                <li>✅ Exitosos: {success_count}</li>
                <li>❌ Fallidos: {fail_count}</li>
                <li>⏭️ Saltados: {skip_count}</li>
                <li>🔁 Total Casos: {total_count}</li>
            </ul>
        </div>

        <h2>🔍 Detalle por Caso</h2>
        <table>
            <tr>
                <th>Caso</th>
                <th>Request</th>
                <th>Response</th>
            </tr>
    """.format(
        current_time=current_time,
        success_count=success_count,
        fail_count=fail_count,
        skip_count=skip_count,
        total_count=total_count
    )

    for detail in case_details_list:
        case_num = detail["case"]
        doc_num = detail["document_number"]
        request_body = json.dumps(detail["request_body"], indent=2, ensure_ascii=False)
        response_status = detail.get("response_status", "ERROR")
        response_body = json.dumps(detail.get("response_body", {}), indent=2, ensure_ascii=False)

        row_class = "success" if detail["success"] else "error"
        if detail["status"] == "SKIPPED":
            row_class = "skipped"
            html += f"""
            <tr class="{row_class}">
                <td>{case_num}<br><small>DNI: {doc_num}</small></td>
                <td colspan="2"><em>⏭️ Caso saltado (ejecutar=no)</em></td>
            </tr>
            """
        else:
            html += f"""
            <tr class="{row_class}">
                <td>{case_num}<br><small>DNI: {doc_num}</small></td>
                <td><div class="code"><pre>{request_body}</pre></div></td>
                <td>Status: {response_status}<br><div class="code"><pre>{response_body}</pre></div></td>
            </tr>
            """

    html += """
        </table>
        <footer>
            <p><em>Reporte generado automáticamente por el script de automatización QA.</em></p>
        </footer>
    </body>
    </html>
    """

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    logging.info(f"📄 Reporte HTML generado: {html_path}")

# === Lectura del CSV y ejecución === #
def run_tests():
    if not os.path.exists(CSV_FILE):
        logging.critical(f"❌ Archivo {CSV_FILE} no encontrado.")
        return

    results = []
    case_details_list = []  # Para el reporte HTML
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
            rows = list(reader)
            total_cases = len(rows)

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
                    case_details_list.append({
                        "case": idx,
                        "document_number": row["document_number"],
                        "request_body": {},
                        "response_status": None,
                        "response_body": {},
                        "success": False,
                        "status": "SKIPPED"
                    })
                    continue

                # Enviar solicitud
                executed_num = len([r for r in results if r["status"] != "SKIPPED"]) + 1
                response, response_body = send_card_report(row, executed_num, total_cases)
                success = response is not None and response.status_code in [200, 201]

                # Resultados
                results.append({
                    "case": idx,
                    "document_number": row["document_number"],
                    "status": response.status_code if response else "ERROR",
                    "success": success
                })

                # Detalles para HTML
                body = create_request_body(row)
                case_details_list.append({
                    "case": idx,
                    "document_number": row["document_number"],
                    "request_body": body,
                    "response_status": response.status_code if response else "ERROR",
                    "response_body": response_body,
                    "success": success,
                    "status": "SUCCESS" if success else "FAILED"
                })

                # ⏱️ Espera
                if DELAY_BETWEEN_REQUESTS > 0 and executed_num < total_cases:
                    time.sleep(DELAY_BETWEEN_REQUESTS)

    except Exception as e:
        logging.critical(f"❌ Error al procesar el archivo CSV: {e}")
        return

    # === Resumen final en log === #
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

    # === Generar reporte HTML === #
    generate_html_report(results, case_details_list)

# === Ejecutar === #
if __name__ == "__main__":
    run_tests()