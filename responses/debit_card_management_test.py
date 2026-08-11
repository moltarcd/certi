# templates_alta_td.py
import copy

# ======================================================
# OBJETO BASE REUTILIZABLE
# ======================================================
BASE_PAYLOAD =  {
    "bank_code": "007",
    "origin": {"ip_address": "10.10.10.3", "channel": "Z"},
    "client": {
        "document_type": "DNI", 
		"document_number": "26778160", 
		"gender": "M",
        "first_name": "Arturo", 
		"lastname": "Shark", 
		"marital_status": "Separated",
        "birth_date": "2000-02-01", 
		"area_code": "11", 
		"phone_number": "12345678", 
		"holder_cuit": "20267781605"
    },
    "card": {
        "card_number": "Z8aMtaYPI+4fRVXGwB93g31chQmzYah5ilND75AQFlI=abcdefgh12345678",
        "member": "001", 
		"expiration_date": "2611", 
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
    "accounts": [{"account_number": "000011111978011", "account_type": "CCD", "account_status": "2"}]
}


# ======================================================
# MODIFICADORES DINÁMICOS
# ======================================================
def borrar(path):
    def f(payload):
        keys = path.split(".")
        ref = payload
        for k in keys[:-1]:
            ref = ref[int(k)] if isinstance(ref, list) else ref[k]
        last = keys[-1]
        if isinstance(ref, list): del ref[int(last)]
        else: del ref[last]
    return f

def setear(path, value):
    def f(payload):
        keys = path.split(".")
        ref = payload
        for k in keys[:-1]:
            ref = ref[int(k)] if isinstance(ref, list) else ref[k]
        last = keys[-1]
        if isinstance(ref, list): ref[int(last)] = value
        else: ref[last] = value
    return f

# ======================================================
# RESPUESTA EXITOSA BASE (HAPPY PATH)
# ======================================================
HAPPY_RESPONSE = """{
    'bank_code': 'string',
    'origin': {
        'ip_address': 'string',
        'channel': 'string'
    },
    'client': {
        'document_type': 'string',
        'document_number': 'string',
        'gender': 'string',
        'first_name': 'string',
        'lastname': 'string',
        'marital_status': 'string',
        'birth_date': 'yyyy-MM-dd',
        'area_code': 'string',
        'phone_number': 'string',
        'holder_cuit': 'string'
    },
    'card': {
        'masked_card_number': 'string',
        'member': 'string',
        'expiration_date': 'yyMM',
        'client_class': 'string',
        'card_status': 'string',
        'branch': 'string'
    },
    'address': {
        'street': 'string',
        'number': 'string',
        'floor': 'string',
        'department': 'string',
        'province': 'string',
        'city': 'string',
        'zip_code': 'string'
    },
    'accounts': [
        {
            'account_number': 'string',
            'account_type': 'string',
            'account_status': 'string'
        }
    ]
}"""


# ======================================================
# MATRIZ DE CASOS DE PRUEBA (TEST_CASES)
# ======================================================
TEST_CASES = [
    # ---------- C201 – CASOS EXITOSOS ----------
    {"id":"C201-01 Happy Path - Creación exitosa","requisito":"Creación de tarjeta","descripcion":"Creación de tarjeta con todos los campos válidos","expected_code":"201","expected_response":HAPPY_RESPONSE,"modificador":lambda p: p},
    {"id":"C201-02 Tipo Documento DNI","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento DNI","expected_code":"201","expected_response":HAPPY_RESPONSE,"modificador":setear("client.document_type","DNI")},
    {"id":"C201-03 Tipo Documento CI","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento CI","expected_code":"201","expected_response":HAPPY_RESPONSE,"modificador":setear("client.document_type","CI")},
    {"id":"C201-04 Tipo Documento PAS","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento PAS","expected_code":"201","expected_response":HAPPY_RESPONSE,"modificador":setear("client.document_type","PAS")},
    {"id":"C201-05 Tipo Documento LC","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento LC","expected_code":"201","expected_response":HAPPY_RESPONSE,"modificador":setear("client.document_type","LC")},
    {"id":"C201-06 Tipo Documento LE","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento LE","expected_code":"201","expected_response":HAPPY_RESPONSE,"modificador":setear("client.document_type","LE")},
    {"id":"C201-07 Tipo Documento CUIT","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento CUIT","expected_code":"201","expected_response":HAPPY_RESPONSE,"modificador":setear("client.document_type","CUIT")},
    {"id":"C201-08 Tipo Documento CUIL","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento CUIL","expected_code":"201","expected_response":HAPPY_RESPONSE,"modificador":setear("client.document_type","CUIL")},
    {"id":"C201-09 Género Femenino","requisito":"Género válido","descripcion":"Enviar género F","expected_code":"201","expected_response":HAPPY_RESPONSE,"modificador":setear("client.gender","F")},
    {"id":"C201-10 Género Masculino","requisito":"Género válido","descripcion":"Enviar género M","expected_code":"201","expected_response":HAPPY_RESPONSE,"modificador":setear("client.gender","M")},
    {"id":"C201-11 Estado Civil Casado","requisito":"Estado civil válido","descripcion":"Enviar marital_status Married","expected_code":"201","expected_response":HAPPY_RESPONSE,"modificador":setear("client.marital_status","Married")},
    {"id":"C201-12 Estado Civil Separado","requisito":"Estado civil válido","descripcion":"Enviar marital_status Separated","expected_code":"201","expected_response":HAPPY_RESPONSE,"modificador":setear("client.marital_status","Separated")},
    {"id":"C201-13 Tipo Cuenta CCD","requisito":"Tipo de cuenta válido","descripcion":"Enviar account_type CCD","expected_code":"201","expected_response":HAPPY_RESPONSE,"modificador":setear("accounts.0.account_type","CCD")},
    {"id":"C201-14 Tipo Cuenta CAA","requisito":"Tipo de cuenta válido","descripcion":"Enviar account_type CAA","expected_code":"201","expected_response":HAPPY_RESPONSE,"modificador":setear("accounts.0.account_type","CAA")},
    {"id":"C201-15 Estado Cuenta Activa","requisito":"Estado de cuenta válido","descripcion":"Enviar account_status 2 (activa)","expected_code":"201","expected_response":HAPPY_RESPONSE,"modificador":setear("accounts.0.account_status","2")},
    {"id":"C201-16 Múltiples cuentas","requisito":"Múltiples cuentas","descripcion":"Enviar dos cuentas asociadas","expected_code":"201","expected_response":HAPPY_RESPONSE,"modificador":lambda p: p["accounts"].append({"account_number": "000011111978012", "account_type": "CAA", "account_status": "2"})},

    # ---------- C400 – ERRORES DE VALIDACIÓN ----------
    {"id":"C400-01 bank_code caracteres especiales","requisito":"Validación de formato","descripcion":"bank_code con caracteres especiales - ACV-400","expected_code":"ACV-400","expected_response":"{'error': {'code': 'ACV-400', 'message': 'Validation failed: Field bank_code cannot contain special characters'}}","modificador":setear("bank_code","007@#$")},
    {"id":"C400-02 bank_code requerido","requisito":"Campo requerido","descripcion":"Falta bank_code - ACV-400","expected_code":"ACV-400","expected_response":"{'error': {'code': 'ACV-400', 'message': 'Required String parameter bank_code is not present'}}","modificador":borrar("bank_code")},
    {"id":"C400-03 Campo requerido - client","requisito":"Campo requerido","descripcion":"Falta objeto client - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":"{'error': {'code': 'DCM-BAD_REQUEST', 'message': \"Field 'client' is required\"}}","modificador":borrar("client")},
    {"id":"C400-04 Campo requerido - document_type","requisito":"Campo requerido","descripcion":"Falta document_type - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":"{'error': {'code': 'DCM-BAD_REQUEST', 'message': \"Field 'document_type' is required\"}}","modificador":borrar("client.document_type")},
    {"id":"C400-05 Campo requerido - document_number","requisito":"Campo requerido","descripcion":"Falta document_number - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":"{'error': {'code': 'DCM-BAD_REQUEST', 'message': \"Field 'document_number' is required\"}}","modificador":borrar("client.document_number")},
    {"id":"C400-06 Campo requerido - first_name","requisito":"Campo requerido","descripcion":"Falta first_name - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":"{'error': {'code': 'DCM-BAD_REQUEST', 'message': \"Field 'first_name' is required\"}}","modificador":borrar("client.first_name")},
    {"id":"C400-07 Campo requerido - lastname","requisito":"Campo requerido","descripcion":"Falta lastname - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":"{'error': {'code': 'DCM-BAD_REQUEST', 'message': \"Field 'lastname' is required\"}}","modificador":borrar("client.lastname")},
    {"id":"C400-08 Campo requerido - birth_date","requisito":"Campo requerido","descripcion":"Falta birth_date - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":"{'error': {'code': 'DCM-BAD_REQUEST', 'message': \"Field 'birth_date' is required\"}}","modificador":borrar("client.birth_date")},
    {"id":"C400-09 Campo requerido - phone_number","requisito":"Campo requerido","descripcion":"Falta phone_number - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":"{'error': {'code': 'DCM-BAD_REQUEST', 'message': \"Field 'phone_number' is required\"}}","modificador":borrar("client.phone_number")},
    {"id":"C400-10 Campo requerido - card","requisito":"Campo requerido","descripcion":"Falta objeto card - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":"{'error': {'code': 'DCM-BAD_REQUEST', 'message': \"Field 'card' is required\"}}","modificador":borrar("card")},
    {"id":"C400-11 Campo requerido - card_number","requisito":"Campo requerido","descripcion":"Falta card_number - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":"{'error': {'code': 'DCM-BAD_REQUEST', 'message': \"Field 'card_number' is required\"}}","modificador":borrar("card.card_number")},
    {"id":"C400-12 Campo requerido - expiration_date","requisito":"Campo requerido","descripcion":"Falta expiration_date - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":"{'error': {'code': 'DCM-BAD_REQUEST', 'message': \"Field 'expiration_date' is required\"}}","modificador":borrar("card.expiration_date")},
    {"id":"C400-13 Campo requerido - address","requisito":"Campo requerido","descripcion":"Falta objeto address - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":"{'error': {'code': 'DCM-BAD_REQUEST', 'message': \"Field 'address' is required\"}}","modificador":borrar("address")},
    {"id":"C400-14 Campo requerido - street","requisito":"Campo requerido","descripcion":"Falta street - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":"{'error': {'code': 'DCM-BAD_REQUEST', 'message': \"Field 'street' is required\"}}","modificador":borrar("address.street")},
    {"id":"C400-15 Campo requerido - accounts","requisito":"Campo requerido","descripcion":"Falta accounts - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":"{'error': {'code': 'DCM-BAD_REQUEST', 'message': \"Field 'accounts' is required\"}}","modificador":borrar("accounts")},
    {"id":"C400-16 Longitud excedida - document_number","requisito":"Longitud máxima","descripcion":"document_number demasiado largo - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":"{'error': {'code': 'DCM-BAD_REQUEST', 'message': 'The data entered for document_number is incorrect or exceeds the maximum length'}}","modificador":setear("client.document_number","123456789012345")},
    {"id":"C400-17 Longitud excedida - first_name","requisito":"Longitud máxima","descripcion":"first_name demasiado largo - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":"{'error': {'code': 'DCM-BAD_REQUEST', 'message': 'The data entered for first_name is incorrect or exceeds the maximum length'}}","modificador":setear("client.first_name","A"*101)},
    {"id":"C400-18 Longitud excedida - street","requisito":"Longitud máxima","descripcion":"street demasiado largo - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":"{'error': {'code': 'DCM-BAD_REQUEST', 'message': 'The data entered for street is incorrect or exceeds the maximum length'}}","modificador":setear("address.street","A"*101)},
    {"id":"C400-19 Fecha expiración inválida - vigencia","requisito":"Validación de fecha","descripcion":"Fecha de expiración supera vigencia del BIN - DCM - Data problem","expected_code":"DCM-DATA_PROBLEM","expected_response":"{'error': {'code': 'DCM-DATA_PROBLEM', 'message': 'Error calculating the validity.The entered date is not correct or exceeds the years stored in BD'}}","modificador":setear("card.expiration_date","4011")},
    
    {"id":"C400-20 Formato inválido - datos no numéricos","requisito":"Formato de datos","descripcion":"Datos inválidos en campos numéricos - DCM - INVALID_DATA","expected_code":"DCM - INVALID_DATA","expected_response":"{'error': {'code': 'DCM - INVALID_DATA', 'message': 'The transaction is rejected due to a problem in the format of the message'}}","modificador":setear("client.phone_number","ABCDEFG")},
    {"id":"C400-21 Tarjeta inválida - cifrado incorrecto","requisito":"Validación de tarjeta","descripcion":"Número de tarjeta con cifrado incorrecto - DCM - INVALID_CARD","expected_code":"DCM - INVALID_CARD","expected_response":"{'error': {'code': 'DCM - INVALID_CARD', 'message': 'The inserted card is not valid'}}","modificador":setear("card.card_number","tarjeta_invalida")},
    {"id":"C400-22 Tarjeta inválida - no pertenece a la institución","requisito":"Validación de tarjeta","descripcion":"Tarjeta no pertenece a la institución - DCM - INVALID_CARD","expected_code":"DCM-INVALID_CARD","expected_response":"{'error': {'code': 'DCM - INVALID_CARD', 'message': 'The inserted card is not valid'}}","modificador":setear("card.card_number","UJJd/L0hwG8sGxuQ0lH82PEK+DbLAeYxRCN2KHBw8eM=abcdefgh12345678")},
    {"id":"C400-23 Datos inconsistentes","requisito":"Consistencia de datos","descripcion":"Los datos no coinciden con registros anteriores - DCM-INCONSISTENT DATA","expected_code":"DCM-INCONSISTENT DATA","expected_response":"{'error': {'code': 'DCM-INCONSISTENT DATA', 'message': 'The data entered is inconsistent'}}","modificador":lambda p: p},
# ---------- C400 – ERRORES DE VALIDACIÓN CUIt ----------

{"id":"C400-24 Holder CUIT vacío",
 "requisito":"holder_cuit obligatorio",
 "descripcion":"Enviar holder_cuit vacío",
 "expected_code":"DCM-BAD_REQUEST",
 "expected_response":"holder_cuit is required",
 "modificador":setear("client.holder_cuit","")},

{"id":"C400-25 Holder CUIT nulo",
 "requisito":"holder_cuit obligatorio",
 "descripcion":"Enviar holder_cuit null",
 "expected_code":"DCM-BAD_REQUEST",
 "expected_response":"holder_cuit is required",
 "modificador":setear("client.holder_cuit",None)},

{"id":"C400-26 Holder CUIT ausente",
 "requisito":"holder_cuit obligatorio",
 "descripcion":"Eliminar holder_cuit del request",
 "expected_code":"DCM-BAD_REQUEST",
 "expected_response":"holder_cuit is required",
 "modificador":borrar("client.holder_cuit")},

{"id":"C400-27 Holder CUIT menor a 11 dígitos",
 "requisito":"Longitud válida de holder_cuit",
 "descripcion":"Enviar holder_cuit con 10 dígitos",
 "expected_code":"DCM-BAD_REQUEST",
 "expected_response":"holder_cuit length invalid",
 "modificador":setear("client.holder_cuit","2726767880")},

{"id":"C400-28 Holder CUIT mayor a 11 dígitos",
 "requisito":"Longitud válida de holder_cuit",
 "descripcion":"Enviar holder_cuit con 12 dígitos",
 "expected_code":"DCM-BAD_REQUEST",
 "expected_response":"holder_cuit length invalid",
 "modificador":setear("client.holder_cuit","272676788055")},

{"id":"C400-29 Holder CUIT con letras",
 "requisito":"Formato numérico de holder_cuit",
 "descripcion":"Enviar holder_cuit alfanumérico",
 "expected_code":"DCM-BAD_REQUEST",
 "expected_response":"holder_cuit format invalid",
 "modificador":setear("client.holder_cuit","27A67678805")},

{"id":"C400-30 Holder CUIT con caracteres especiales",
 "requisito":"Formato numérico de holder_cuit",
 "descripcion":"Enviar holder_cuit con guiones",
 "expected_code":"DCM-BAD_REQUEST",
 "expected_response":"holder_cuit format invalid",
 "modificador":setear("client.holder_cuit","27-26767880-5")},


    # ---------- C401 – ERRORES DE AUTENTICACIÓN ----------
    {"id":"C401-01 Token ausente","requisito":"Autenticación","descripcion":"Request sin token de autorización - APIM-401","expected_code":"APIM-401","expected_response":"{'error': {'code': 'APIM-401', 'title': 'Unauthorized'}}","modificador":lambda p: p, "headers_override": {"Content-Type": "application/json"}},
    {"id":"C401-02 Token inválido","requisito":"Autenticación","descripcion":"Token inválido - APIM-401","expected_code":"APIM-401","expected_response":"{'error': {'code': 'APIM-401', 'title': 'Unauthorized'}}","modificador":lambda p: p, "headers_override": {"Authorization": "Bearer token_invalido", "Content-Type": "application/json"}},

    # ---------- C404 – RECURSO NO ENCONTRADO ----------
    {"id":"C404-01 bank_code no encontrado","requisito":"Validación de banco","descripcion":"bank_code no encontrado o sin relación - ACV-404","expected_code":"ACV-404","expected_response":"{'error': {'code': 'ACV-404', 'message': 'Identifier or bank_code not Found. Owner not found'}}","modificador":setear("bank_code","999")},

    # ---------- C500 – ERRORES DE SERVIDOR ----------
    {"id":"C500-01 Error procesando datos","requisito":"Error de servidor","descripcion":"Error procesando datos - DCM – DATA_PROBLEM","expected_code":"DCM – DATA_PROBLEM","expected_response":"{'error': {'code': 'DCM – DATA_PROBLEM', 'message': 'Error processing data'}}","modificador":lambda p: p},
    {"id":"C500-02 Error de comunicación(legacy A99)","requisito":"Error de servidor","descripcion":"Error de comunicación con host - DCM – INTERNAL SERVER ERROR","expected_code":"DCM – INTERNAL SERVER ERROR","expected_response":"{'error': {'code': 'DCM – INTERNAL SERVER ERROR', 'message': 'An unexpected error occurred'}}","modificador":lambda p: p},
    {"id":"C500-03 Timeout del backend(legacy 1010)","requisito":"Error de servidor","descripcion":"Timeout en comunicación con backend - DCM – INTERNAL SERVER ERROR","expected_code":"DCM – INTERNAL SERVER ERROR","expected_response":"{'error': {'code': 'DCM – INTERNAL SERVER ERROR', 'message': 'Host communication error'}}","modificador":lambda p: p},
    {"id":"C500-04 Problemas identificación cliente","requisito":"Error de servidor","descripcion":"Problemas en identificación del cliente - DCM – INTERNAL SERVER ERROR","expected_code":"DCM – INTERNAL SERVER ERROR","expected_response":"{'error': {'code': 'DCM – INTERNAL SERVER ERROR', 'message': 'user identification problems'}}","modificador":lambda p: p},
]