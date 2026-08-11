import copy


BASE_PAYLOAD = {
    "client": {
        "document_type": "DNI",
        "document_number": "43081325",
        "gender": "M"
    },
    "origin": {
        "ip": "10.10.10.3",
        "channel": "Z"
    },
    "card": {
        "bin": "451769",
        "last_four_digits": "4136",
        "member": "001"
    },
    "rule_value": "DISABLED"
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
    {"id":"C200-01 Habilitar tarjeta","requisito":"Happy Path","descripcion":"Habilitar tarjeta de débito (ENABLED)","expected_code":"200","expected_response":"{'rule': 'status', 'rule_value': 'ENABLED'}","modificador":setear("value","ENABLED")},
    {"id":"C200-02 Deshabilitar tarjeta","requisito":"Happy Path","descripcion":"Deshabilitar tarjeta de débito (DISABLED)","expected_code":"200","expected_response":"{'rule': 'status', 'rule_value': 'DISABLED'}","modificador":setear("value","DISABLED")},

#    {"id":"C200-03 Tipo Doc Válidos - DNI","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento DNI","expected_code":"200","expected_response":"{'ok': {'rule': 'status', 'rule_value': 'ENABLED'}}","modificador":setear("client.document_type","DNI")},
#    {"id":"C200-03 Tipo Doc Válidos - CI","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento CI","expected_code":"200","expected_response":"{'ok': {'rule': 'status', 'rule_value': 'ENABLED'}}","modificador":setear("client.document_type","CI")},
#    {"id":"C200-03 Tipo Doc Válidos - PAS","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento PAS","expected_code":"200","expected_response":"{'ok': {'rule': 'status', 'rule_value': 'ENABLED'}}","modificador":setear("client.document_type","PAS")},
#    {"id":"C200-03 Tipo Doc Válidos - LC","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento LC","expected_code":"200","expected_response":"{'ok': {'rule': 'status', 'rule_value': 'ENABLED'}}","modificador":setear("client.document_type","LC")},
#    {"id":"C200-03 Tipo Doc Válidos - LE","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento LE","expected_code":"200","expected_response":"{'ok': {'rule': 'status', 'rule_value': 'ENABLED'}}","modificador":setear("client.document_type","LE")},
#    {"id":"C200-03 Tipo Doc Válidos - CUIT","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento CUIT","expected_code":"200","expected_response":"{'ok': {'rule': 'status', 'rule_value': 'ENABLED'}}","modificador":setear("client.document_type","CUIT")},
#    {"id":"C200-03 Tipo Doc Válidos - CUIL","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento CUIL","expected_code":"200","expected_response":"{'ok': {'rule': 'status', 'rule_value': 'ENABLED'}}","modificador":setear("client.document_type","CUIL")},
#    {"id":"C200-04 Gender Válidos - F","requisito":"Género válido","descripcion":"Enviar género Femenino","expected_code":"200","expected_response":"{'ok': {'rule': 'status', 'rule_value': 'ENABLED'}}","modificador":setear("client.gender","F")},
#    {"id":"C200-04 Gender Válidos - M","requisito":"Género válido","descripcion":"Enviar género Masculino","expected_code":"200","expected_response":"{'ok': {'rule': 'status', 'rule_value': 'ENABLED'}}","modificador":setear("client.gender","M")},
#    {"id":"C200-04 Gender Válidos - X","requisito":"Género válido","descripcion":"Enviar género Otro","expected_code":"200","expected_response":"{'ok': {'rule': 'status', 'rule_value': 'ENABLED'}}","modificador":setear("client.gender","X")},
#    {"id":"C200-05 Channel Válido - Z","requisito":"Canal válido","descripcion":"Enviar canal Z","expected_code":"200","expected_response":"{'ok': {'rule': 'status', 'rule_value': 'ENABLED'}}","modificador":setear("origin.channel","Z")},
#    {"id":"C200-05 Channel Válido - M","requisito":"Canal válido","descripcion":"Enviar canal M","expected_code":"200","expected_response":"{'ok': {'rule': 'status', 'rule_value': 'ENABLED'}}","modificador":setear("origin.channel","M")},
#    {"id":"C200-05 Channel Válido - C","requisito":"Canal válido","descripcion":"Enviar canal C","expected_code":"200","expected_response":"{'ok': {'rule': 'status', 'rule_value': 'ENABLED'}}","modificador":setear("origin.channel","C")},
#    {"id":"C200-06 Member Válido","requisito":"Member válido","descripcion":"Enviar member 001","expected_code":"200","expected_response":"{'ok': {'rule': 'status', 'rule_value': 'ENABLED'}}","modificador":setear("card.member","001")},

    # ---------- C400 – ERRORES DE NEGOCIO ----------
    {"id":"C400-01 Conflicto de regla - Legacy Code B29","requisito":"Error de negocio","descripcion":"Apagar(DISABLED) tarjeta en estado 7 ","expected_code":"CRM-RULE_CONFLICT","expected_response":"{'errors': [{'status': '400', 'code': 'CRM-RULE_CONFLICT', 'title': 'Rule conflict'}]}","modificador":lambda p: p},
    {"id":"C400-02 Conflicto de regla - Legacy Code B33","requisito":"Error de negocio","descripcion":"Prender(ENABLED) tarjeta en estado 1 ","expected_code":"CRM-RULE_CONFLICT","expected_response":"{'errors': [{'status': '400', 'code': 'CRM-RULE_CONFLICT', 'title': 'Rule conflict'}]}","modificador":lambda p: p},
    {"id":"C400-03 Regla inválida","requisito":"Error de negocio","descripcion":"Estado de tarjeta no permite Prender/Apagar - Legacy Code B30","expected_code":"CRM-INVALID_RULE","expected_response":"{'errors': [{'status': '400', 'code': 'CRM-INVALID_RULE', 'title': 'Invalid rule'}]}","modificador":lambda p: p},
    
    {"id":"C400-04 Transacción no habilitada","requisito":"Error de negocio","descripcion":"Institución no habilitada - Legacy Code B57","expected_code":"CRM-TRX_NOT_ENABLED","expected_response":"{'errors': [{'status': '400', 'code': 'CRM-TRX_NOT_ENABLED', 'title': 'The selected operation is not enabled for the Institution'}]}","modificador":lambda p: p},
    {"id":"C400-05 Tarjeta inválida","requisito":"Error de negocio","descripcion":"Tarjeta no existe en CAF - Legacy Code B65","expected_code":"CRM-INVALID_CARD","expected_response":"{'errors': [{'status': '400', 'code': 'CRM-INVALID_CARD', 'title': 'The inserted card is not valid'}]}","modificador":setear("card.bin","999999")},
    
    {"id":"C400-06 Usuario no habilitado","requisito":"Error de negocio","descripcion":"Usuario no es de Homebanking - Legacy Code B50","expected_code":"CRM-INVALID_CARD","expected_response":"{'errors': [{'status': '400', 'code': 'CRM-INVALID_CARD', 'title': 'The inserted card is not valid'}]}","modificador":setear("client.document_number","99999999")},

    # ---------- CAMPOS REQUERIDOS ----------
    {"id":"C400-07 Client is required","requisito":"Campo requerido","descripcion":"Falta client","expected_code":"CRM-400","expected_response":"{'errors': [{'status': '400', 'code': 'CRM-400', 'title': 'Validation Failed: \"client\" is required'}]}","modificador":borrar("client")},
    
    {"id":"C400-08 Document type is required","requisito":"Campo requerido","descripcion":"Falta document_type","expected_code":"CRM-400","expected_response":"{'errors': [{'status': '400', 'code': 'CRM-400', 'title': 'Validation Failed: \"client.document_type\" is required'}]}","modificador":borrar("client.document_type")},
    
    {"id":"C400-09 Document number is required","requisito":"Campo requerido","descripcion":"Falta document_number","expected_code":"CRM-400","expected_response":"{'errors': [{'status': '400', 'code': 'CRM-400', 'title': 'Validation Failed: \"client.document_number\" is required'}]}","modificador":borrar("client.document_number")},
    
    {"id":"C400-10 Gender is required","requisito":"Campo requerido","descripcion":"Falta gender","expected_code":"CRM-400","expected_response":"{'errors': [{'status': '400', 'code': 'CRM-400', 'title': 'Validation Failed: \"client.gender\" is required'}]}","modificador":borrar("client.gender")},
    
    {"id":"C400-11 Origin is required","requisito":"Campo requerido","descripcion":"Falta origin","expected_code":"CRM-400","expected_response":"{'errors': [{'status': '400', 'code': 'CRM-400', 'title': 'Validation Failed: \"origin\" is required'}]}","modificador":borrar("origin")},
    
    {"id":"C400-12 IP is required","requisito":"Campo requerido","descripcion":"Falta origin.ip","expected_code":"CRM-400","expected_response":"{'errors': [{'status': '400', 'code': 'CRM-400', 'title': 'Validation Failed: \"origin.ip\" is required'}]}","modificador":borrar("origin.ip")},
    
    {"id":"C400-13 Channel is required","requisito":"Campo requerido","descripcion":"Falta origin.channel","expected_code":"CRM-400","expected_response":"{'errors': [{'status': '400', 'code': 'CRM-400', 'title': 'Validation Failed: \"origin.channel\" is required'}]}","modificador":borrar("origin.channel")},
    
    {"id":"C400-14 Card is required","requisito":"Campo requerido","descripcion":"Falta card","expected_code":"CRM-400","expected_response":"{'errors': [{'status': '400', 'code': 'CRM-400', 'title': 'Validation Failed: \"card\" is required'}]}","modificador":borrar("card")},
    
    {"id":"C400-15 Bin is required","requisito":"Campo requerido","descripcion":"Falta card.bin","expected_code":"CRM-400","expected_response":"{'errors': [{'status': '400', 'code': 'CRM-400', 'title': 'Validation Failed: \"card.bin\" is required'}]}","modificador":borrar("card.bin")},
    
    {"id":"C400-16 Last four digits is required","requisito":"Campo requerido","descripcion":"Falta card.last_four_digits","expected_code":"CRM-400","expected_response":"{'errors': [{'status': '400', 'code': 'CRM-400', 'title': 'Validation Failed: \"card.last_four_digits\" is required'}]}","modificador":borrar("card.last_four_digits")},
    
    {"id":"C400-17 Member is required","requisito":"Campo requerido","descripcion":"Falta card.member","expected_code":"CRM-400","expected_response":"{'errors': [{'status': '400', 'code': 'CRM-400', 'title': 'Validation Failed: \"card.member\" is required'}]}","modificador":borrar("card.member")},
    
    {"id":"C400-18 Rule value is required","requisito":"Campo requerido","descripcion":"Falta rule_value","expected_code":"CRM-400","expected_response":"{'errors': [{'status': '400', 'code': 'CRM-400', 'title': 'Validation Failed: \"rule_value\" is required'}]}","modificador":borrar("rule_value")},

    # ---------- LONGITUD Y FORMATO ----------
    {"id":"C400-19 Document number alfanumérico","requisito":"Formato inválido","descripcion":"document_number con letras (debe ser numérico)","expected_code":"CRM-400","expected_response":"{'errors': [{'status': '400', 'code': 'CRM-400', 'title': 'Validation Failed: At this time the selected transaction cannot be made. The data entered for \"client.document_number\" is incorrect'}]}","modificador":setear("client.document_number","ABC123")},
    
    {"id":"C400-20 BIN con letras","requisito":"Formato inválido","descripcion":"card.bin con letras","expected_code":"CRM-400","expected_response":"{'errors': [{'status': '400', 'code': 'CRM-400', 'title': 'Validation Failed: At this time the selected transaction cannot be made. The data entered for \"card.bin\" is incorrect'}]}","modificador":setear("card.bin","ABCDEF")},
    
    {"id":"C400-21 Last four digits con letras","requisito":"Formato inválido","descripcion":"card.last_four_digits con letras","expected_code":"CRM-400","expected_response":"{'errors': [{'status': '400', 'code': 'CRM-400', 'title': 'Validation Failed: At this time the selected transaction cannot be made. The data entered for \"card.last_four_digits\" is incorrect'}]}","modificador":setear("card.last_four_digits","ABCD")},
    
    {"id":"C400-22 IP inválida","requisito":"Formato inválido","descripcion":"origin.ip con formato inválido","expected_code":"CRM-400","expected_response":"{'errors': [{'status': '400', 'code': 'CRM-400', 'title': 'Validation Failed: At this time the selected transaction cannot be made. The data entered for \"origin.ip\" is incorrect'}]}","modificador":setear("origin.ip","999.999")},
    
    {"id":"C400-23 Gender inválido","requisito":"Formato inválido","descripcion":"gender con valor no permitido","expected_code":"CRM-400","expected_response":"{'errors': [{'status': '400', 'code': 'CRM-400', 'title': 'Validation Failed: gender field value must be F , M or X.'}]}","modificador":setear("client.gender","Z")},
    
    {"id":"C400-24 Channel inválido","requisito":"Formato inválido","descripcion":"origin.channel con valor no permitido","expected_code":"CRM-400","expected_response":"{'errors': [{'status': '400', 'code': 'CRM-400', 'title': 'Validation Failed: At this time the selected transaction cannot be made. The data entered for \"origin.channel\" is incorrect'}]}","modificador":setear("origin.channel","X")},
    
    {"id":"C400-25 Member inválido","requisito":"Formato inválido","descripcion":"card.member con valor no permitido","expected_code":"CRM-400","expected_response":"{'errors': [{'status': '400', 'code': 'CRM-400', 'title': 'Validation Failed: At this time the selected transaction cannot be made. The data entered for member is incorrect.'}]}","modificador":setear("card.member","999")},
    
    {"id":"C400-26 Rule value inválido","requisito":"Formato inválido","descripcion":"rule_value con valor no permitido","expected_code":"CRM-400","expected_response":"{'errors': [{'status': '400', 'code': 'CRM-INVALID_RULE', 'title': 'Validation Failed: At this time the selected transaction cannot be made. The data entered for rule_value is incorrect.'}]}","modificador":setear("rule_value","INVALID")},
    {"id":"C400-03 Regla inválida","requisito":"Error de negocio","descripcion":"Estado de tarjeta no permite Prender/Apagar - Legacy Code B28","expected_code":"CRM-INVALID_RULE","expected_response":"{'errors': [{'status': '400', 'code': 'CRM-INVALID_RULE', 'title': 'Invalid rule'}]}","modificador":lambda p: p},

    # ---------- C401 – ERRORES DE AUTENTICACIÓN ----------
    {"id":"C401-01 Token ausente","requisito":"Autenticación","descripcion":"Request sin token de autorización","expected_code":"APIM-401","expected_response":"{'errors': [{'status': '401', 'code': 'APIM-401', 'title': 'Unauthorized'}]}","modificador":lambda p: p, "headers_override": {"Content-Type": "application/json", "x-apip-client-id": "test", "x-apip-partner-id": "test", "x-apip-cuit": "20304050607"}},

    {"id":"C401-02 Token inválido","requisito":"Autenticación","descripcion":"Token inválido","expected_code":"APIM-401","expected_response":"{'errors': [{'status': '401', 'code': 'APIM-401', 'title': 'Unauthorized'}]}","modificador":lambda p: p, "headers_override": {"Authorization": "Bearer token_invalido", "Content-Type": "application/json", "x-apip-client-id": "test", "x-apip-partner-id": "test", "x-apip-cuit": "20304050607"}},

    # ---------- C500 – ERRORES DE SERVIDOR ----------
    {"id":"C500-01 Error de sistema","requisito":"Error de servidor","descripcion":"Error de comunicación con host","expected_code":"CRM-500","expected_response":"{'errors': [{'status': '500', 'code': 'CRM-500', 'title': 'Host communication error'}]}","modificador":lambda p: p},
    
    {"id":"C500-02 Gateway timeout","requisito":"Error de servidor","descripcion":"Timeout en gateway","expected_code":"CRM-504","expected_response":"{'errors': [{'status': '504', 'code': 'CRM-504', 'title': 'Gateway timeout'}]}","modificador":lambda p: p}
]