import copy

# ======================================================
# OBJETO BASE REUTILIZABLE
# ======================================================
BASE_PAYLOAD = {
    "client": {
        "document_type": "DNI",
        "document_number": 13722583,
        "gender": "M"
    },
    "card_details": {
        "bin": "451758",
        "last_four_digits": "0722"
    },
    "ip": "198.51.100.42",
    "reason": 2
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

TEST_CASES = [

    # =========================================================================
    # ---------- C200 – CASOS EXITOSOS (HTTP 200) ----------
    # =========================================================================
    {
        "id": "C200-01",
        "requisito": "Happy Path / Estado Tarjeta",
        "descripcion": "Denunciar tarjeta Activa (estado=1) por Extravío (reason=2)",
        "expected_code": "200",
        "expected_response": "{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}",
        "modificador": setear("reason", 2)
    },
    {
        "id": "C200-02",
        "requisito": "Happy Path / Estado Tarjeta",
        "descripcion": "Denunciar tarjeta Activa (estado=1) por Robo (reason=3)",
        "expected_code": "200",
        "expected_response": "{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}",
        "modificador": setear("reason", 3)
    },
    {
        "id": "C200-03",
        "requisito": "Happy Path / Estado Tarjeta",
        "descripcion": "Denunciar tarjeta Activa (estado=1) por Fraude (reason=6)",
        "expected_code": "200",
        "expected_response": "{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}",
        "modificador": setear("reason", 6)
    },
    {
        "id": "C200-04",
        "requisito": "Estado Tarjeta",
        "descripcion": "Denunciar tarjeta Restringida Extracciones (estado=4) por Extravío",
        "expected_code": "200",
        "expected_response": "{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}",
        "modificador": setear("reason", 2) # Depende del estado mockeado en la tarjeta asociada
    },
    {
        "id": "C200-05",
        "requisito": "Estado Tarjeta",
        "descripcion": "Denunciar tarjeta Restringida Extracciones (estado=4) por Robo",
        "expected_code": "200",
        "expected_response": "{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}",
        "modificador": setear("reason", 3)
    },
    {
        "id": "C200-06",
        "requisito": "Estado Tarjeta",
        "descripcion": "Denunciar tarjeta Restringida Extracciones (estado=4) por Fraude",
        "expected_code": "200",
        "expected_response": "{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}",
        "modificador": setear("reason", 6)
    },
    {
        "id": "C200-07",
        "requisito": "Estado Tarjeta",
        "descripcion": "Denunciar tarjeta Cerrada (estado=9) por Extravío",
        "expected_code": "200",
        "expected_response": "{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}",
        "modificador": setear("reason", 2)
    },
    {
        "id": "C200-08",
        "requisito": "Estado Tarjeta",
        "descripcion": "Denunciar tarjeta Cerrada (estado=9) por Robo",
        "expected_code": "200",
        "expected_response": "{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}",
        "modificador": setear("reason", 3)
    },
    {
        "id": "C200-09",
        "requisito": "Estado Tarjeta",
        "descripcion": "Denunciar tarjeta Cerrada (estado=9) por Fraude",
        "expected_code": "200",
        "expected_response": "{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}",
        "modificador": setear("reason", 6)
    },
    {
        "id": "C200-10",
        "requisito": "Coincidencia Tarjeta",
        "descripcion": "Cliente con múltiples tarjetas donde sólo una coincide con BIN + últimos 4",
        "expected_code": "200",
        "expected_response": "{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}",
        "modificador": lambda p: p  
    },
    {
        "id": "C200-11",
        "requisito": "Longitud BIN",
        "descripcion": "BIN de 6 dígitos válido",
        "expected_code": "200",
        "expected_response": "{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}",
        "modificador": setear("card_details.bin", "451758")
    },
    {
        "id": "C200-12",
        "requisito": "Longitud BIN",
        "descripcion": "BIN de 8 dígitos válido",
        "expected_code": "200",
        "expected_response": "{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}",
        "modificador": setear("card_details.bin", "45175812")
    },
    {
        "id": "C200-13",
        "requisito": "Flujo Desacoplado",
        "descripcion": "Cliente sin usuario UDF (Tarjeta existente en base propia)",
        "expected_code": "200",
        "expected_response": "{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}",
        "modificador": lambda p: p
    },
    {
        "id": "C200-14",
        "requisito": "Tipos de documento válidos",
        "descripcion": "document_type=DNI",
        "expected_code": "200",
        "expected_response": "{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}",
        "modificador": setear("client.document_type", "DNI")
    },
    {
        "id": "C200-15",
        "requisito": "Tipos de documento válidos",
        "descripcion": "document_type=CI",
        "expected_code": "200",
        "expected_response": "{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}",
        "modificador": setear("client.document_type", "CI")
    },
    {
        "id": "C200-16",
        "requisito": "Tipos de documento válidos",
        "descripcion": "document_type=PAS",
        "expected_code": "200",
        "expected_response": "{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}",
        "modificador": setear("client.document_type", "PAS")
    },
    {
        "id": "C200-17",
        "requisito": "Tipos de documento válidos",
        "descripcion": "document_type=LC",
        "expected_code": "200",
        "expected_response": "{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}",
        "modificador": setear("client.document_type", "LC")
    },
    {
        "id": "C200-18",
        "requisito": "Tipos de documento válidos",
        "descripcion": "document_type=LE",
        "expected_code": "200",
        "expected_response": "{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}",
        "modificador": setear("client.document_type", "LE")
    },
    {
        "id": "C200-19",
        "requisito": "Tipos de documento válidos",
        "descripcion": "document_type=CUIT",
        "expected_code": "200",
        "expected_response": "{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}",
        "modificador": setear("client.document_type", "CUIT")
    },
    {
        "id": "C200-20",
        "requisito": "Tipos de documento válidos",
        "descripcion": "document_type=CUIL",
        "expected_code": "200",
        "expected_response": "{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}",
        "modificador": setear("client.document_type", "CUIL")
    },
    {
        "id": "C200-21",
        "requisito": "Género válido",
        "descripcion": "gender=M",
        "expected_code": "200",
        "expected_response": "{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}",
        "modificador": setear("client.gender", "M")
    },
    {
        "id": "C200-22",
        "requisito": "Género válido",
        "descripcion": "gender=F",
        "expected_code": "200",
        "expected_response": "{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}",
        "modificador": setear("client.gender", "F")
    },
    {
        "id": "C200-23",
        "requisito": "Género válido",
        "descripcion": "gender=X",
        "expected_code": "200",
        "expected_response": "{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}",
        "modificador": setear("client.gender", "X")
    },

    # =========================================================================
    # ---------- C400 – CASOS DE NEGOCIO (TARJETA NO DENUNCIABLE) ----------
    # =========================================================================
    {
        "id": "C400-01",
        "requisito": "Error de negocio",
        "descripcion": "Intentar denunciar tarjeta ya denunciada estado=2 (Extraviada)",
        "expected_code": "DTC-400",
        "expected_response": "{'errors': [{'status': '400', 'code': 'DTC-400', 'title': 'Card Already Reported (B28)'}]}",
        "modificador": lambda p: p  # Requiere tarjeta previamente en estado 2
    },
    {
        "id": "C400-02",
        "requisito": "Error de negocio",
        "descripcion": "Intentar denunciar tarjeta ya denunciada estado=3 (Robada)",
        "expected_code": "DTC-400",
        "expected_response": "{'errors': [{'status': '400', 'code': 'DTC-400', 'title': 'Card Already Reported (B28)'}]}",
        "modificador": lambda p: p  # Requiere tarjeta previamente en estado 3
    },
    {
        "id": "C400-03",
        "requisito": "Error de negocio",
        "descripcion": "Intentar denunciar tarjeta ya denunciada estado=6 (Inhabilitada)",
        "expected_code": "DTC-400",
        "expected_response": "{'errors': [{'status': '400', 'code': 'DTC-400', 'title': 'Card Already Reported (B28)'}]}",
        "modificador": lambda p: p  # Requiere tarjeta previamente en estado 6
    },
    {
        "id": "C400-04",
        "requisito": "Error de negocio",
        "descripcion": "Intentar denunciar tarjeta Apagada estado=7",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'Operación no permitida según negocio.'}",
        "modificador": lambda p: p
    },
    {
        "id": "C400-05",
        "requisito": "Error de negocio",
        "descripcion": "Intentar denunciar tarjeta Inactiva estado=0",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'Operación no permitida.'}",
        "modificador": lambda p: p
    },
    {
        "id": "C400-06",
        "requisito": "Error de negocio",
        "descripcion": "Reintentar denunciar una tarjeta ya denunciada previamente por la API",
        "expected_code": "DTC-400",
        "expected_response": "{'errors': [{'status': '400', 'code': 'DTC-400', 'title': 'Card Already Reported'}]}",
        "modificador": lambda p: p
    },

    # =========================================================================
    # ---------- C400 – CASOS DE VALIDACIÓN (CONTRATO / VALORES) ----------
    # =========================================================================
    {
        "id": "C400-07",
        "requisito": "Campo inválido",
        "descripcion": "reason=1",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'Validation Failed'}",
        "modificador": setear("reason", 1)
    },
    {
        "id": "C400-08",
        "requisito": "Campo inválido",
        "descripcion": "reason=4",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'Validation Failed'}",
        "modificador": setear("reason", 4)
    },
    {
        "id": "C400-09",
        "requisito": "Campo inválido",
        "descripcion": "reason=5",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'Validation Failed'}",
        "modificador": setear("reason", 5)
    },
    {
        "id": "C400-10",
        "requisito": "Campo inválido",
        "descripcion": "reason=99",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'Validation Failed'}",
        "modificador": setear("reason", 99)
    },
    {
        "id": "C400-11",
        "requisito": "Campo inválido",
        "descripcion": "reason=-1",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'Validation Failed'}",
        "modificador": setear("reason", -1)
    },
    {
        "id": "C400-12",
        "requisito": "Formato inválido",
        "descripcion": "reason=\"A\"",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'Validation Failed'}",
        "modificador": setear("reason", "A")
    },
    {
        "id": "C400-13",
        "requisito": "Campo requerido",
        "descripcion": "reason nulo",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'Validation Failed'}",
        "modificador": setear("reason", None)
    },
    {
        "id": "C400-14",
        "requisito": "Campo requerido",
        "descripcion": "bank_code ausente",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'Bank code is required'}",
        "modificador": lambda p: p,
        "url_override": "https://api-qa.newpay.com.ar/v1/debit_lost_stolen_card_reporting/"
    },
    {
        "id": "C400-15",
        "requisito": "Longitud inválida",
        "descripcion": "bank_code=12",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400'}",
        "modificador": lambda p: p  # Generalmente manejado vía URL override si aplica
    },
    {
        "id": "C400-16",
        "requisito": "Longitud inválida",
        "descripcion": "bank_code=1234",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400'}",
        "modificador": lambda p: p
    },
    {
        "id": "C400-17",
        "requisito": "Formato inválido",
        "descripcion": "bank_code=ABC",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400'}",
        "modificador": lambda p: p
    },
    {
        "id": "C400-18",
        "requisito": "Campo requerido",
        "descripcion": "client ausente",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'Client information is required'}",
        "modificador": borrar("client")
    },
    {
        "id": "C400-19",
        "requisito": "Campo requerido",
        "descripcion": "document_type ausente",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'Document type is required'}",
        "modificador": borrar("client.document_type")
    },
    {
        "id": "C400-20",
        "requisito": "Formato inválido",
        "descripcion": "document_type=ABC",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400'}",
        "modificador": setear("client.document_type", "ABC")
    },
    {
        "id": "C400-21",
        "requisito": "Campo requerido",
        "descripcion": "document_number ausente",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'Document number is required'}",
        "modificador": borrar("client.document_number")
    },
    {
        "id": "C400-22",
        "requisito": "Longitud inválida",
        "descripcion": "document_number=1234",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400'}",
        "modificador": setear("client.document_number", 1234)
    },
    {
        "id": "C400-23",
        "requisito": "Longitud inválida",
        "descripcion": "document_number=1234567890123",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'At this time the selected transaction cannot be made. The data entered is incorrect or exceeds the maximum length.'}",
        "modificador": setear("client.document_number", 1234567890123)
    },
    {
        "id": "C400-24",
        "requisito": "Formato inválido",
        "descripcion": "document_number=\"ABC123\"",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'The transaction is rejected due to a problem in the format of the message.'}",
        "modificador": setear("client.document_number", "ABC123")
    },
    {
        "id": "C400-25",
        "requisito": "Campo requerido",
        "descripcion": "gender ausente",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'Gender is required'}",
        "modificador": borrar("client.gender")
    },
    {
        "id": "C400-26",
        "requisito": "Formato inválido",
        "descripcion": "gender=Z",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'Invalid gender value'}",
        "modificador": setear("client.gender", "Z")
    },
    {
        "id": "C400-27",
        "requisito": "Campo requerido",
        "descripcion": "card_details ausente",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'Card details are required'}",
        "modificador": borrar("card_details")
    },
    {
        "id": "C400-28",
        "requisito": "Campo requerido",
        "descripcion": "bin ausente",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'Card bin is required'}",
        "modificador": borrar("card_details.bin")
    },
    {
        "id": "C400-29",
        "requisito": "Longitud inválida",
        "descripcion": "bin=12345",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'Invalid BIN length'}",
        "modificador": setear("card_details.bin", "12345")
    },
    {
        "id": "C400-30",
        "requisito": "Longitud inválida",
        "descripcion": "bin=1234567",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'Invalid BIN length'}",
        "modificador": setear("card_details.bin", "1234567")
    },
    {
        "id": "C400-31",
        "requisito": "Formato inválido",
        "descripcion": "bin=ABCDEF",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'The transaction is rejected due to a problem in the format of the message.'}",
        "modificador": setear("card_details.bin", "ABCDEF")
    },
    {
        "id": "C400-32",
        "requisito": "Campo requerido",
        "descripcion": "last_four_digits ausente",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'Last four digits is required'}",
        "modificador": borrar("card_details.last_four_digits")
    },
    {
        "id": "C400-33",
        "requisito": "Longitud inválida",
        "descripcion": "last_four_digits=123",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'Invalid last four digits length'}",
        "modificador": setear("card_details.last_four_digits", "123")
    },
    {
        "id": "C400-34",
        "requisito": "Longitud inválida",
        "descripcion": "last_four_digits=12345",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'Invalid last four digits length'}",
        "modificador": setear("card_details.last_four_digits", "12345")
    },
    {
        "id": "C400-35",
        "requisito": "Formato inválido",
        "descripcion": "last_four_digits=ABCD",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'The transaction is rejected due to a problem in the format of the message.'}",
        "modificador": setear("card_details.last_four_digits", "ABCD")
    },
    {
        "id": "C400-36",
        "requisito": "Campo requerido",
        "descripcion": "ip ausente",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'IP address is required'}",
        "modificador": borrar("ip")
    },
    {
        "id": "C400-37",
        "requisito": "Formato inválido",
        "descripcion": "ip=999.999",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'The transaction is rejected due to a problem in the format of the message.'}",
        "modificador": setear("ip", "999.999")
    },
    {
        "id": "C400-38",
        "requisito": "Longitud inválida",
        "descripcion": "ip=999.999.999.999.999",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'The transaction is rejected due to a problem in the format of the message.'}",
        "modificador": setear("ip", "999.999.999.999.999")
    },
    {
        "id": "C400-39",
        "requisito": "Atributos extra",
        "descripcion": "Request contiene campos no definidos (ejemplo afip.cuit)",
        "expected_code": "DTC-400",
        "expected_response": "{'code': 'DTC-400', 'message': 'Rechazo por contrato'}",
        "modificador": lambda p: p.update({"afip": {"cuit": "20123456789"}}) or p
    },

    # =========================================================================
    # ---------- C401 – ERRORES DE AUTENTICACIÓN ----------
    # =========================================================================
    {
        "id": "C401-01",
        "requisito": "Autenticación",
        "descripcion": "Token ausente",
        "expected_code": "APIM-401",
        "expected_response": "{'message': 'Unauthorized'}",
        "modificador": lambda p: p,
        "headers_override": {"Content-Type": "application/json"}
    },
    {
        "id": "C401-02",
        "requisito": "Autenticación",
        "descripcion": "Token inválido",
        "expected_code": "APIM-401",
        "expected_response": "{'message': 'Unauthorized'}",
        "modificador": lambda p: p,
        "headers_override": {"Authorization": "Bearer token_invalido", "Content-Type": "application/json"}
    },
    {
        "id": "C401-03",
        "requisito": "Autenticación",
        "descripcion": "OAuth expirado",
        "expected_code": "APIM-401",
        "expected_response": "{'message': 'Unauthorized'}",
        "modificador": lambda p: p,
        "headers_override": {"Authorization": "Bearer token_expirado", "Content-Type": "application/json"}
    },
    {
        "id": "C401-04",
        "requisito": "Autenticación",
        "descripcion": "API Key inválida",
        "expected_code": "APIM-401",
        "expected_response": "{'message': 'Unauthorized'}",
        "modificador": lambda p: p,
        "headers_override": {"x-api-key": "invalid_key", "Content-Type": "application/json"}
    },
    {
        "id": "—C401-05",
        "requisito": "Autenticación",
        "descripcion": "x-apip-cuit ausente",
        "expected_code": "APIM-401",
        "expected_response": "{'message': 'Unauthorized'}",
        "modificador": lambda p: p  # Requiere remover el header específico en la lógica de request
    },

    # =========================================================================
    # ---------- C404 – ERRORES DE RECURSO NO ENCONTRADO ----------
    # =========================================================================
    {
        "id": "C404-01",
        "requisito": "Recurso no encontrado",
        "descripcion": "La tarjeta no pertenece al cliente (B50)",
        "expected_code": "DTC-404",
        "expected_response": "{'errors': [{'status': '404', 'code': 'DTC-404', 'title': 'Cards Not Found'}]}",
        "modificador": lambda p: p["client"].update({"document_number": 99999999}) or p
    },
    {
        "id": "C404-02",
        "requisito": "Recurso no encontrado",
        "descripcion": "BIN válido pero de otra tarjeta",
        "expected_code": "DTC-404",
        "expected_response": "{'errors': [{'status': '404', 'code': 'DTC-404'}]}",
        "modificador": setear("card_details.bin", "444444")
    },
    {
        "id": "C404-03",
        "requisito": "Recurso no encontrado",
        "descripcion": "Ultimos 4 válidos pero de otra tarjeta",
        "expected_code": "DTC-404",
        "expected_response": "{'errors': [{'status': '404', 'code': 'DTC-404'}]}",
        "modificador": setear("card_details.last_four_digits", "1111")
    },
    {
        "id": "C404-04",
        "requisito": "Recurso no encontrado",
        "descripcion": "Cliente sin tarjetas asociadas",
        "expected_code": "DTC-404",
        "expected_response": "{'errors': [{'status': '404', 'code': 'DTC-404'}]}",
        "modificador": setear("client.document_number", 11112222) # Un cliente real simulado sin productos
    },
    {
        "id": "C404-05",
        "requisito": "Recurso no encontrado",
        "descripcion": "BIN=999999 y last_four_digits=0000 (tarjeta inexistente)",
        "expected_code": "DTC-404",
        "expected_response": "{'errors': [{'status': '404', 'code': 'DTC-404', 'title': 'There is no information for the query made.'}]}",
        "modificador": lambda p: p["card_details"].update({"bin": "999999", "last_four_digits": "0000"}) or p
    },
    {
        "id": "C404-06",
        "requisito": "Recurso no encontrado",
        "descripcion": "No existe coincidencia entre BIN + últimos 4",
        "expected_code": "DTC-404",
        "expected_response": "{'errors': [{'status': '404', 'code': 'DTC-404'}]}",
        "modificador": lambda p: p["card_details"].update({"bin": "451758", "last_four_digits": "9999"}) or p
    },

    # =========================================================================
    # ---------- C500 – ERRORES INTERNOS DE SERVIDOR ----------
    # =========================================================================
    {
        "id": "C500-01",
        "requisito": "Error de servidor",
        "descripcion": "Error B54 Base de Datos",
        "expected_code": "DTC-DATA BASE ERROR",
        "expected_response": "{'errors': [{'status': '500', 'code': 'DTC-DATA BASE ERROR', 'title': 'System error.'}]}",
        "modificador": lambda p: p  # Requiere inyección de fallas/mock en base de datos
    },
    {
        "id": "C500-02",
        "requisito": "Error de servidor",
        "descripcion": "Error A99 Formato Request",
        "expected_code": "DTC-500",
        "expected_response": "{'errors': [{'status': '500', 'code': 'DTC-500', 'title': 'System error'}]}",
        "modificador": lambda p: p
    },
    {
        "id": "C500-03",
        "requisito": "Error de servidor",
        "descripcion": "Error al descifrar PAN",
        "expected_code": "DTC-500",
        "expected_response": "{'code': 'DTC-500'}",
        "modificador": lambda p: p
    },
    {
        "id": "C500-04",
        "requisito": "Error de servidor",
        "descripcion": "Error al cifrar PAN",
        "expected_code": "DTC-500",
        "expected_response": "{'code': 'DTC-500'}",
        "modificador": lambda p: p
    },
    {
        "id": "C500-05",
        "requisito": "Error de servidor",
        "descripcion": "Timeout Centro de Servicios",
        "expected_code": "DTC-500",
        "expected_response": "{'code': 'DTC-500'}",
        "modificador": lambda p: p
    },
    {
        "id": "C500-06",
        "requisito": "Error de servidor",
        "descripcion": "Centro de Servicios caído",
        "expected_code": "DTC-500",
        "expected_response": "{'code': 'DTC-500'}",
        "modificador": lambda p: p
    },
    {
        "id": "C500-07",
        "requisito": "Error de servidor",
        "descripcion": "Timeout Tandem",
        "expected_code": "DTC-500",
        "expected_response": "{'code': 'DTC-500'}",
        "modificador": lambda p: p
    },
    {
        "id": "C500-08",
        "requisito": "Error de servidor",
        "descripcion": "Error Access Validation",
        "expected_code": "DTC-500",
        "expected_response": "{'code': 'DTC-500'}",
        "modificador": lambda p: p
    },
    {
        "id": "C500-09",
        "requisito": "Error de servidor",
        "descripcion": "Código upstream no mapeado",
        "expected_code": "DTC-500",
        "expected_response": "{'code': 'DTC-500'}",
        "modificador": lambda p: p
    },
    {
        "id": "C500-10",
        "requisito": "Error de servidor",
        "descripcion": "Error SQL durante consulta de tarjetas",
        "expected_code": "DTC-500",
        "expected_response": "{'code': 'DTC-500'}",
        "modificador": lambda p: p
    },
    {
        "id": "C500-11",
        "requisito": "Error de servidor",
        "descripcion": "Error Secret Manager AES_KEY_DB",
        "expected_code": "DTC-500",
        "expected_response": "{'code': 'DTC-500'}",
        "modificador": lambda p: p
    },
    {
        "id": "C500-12",
        "requisito": "Error de servidor",
        "descripcion": "Error Secret Manager AES_KEY_DCD",
        "expected_code": "DTC-500",
        "expected_response": "{'code': 'DTC-500'}",
        "modificador": lambda p: p
    },
    {
        "id": "C500-13",
        "requisito": "Error de servidor",
        "descripcion": "Error armando ISO en Centro de Servicios",
        "expected_code": "DTC-500",
        "expected_response": "{'code': 'DTC-500'}",
        "modificador": lambda p: p
    }
]