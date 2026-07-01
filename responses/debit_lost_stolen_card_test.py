import copy

# ======================================================
# OBJETO BASE REUTILIZABLE
# ======================================================
BASE_PAYLOAD = {
    "client": {
        "document_type": "DNI",
        "document_number": 41805320,
        "gender": "M"
    },
    "card_details": {
        "bin": "442548",
        "last_four_digits": "9730"
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

# ======================================================
# CASOS DE PRUEBA 
# ======================================================

TEST_CASES = [

    # ---------- C200 – CASOS EXITOSOS ----------
    {"id":"C200-01 Denuncia extravío","requisito":"Happy Path","descripcion":"Denuncia de tarjeta por extravío (reason=2)","expected_code":"200","expected_response":"{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}","modificador":setear("reason",2)},
    
    {"id":"C200-02 Denuncia robo","requisito":"Happy Path","descripcion":"Denuncia de tarjeta por robo (reason=3)","expected_code":"200","expected_response":"{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}","modificador":setear("reason",3)},
    
    {"id":"C200-03 Denuncia fraude","requisito":"Happy Path","descripcion":"Denuncia de tarjeta por fraude (reason=6)","expected_code":"200","expected_response":"{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}","modificador":setear("reason",6)},
    
    {"id":"C200-04 Tipo Doc Válidos - DNI","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento DNI","expected_code":"200","expected_response":"{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}","modificador":setear("client.document_type","DNI")},
    {"id":"C200-04 Tipo Doc Válidos - CI","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento CI","expected_code":"200","expected_response":"{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}","modificador":setear("client.document_type","CI")},
    {"id":"C200-04 Tipo Doc Válidos - PAS","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento PAS","expected_code":"200","expected_response":"{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}","modificador":setear("client.document_type","PAS")},
    {"id":"C200-04 Tipo Doc Válidos - LC","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento LC","expected_code":"200","expected_response":"{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}","modificador":setear("client.document_type","LC")},
    {"id":"C200-04 Tipo Doc Válidos - LE","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento LE","expected_code":"200","expected_response":"{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}","modificador":setear("client.document_type","LE")},
    {"id":"C200-04 Tipo Doc Válidos - CUIT","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento CUIT","expected_code":"200","expected_response":"{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}","modificador":setear("client.document_type","CUIT")},
    {"id":"C200-04 Tipo Doc Válidos - CUIL","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento CUIL","expected_code":"200","expected_response":"{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}","modificador":setear("client.document_type","CUIL")},
    
    {"id":"C200-05 Gender Válidos - F","requisito":"Género válido","descripcion":"Enviar género Femenino","expected_code":"200","expected_response":"{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}","modificador":setear("client.gender","F")},
    {"id":"C200-05 Gender Válidos - M","requisito":"Género válido","descripcion":"Enviar género Masculino","expected_code":"200","expected_response":"{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}","modificador":setear("client.gender","M")},
    {"id":"C200-05 Gender Válidos - X","requisito":"Género válido","descripcion":"Enviar género Otro","expected_code":"200","expected_response":"{'ok': {'code': 'string', 'description': 'string', 'denunciation_code': 'string'}}","modificador":setear("client.gender","X")},

    # ---------- C400 – ERRORES DE NEGOCIO ----------
    {"id":"C400-01 Tarjeta ya denunciada","requisito":"Error de negocio","descripcion":"Tarjeta previamente denunciada - Legacy Code B28","expected_code":"DTC-400","expected_response":"{'errors': [{'status': '400', 'code': 'DTC-400', 'title': 'Card already reported'}]}","modificador":lambda p: p},
    
    {"id":"C400-02 Reason inválido","requisito":"Campo inválido","descripcion":"Valor de reason distinto a 2,3,6","expected_code":"DTC-500","expected_response":"{'code': 'DTC-500', 'message': 'Internal Server Error.'}","modificador":setear("reason",5)},
    
    {"id":"C400-03 Reason formato numérico","requisito":"Formato inválido","descripcion":"Reason con letras en lugar de números","expected_code":"DTC-500","expected_response":"{'code': 'DTC-500', 'message': 'Internal Server Error.'}","modificador":setear("reason","A")},
    
    {"id":"C400-04 Falta bank_code","requisito":"Campo requerido","descripcion":"Falta bank_code en URL","expected_code":"DTC-400","expected_response":"{'code': 'DTC-400', 'message': 'Bank code is required'}","modificador":lambda p: p, "url_override": "https://api-qa.newpay.com.ar/v1/debit_lost_stolen_card_reporting/"},

    # ---------- C404 – ERRORES DE RECURSO NO ENCONTRADO ----------
    {"id":"C404-01 Tarjeta no pertenece al usuario","requisito":"Recurso no encontrado","descripcion":"La tarjeta ingresada no está relacionada al usuario - Legacy Code B50","expected_code":"DTC-404","expected_response":"{'errors': [{'status': '404', 'code': 'DTC-404', 'title': 'Cards not found'}]}","modificador":lambda p: p["client"].update({"document_number": 99999999})},

    {"id":"C404-02 Tarjeta inexistente","requisito":"Recurso no encontrado","descripcion":"No hay información para la consulta realizada - Legacy Code B65","expected_code":"DTC-404","expected_response":"{'errors': [{'status': '404', 'code': 'DTC-404', 'title': 'There is no information for the query made.'}]}","modificador":lambda p: p["card_details"].update({"bin": "999999", "last_four_digits": "0000"})},

    # ---------- C500 – ERRORES DE SERVIDOR ----------
    {"id":"C500-01 Inconsistencia de datos","requisito":"Error de servidor","descripcion":"Error de sistema por inconsistencia de datos - Legacy Code B54","expected_code":"DTC-DATA BASE ERROR","expected_response":"{'errors': [{'status': '500', 'code': 'DTC-DATA BASE ERROR', 'title': 'System error.'}]}","modificador":lambda p: p},  # Depende del backend

    {"id":"C500-02 Error en formato del request","requisito":"Error de servidor","descripcion":"Error en el formato del request - Legacy Code A99","expected_code":"DTC-500","expected_response":"{'errors': [{'status': '500', 'code': 'DTC-500', 'title': 'System error'}]}","modificador":lambda p: p},  # Depende del backend

    # ---------- C401 – ERRORES DE AUTENTICACIÓN ----------
    {"id":"C401-01 Token ausente","requisito":"Autenticación","descripcion":"Request sin token de autorización","expected_code":"APIM-401","expected_response":"{'message': 'Unauthorized'}","modificador":lambda p: p, "headers_override": {"Content-Type": "application/json"}},

    {"id":"C401-02 Token inválido","requisito":"Autenticación","descripcion":"Token inválido","expected_code":"APIM-401","expected_response":"{'message': 'Unauthorized'}","modificador":lambda p: p, "headers_override": {"Authorization": "Bearer token_invalido", "Content-Type": "application/json"}},

    # ---------- CAMPOS REQUERIDOS ----------
    {"id":"C400-05 Client is required","requisito":"Campo requerido","descripcion":"Falta client","expected_code":"DTC-400","expected_response":"{'code': 'DTC-400', 'message': 'Client information is required'}","modificador":borrar("client")},
    
    {"id":"C400-06 Document type is required","requisito":"Campo requerido","descripcion":"Falta document_type","expected_code":"DTC-400","expected_response":"{'code': 'DTC-400', 'message': 'Document type is required'}","modificador":borrar("client.document_type")},
    
    {"id":"C400-07 Document number is required","requisito":"Campo requerido","descripcion":"Falta document_number","expected_code":"DTC-400","expected_response":"{'code': 'DTC-400', 'message': 'Document number is required'}","modificador":borrar("client.document_number")},
    
    {"id":"C400-08 Gender is required","requisito":"Campo requerido","descripcion":"Falta gender","expected_code":"DTC-400","expected_response":"{'code': 'DTC-400', 'message': 'Gender is required'}","modificador":borrar("client.gender")},
    
    {"id":"C400-09 Card details is required","requisito":"Campo requerido","descripcion":"Falta card_details","expected_code":"DTC-400","expected_response":"{'code': 'DTC-400', 'message': 'Card details are required'}","modificador":borrar("card_details")},
    
    {"id":"C400-10 Bin is required","requisito":"Campo requerido","descripcion":"Falta bin","expected_code":"DTC-400","expected_response":"{'code': 'DTC-400', 'message': 'Card bin is required'}","modificador":borrar("card_details.bin")},
    
    {"id":"C400-11 Last four digits is required","requisito":"Campo requerido","descripcion":"Falta last_four_digits","expected_code":"DTC-400","expected_response":"{'code': 'DTC-400', 'message': 'Last four digits is required'}","modificador":borrar("card_details.last_four_digits")},
    
    {"id":"C400-12 IP is required","requisito":"Campo requerido","descripcion":"Falta ip","expected_code":"DTC-400","expected_response":"{'code': 'DTC-400', 'message': 'IP address is required'}","modificador":borrar("ip")},
    
    {"id":"C400-13 Reason is required","requisito":"Campo requerido","descripcion":"Falta reason","expected_code":"DTC-500","expected_response":"{'code': 'DTC-500', 'message': 'Internal Server Error.'}","modificador":borrar("reason")},

    # ---------- LONGITUD ----------
    {"id":"C400-14 BIN length","requisito":"Longitud inválida","descripcion":"card_details.bin demasiado largo","expected_code":"DTC-400","expected_response":"{'code': 'DTC-400', 'message': 'Invalid BIN length'}","modificador":setear("card_details.bin","123456789")},
    
    {"id":"C400-15 Last4 length","requisito":"Longitud inválida","descripcion":"card_details.last_four_digits demasiado largo","expected_code":"DTC-400","expected_response":"{'code': 'DTC-400', 'message': 'Invalid last four digits length'}","modificador":setear("card_details.last_four_digits","12345")},
    
    {"id":"C400-16 Document number length","requisito":"Longitud inválida","descripcion":"document_number demasiado largo","expected_code":"DTC-400","expected_response":"{'code': 'DTC-400', 'message': 'At this time the selected transaction cannot be made. The data entered is incorrect or exceeds the maximum length.'}","modificador":setear("client.document_number",123456789012345)},
    
    {"id":"C400-17 IP length","requisito":"Longitud inválida","descripcion":"ip inválida (demasiado larga)","expected_code":"DTC-400","expected_response":"{'code': 'DTC-400', 'message': 'The transaction is rejected due to a problem in the format of the message.'}","modificador":setear("ip","999.999.999.999.999")},

    # ---------- FORMATO / DOMINIO ----------
    {"id":"C400-18 BIN Format","requisito":"Formato inválido","descripcion":"card_details.bin con letras","expected_code":"DTC-400","expected_response":"{'code': 'DTC-400', 'message': 'The transaction is rejected due to a problem in the format of the message.'}","modificador":setear("card_details.bin","ABCDEF")},
    
    {"id":"C400-19 Last4 Format","requisito":"Formato inválido","descripcion":"card_details.last_four_digits con letras","expected_code":"DTC-400","expected_response":"{'code': 'DTC-400', 'message': 'The transaction is rejected due to a problem in the format of the message.'}","modificador":setear("card_details.last_four_digits","ABCD")},
    
    {"id":"C400-20 Document number Format","requisito":"Formato inválido","descripcion":"document_number alfanumérico (debe ser numérico)","expected_code":"DTC-400","expected_response":"{'code': 'DTC-400', 'message': 'The transaction is rejected due to a problem in the format of the message.'}","modificador":setear("client.document_number","ABC123")},
    
    {"id":"C400-21 IP Format","requisito":"Formato inválido","descripcion":"ip con formato inválido","expected_code":"DTC-400","expected_response":"{'code': 'DTC-400', 'message': 'The transaction is rejected due to a problem in the format of the message.'}","modificador":setear("ip","999.999")},
    
    {"id":"C400-22 Gender inválido","requisito":"Formato inválido","descripcion":"gender con valor no permitido","expected_code":"DTC-400","expected_response":"{'code': 'DTC-400', 'message': 'Invalid gender value'}","modificador":setear("client.gender","Z")},
]
