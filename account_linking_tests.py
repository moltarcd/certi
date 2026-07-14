import requests
import json
import copy
import sys
import os
from collections import defaultdict
from datetime import datetime
import re
import time
from responses.cbu_management_test import BASE_PAYLOAD, TEST_CASES
from reporter import APITestReporter, TestCaseResult

# Garantizamos que Python resuelva correctamente las rutas del paquete responses
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ======================================================
# CONFIGURACIÓN
# ======================================================

URL = "https://api-qa.newpay.com.ar/v1/account-linking/bind"

HEADERS_BASE = {
    "Content-Type": "application/json",
    "Authorization": "Bearer c2bebe58e3215853e619dd5fe048",
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
            if json_resp.get("success") is True:
                return "200"
            return str(resp.status_code)
        
        # Para respuestas de error, intentar obtener el código del body
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
    SLEEP_BETWEEN_TESTS = 0.5  # Segundos de espera entre casos

    # OPTIMIZACIÓN 1: Uso de Session para reutilizar conexiones TCP/SSL
    with requests.Session() as session:
        
        for i, tc in enumerate(TEST_CASES):
            # Crear payload
            payload = copy.deepcopy(BASE_PAYLOAD)

            # Asignar cuenta única para casos C200 (Mantiene tu lógica original)
            if tc["id"].startswith("C200") and "cuenta_desde_caso" in globals():
                payload["accounts"][0]["number"] = cuenta_desde_caso(tc["id"])

            tc["modificador"](payload)
            
            # Guardar payload 
            payload_str = json.dumps(payload, indent=2, ensure_ascii=False)

            # Ejecutar la solicitud (POST)
            print(f"Ejecutando caso {i+1}/{len(TEST_CASES)}: {tc['id']}")
            try:
                # OPTIMIZACIÓN 2: session.post con timeout controlado de 3s contra cuelgues de red
                response = session.post(URL, headers=HEADERS_BASE, json=payload, timeout=3.0)
            except Exception as e:
                # Captura y mapeo oficial de fallos de red hacia el Reporter
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
                    es_exitoso = (response.status_code == 200 and json_resp.get("success") is True)
                except:
                    es_exitoso = False
                
                expected_display = "200"
                obtained_display = "200" if es_exitoso else str(response.status_code)
            else:
                es_exitoso = (tc['expected_code'] == obtained)
                expected_display = tc['expected_code']
                obtained_display = obtained

            # PASO 2 Y 3: Inyección de datos tipados mediante la Dataclass oficial TestCaseResult
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
            
            # Respeto de tiempo entre ráfagas si aplica
            if i < len(TEST_CASES) - 1:
                print(f"Esperando {SLEEP_BETWEEN_TESTS} segundos...")
                time.sleep(SLEEP_BETWEEN_TESTS)

    # PASO 4: Orquestador desacoplado para la generación unificada de los reportes
    reporter = APITestReporter(url_endpoint=URL)
    reporter.generar_todos(resultados)


if __name__ == "__main__":
    ejecutar_pruebas()