import requests
import json
import csv

# === Datos fijos ===
url = "https://api-qa.prismamediosdepago.com/v1/debit_card_management/cards "  # Sin espacios
access_token = "2930df2264d7b48908a962ec22e5"

# === Plantilla base del body ===
base_body = {
    "bank_code": "384",
    "origin": {
        "ip_address": "10.10.10.3",
        "channel": "Z"
    },
    "client": {
        "document_type": "DNI",
        "gender": "M",
        "first_name": " uala",
        "marital_status": "Separated",
        "birth_date": "2000-01-01",
        "area_code": "11",
        "phone_number": "12345678"
    },
    "card": {
        "member": "001",
        "expiration_date": "2511",
        "client_class": "9",
        "card_status": "1",
        "branch": "123"
    },
    "address": {
        "street": "Lavarden",
        "number": "245",
        "floor": "2",
        "department": "9",
        "province": "LRJ",
        "city": "La Rioja",
        "zip_code": "5300"
    },
    "accounts": [
        {"account_type": "CCP", "account_status": "1"},
        {"account_type": "CCP", "account_status": "1"},
        {"account_type": "CCP", "account_status": "1"}
    ]
}

# === Headers mínimos necesarios (sin Postman-Token) ===
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {access_token}",
    "User-Agent": "Python-Script",
    "Accept": "*/*",
    "Host": "api-qa.prismamediosdepago.com",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Content-Length": ""  # Se calculará dinámicamente
}

# === Función para hacer el alta ===
def hacer_alta_cliente(datos):
    body = base_body.copy()

    # Rellenar cliente
    body["client"] = {
        **body["client"],
        "document_number": datos["document_number"],
        "lastname": datos["lastname"],
        "holder_cuit": datos["holder_cuit"]
    }

    # Rellenar tarjeta
    body["card"] = {
        **body["card"],
        "card_number": datos["card_number"]
    }

    # Rellenar cuentas
    body["accounts"][0]["account_number"] = datos["account_number"]
    body["accounts"][1]["account_number"] = datos["account_number2"]
    body["accounts"][2]["account_number"] = datos["account_number3"]

    # Serializar body
    body_json = json.dumps(body)
    headers["Content-Length"] = str(len(body_json))

    # Hacer solicitud
    response = requests.post(url, data=body_json, headers=headers)

    return {
        "datos": datos,
        "status_code": response.status_code,
        "response": response.json() if response.text else {}
    }

# === Leer CSV y hacer altas ===
def hacer_altas_desde_csv(ruta_csv):
    with open(ruta_csv, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        resultados = []
        for fila in reader:
            resultado = hacer_alta_cliente(fila)
            resultados.append(resultado)

            print(f"\n✅ Alta para {fila['lastname']} - {fila['document_number']}")
            print("Status Code:", resultado["status_code"])
            print("Respuesta:", resultado["response"])

        return resultados

# === Ejecutar proceso ===
if __name__ == "__main__":
    ruta_csv = "datos_altas.csv"
    resultados = hacer_altas_desde_csv(ruta_csv)

    print("\n✅ Resumen de altas realizadas:")
    for r in resultados:
        print(f"{r['datos']['lastname']} - {r['datos']['document_number']} -> {r['status_code']}")