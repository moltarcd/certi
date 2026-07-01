import copy

# ======================================================
# OBJETO BASE REUTILIZABLE
# ======================================================
BASE_PAYLOAD = {
    "bank_code": "007",
    "client": {
        "document_type": "DNI",
        "document_number": "41805083"
    },
    "accounts": [
        {
            "number": "100011111978960",
            "type": "CCP",
            "status": "1",
            "acct_origin": "0"
            
            
        }
    ],
    "card": {
        "bin": "442548",
        "last_four_digits": "9623",
        "member": "001"
    },
    "origin": {
        "ip_address": "192.168.1.100",
        "channel": "Z"
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

def cuenta_desde_caso(case_id):
    numeros = re.sub(r"\D", "", case_id)
    return numeros.zfill(15)

# ======================================================
# CASOS DE PRUEBA
# ======================================================

TEST_CASES = [

# ---------- C200 – CASOS ESPECIALES ----------
    {"id":"C200-01 Vinculación de 1 cuenta","requisito":"Happy Path","descripcion":"Todos los datos ok vinculación exitosa de 1 cuenta","expected_code":"200","modificador":lambda p: p},    
    {"id":"C200-02 Vinculación de 6 cuentas","requisito":"Happy Path","descripcion":"Todos los datos ok vinculación exitosa de 6 cuentas","expected_code":"200","modificador":lambda p: p.update({"accounts": [
        {"number": "11001111197896591", "type": "CCP", "status": "0","acct_origin": "0"},
        {"number": "21001111197896592", "type": "CCP", "status": "0","acct_origin": "0"},
        {"number": "31001111197896593", "type": "CCP", "status": "0","acct_origin": "0"},
        {"number": "41001111197896594", "type": "CCP", "status": "0","acct_origin": "0"},
        {"number": "51001111197896595", "type": "CCP", "status": "0","acct_origin": "0"},
        {"number": "61001111197896596", "type": "CCP", "status": "0","acct_origin": "0"}
    ]})},
    
    {"id":"C200-03 Tipo Doc Válidos - DNI","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento DNI","expected_code":"200","modificador":setear("client.document_type","DNI")},
##    {"id":"C200-03 Tipo Doc Válidos - CI","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento CI","expected_code":"200","modificador":setear("client.document_type","CI")},
##    {"id":"C200-03 Tipo Doc Válidos - PAS","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento PAS","expected_code":"200","modificador":setear("client.document_type","PAS")},
##    {"id":"C200-03 Tipo Doc Válidos - LC","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento LC","expected_code":"200","modificador":setear("client.document_type","LC")},
##    {"id":"C200-03 Tipo Doc Válidos - LE","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento LE","expected_code":"200","modificador":setear("client.document_type","LE")},
##    {"id":"C200-03 Tipo Doc Válidos - CUIT","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento CUIT","expected_code":"200","modificador":setear("client.document_type","CUIT")},
##    {"id":"C200-03 Tipo Doc Válidos - CUIL","requisito":"Tipos de documento válidos","descripcion":"Enviar tipo de documento CUIL","expected_code":"200","modificador":setear("client.document_type","CUIL")},    
     {"id":"C200-04 Tipo Cuenta Válidos - CCP","requisito":"Tipos de cuenta válidos","descripcion":"Enviar tipo de cuenta CCP","expected_code":"200","modificador":setear("accounts.0.type","CCP")},
     {"id":"C200-05 Tipo Cuenta Válidos - CCD","requisito":"Tipos de cuenta válidos","descripcion":"Enviar tipo de cuenta CCD","expected_code":"200","modificador":setear("accounts.0.type","CCD")},
     {"id":"C200-06 Tipo Cuenta Válidos - CAP","requisito":"Tipos de cuenta válidos","descripcion":"Enviar tipo de cuenta CAP","expected_code":"200","modificador":setear("accounts.0.type","CAP")},
     {"id":"C200-07 Tipo Cuenta Válidos - CAD","requisito":"Tipos de cuenta válidos","descripcion":"Enviar tipo de cuenta CAD","expected_code":"200","modificador":setear("accounts.0.type","CAD")},
     {"id":"C200-08 Estado Cuenta Válidos - 0","requisito":"Estados de cuenta válidos","descripcion":"Enviar estado de cuenta 0","expected_code":"200","modificador":setear("accounts.0.status","0")},
     {"id":"C200-09 Estado Cuenta Válidos - 1","requisito":"Estados de cuenta válidos","descripcion":"Enviar estado de cuenta 1","expected_code":"200","modificador":setear("accounts.0.status","1")},
     {"id":"C200-10 Estado Cuenta Válidos - 2","requisito":"Estados de cuenta válidos","descripcion":"Enviar estado de cuenta 2","expected_code":"200","modificador":setear("accounts.0.status","2")},
     {"id":"C200-11 Estado Cuenta Válidos - 3","requisito":"Estados de cuenta válidos","descripcion":"Enviar estado de cuenta 3","expected_code":"200","modificador":setear("accounts.0.status","3")},
     {"id":"C200-12 Estado Cuenta Válidos - 4","requisito":"Estados de cuenta válidos","descripcion":"Enviar estado de cuenta 4","expected_code":"200","modificador":setear("accounts.0.status","4")},
     {"id":"C200-13 Estado Cuenta Válidos - 9","requisito":"Estados de cuenta válidos","descripcion":"Enviar estado de cuenta 9","expected_code":"200","modificador":setear("accounts.0.status","9")},
# ---------- C200 – COMBINACIONES TYPE / ACCT_ORIGIN ---------
  #  {"id":"C200-14 CCP acct_origin 0","requisito":"Combinación válida","descripcion":"Tipo de cuenta CCP con acct_origin 0","expected_code":"200","modificador":lambda p: [setear("accounts.0.type","CCP")(p), setear("accounts.0.acct_origin","0")(p)]},
  #  {"id":"C200-15 CCP acct_origin 1","requisito":"Combinación válida","descripcion":"Tipo de cuenta CCP con acct_origin 1","expected_code":"200","modificador":lambda p: [setear("accounts.0.type","CCP")(p), setear("accounts.0.acct_origin","1")(p)]},
  #  {"id":"C200-16 CCP acct_origin 2","requisito":"Combinación válida","descripcion":"Tipo de cuenta CCP con acct_origin 2","expected_code":"200","modificador":lambda p: [setear("accounts.0.type","CCP")(p), setear("accounts.0.acct_origin","2")(p)]},
  #  {"id":"C200-17 CCP acct_origin 6","requisito":"Combinación válida","descripcion":"Tipo de cuenta CCP con acct_origin 6","expected_code":"200","modificador":lambda p: [setear("accounts.0.type","CCP")(p), setear("accounts.0.acct_origin","6")(p)]},
  #  {"id":"C200-18 CCP acct_origin 7","requisito":"Combinación válida","descripcion":"Tipo de cuenta CCP con acct_origin 7","expected_code":"200","modificador":lambda p: [setear("accounts.0.type","CCP")(p), setear("accounts.0.acct_origin","7")(p)]},
  #  {"id":"C200-19 CCP acct_origin 9","requisito":"Combinación válida","descripcion":"Tipo de cuenta CCP con acct_origin 9","expected_code":"200","modificador":lambda p: [setear("accounts.0.type","CCP")(p), setear("accounts.0.acct_origin","9")(p)]},
  #  {"id":"C200-20 CCD acct_origin 0","requisito":"Combinación válida","descripcion":"Tipo de cuenta CCD con acct_origin 0","expected_code":"200","modificador":lambda p: [setear("accounts.0.type","CCD")(p), setear("accounts.0.acct_origin","0")(p)]},
  #  {"id":"C200-21 CCD acct_origin 1","requisito":"Combinación válida","descripcion":"Tipo de cuenta CCD con acct_origin 1","expected_code":"200","modificador":lambda p: [setear("accounts.0.type","CCD")(p), setear("accounts.0.acct_origin","1")(p)]},
  #  {"id":"C200-22 CCD acct_origin 2","requisito":"Combinación válida","descripcion":"Tipo de cuenta CCD con acct_origin 2","expected_code":"200","modificador":lambda p: [setear("accounts.0.type","CCD")(p), setear("accounts.0.acct_origin","2")(p)]},
  #  {"id":"C200-23 CCD acct_origin 3","requisito":"Combinación válida","descripcion":"Tipo de cuenta CCD con acct_origin 3","expected_code":"200","modificador":lambda p: [setear("accounts.0.type","CCD")(p), setear("accounts.0.acct_origin","3")(p)]},
  #  {"id":"C200-24 CCD acct_origin 7","requisito":"Combinación válida","descripcion":"Tipo de cuenta CCD con acct_origin 7","expected_code":"200","modificador":lambda p: [setear("accounts.0.type","CCD")(p), setear("accounts.0.acct_origin","7")(p)]},
  #  {"id":"C200-25 CCD acct_origin 9","requisito":"Combinación válida","descripcion":"Tipo de cuenta CCD con acct_origin 9","expected_code":"200","modificador":lambda p: [setear("accounts.0.type","CCD")(p), setear("accounts.0.acct_origin","9")(p)]},
  #  {"id":"C200-26 CAP acct_origin 0","requisito":"Combinación válida","descripcion":"Tipo de cuenta CAP con acct_origin 0","expected_code":"200","modificador":lambda p: [setear("accounts.0.type","CAP")(p), setear("accounts.0.acct_origin","0")(p)]},
  #  {"id":"C200-27 CAP acct_origin 2","requisito":"Combinación válida","descripcion":"Tipo de cuenta CAP con acct_origin 2","expected_code":"200","modificador":lambda p: [setear("accounts.0.type","CAP")(p), setear("accounts.0.acct_origin","2")(p)]},
  #  {"id":"C200-28 CAP acct_origin 5","requisito":"Combinación válida","descripcion":"Tipo de cuenta CAP con acct_origin 5","expected_code":"200","modificador":lambda p: [setear("accounts.0.type","CAP")(p), setear("accounts.0.acct_origin","5")(p)]},
  #  {"id":"C200-29 CAP acct_origin 7","requisito":"Combinación válida","descripcion":"Tipo de cuenta CAP con acct_origin 7","expected_code":"200","modificador":lambda p: [setear("accounts.0.type","CAP")(p), setear("accounts.0.acct_origin","7")(p)]},
  #  {"id":"C200-30 CAP acct_origin 9","requisito":"Combinación válida","descripcion":"Tipo de cuenta CAP con acct_origin 9","expected_code":"200","modificador":lambda p: [setear("accounts.0.type","CAP")(p), setear("accounts.0.acct_origin","9")(p)]},
  #  {"id":"C200-31 CAD acct_origin 0","requisito":"Combinación válida","descripcion":"Tipo de cuenta CAD con acct_origin 0","expected_code":"200","modificador":lambda p: [setear("accounts.0.type","CAD")(p), setear("accounts.0.acct_origin","0")(p)]},
  #  {"id":"C200-32 CAD acct_origin 2","requisito":"Combinación válida","descripcion":"Tipo de cuenta CAD con acct_origin 2","expected_code":"200","modificador":lambda p: [setear("accounts.0.type","CAD")(p), setear("accounts.0.acct_origin","2")(p)]},
  #  {"id":"C200-33 CAD acct_origin 5","requisito":"Combinación válida","descripcion":"Tipo de cuenta CAD con acct_origin 5","expected_code":"200","modificador":lambda p: [setear("accounts.0.type","CAD")(p), setear("accounts.0.acct_origin","5")(p)]},
  #  {"id":"C200-34 CAD acct_origin 7","requisito":"Combinación válida","descripcion":"Tipo de cuenta CAD con acct_origin 7","expected_code":"200","modificador":lambda p: [setear("accounts.0.type","CAD")(p), setear("accounts.0.acct_origin","7")(p)]},
  #  {"id":"C200-35 CAD acct_origin 9","requisito":"Combinación válida","descripcion":"Tipo de cuenta CAD con acct_origin 9","expected_code":"200","modificador":lambda p: [setear("accounts.0.type","CAD")(p), setear("accounts.0.acct_origin","9")(p)]},
# ---------- C01 – CAMPOS REQUERIDOS ----------
    {"id":"C400-01 Bank_Code is required","requisito":"Campo requerido","descripcion":"Falta bank_code","expected_code":"AL-BAD_REQUEST","modificador":borrar("bank_code")},
    {"id":"C400-02 Client is required","requisito":"Campo requerido","descripcion":"Falta client","expected_code":"AL-BAD_REQUEST","modificador":borrar("client")},
    {"id":"C400-03 DocNum is required","requisito":"Campo requerido","descripcion":"Falta document_number","expected_code":"AL-BAD_REQUEST","modificador":borrar("client.document_number")},
    {"id":"C400-04 Accounts is required","requisito":"Campo requerido","descripcion":"Falta accounts","expected_code":"AL-BAD_REQUEST","modificador":borrar("accounts")},
    {"id":"C400-05 AccNum is required","requisito":"Campo requerido","descripcion":"Falta accounts.number","expected_code":"AL-BAD_REQUEST","modificador":borrar("accounts.0.number")},
    {"id":"C400-06 AccType is required","requisito":"Campo requerido","descripcion":"Falta accounts.type","expected_code":"AL-BAD_REQUEST","modificador":borrar("accounts.0.type")},
    {"id":"C400-07 AccSt is required","requisito":"Campo requerido","descripcion":"Falta accounts.status","expected_code":"AL-BAD_REQUEST","modificador":borrar("accounts.0.status")},
    {"id":"C400-08 Card is required","requisito":"Campo requerido","descripcion":"Falta card","expected_code":"AL-BAD_REQUEST","modificador":borrar("card")},
    {"id":"C400-09 Bin is required","requisito":"Campo requerido","descripcion":"Falta card.bin","expected_code":"AL-BAD_REQUEST","modificador":borrar("card.bin")},
    {"id":"C400-10 Last4 is required","requisito":"Campo requerido","descripcion":"Falta card.last_four_digits","expected_code":"AL-BAD_REQUEST","modificador":borrar("card.last_four_digits")},
    {"id":"C400-11 Member is required","requisito":"Campo requerido","descripcion":"Falta card.member","expected_code":"AL-BAD_REQUEST","modificador":borrar("card.member")},
    {"id":"C400-12 Origin is required","requisito":"Campo requerido","descripcion":"Falta origin","expected_code":"AL-BAD_REQUEST","modificador":borrar("origin")},
    {"id":"C400-13 IP is required","requisito":"Campo requerido","descripcion":"Falta origin.ip_address","expected_code":"AL-BAD_REQUEST","modificador":borrar("origin.ip_address")},
    {"id":"C400-14 Channel is required","requisito":"Campo requerido","descripcion":"Falta origin.channel","expected_code":"AL-BAD_REQUEST","modificador":borrar("origin.channel")},
# ---------- C02 – LONGITUD ----------
    {"id":"C400-15 Bank_Code length","requisito":"Longitud inválida","descripcion":"bank_code largo","expected_code":"AL-BAD_REQUEST","modificador":setear("bank_code","12345")},
    {"id":"C400-16 DocNum length","requisito":"Longitud inválida","descripcion":"document_number largo","expected_code":"AL-BAD_REQUEST","modificador":setear("client.document_number","123456789012345")},
    {"id":"C400-17 AccNum length","requisito":"Longitud inválida","descripcion":"accounts.number largo","expected_code":"AL-BAD_REQUEST","modificador":setear("accounts.0.number","1"*30)},
    {"id":"C400-18 AccType length","requisito":"Longitud inválida","descripcion":"accounts.type largo","expected_code":"AL-BAD_REQUEST","modificador":setear("accounts.0.type","AAAA")},
    {"id":"C400-19 AccSt length","requisito":"Longitud inválida","descripcion":"accounts.status largo","expected_code":"AL-BAD_REQUEST","modificador":setear("accounts.0.status","999")},
    {"id":"C400-20 BIN length","requisito":"Longitud inválida","descripcion":"card.bin largo","expected_code":"AL-BAD_REQUEST","modificador":setear("card.bin","123456789")},
    {"id":"C400-21 Last4 length","requisito":"Longitud inválida","descripcion":"card.last_four_digits largo","expected_code":"AL-BAD_REQUEST","modificador":setear("card.last_four_digits","12345")},
    {"id":"C400-22 Member length","requisito":"Longitud inválida","descripcion":"card.member largo","expected_code":"AL-BAD_REQUEST","modificador":setear("card.member","0012")},
    {"id":"C400-23 IP length","requisito":"Longitud inválida","descripcion":"origin.ip_address inválida","expected_code":"AL-BAD_REQUEST","modificador":setear("origin.ip_address","999.999.999.999.999")},
    {"id":"C400-24 Channel length","requisito":"Longitud inválida","descripcion":"origin.channel largo","expected_code":"AL-BAD_REQUEST","modificador":setear("origin.channel","ZZ")},
# ---------- C03 – FORMATO / DOMINIO ----------
   {"id":"C400-25 Bank_Code Format","requisito":"Formato inválido","descripcion":"bank_code alfanumérico","expected_code":"AL-INVALID_DATA","modificador":setear("bank_code","A12")},
   {"id":"C400-26 DocNum Format","requisito":"Formato inválido","descripcion":"document_number letras","expected_code":"AL-BAD_REQUEST","modificador":setear("client.document_number","ABC123")},
   {"id":"C400-27 AccNum Format","requisito":"Formato inválido","descripcion":"accounts.number símbolos","expected_code":"AL-INVALID_DATA","modificador":setear("accounts.0.number","###")},
   {"id":"C400-28 AccType Format","requisito":"Formato inválido","descripcion":"accounts.type numérico","expected_code":"AL-BAD_REQUEST","modificador":setear("accounts.0.type","123")},
   {"id":"C400-29 AccSt Format","requisito":"Formato inválido","descripcion":"accounts.status letras","expected_code":"AL-INVALID_DATA","modificador":setear("accounts.0.status","A")},
   {"id":"C400-30 BIN Format","requisito":"Formato inválido","descripcion":"card.bin letras","expected_code":"AL-INVALID_DATA","modificador":setear("card.bin","ABCDEF")},
   {"id":"C400-31 Last4 Format","requisito":"Formato inválido","descripcion":"card.last_four_digits letras","expected_code":"AL-INVALID_DATA","modificador":setear("card.last_four_digits","ABCD")},
   {"id":"C400-32 Member Format","requisito":"Formato inválido","descripcion":"card.member símbolos","expected_code":"AL-INVALID_DATA","modificador":setear("card.member","@@@")},
   {"id":"C400-33 IP Format","requisito":"Formato inválido","descripcion":"ip inválida","expected_code":"AL-INVALID_DATA","modificador":setear("origin.ip_address","999.999")},
   {"id":"C400-34 Channel Format","requisito":"Formato inválido","descripcion":"channel inválido","expected_code":"AL-BAD_REQUEST","modificador":setear("origin.channel","X")},
# ---------- FUNCIONALES ----------
   {"id":"C400-36 Invalid card BIN(Legacy 14)","requisito":"Tarjeta inválida","descripcion":"BIN inexistente","expected_code":"AL-INVALID_CARD","modificador":lambda p: p["card"].update({"bin":"000000"})},
   {"id":"C400-37 Invalid card Last4(Legacy 14)","requisito":"Tarjeta inválida","descripcion":"Últimos 4 dígitos inválidos","expected_code":"AL-INVALID_CARD","modificador":lambda p: p["card"].update({"last_four_digits":"0000"})},
   {"id":"C400-38 Invalid card status(Legacy 52)","requisito":"Estado de tarjeta inválido","descripcion":"Estado no permite vinculación","expected_code":"AL-INVALID_CARD_STATUS","modificador":lambda p: p["card"].update({"status":"9"})},
   {"id":"C400-39 Data mismatch","requisito(Legacy 31)":"Documento no coincide","descripcion":"Documento distinto al titular","expected_code":"AL-INVALID_CARD","modificador":lambda p: p["client"].update({"document_number":"11111111"})},
   {"id":"C400-40 Max accounts reached(Legacy 76)","requisito":"Máximo de cuentas alcanzado","descripcion":"Tarjeta con máximo de cuentas","expected_code":"AL-MAX_ACCOUNTS_REACHED","modificador":lambda p: p},
   {"id":"C400-41 Client not found(Legacy 50)","requisito":"Cliente inexistente","descripcion":"Cliente no encontrado","expected_code":"AL-INVALID_CARD","modificador":lambda p: p["client"].update({"document_number":"99999999"})},
   {"id":"C400-42 Max per request","requisito":"Máximo de cuentas Por Request","descripcion":"Tarjeta con máximo de cuentas","expected_code":"AL-AL-BAD_REQUEST","modificador":lambda p: p},
   {"id":"C400-43 Tipo Doc no permitido","requisito":"Formato inválido","descripcion":"document_number no valido","expected_code":"AL-BAD_REQUEST","modificador":setear("client.document_number","PNI")},
   {"id":"C400-44 Tipo Cta no permitido","requisito":"Formato inválido","descripcion":"accounts.type no valido","expected_code":"AL-BAD_REQUEST","modificador":setear("accounts.0.type","CCC")},
   {"id":"C400-45 Estado Cta No Permitido","requisito":"Formato inválido","descripcion":"accounts.status 7","expected_code":"AL-BAD_REQUEST","modificador":setear("accounts.0.status","7")},
   {"id":"C400-46 Miembro no permitido","requisito":"Formato inválido","descripcion":"card.member 002","expected_code":"AL-INVALID_DATA","modificador":setear("card.member","@@@")},
   {"id":"C400-48 Tx98 No configurado(Legacy 54)","requisito":"Código banco inválido","descripcion":"bank_code inexistente","expected_code":"AL-DATA_PROBLEM","modificador":lambda p: p.update({"bank_code":"386"})},
   {"id":"C400-49 Tx98 MAX","requisito":"Código banco inválido","descripcion":"bank_code inexistente","expected_code":"AL-DATA_PROBLEM","modificador":lambda p: p.update({"bank_code":"999"})},
## ---------- C400 – VALIDACIONES TYPE / ACCT_ORIGIN ----------
   # {"id":"C400-50 CCP acct_origin 5","requisito":"Combinación inválida","descripcion":"Tipo CCP con acct_origin no permitido","expected_code":"AL-BAD_REQUEST","modificador":lambda p: [setear("accounts.0.type","CCP")(p), setear("accounts.0.acct_origin","5")(p)]},
   # {"id":"C400-51 CCD acct_origin 5","requisito":"Combinación inválida","descripcion":"Tipo CCD con acct_origin no permitido","expected_code":"AL-BAD_REQUEST","modificador":lambda p: [setear("accounts.0.type","CCD")(p), setear("accounts.0.acct_origin","5")(p)]},
   # {"id":"C400-52 CAP acct_origin 1","requisito":"Combinación inválida","descripcion":"Tipo CAP con acct_origin no permitido","expected_code":"AL-BAD_REQUEST","modificador":lambda p: [setear("accounts.0.type","CAP")(p), setear("accounts.0.acct_origin","1")(p)]},
   # {"id":"C400-53 CAD acct_origin 1","requisito":"Combinación inválida","descripcion":"Tipo CAD con acct_origin no permitido","expected_code":"AL-BAD_REQUEST","modificador":lambda p: [setear("accounts.0.type","CAD")(p), setear("accounts.0.acct_origin","1")(p)]},
   # {"id":"C400-54 CAP acct_origin 6","requisito":"Combinación inválida","descripcion":"Tipo CAP con acct_origin no permitido","expected_code":"AL-BAD_REQUEST","modificador":lambda p: [setear("accounts.0.type","CAP")(p), setear("accounts.0.acct_origin","6")(p)]},
   # {"id":"C400-55 CAD acct_origin 6","requisito":"Combinación inválida","descripcion":"Tipo CAD con acct_origin no permitido","expected_code":"AL-BAD_REQUEST","modificador":lambda p: [setear("accounts.0.type","CAD")(p), setear("accounts.0.acct_origin","6")(p)]},
   # {"id":"C400-05 Type inválido","requisito":"Dominio inválido","descripcion":"type inválido con acct_origin válido","expected_code":"AL-BAD_REQUEST","modificador":setear("accounts.0.type","XXX")},
   # {"id":"C400-57 acct_origin longitud inválida","requisito":"Longitud inválida","descripcion":"acct_origin supera longitud permitida","expected_code":"AL-BAD_REQUEST","modificador":setear("accounts.0.acct_origin","99")},
   # {"id":"C400-58 acct_origin string","requisito":"Formato inválido","descripcion":"acct_origin alfabético","expected_code":"AL-BAD_REQUEST","modificador":setear("accounts.0.acct_origin","A")},
   # {"id":"C400-59 Falta type","requisito":"Campo requerido","descripcion":"type vacío","expected_code":"AL-BAD_REQUEST","modificador":setear("accounts.0.type","")},
   # {"id":"C400-60 Falta acct_origin","requisito":"Campo requerido","descripcion":"acct_origin vacío","expected_code":"AL-BAD_REQUEST","modificador":setear("accounts.0.acct_origin","")},
   # {"id":"C400-61 Sin campo type","requisito":"Campo requerido","descripcion":"No se informa type","expected_code":"AL-BAD_REQUEST","modificador":borrar("accounts.0.type")},
   # {"id":"C400-62 Sin campo acct_origin","requisito":"Campo requerido","descripcion":"No se informa acct_origin","expected_code":"AL-BAD_REQUEST","modificador":borrar("accounts.0.acct_origin")},
]
