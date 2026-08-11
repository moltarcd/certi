"""
Módulo de Payloads, Headers y Casos de Prueba para Debit Card Data API (Newpay)
Compatible con la ejecución automatizada POST / GET y la suite de reportes.
"""

import copy

# Configuración Base para el Runner
BASE_URL = "https://api-qa.newpay.com.ar/v1/debit-card-data"

# Bearer Token por defecto para el flujo principal por documento
DEFAULT_AUTH_TOKEN = "Bearer 005a3486ff4dfcb0c499ccced230"
# Bearer Token específico para las consultas por tarjeta
BY_CARD_AUTH_TOKEN = "Bearer 005a3486ff4dfcb0c499ccced230"

DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "x-apip-cuit": "20-43573454-6",
    "company": "PRISMA",
    "Authorization": DEFAULT_AUTH_TOKEN,
    "User-Agent": "PostmanRuntime/7.32.3",
    "Accept": "*/*"
}

# Payloads Base desde los cURL oficializados
BASE_PAYLOAD_BY_DOCUMENT = {
    "gender": "M",
    "bank_code": "P01",
    "document_type": "1",
    "document_number": 13722583
}

BASE_PAYLOAD_BY_CARD = {
    "debit_card_number": "pOHe51E3i1TJoMrqXcalabStm+6sAUNOZOnjeo3wN5fX6F9RK5gPlcKjvBA=",
    "bank_code": "007"
}

BASE_PAYLOAD = BASE_PAYLOAD_BY_DOCUMENT

# Funciones Mutadoras Helper
def setear(data: dict, path: str, value):
    """Seta un valor en un diccionario usando dot-notation."""
    keys = path.split(".")
    d = data
    for k in keys[:-1]:
        d = d.setdefault(k, {})
    d[keys[-1]] = value
    return data

def borrar(data: dict, path: str):
    """Elimina una clave de un diccionario usando dot-notation."""
    keys = path.split(".")
    d = data
    for k in keys[:-1]:
        if k not in d:
            return data
        d = d[k]
    d.pop(keys[-1], None)
    return data

def aplicar_modificaciones(payload: dict, modificaciones: list):
    """Aplica secuencialmente la lista de reglas ("setear"/"borrar") sobre el payload."""
    for mod in modificaciones:
        accion = mod[0]
        if accion == "setear":
            setear(payload, mod[1], mod[2])
        elif accion == "borrar":
            borrar(payload, mod[1])

# MATRIZ COMPLETA DE CASOS DE PRUEBA
TEST_CASES = [
    # =========================================================================
    # ENDPOINT: /by-card (POST)
    # =========================================================================
    {
        "id": "C200-01 - by-card - Consulta exitosa",
        "requisito": "by-card - Consulta exitosa",
        "descripcion": "Consulta exitosa por tarjeta enviando bank_code y encrypted_card válidos",
        "endpoint": "/by-card",
        "method": "POST",
        "payload_base": BASE_PAYLOAD_BY_CARD,
        "headers_override": {
            **DEFAULT_HEADERS,
            "Authorization": BY_CARD_AUTH_TOKEN
        },
        "modifications": [],
        "expected_http": 200,
        "expected_code": "DCD-OK",
        "expected_response": {"debit_card": {"bank_code": "007"}, "client": {}}
    },
    {
        "id": "C400-01 - by-card - bank_code inválido",
        "requisito": "by-card - bank_code inválido",
        "descripcion": "Consulta rechazada por bank_code inválido (letras o caracteres especiales)",
        "endpoint": "/by-card",
        "method": "POST",
        "payload_base": BASE_PAYLOAD_BY_CARD,
        "headers_override": {
            **DEFAULT_HEADERS,
            "Authorization": BY_CARD_AUTH_TOKEN
        },
        "modifications": [("setear", "bank_code", "ABC@#")],
        "expected_http": 400,
        "expected_code": "DCD-BAD_REQUEST",
        "expected_response": {"error": {"message": "Invalid Debit Card"}}
    },
    {
        "id": "C400-02 - by-card - bank_code inexistente",
        "requisito": "by-card - bank_code inexistente",
        "descripcion": "Consulta rechazada por enviar código de banco no registrado en la entidad",
        "endpoint": "/by-card",
        "method": "POST",
        "payload_base": BASE_PAYLOAD_BY_CARD,
        "headers_override": {
            **DEFAULT_HEADERS,
            "Authorization": BY_CARD_AUTH_TOKEN
        },
        "modifications": [("setear", "bank_code", "999")],
        "expected_http": 400,
        "expected_code": "DCD-BAD_REQUEST",
        "expected_response": {"error": {"message": "Invalid Debit Card"}}
    },
    {
        "id": "C400-03",
        "requisito": "by-card - bank_code incorrecto para la TD",
        "descripcion": "Consulta rechazada por enviar código de banco distinto al asociado a la tarjeta de débito",
        "endpoint": "/by-card",
        "method": "POST",
        "payload_base": BASE_PAYLOAD_BY_CARD,
        "headers_override": {
            **DEFAULT_HEADERS,
            "Authorization": BY_CARD_AUTH_TOKEN
        },
        "modifications": [("setear", "bank_code", "011")],
        "expected_http": 400,
        "expected_code": "DCD-BAD_REQUEST",
        "expected_response": {"error": {"message": "Invalid Debit Card"}}
    },
    {
        "id": "C400-04",
        "requisito": "by-card - TD mal cifrada",
        "descripcion": "Consulta rechazada por PAN cifrado incorrectamente",
        "endpoint": "/by-card",
        "method": "POST",
        "payload_base": BASE_PAYLOAD_BY_CARD,
        "headers_override": {
            **DEFAULT_HEADERS,
            "Authorization": BY_CARD_AUTH_TOKEN
        },
        "modifications": [("setear", "debit_card_number", "c2hvcnRfaXZfP3M=")],
        "expected_http": 400,
        "expected_code": "DCD-BAD_REQUEST",
        "expected_response": {"error": {"message": "Invalid encrypted debit card number."}}
    },
    {
        "id": "C400-05",
        "requisito": "by-card - TD inexistente",
        "descripcion": "Consulta rechazada por enviar datos de tarjeta que no existe en el repositorio Tarjetas_NP",
        "endpoint": "/by-card",
        "method": "POST",
        "payload_base": BASE_PAYLOAD_BY_CARD,
        "headers_override": {
            **DEFAULT_HEADERS,
            "Authorization": BY_CARD_AUTH_TOKEN
        },
        "modifications": [("setear", "debit_card_number", "IvInvalidoOInexistenteEnTablaBase64==")],
        "expected_http": 400,
        "expected_code": "DCD-BAD_REQUEST",
        "expected_response": {"error": {"message": "Invalid Debit Card"}}
    },
    {
        "id": "C400-06",
        "requisito": "by-card - Campo obligatorio bank_code",
        "descripcion": "Consulta rechazada al omitir el campo requerido 'bank_code'",
        "endpoint": "/by-card",
        "method": "POST",
        "payload_base": BASE_PAYLOAD_BY_CARD,
        "headers_override": {
            **DEFAULT_HEADERS,
            "Authorization": BY_CARD_AUTH_TOKEN
        },
        "modifications": [("borrar", "bank_code")],
        "expected_http": 400,
        "expected_code": "DCD-BAD_REQUEST",
        "expected_response": {"error": {"title": "Bad Request", "message": "Validation failed"}}
    },
    {
        "id": "C400-07",
        "requisito": "by-card - Campo obligatorio debit_card_number",
        "descripcion": "Consulta rechazada al omitir el campo requerido 'debit_card_number'",
        "endpoint": "/by-card",
        "method": "POST",
        "payload_base": BASE_PAYLOAD_BY_CARD,
        "headers_override": {
            **DEFAULT_HEADERS,
            "Authorization": BY_CARD_AUTH_TOKEN
        },
        "modifications": [("borrar", "debit_card_number")],
        "expected_http": 400,
        "expected_code": "DCD-BAD_REQUEST",
        "expected_response": {"error": {"title": "Bad Request", "message": "Validation failed"}}
    },

    # =========================================================================
    # ENDPOINT: /by-document (POST)
    # =========================================================================
    {
        "id": "C200-02",
        "requisito": "by-document - Tipos de documento válidos",
        "descripcion": "Consulta exitosa probando tipos de documento permitidos (DNI, LC, LE, CUIT/CUIL, CI, Pasaporte)",
        "endpoint": "/by-document",
        "method": "POST",
        "payload_base": BASE_PAYLOAD_BY_DOCUMENT,
        "modifications": [("setear", "document_type", "1")],
        "expected_http": 200,
        "expected_code": "DCD-OK",
        "expected_response": [{"debit_card": {}, "client": {"document_type": "1"}}]
    },
    {
        "id": "C200-03",
        "requisito": "by-document - Género válido",
        "descripcion": "Consulta exitosa especificando género válido (M o F)",
        "endpoint": "/by-document",
        "method": "POST",
        "payload_base": BASE_PAYLOAD_BY_DOCUMENT,
        "modifications": [("setear", "gender", "M")],
        "expected_http": 200,
        "expected_code": "DCD-OK",
        "expected_response": [{"client": {"gender": "M"}}]
    },
    {
        "id": "C200-04",
        "requisito": "by-document - Cliente con múltiples tarjetas",
        "descripcion": "Consulta exitosa retornando el listado completo de tarjetas asociadas a un mismo cliente",
        "endpoint": "/by-document",
        "method": "POST",
        "payload_base": BASE_PAYLOAD_BY_DOCUMENT,
        "modifications": [("setear", "document_number", 30111222)],
        "expected_http": 200,
        "expected_code": "DCD-OK",
        "expected_response": [{"debit_card": {}}, {"debit_card": {}}]
    },
    {
        "id": "C200-05",
        "requisito": "by-document - Header Company=PRISMA",
        "descripcion": "Consulta exitosa enviando header company=PRISMA y datos válidos del cliente",
        "endpoint": "/by-document",
        "method": "POST",
        "payload_base": BASE_PAYLOAD_BY_DOCUMENT,
        "modifications": [],
        "expected_http": 200,
        "expected_code": "DCD-OK",
        "expected_response": [{"client": {}}]
    },
    {
        "id": "C200-06",
        "requisito": "by-document - Header PRISMA + bank_code genérico P01",
        "descripcion": "Consulta exitosa con Header PRISMA y bank_code P01 devolviendo tarjetas de todos los bancos del cliente",
        "endpoint": "/by-document",
        "method": "POST",
        "payload_base": BASE_PAYLOAD_BY_DOCUMENT,
        "modifications": [("setear", "bank_code", "P01")],
        "expected_http": 200,
        "expected_code": "DCD-OK",
        "expected_response": [{"debit_card": {}}]
    },
    {
        "id": "C400-08",
        "requisito": "by-document - Tipo de documento inválido",
        "descripcion": "Consulta rechazada por enviar un tipo de documento no contemplado (ej: 99)",
        "endpoint": "/by-document",
        "method": "POST",
        "payload_base": BASE_PAYLOAD_BY_DOCUMENT,
        "modifications": [("setear", "document_type", "99")],
        "expected_http": 400,
        "expected_code": "DCD-BAD_REQUEST",
        "expected_response": {"error": {"message": "Invalid Client"}}
    },
    {
        "id": "C400-09",
        "requisito": "by-document - document_number inválido",
        "descripcion": "Consulta rechazada por incluir letras o caracteres especiales en el número de documento",
        "endpoint": "/by-document",
        "method": "POST",
        "payload_base": BASE_PAYLOAD_BY_DOCUMENT,
        "modifications": [("setear", "document_number", "34019031ABC")],
        "expected_http": 400,
        "expected_code": "DCD-BAD_REQUEST",
        "expected_response": {"error": {"message": "Invalid Client"}}
    },
    {
        "id": "C400-10",
        "requisito": "by-document - Género inválido",
        "descripcion": "Consulta rechazada por enviar género incorrecto o no registrado (ej: X)",
        "endpoint": "/by-document",
        "method": "POST",
        "payload_base": BASE_PAYLOAD_BY_DOCUMENT,
        "modifications": [("setear", "gender", "X")],
        "expected_http": 400,
        "expected_code": "DCD-BAD_REQUEST",
        "expected_response": {"error": {"message": "Invalid Client"}}
    },
    {
        "id": "C400-11",
        "requisito": "by-document - Cliente inexistente",
        "descripcion": "Consulta rechazada por número de documento inexistente (CLIENT NOT FOUND)",
        "endpoint": "/by-document",
        "method": "POST",
        "payload_base": BASE_PAYLOAD_BY_DOCUMENT,
        "modifications": [("setear", "document_number", 99999999)],
        "expected_http": 400,
        "expected_code": "DCD-BAD_REQUEST",
        "expected_response": {"error": {"message": "Invalid Client"}}
    },
    {
        "id": "C400-12",
        "requisito": "by-document - Sin document_type",
        "descripcion": "Consulta rechazada al omitir el campo obligatorio document_type",
        "endpoint": "/by-document",
        "method": "POST",
        "payload_base": BASE_PAYLOAD_BY_DOCUMENT,
        "modifications": [("borrar", "document_type")],
        "expected_http": 400,
        "expected_code": "DCD-BAD_REQUEST",
        "expected_response": {"error": {"title": "Bad Request", "message": "Validation failed"}}
    },
    {
        "id": "C400-13",
        "requisito": "by-document - Sin document_number",
        "descripcion": "Consulta rechazada al omitir el campo obligatorio document_number",
        "endpoint": "/by-document",
        "method": "POST",
        "payload_base": BASE_PAYLOAD_BY_DOCUMENT,
        "modifications": [("borrar", "document_number")],
        "expected_http": 400,
        "expected_code": "DCD-BAD_REQUEST",
        "expected_response": {"error": {"title": "Bad Request", "message": "Validation failed"}}
    },
    {
        "id": "C400-14",
        "requisito": "by-document - Sin género ni fecha de nacimiento",
        "descripcion": "Consulta rechazada al omitir simultáneamente gender y birth_date (Regla: al menos uno es requerido)",
        "endpoint": "/by-document",
        "method": "POST",
        "payload_base": BASE_PAYLOAD_BY_DOCUMENT,
        "modifications": [("borrar", "gender"), ("borrar", "birth_date")],
        "expected_http": 400,
        "expected_code": "DCD-BAD_REQUEST",
        "expected_response": {"error": {"title": "Bad Request", "message": "Validation failed"}}
    },
    {
        "id": "C400-15",
        "requisito": "by-document - Header PRISMA + banco específico no autorizado",
        "descripcion": "Rechazo según configuración de Access Validation si Prisma consulta un banco no vinculado",
        "endpoint": "/by-document",
        "method": "POST",
        "payload_base": BASE_PAYLOAD_BY_DOCUMENT,
        "modifications": [("setear", "bank_code", "088")],
        "expected_http": 400,
        "expected_code": "DCD-BAD_REQUEST",
        "expected_response": {"error": {"message": "Invalid Data"}}
    },
    {
        "id": "C401-01",
        "requisito": "by-document - Bearer Token inválido",
        "descripcion": "Rechazo de acceso por enviar un token Bearer expirado o no autorizado",
        "endpoint": "/by-document",
        "method": "POST",
        "payload_base": BASE_PAYLOAD_BY_DOCUMENT,
        "modifications": [],
        "headers_override": {
            **DEFAULT_HEADERS,
            "Authorization": "Bearer token_invalido_12345"
        },
        "expected_http": 401,
        "expected_code": "UNAUTHORIZED",
        "expected_response": {"error": {"title": "Unauthorized"}}
    }
]

# Modificadores dinámicos para los Test Cases
for tc in TEST_CASES:
    if "headers_override" not in tc:
        tc["headers_override"] = DEFAULT_HEADERS.copy()
        
    if tc.get("method", "POST") == "POST":
        base_payload = tc.get("payload_base", BASE_PAYLOAD_BY_DOCUMENT)
        mods = tc.get("modifications", [])
        
        tc["modificador"] = lambda p, m=mods, b=base_payload: (
            p.clear(), 
            p.update(copy.deepcopy(b)), 
            aplicar_modificaciones(p, m)
        )