import copy
# ======================================================
# OBJETO BASE REUTILIZABLE
# ======================================================
BASE_PAYLOAD = { 
    "origin": { 
        "channel": "Z", 
        "ip_address": "10.10.10.3" 
    }, 
    "client": { 
        "document_number": "26778152", 
        "gender": "F", 
        "document_type": "DNI" 
    }, 
    "card": { 
        "card_number": "IicQHd8TzbxmHGan/a78qHzxRFTZQW7wHVruwUmEDGY=abcdefgh12345678", 
        "member": "001", 
        "expiration_date": "1126" 
  } 
} 

# ======================================================
# MODIFICADORES 
# ======================================================

def borrar(path):
    def f(payload):
        keys = path.split(".")
        ref = payload

        for k in keys[:-1]:
            if isinstance(ref, list):
                ref = ref[int(k)]
            else:
                ref = ref[k]

        last = keys[-1]
        if isinstance(ref, list):
            del ref[int(last)]
        else:
            del ref[last]

    return f


def setear(path, value):
    def f(payload):
        keys = path.split(".")
        ref = payload

        for k in keys[:-1]:
            if isinstance(ref, list):
                ref = ref[int(k)]
            else:
                ref = ref[k]

        last = keys[-1]
        if isinstance(ref, list):
            ref[int(last)] = value
        else:
            ref[last] = value

    return f

# ======================================================
# CASOS DE PRUEBA 
# ======================================================

TEST_CASES = [

    # ---------- C200 – CASOS EXITOSOS ----------
    {"id":"C200-01 Happy Path - Consulta exitosa",
     "requisito":"Consulta exitosa de código de seguridad",
     "descripcion":"Consulta de código de seguridad con todos los datos correctos",
     "expected_code":"200",
     "expected_response":"{'card_number': 'string', 'member': '001', 'security_code': '123'}",
     "modificador":lambda p: p},

    # ---------- C400 – ERRORES DE NEGOCIO (mapeo de errores) ----------
    {"id":"C400-01 Transacción no habilitada",
     "requisito":"Error de negocio",
     "descripcion":"Transacción inhabilitada para la Institución - Legacy Code B57",
     "expected_code":"DCSC-TRX_NOT_ENABLED",
     "expected_response":"{'error': {'type': 'string', 'code': 'DCSC-TRX_NOT_ENABLED', 'status': '400 BAD_REQUEST', 'title': 'Transaction not enabled', 'message': 'The selected operation is not enabled for the Institution', 'details': [{'message': 'string'}]}}",
     "modificador":lambda p: p},

    {"id":"C400-02 Tarjeta inválida",
     "requisito":"Error de negocio",
     "descripcion":"Tarjeta no válida o no pertenece a la institución - Legacy Code B65",
     "expected_code":"DCSC-INVALID_CARD",
     "expected_response":"{'error': {'type': 'string', 'code': 'DCSC-INVALID_CARD', 'status': '400 BAD_REQUEST', 'title': 'Invalid card', 'message': 'The inserted card is not valid.', 'details': [{'message': 'string'}]}}",
     "modificador":setear("card.card_number", "tarjeta_invalida_123456")},

    {"id":"C400-03 Error de base de datos",
     "requisito":"Error de negocio",
     "descripcion":"Problema con datos de la cuenta - Legacy Code B54",
     "expected_code":"DCSC-DATA_PROBLEM",
     "expected_response":"{'error': {'type': 'string', 'code': 'DCSC-DATA_PROBLEM', 'status': '400 BAD_REQUEST', 'title': 'Data problem', 'message': 'The account entered is not in our database or we cannot access its data.', 'details': [{'message': 'string'}]}}",
     "modificador":lambda p: p},

    {"id":"C400-04 Destino no disponible",
     "requisito":"Error de sistema",
     "descripcion":"Conexión con la institución caída - Legacy Code B72",
     "expected_code":"DCSC-DESTINATION_NOT_AVAILABLE",
     "expected_response":"{'error': {'type': 'string', 'code': 'DCSC-DESTINATION_NOT_AVAILABLE', 'status': '400 BAD_REQUEST', 'title': 'System error - Destination not available', 'message': 'The selected operation cannot be performed right now. Please retry again.', 'details': [{'message': 'string'}]}}",
     "modificador":lambda p: p},

    # ---------- CAMPOS REQUERIDOS ----------
    {"id":"C400-05 Origin requerido",
     "requisito":"Campo requerido",
     "descripcion":"Falta objeto origin completo",
     "expected_code":"DCSC-BAD_REQUEST",
     "expected_response":"{'error': {'type': 'string', 'code': 'DCSC-BAD_REQUEST', 'status': '400 BAD_REQUEST', 'title': 'Validation Failed', 'message': 'Validation Failed: At this time the selected transaction cannot be made. The data entered for \"origin\" is incorrect', 'details': [{'message': '\"origin\" is required'}]}}",
     "modificador":borrar("origin")},

    {"id":"C400-06 Channel requerido",
     "requisito":"Campo requerido",
     "descripcion":"Falta origin.channel",
     "expected_code":"DCSC-BAD_REQUEST",
     "expected_response":"{'error': {'type': 'string', 'code': 'DCSC-BAD_REQUEST', 'status': '400 BAD_REQUEST', 'title': 'Validation Failed', 'message': 'Validation Failed: At this time the selected transaction cannot be made. The data entered for \"origin.channel\" is incorrect', 'details': [{'message': '\"origin.channel\" is required'}]}}",
     "modificador":borrar("origin.channel")},

    {"id":"C400-07 IP Address requerido",
     "requisito":"Campo requerido",
     "descripcion":"Falta origin.ip_address",
     "expected_code":"DCSC-BAD_REQUEST",
     "expected_response":"{'error': {'type': 'string', 'code': 'DCSC-BAD_REQUEST', 'status': '400 BAD_REQUEST', 'title': 'Validation Failed', 'message': 'Validation Failed: At this time the selected transaction cannot be made. The data entered for \"origin.ip_address\" is incorrect', 'details': [{'message': '\"origin.ip_address\" is required'}]}}",
     "modificador":borrar("origin.ip_address")},

    {"id":"C400-08 Client requerido",
     "requisito":"Campo requerido",
     "descripcion":"Falta objeto client completo",
     "expected_code":"DCSC-BAD_REQUEST",
     "expected_response":"{'error': {'type': 'string', 'code': 'DCSC-BAD_REQUEST', 'status': '400 BAD_REQUEST', 'title': 'Validation Failed', 'message': 'Validation Failed: At this time the selected transaction cannot be made. The data entered for \"client\" is incorrect', 'details': [{'message': '\"client\" is required'}]}}",
     "modificador":borrar("client")},

    {"id":"C400-09 Document number requerido",
     "requisito":"Campo requerido",
     "descripcion":"Falta client.document_number",
     "expected_code":"DCSC-BAD_REQUEST",
     "expected_response":"{'error': {'type': 'string', 'code': 'DCSC-BAD_REQUEST', 'status': '400 BAD_REQUEST', 'title': 'Validation Failed', 'message': 'Validation Failed: At this time the selected transaction cannot be made. The data entered for \"client.document_number\" is incorrect', 'details': [{'message': '\"client.document_number\" is required'}]}}",
     "modificador":borrar("client.document_number")},

    {"id":"C400-10 Gender requerido",
     "requisito":"Campo requerido",
     "descripcion":"Falta client.gender",
     "expected_code":"DCSC-BAD_REQUEST",
     "expected_response":"{'error': {'type': 'string', 'code': 'DCSC-BAD_REQUEST', 'status': '400 BAD_REQUEST', 'title': 'Validation Failed', 'message': 'Validation Failed: At this time the selected transaction cannot be made. The data entered for \"client.gender\" is incorrect', 'details': [{'message': '\"client.gender\" is required'}]}}",
     "modificador":borrar("client.gender")},

    {"id":"C400-11 Document type requerido",
     "requisito":"Campo requerido",
     "descripcion":"Falta client.document_type",
     "expected_code":"DCSC-BAD_REQUEST",
     "expected_response":"{'error': {'type': 'string', 'code': 'DCSC-BAD_REQUEST', 'status': '400 BAD_REQUEST', 'title': 'Validation Failed', 'message': 'Validation Failed: At this time the selected transaction cannot be made. The data entered for \"client.document_type\" is incorrect', 'details': [{'message': '\"client.document_type\" is required'}]}}",
     "modificador":borrar("client.document_type")},

    {"id":"C400-12 Card requerido",
     "requisito":"Campo requerido",
     "descripcion":"Falta objeto card completo",
     "expected_code":"DCSC-BAD_REQUEST",
     "expected_response":"{'error': {'type': 'string', 'code': 'DCSC-BAD_REQUEST', 'status': '400 BAD_REQUEST', 'title': 'Validation Failed', 'message': 'Validation Failed: At this time the selected transaction cannot be made. The data entered for \"card\" is incorrect', 'details': [{'message': '\"card\" is required'}]}}",
     "modificador":borrar("card")},

    {"id":"C400-13 Card number requerido",
     "requisito":"Campo requerido",
     "descripcion":"Falta card.card_number",
     "expected_code":"DCSC-BAD_REQUEST",
     "expected_response":"{'error': {'type': 'string', 'code': 'DCSC-BAD_REQUEST', 'status': '400 BAD_REQUEST', 'title': 'Validation Failed', 'message': 'Validation Failed: At this time the selected transaction cannot be made. The data entered for \"card.member\" is incorrect', 'details': [{'message': '\"card.member\" is required'}]}}",
     "modificador":borrar("card.card_number")},

    {"id":"C400-14 Member requerido",
     "requisito":"Campo requerido",
     "descripcion":"Falta card.member",
     "expected_code":"DCSC-BAD_REQUEST",
     "expected_response":"{'error': {'type': 'string', 'code': 'DCSC-BAD_REQUEST', 'status': '400 BAD_REQUEST', 'title': 'Validation Failed', 'message': 'Validation Failed: At this time the selected transaction cannot be made. The data entered for \"card.member\" is incorrect', 'details': [{'message': '\"card.member\" is required'}]}}",
     "modificador":borrar("card.member")},

    {"id":"C400-15 Expiration date requerido",
     "requisito":"Campo requerido",
     "descripcion":"Falta card.expiration_date",
     "expected_code":"DCSC-BAD_REQUEST",
     "expected_response":"{'error': {'type': 'string', 'code': 'DCSC-BAD_REQUEST', 'status': '400 BAD_REQUEST', 'title': 'Validation Failed', 'message': 'Validation Failed: At this time the selected transaction cannot be made. The data entered for \"card.expiration_date\" is incorrect', 'details': [{'message': '\"card.expiration_date\" is required'}]}}",
     "modificador":borrar("card.expiration_date")},

    # ---------- FORMATO Y VALIDACIONES ----------
    {"id":"C400-16 Formato documento inválido",
     "requisito":"Formato inválido",
     "descripcion":"document_number con formato incorrecto (debe ser numérico)",
     "expected_code":"DCSC-BAD_REQUEST",
     "expected_response":"{'error': {'type': 'string', 'code': 'DCSC-BAD_REQUEST', 'status': '400 BAD_REQUEST', 'title': 'Validation Failed', 'message': 'Validation Failed: At this time the selected transaction cannot be made. The data entered for \"client.document_number\" is incorrect', 'details': [{'message': 'Invalid document number format'}]}}",
     "modificador":setear("client.document_number", "ABC123")},

    {"id":"C400-17 Gender inválido",
     "requisito":"Formato inválido",
     "descripcion":"gender con valor no permitido",
     "expected_code":"DCSC-BAD_REQUEST",
     "expected_response":"{'error': {'type': 'string', 'code': 'DCSC-BAD_REQUEST', 'status': '400 BAD_REQUEST', 'title': 'Validation Failed', 'message': 'Validation Failed: At this time the selected transaction cannot be made. The data entered for \"client.gender\" is incorrect', 'details': [{'message': 'Gender must be M, F or X'}]}}",
     "modificador":setear("client.gender", "Z")},

    {"id":"C400-18 Document type inválido",
     "requisito":"Formato inválido",
     "descripcion":"document_type con valor no permitido",
     "expected_code":"DCSC-BAD_REQUEST",
     "expected_response":"{'error': {'type': 'string', 'code': 'DCSC-BAD_REQUEST', 'status': '400 BAD_REQUEST', 'title': 'Validation Failed', 'message': 'Validation Failed: At this time the selected transaction cannot be made. The data entered for \"client.document_type\" is incorrect', 'details': [{'message': 'Invalid document type'}]}}",
     "modificador":setear("client.document_type", "INVALIDO")},

    {"id":"C400-19 Channel inválido",
     "requisito":"Formato inválido",
     "descripcion":"channel con valor no permitido",
     "expected_code":"DCSC-BAD_REQUEST",
     "expected_response":"{'error': {'type': 'string', 'code': 'DCSC-BAD_REQUEST', 'status': '400 BAD_REQUEST', 'title': 'Validation Failed', 'message': 'Validation Failed: At this time the selected transaction cannot be made. The data entered for \"origin.channel\" is incorrect', 'details': [{'message': 'Invalid channel'}]}}",
     "modificador":setear("origin.channel", "X")},

    {"id":"C400-20 IP address inválido",
     "requisito":"Formato inválido",
     "descripcion":"ip_address con formato inválido",
     "expected_code":"DCSC-BAD_REQUEST",
     "expected_response":"{'error': {'type': 'string', 'code': 'DCSC-BAD_REQUEST', 'status': '400 BAD_REQUEST', 'title': 'Validation Failed', 'message': 'Validation Failed: At this time the selected transaction cannot be made. The data entered for \"origin.ip_address\" is incorrect', 'details': [{'message': 'Invalid IP address format'}]}}",
     "modificador":setear("origin.ip_address", "999.999.999.999")},

    {"id":"C400-21 Member inválido",
     "requisito":"Formato inválido",
     "descripcion":"member con valor no permitido",
     "expected_code":"DCSC-INVALID_CARD",
     "expected_response":"{'error': {'type': 'string', 'code': 'DCSC-INVALID_CARD', 'status': '400 BAD_REQUEST', 'title': 'Invalid card', 'message': 'The inserted card is not valid.', 'details': [{'message': 'Invalid member'}]}}",
     "modificador":setear("card.member", "999")},

    {"id":"C400-22 Expiration date inválido",
     "requisito":"Formato inválido",
     "descripcion":"expiration_date con formato incorrecto",
     "expected_code":"DCSC-BAD_REQUEST",
     "expected_response":"{'error': {'type': 'string', 'code': 'DCSC-BAD_REQUEST', 'status': '400 BAD_REQUEST', 'title': 'Validation Failed', 'message': 'Validation Failed: At this time the selected transaction cannot be made. The data entered for \"card.expiration_date\" is incorrect', 'details': [{'message': 'Invalid expiration date format (MMYY expected)'}]}}",
     "modificador":setear("card.expiration_date", "13/25")},

    {"id":"C400-23 Expiration date vencida",
     "requisito":"Validación de negocio",
     "descripcion":"Tarjeta con fecha de vencimiento expirada",
     "expected_code":"DCSC-INVALID_CARD",
     "expected_response":"{'error': {'type': 'string', 'code': 'DCSC-INVALID_CARD', 'status': '400 BAD_REQUEST', 'title': 'Invalid card', 'message': 'The inserted card is not valid.', 'details': [{'message': 'Card has expired'}]}}",
     "modificador":setear("card.expiration_date", "0120")},  # Enero 2020 (expirada)

    # ---------- C401 – ERRORES DE AUTENTICACIÓN ----------
    {"id":"C401-01 Token ausente",
     "requisito":"Autenticación",
     "descripcion":"Request sin token de autorización",
     "expected_code":"401",
     "expected_response":"{'error': {'type': 'string', 'code': '401', 'status': '401 UNAUTHORIZED', 'title': 'Unauthorized', 'message': 'Missing or invalid authorization token'}}",
     "modificador":lambda p: p,
     "headers_override": {"Content-Type": "application/json"}},

    {"id":"C401-02 Token inválido",
     "requisito":"Autenticación",
     "descripcion":"Token inválido o expirado",
     "expected_code":"401",
     "expected_response":"{'error': {'type': 'string', 'code': '401', 'status': '401 UNAUTHORIZED', 'title': 'Unauthorized', 'message': 'Invalid authorization token'}}",
     "modificador":lambda p: p,
     "headers_override": {"Authorization": "Bearer token_invalido_123", "Content-Type": "application/json"}},

    # ---------- C500 – ERRORES DE SERVIDOR ----------
    {"id":"C500-01 Error de comunicación con host",
     "requisito":"Error de servidor",
     "descripcion":"Error de comunicación con el host",
     "expected_code":"DCSC-500",
     "expected_response":"{'error': {'type': 'string', 'code': 'DCSC-500', 'status': '500 INTERNAL_SERVER_ERROR', 'title': 'Host communication error', 'message': 'Error communicating with host', 'details': [{'message': 'Host communication error'}]}}",
     "modificador":lambda p: p},

    {"id":"C504-01 Gateway timeout",
     "requisito":"Error de servidor",
     "descripcion":"Timeout en gateway",
     "expected_code":"DCSC-504",
     "expected_response":"{'error': {'type': 'string', 'code': 'DCSC-504', 'status': '504 GATEWAY_TIMEOUT', 'title': 'Gateway timeout', 'message': 'Gateway timeout', 'details': [{'message': 'Gateway timeout'}]}}",
     "modificador":lambda p: p}
]
