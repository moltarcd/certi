import copy
# ======================================================
# OBJETO BASE REUTILIZABLE
# ======================================================
BASE_PAYLOAD = {
  "document_type": "DNI",
  "document_number": 31680796,
  "debit_bank_id": "BSTN",
  "cbu": "0150501602000001452345",
  "account_number": "05330113429563",
  "account_type": "11",
  "currency": "ARS",
  "holder_cuit": "20316807969",
  "second_holder_cuit": "",
  "third_holder_cuit": "",
  "denomination": "Caceres claudio",
  "allow_cash_deposits": "S",
  "allow_check_deposits": "S",
  "allow_receive_transfers": "S",
  "last_transfers_date": ""
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
    # C200 - HAPPY PATH
    {"id":"C200-01 Alta CBU OK - Caja de ahorro pesos", "requisito":"Happy Path", "descripcion":"Alta exitosa de CBU", "expected_code":"200", "modificador":lambda p: p},
    {"id":"C200-02 Alta CBU OK - Caja de ahorro USD", "requisito":"Happy Path", "descripcion":"Alta cuenta moneda USD", "expected_code":"200", "modificador":setear("currency","USD")},
    {"id":"C200-03 Alta CBU OK - Cuenta Corriente Pesos", "requisito":"Happy Path", "descripcion":"Alta con segundo titular", "expected_code":"200", "modificador":setear("second_holder_cuit","27316807961")},
    {"id":"C200-04 Alta CBU OK - Cuenta Corriente Pesos", "requisito":"Happy Path", "descripcion":"Nombre con espacios múltiples", "expected_code":"200", "modificador":setear("denomination","Juan   Carlos   Perez")},
    {"id":"C200-05 Alta CBU OK - Cuenta Indefinida", "requisito":"Happy Path", "descripcion":"Caracteres unicode", "expected_code":"200", "modificador":setear("denomination","José Álvarez Ñandú")},
    # REQUIRED
    {"id":"C400-01 document_type requerido", "requisito":"Campo requerido", "descripcion":"Falta document_type", "expected_code":"CBUMGM-DATA_PROBLEM", "modificador":borrar("document_type")},
    {"id":"C400-02 document_number requerido", "requisito":"Campo requerido", "descripcion":"Falta document_number", "expected_code":"CBUMGM-DATA_PROBLEM", "modificador":borrar("document_number")},
    {"id":"C400-03 debit_bank_id requerido", "requisito":"Campo requerido", "descripcion":"Falta debit_bank_id", "expected_code":"CBUMGM-DATA_PROBLEM", "modificador":borrar("debit_bank_id")},
    {"id":"C400-04 cbu requerido", "requisito":"Campo requerido", "descripcion":"Falta cbu", "expected_code":"CBUMGM-DATA_PROBLEM", "modificador":borrar("cbu")},
    {"id":"C400-05 account_number requerido", "requisito":"Campo requerido", "descripcion":"Falta account_number", "expected_code":"CBUMGM-DATA_PROBLEM", "modificador":borrar("account_number")},
    {"id":"C400-06 account_type requerido", "requisito":"Campo requerido", "descripcion":"Falta account_type", "expected_code":"CBUMGM-DATA_PROBLEM", "modificador":borrar("account_type")},
    # LONGITUD
    {"id":"C401-01 cbu longitud inválida", "requisito":"Longitud inválida", "descripcion":"CBU excede longitud", "expected_code":"CBUMGM-DATA_PROBLEM", "modificador":setear("cbu","123456789012345678901234")},
    {"id":"C401-02 holder_cuit longitud inválida", "requisito":"Longitud inválida", "descripcion":"CUIT largo inválido", "expected_code":"CBUMGM-DATA_PROBLEM", "modificador":setear("holder_cuit","12345678901234567890")},
    # FORMATO
    {"id":"C402-01 CBU checksum inválido", "requisito":"Formato inválido", "descripcion":"CBU checksum inválido", "expected_code":"CBUMGM-DATA_PROBLEM", "modificador":setear("cbu","0150501602000001452346")},
    {"id":"C402-02 CUIT inválido", "requisito":"Formato inválido", "descripcion":"CUIT alfanumérico", "expected_code":"CBUMGM-DATA_PROBLEM", "modificador":setear("holder_cuit","20ABC123456")},
    {"id":"C402-03 Fecha inválida", "requisito":"Formato inválido", "descripcion":"last_transfers_date inválida", "expected_code":"CBUMGM-DATA_PROBLEM", "modificador":setear("last_transfers_date","2026-99-99")},
    {"id":"C402-04 Moneda minúscula", "requisito":"Formato inválido", "descripcion":"currency en minúsculas", "expected_code":"CBUMGM-DATA_PROBLEM", "modificador":setear("currency","ars")},
    {"id":"C402-05 account_type vacío", "requisito":"Formato inválido", "descripcion":"account_type vacío", "expected_code":"CBUMGM-DATA_PROBLEM", "modificador":setear("account_type","")},
    {"id":"C402-06 account_type null", "requisito":"Formato inválido", "descripcion":"account_type null", "expected_code":"CBUMGM-DATA_PROBLEM", "modificador":setear("account_type",None)},
    # FUNCIONALES
    {"id":"C500-01 Titular distinto documento", "requisito":"Inconsistencia de datos", "descripcion":"CUIT no corresponde al documento", "expected_code":"CBUMGM-DATA_PROBLEM", "modificador":setear("holder_cuit","20999999991")},
    {"id":"C500-02 Cuenta duplicada", "requisito":"Cuenta existente", "descripcion":"CBU ya existente", "expected_code":"CBUMGM-ACCOUNT_PROBLEM", "modificador":lambda p: p},
    {"id":"C500-03 Institución no habilitada", "requisito":"Institución inválida", "descripcion":"Entidad no habilitada", "expected_code":"CBUMGM-TRX_NOT_ENABLED", "modificador":setear("debit_bank_id","XXXX")},
    {"id":"C500-04 JSON inválido", "requisito":"Formato JSON", "descripcion":"Payload inválido", "expected_code":"CBUMGM-WRONG_PERFORM", "modificador":lambda p: p.update({"document_number": {}})}
]
