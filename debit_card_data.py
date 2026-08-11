import requests
import json
import copy
import sys
import os
import urllib3
from datetime import datetime
from collections import defaultdict
from responses.debit_card_data_test import BASE_URL, DEFAULT_HEADERS, BASE_PAYLOAD, TEST_CASES
from reporter import APITestReporter, TestCaseResult

# Deshabilitar advertencias SSL en entorno QA
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Garantizamos que Python resuelva las rutas locales del paquete responses
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ======================================================
# CONFIGURACIÓN
# ======================================================

URL = BASE_URL
HEADERS_BASE = DEFAULT_HEADERS

# ======================================================
# EJECUCIÓN 
# ======================================================

def obtener_codigo_error(resp):
    try:
        json_resp = resp.json()
        
        # Para respuestas exitosas (200)
        if resp.status_code == 200:
            if "ok" in json_resp or isinstance(json_resp, list) or "debit_card" in json_resp:
                return "DCD-OK"
            return str(resp.status_code)
        
        # Para el formato de errores: {"errors":[{"status":"400","code":"DCD-400","title":"..."}]}
        if "errors" in json_resp and isinstance(json_resp["errors"], list) and len(json_resp["errors"]) > 0:
            error = json_resp["errors"][0]
            if "code" in error:
                return error["code"]
            elif "status" in error:
                return error["status"]
        
        # Para respuestas de error en formato estándar
        if "code" in json_resp:
            return json_resp["code"]
        elif "error" in json_resp and isinstance(json_resp["error"], dict):
            return json_resp["error"].get("code", "DCD-BAD_REQUEST")
        elif "error" in json_resp and isinstance(json_resp["error"], str):
            return json_resp["error"]
        else:
            return str(resp.status_code)
    except Exception:
        return str(resp.status_code) if resp.status_code else "N/A"


def ejecutar_pruebas():
    resultados = []

    # OPTIMIZACIÓN 1: Sesión Keep-Alive para procesar el loop velozmente por CLI
    with requests.Session() as session:
        session.verify = False
        
        for tc in TEST_CASES:
            # Construcción de la URL final según el endpoint
            endpoint = tc.get("endpoint", "")
            full_url = f"{URL}{endpoint}" if endpoint else URL
            
            method = tc.get("method", "POST")
            headers = tc.get("headers_override", HEADERS_BASE.copy())
            
            payload = {}
            payload_str = "N/A"
            params = tc.get("params", None)

            # Preparar payload si es POST
            if method == "POST":
                if "modificador" in tc and callable(tc["modificador"]):
                    tc["modificador"](payload)
                else:
                    payload = copy.deepcopy(tc.get("payload_base", BASE_PAYLOAD))
                payload_str = json.dumps(payload, indent=2, ensure_ascii=False)

            # Ejecutar la solicitud HTTP
            try:
                if method == "GET":
                    response = session.get(full_url, headers=headers, params=params, timeout=5.0)
                    payload_str = f"GET Params: {json.dumps(params)}" if params else "GET (Sin params)"
                else:
                    response = session.post(full_url, headers=headers, json=payload, timeout=5.0)

            except Exception as e:
                resultados.append(TestCaseResult(
                    id=tc["id"],
                    requisito=tc.get("requisito", "N/A"),
                    descripcion=tc["descripcion"],
                    expected_code=tc.get("expected_code", str(tc.get("expected_http", 0))),
                    obtained_code="CONNECTION_ERROR",
                    http_status=0,
                    response=str(e),
                    payload=payload_str,
                    es_exitoso=False
                ))
                continue
            
            obtained = obtener_codigo_error(response)
            expected = tc.get("expected_code", str(tc.get("expected_http")))
            
            # Evaluación del resultado
            if tc['id'].startswith('C200'):
                es_exitoso = (response.status_code == 200)
                expected_display = expected if expected else "200"
                obtained_display = obtained if es_exitoso else str(response.status_code)
            else:
                es_exitoso = (response.status_code == tc.get("expected_http") or expected == obtained)
                expected_display = str(expected)
                obtained_display = obtained

            resultados.append(TestCaseResult(
                id=tc["id"],
                requisito=tc.get("requisito", "N/A"),
                descripcion=tc["descripcion"],
                expected_code=expected_display,
                expected_response=json.dumps(tc.get('expected_response', {}), ensure_ascii=False),
                obtained_code=obtained_display,
                http_status=response.status_code,
                response=response.text,
                payload=payload_str,
                es_exitoso=es_exitoso
            ))

    reporter = APITestReporter(url_endpoint=URL)
    reporter.generar_todos(resultados)


if __name__ == "__main__":
    ejecutar_pruebas()