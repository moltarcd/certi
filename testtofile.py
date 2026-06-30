import os
import json

# 1. Definición de la API y ruta destino
API_NAME = "alta_td"
TARGET_DIR = os.path.join("responses", API_NAME)

if not os.path.exists(TARGET_DIR):
    os.makedirs(TARGET_DIR)
    print(f"📁 Carpeta creada con éxito: {TARGET_DIR}")

# =====================================================================
# 2. STUBS / MOCKS DE TUS FUNCIONES MODIFICADORAS
# Declaramos estas funciones para que Python no falle por "NameError"
# =====================================================================
def setear(path, valor):
    # Devuelve una función lambda vacía solo para cumplir con la sintaxis
    return lambda p: p

def borrar(path):
    return lambda p: p

# =====================================================================
# 3. TU ARRAY "TEST_CASES" REAL (Tal cual lo tenías originalmente)
# =====================================================================
TEST_CASES = [
    # ---------- C201 – CASOS EXITOSOS (HTTP 201 Created) ----------
    {"id":"C201-01 Happy Path - Creación exitosa","requisito":"Creación de tarjeta","descripcion":"Creación de tarjeta con todos los campos válidos","expected_code":"201","expected_response":{"bank_code": "007", "origin": {"ip_address": "192.168.1.1", "channel": "WEB"}, "client": {"document_type": "DNI", "document_number": "30123456", "gender": "M", "first_name": "Juan", "lastname": "Perez", "marital_status": "Single", "birth_date": "1990-01-01", "area_code": "11", "phone_number": "44445555", "holder_cuit": "20301234567"}, "card": {"masked_card_number": "4556********1234", "member": "1", "expiration_date": "2030-12", "client_class": "Classic", "card_status": "1", "branch": "001"}, "address": {"street": "Av. Corrientes", "number": "1234", "floor": "2", "department": "B", "province": "CABA", "city": "CABA", "zip_code": "1043"}, "accounts": [{"account_number": "000011111978012", "account_type": "CCD", "account_status": "2"}]},"modificador":lambda p: p},
    
    {"id":"C201-02 Tipo Documento DNI","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento DNI","expected_code":"201","expected_response":"{'bank_code': '007', ...}","modificador":setear("client.document_type","DNI")},
    {"id":"C201-03 Tipo Documento CI","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento CI","expected_code":"201","expected_response":"{'bank_code': '007', ...}","modificador":setear("client.document_type","CI")},
    {"id":"C201-04 Tipo Documento PAS","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento PAS","expected_code":"201","expected_response":"{'bank_code': '007', ...}","modificador":setear("client.document_type","PAS")},
    {"id":"C201-05 Tipo Documento LC","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento LC","expected_code":"201","expected_response":"{'bank_code': '007', ...}","modificador":setear("client.document_type","LC")},
    {"id":"C201-06 Tipo Documento LE","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento LE","expected_code":"201","expected_response":"{'bank_code': '007', ...}","modificador":setear("client.document_type","LE")},
    {"id":"C201-07 Tipo Documento CUIT","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento CUIT","expected_code":"201","expected_response":"{'bank_code': '007', ...}","modificador":setear("client.document_type","CUIT")},
    {"id":"C201-08 Tipo Documento CUIL","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento CUIL","expected_code":"201","expected_response":"{'bank_code': '007', ...}","modificador":setear("client.document_type","CUIL")},
    {"id":"C201-09 Género Femenino","requisito":"Género válido","descripcion":"Enviar género F","expected_code":"201","expected_response":"{'bank_code': '007', ...}","modificador":setear("client.gender","F")},
    {"id":"C201-10 Género Masculino","requisito":"Género válido","descripcion":"Enviar género M","expected_code":"201","expected_response":"{'bank_code': '007', ...}","modificador":setear("client.gender","M")},
    {"id":"C201-11 Estado Civil Casado","requisito":"Estado civil válido","descripcion":"Enviar marital_status Married","expected_code":"201","expected_response":"{'bank_code': '007', ...}","modificador":setear("client.marital_status","Married")},
    {"id":"C201-12 Estado Civil Separado","requisito":"Estado civil válido","descripcion":"Enviar marital_status Separated","expected_code":"201","expected_response":"{'bank_code': '007', ...}","modificador":setear("client.marital_status","Separated")},
    {"id":"C201-13 Tipo Cuenta CCD","requisito":"Tipo de cuenta válido","descripcion":"Enviar account_type CCD","expected_code":"201","expected_response":"{'bank_code': '007', ...}","modificador":setear("accounts.0.account_type","CCD")},
    {"id":"C201-14 Tipo Cuenta CAA","requisito":"Tipo de cuenta válido","descripcion":"Enviar account_type CAA","expected_code":"201","expected_response":"{'bank_code': '007', ...}","modificador":setear("accounts.0.account_type","CAA")},
    {"id":"C201-15 Estado Cuenta Activa","requisito":"Estado de cuenta válido","descripcion":"Enviar account_status 2 (activa)","expected_code":"201","expected_response":"{'bank_code': '007', ...}","modificador":setear("accounts.0.account_status","2")},
    {"id":"C201-16 Múltiples cuentas","requisito":"Múltiples cuentas","descripcion":"Enviar dos cuentas asociadas","expected_code":"201","expected_response":"{'bank_code': '007', ...}","modificador":lambda p: p},

    # ---------- C400 – ERRORES DE VALIDACIÓN (HTTP 400) ----------
    {"id":"C400-01 bank_code caracteres especiales","requisito":"Validación de formato","descripcion":"bank_code con caracteres especiales - ACV-400","expected_code":"ACV-400","expected_response":{"error": {"code": "ACV-400", "message": "Validation failed: Field bank_code cannot contain special characters"}},"modificador":setear("bank_code","007@#$")},
    {"id":"C400-02 bank_code requerido","requisito":"Campo requerido","descripcion":"Falta bank_code - ACV-400","expected_code":"ACV-400","expected_response":{"error": {"code": "ACV-400", "message": "Required String parameter bank_code is not present"}},"modificador":borrar("bank_code")},
    {"id":"C400-03 Campo requerido - client","requisito":"Campo requerido","descripcion":"Falta objeto client - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":{"error": {"code": "DCM-BAD_REQUEST", "message": "Field 'client' is required"}},"modificador":borrar("client")},
    {"id":"C400-04 Campo requerido - document_type","requisito":"Campo requerido","descripcion":"Falta document_type - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":{"error": {"code": "DCM-BAD_REQUEST", "message": "Field 'document_type' is required"}},"modificador":borrar("client.document_type")},
    {"id":"C400-05 Campo requerido - document_number","requisito":"Campo requerido","descripcion":"Falta document_number - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":{"error": {"code": "DCM-BAD_REQUEST", "message": "Field 'document_number' is required"}},"modificador":borrar("client.document_number")},
    {"id":"C400-06 Campo requerido - first_name","requisito":"Campo requerido","descripcion":"Falta first_name - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":{"error": {"code": "DCM-BAD_REQUEST", "message": "Field 'first_name' is required"}},"modificador":borrar("client.first_name")},
    {"id":"C400-07 Campo requerido - lastname","requisito":"Campo requerido","descripcion":"Falta lastname - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":{"error": {"code": "DCM-BAD_REQUEST", "message": "Field 'lastname' is required"}},"modificador":borrar("client.lastname")},
    {"id":"C400-08 Campo requerido - birth_date","requisito":"Campo requerido","descripcion":"Falta birth_date - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":{"error": {"code": "DCM-BAD_REQUEST", "message": "Field 'birth_date' is required"}},"modificador":borrar("client.birth_date")},
    {"id":"C400-09 Campo requerido - phone_number","requisito":"Campo requerido","descripcion":"Falta phone_number - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":{"error": {"code": "DCM-BAD_REQUEST", "message": "Field 'phone_number' is required"}},"modificador":borrar("client.phone_number")},
    {"id":"C400-10 Campo requerido - card","requisito":"Campo requerido","descripcion":"Falta objeto card - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":{"error": {"code": "DCM-BAD_REQUEST", "message": "Field 'card' is required"}},"modificador":borrar("card")},
    {"id":"C400-11 Campo requerido - card_number","requisito":"Campo requerido","descripcion":"Falta card_number - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":{"error": {"code": "DCM-BAD_REQUEST", "message": "Field 'card_number' is required"}},"modificador":borrar("card.card_number")},
    {"id":"C400-12 Campo requerido - expiration_date","requisito":"Campo requerido","descripcion":"Falta expiration_date - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":{"error": {"code": "DCM-BAD_REQUEST", "message": "Field 'expiration_date' is required"}},"modificador":borrar("card.expiration_date")},
    {"id":"C400-13 Campo requerido - address","requisito":"Campo requerido","descripcion":"Falta objeto address - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":{"error": {"code": "DCM-BAD_REQUEST", "message": "Field 'address' is required"}},"modificador":borrar("address")},
    {"id":"C400-14 Campo requerido - street","requisito":"Campo requerido","descripcion":"Falta street - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":{"error": {"code": "DCM-BAD_REQUEST", "message": "Field 'street' is required"}},"modificador":borrar("address.street")},
    {"id":"C400-15 Campo requerido - accounts","requisito":"Campo requerido","descripcion":"Falta accounts - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":{"error": {"code": "DCM-BAD_REQUEST", "message": "Field 'accounts' is required"}},"modificador":borrar("accounts")},
    {"id":"C400-16 Longitud excedida - document_number","requisito":"Longitud máxima","descripcion":"document_number demasiado largo (>11?) - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":{"error": {"code": "DCM-BAD_REQUEST", "message": "The data entered for document_number is incorrect or exceeds the maximum length"}},"modificador":setear("client.document_number","123456789012345")},
    {"id":"C400-17 Longitud excedida - first_name","requisito":"Longitud máxima","descripcion":"first_name demasiado largo - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":{"error": {"code": "DCM-BAD_REQUEST", "message": "The data entered for first_name is incorrect or exceeds the maximum length"}},"modificador":setear("client.first_name","A"*101)},
    {"id":"C400-18 Longitud excedida - street","requisito":"Longitud máxima","descripcion":"street demasiado largo - DCM-BAD_REQUEST","expected_code":"DCM-BAD_REQUEST","expected_response":{"error": {"code": "DCM-BAD_REQUEST", "message": "The data entered for street is incorrect or exceeds the maximum length"}},"modificador":setear("address.street","A"*101)},
    {"id":"C400-19 Fecha expiración inválida - vigencia","requisito":"Validación de fecha","descripcion":"Fecha de expiración supera vigencia del BIN - DCM - Data problem","expected_code":"DCM - Data problem","expected_response":{"error": {"code": "DCM - Data problem", "message": "Error calculating the validity. The entered date is not correct or exceeds the years stored in BD"}},"modificador":setear("card.expiration_date","9999")},
    {"id":"C400-20 Formato inválido - datos no numéricos","requisito":"Formato de datos","descripcion":"Datos inválidos en campos numéricos - DCM - INVALID_DATA","expected_code":"DCM - INVALID_DATA","expected_response":{"error": {"code": "DCM - INVALID_DATA", "message": "The transaction is rejected due to a problem in the format of the message"}},"modificador":setear("client.phone_number","ABCDEFG")},
    {"id":"C400-21 Tarjeta inválida - cifrado incorrecto","requisito":"Validación de tarjeta","descripcion":"Número de tarjeta con cifrado incorrecto - DCM - INVALID_CARD","expected_code":"DCM - INVALID_CARD","expected_response":{"error": {"code": "DCM - INVALID_CARD", "message": "The inserted card is not valid"}},"modificador":setear("card.card_number","tarjeta_invalida")},
    {"id":"C400-22 Tarjeta inválida - no pertenece a la institución","requisito":"Validación de tarjeta","descripcion":"Tarjeta no pertenece a la institución - DCM - INVALID_CARD","expected_code":"DCM - INVALID_CARD","expected_response":{"error": {"code": "DCM - INVALID_CARD", "message": "The inserted card is not valid"}},"modificador":setear("card.card_number","12345678901234567890123456789012")},
    {"id":"C400-23 Datos inconsistentes","requisito":"Consistencia de datos","descripcion":"Los datos no coinciden con registros anteriores - DCM-INCONSISTENT DATA","expected_code":"DCM-INCONSISTENT DATA","expected_response":{"error": {"code": "DCM-INCONSISTENT DATA", "message": "The data entered is inconsistent"}},"modificador":lambda p: p},

    # ---------- C401 – ERRORES DE AUTENTICACIÓN ----------
    {"id":"C401-01 Token ausente","requisito":"Autenticación","descripcion":"Request sin token de autorización - APIM-401","expected_code":"APIM-401","expected_response":{"error": {"code": "APIM-401", "title": "Unauthorized"}},"modificador":lambda p: p, "headers_override": {"Content-Type": "application/json"}},
    {"id":"C401-02 Token inválido","requisito":"Autenticación","descripcion":"Token inválido - APIM-401","expected_code":"APIM-401","expected_response":{"error": {"code": "APIM-401", "title": "Unauthorized"}},"modificador":lambda p: p, "headers_override": {"Authorization": "Bearer token_invalido", "Content-Type": "application/json"}},

    # ---------- C404 – RECURSO NO ENCONTRADO ----------
    {"id":"C404-01 bank_code no encontrado","requisito":"Validación de banco","descripcion":"bank_code no encontrado o sin relación - ACV-404","expected_code":"ACV-404","expected_response":{"error": {"code": "ACV-404", "message": "Identifier or bank_code not Found. Owner not found"}},"modificador":setear("bank_code","999")},

    # ---------- C500 – ERRORES DE SERVIDOR ----------
    {"id":"C500-01 Error procesando datos","requisito":"Error de servidor","descripcion":"Error procesando datos - DCM – DATA_PROBLEM","expected_code":"DCM – DATA_PROBLEM","expected_response":{"error": {"code": "DCM – DATA_PROBLEM", "message": "Error processing data"}},"modificador":lambda p: p},
    {"id":"C500-02 Error de comunicación(legacy A99)","requisito":"Error de servidor","descripcion":"Error de comunicación con host - DCM – INTERNAL SERVER ERROR","expected_code":"DCM – INTERNAL SERVER ERROR","expected_response":{"error": {"code": "DCM – INTERNAL SERVER ERROR", "message": "An unexpected error occurred"}},"modificador":lambda p: p},
    {"id":"C500-03 Timeout del backend(legacy 1010)","requisito":"Error de servidor","descripcion":"Timeout en comunicación con backend - DCM – INTERNAL SERVER ERROR","expected_code":"DCM – INTERNAL SERVER ERROR","expected_response":{"error": {"code": "DCM – INTERNAL SERVER ERROR", "message": "Host communication error"}},"modificador":lambda p: p},
    {"id":"C500-04 Problemas identificación cliente","requisito":"Error de servidor","descripcion":"Problemas en identificación del cliente - DCM – INTERNAL SERVER ERROR","expected_code":"DCM – INTERNAL SERVER ERROR","expected_response":{"error": {"code": "DCM – INTERNAL SERVER ERROR", "message": "user identification problems"}},"modificador":lambda p: p},
]

# =====================================================================
# 4. LÓGICA DE ESCRITURA MASIVA
# =====================================================================
print("🚀 Iniciando la generación de respuestas esperadas...")

# Tomamos el payload completo del Happy Path (C201-01) para replicarlo en los demás éxitos
happy_path_payload = TEST_CASES[0]["expected_response"]

for tc in TEST_CASES:
    codigo_caso = tc["id"].split(" ")[0]
    filename = f"{codigo_caso}.json"
    filepath = os.path.join(TARGET_DIR, filename)
    
    if not os.path.exists(filepath):
        payload = tc["expected_response"]
        
        # Inyección dinámica para los stubs "..." en los casos exitosos
        if codigo_caso.startswith("C201") and codigo_caso != "C201-01":
            payload = happy_path_payload
            
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
            
        print(f"  ✔ Archivo generado: {API_NAME}/{filename}")
    else:
        print(f"  ⚠ Omitido (Ya existe): {API_NAME}/{filename}")

print("\n✨ ¡Ejecución finalizada con éxito!")