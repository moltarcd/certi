import requests
import json
import copy
import sys
from datetime import datetime
from responses.cbu_management_test import BASE_PAYLOAD, TEST_CASES
from reporter import APITestReporter, TestCaseResult


# ======================================================
# CONFIGURACIÓN
# ======================================================
URL = "https://api-qa.newpay.com.ar/v2/cbu_management/accounts/account/cbu"

HEADERS_BASE = {
    "Content-Type": "application/json",
    "Authorization": "Bearer a68cd80cfbca463413afeaf2dd17",
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
        if resp.status_code == 200:
            if "ok" in json_resp:
                return "200"
            return str(resp.status_code)
        if "errors" in json_resp and len(json_resp["errors"]) > 0:
            return json_resp["errors"][0].get("code", str(resp.status_code))
        return str(resp.status_code)
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

        if tc['id'].startswith('C200'):
            try:
                json_resp = response.json()
                es_exitoso = (response.status_code == 200 and "ok" in json_resp)
            except:
                es_exitoso = False
            expected_display = "200"
            obtained_display = "200" if es_exitoso else str(response.status_code)
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