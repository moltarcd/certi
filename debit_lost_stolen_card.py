import requests
import json
import copy
import sys
import os
from datetime import datetime
from collections import defaultdict
from responses.debit_lost_stolen_card_test import BASE_PAYLOAD, TEST_CASES
from reporter import APITestReporter, TestCaseResult

# Garantizamos que Python resuelva las rutas locales del paquete responses
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ======================================================
# CONFIGURACIÓN
# ======================================================

URL = "https://api-qa.newpay.com.ar/v1/debit_lost_stolen_card_reporting/?bank_code=007"

HEADERS_BASE = {
    "Content-Type": "application/json",
    "Authorization": "Bearer f026d789cb50fcf6fccc17b6e14e",
    "x-apip-client-id": "test",
    "x-apip-partner-id": "test",
    "x-apip-cuit": "20304050607"
}

# ======================================================
# EJECUCIÓN 
# ======================================================

def obtener_codigo_error(resp):
    try:
        json_resp = resp.json()
        
        # Para respuestas exitosas (200)
        if resp.status_code == 200:
            if "ok" in json_resp:
                return "200"
            return str(resp.status_code)
        
        # Para el formato específico de error de esta API: {"errors":[{"status":"400","code":"DTC-400","title":"..."}]}
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
            return json_resp["error"].get("code", str(resp.status_code))
        elif "error" in json_resp and isinstance(json_resp["error"], str):
            return json_resp["error"]
        else:
            return str(resp.status_code)
    except:
        return str(resp.status_code) if resp.status_code else "N/A"


def ejecutar_pruebas():
    resultados = []

    # OPTIMIZACIÓN 1: Sesión Keep-Alive para procesar el loop velozmente por CLI
    with requests.Session() as session:
        
        for tc in TEST_CASES:
            # Crear payload 
            payload = copy.deepcopy(BASE_PAYLOAD)
            tc["modificador"](payload)
            payload_str = json.dumps(payload, indent=2, ensure_ascii=False)

            url = tc.get("url_override", URL)
            headers = tc.get("headers_override", HEADERS_BASE.copy())

            # Ejecutar la solicitud (POST)
            try:
                # OPTIMIZACIÓN 2: session.post con timeout preventivo contra bloqueos
                response = session.post(url, headers=headers, json=payload, timeout=3.0)
            except Exception as e:

                resultados.append(TestCaseResult(
                    id=tc["id"],
                    requisito=tc["requisito"],
                    descripcion=tc["descripcion"],
                    expected_code=tc["expected_code"],
                    obtained_code="CONNECTION_ERROR",
                    http_status=0,
                    response=str(e),
                    payload=payload_str,
                    es_exitoso=False
                ))
                continue
            
            obtained = obtener_codigo_error(response)
            
            # Determinar si el caso es exitoso según el tipo (C200)
            if tc['id'].startswith('C200'):
                try:
                    json_resp = response.json()
                    es_exitoso = (response.status_code == 200 and "ok" in json_resp)
                except:
                    es_exitoso = False
                
                expected_display = "200"
                obtained_display = "200" if es_exitoso else str(response.status_code)
            else:
                # Para casos de error, comparamos los códigos de error personalizados (DTC-XXXX)
                es_exitoso = (tc['expected_code'] == obtained)
                expected_display = tc['expected_code']
                obtained_display = obtained

            resultados.append(TestCaseResult(
                id=tc["id"],
                requisito=tc["requisito"],
                descripcion=tc["descripcion"],
                expected_code=expected_display,
                expected_response=tc.get('expected_response', ''),
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