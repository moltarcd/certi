import requests
import json
import copy
import sys
import os
from datetime import datetime
from collections import defaultdict
from responses.debit_card_security_code import BASE_PAYLOAD, TEST_CASES
from reporter import APITestReporter, TestCaseResult

# Forzamos a Python a mapear la raíz del proyecto para paquetes locales
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ======================================================
# CONFIGURACIÓN 
# ======================================================

URL = "https://api-qa.newpay.com.ar/v1/debit_card_security_code/code_information?bank_code=007"

HEADERS_BASE = {
    "Content-Type": "application/json",
    "Authorization": "Bearer 2f9e087b4a7e0794d8e59112d574"
}

# ======================================================
# EJECUCIÓN 
# ======================================================

def obtener_codigo_error(resp):
    try:
        json_resp = resp.json()
        
        # Para respuestas exitosas (200)
        if resp.status_code == 200:
            if "card_number" in json_resp:
                return "200"
            return str(resp.status_code)
        
        # Para el formato de error específico de esta API: {"error": {"code": "DCSC-XXXX", ...}}
        if "error" in json_resp and isinstance(json_resp["error"], dict):
            error = json_resp["error"]
            if "code" in error:
                return error["code"]
            elif "status" in error:
                status_parts = error["status"].split()
                if status_parts:
                    return status_parts[0]
        
        # Para errores sin estructura específica
        if "code" in json_resp:
            return json_resp["code"]
        elif "status" in json_resp:
            return str(json_resp["status"])
        else:
            return str(resp.status_code)
    except:
        return str(resp.status_code) if resp.status_code else "N/A"


def ejecutar_pruebas():
    resultados = []

    # OPTIMIZACIÓN 1: Uso de Session para canalizar todas las peticiones POST de forma rápida
    with requests.Session() as session:
        
        for tc in TEST_CASES:
            # Crear payload 
            payload = copy.deepcopy(BASE_PAYLOAD)
            tc["modificador"](payload)
            
            # Guardar payload 
            payload_str = json.dumps(payload, indent=2, ensure_ascii=False)

            url = tc.get("url_override", URL)
            headers = tc.get("headers_override", HEADERS_BASE.copy())

            # Ejecutar la solicitud (POST)
            try:
                # OPTIMIZACIÓN 2: session.post con Keep-Alive activo y timeout preventivo
                response = session.post(url, headers=headers, json=payload, timeout=3.0)
            except Exception as e:
                # Captura y formateo de fallos de red hacia el Reporter mediante la Dataclass
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
                    es_exitoso = (response.status_code == 200 and "card_number" in json_resp)
                except:
                    es_exitoso = False
                
                expected_display = "200"
                obtained_display = "200" if es_exitoso else str(response.status_code)
            else:
                # Para casos de error, comparamos los códigos personalizados (DCSC-XXXX)
                es_exitoso = (tc['expected_code'] == obtained)
                expected_display = tc['expected_code']
                obtained_display = obtained

            # PASO 2 Y 3: Construcción estandarizada usando TestCaseResult
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

    # PASO 4: Generación final de reportes desacoplados
    reporter = APITestReporter(url_endpoint=URL)
    reporter.generar_todos(resultados)


if __name__ == "__main__":
    ejecutar_pruebas()