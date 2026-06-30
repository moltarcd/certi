import requests
import json
import copy
import sys
from datetime import datetime
from collections import defaultdict
from reporter import APITestReporter, TestCaseResult

# IMPORTACIÓN DE TEMPLATES (MANTIENE EL SCRIPT LIMPIO)
from responses.debit_card_management_test import BASE_PAYLOAD, TEST_CASES

# ======================================================
# CONFIGURACIÓN
# ======================================================
URL = "https://api-qa.newpay.com.ar/v1/debit_card_management/cards"

HEADERS_BASE = {
    "Content-Type": "application/json",
    "Authorization": "Bearer d7c63152704a3c7063ff37799126",  
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
        if resp.status_code == 201:
            return "201"
        if "error" in json_resp and isinstance(json_resp["error"], dict):
            error = json_resp["error"]
            if "code" in error: return error["code"]
            elif "status" in error: return error["status"]
        return json_resp.get("code", json_resp.get("status", str(resp.status_code)))
    except:
        return str(resp.status_code) if resp.status_code else "N/A"

def ejecutar_pruebas():
    resultados = []

    for tc in TEST_CASES:
        payload = copy.deepcopy(BASE_PAYLOAD)
        tc["modificador"](payload)
        payload_str = json.dumps(payload, indent=2, ensure_ascii=False)

        url = tc.get("url_override", URL)
        headers = tc.get("headers_override", HEADERS_BASE.copy())

        try:
            response = requests.post(url, headers=headers, json=payload)
        except Exception as e:
            resultados.append(TestCaseResult(
                id=tc["id"], requisito=tc["requisito"], descripcion=tc["descripcion"],
                expected_code=tc["expected_code"], obtained_code="CONNECTION_ERROR",
                http_status=0, response=str(e), payload=payload_str, es_exitoso=False
            ))
            continue
        
        obtained = obtener_codigo_error(response)
        
        if tc['id'].startswith('C201'):
            es_exitoso = (response.status_code == 201)
            expected_display = "201"
            obtained_display = "201" if es_exitoso else str(response.status_code)
        else:
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