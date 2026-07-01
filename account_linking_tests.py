import requests
import json
import copy
from datetime import datetime
from collections import defaultdict
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
import re
import time

# ======================================================
# COMPLETAR CON LOS DATOS DEL MAIL DE ENTREGA
# ======================================================

FECHMAIL = "2026-06-01"
HASHMAIL = ""
MSJSMAIL = ""

# ======================================================
# CONFIGURACIÓN
# ======================================================

URL = "https://api-qa.newpay.com.ar/v1/account-linking/bind"

HEADERS_BASE = {
    "Content-Type": "application/json",
    "Authorization": "Bearer c2bebe58e3215853e619dd5fe048",
    "x-apip-client-id": "test",
    "x-apip-partner-id": "test",
    "x-apip-cuit": "20304050607"
}

OUTPUT_HTML = f"reporte_account_linking_qa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
OUTPUT_EXCEL = f"reporte_account_linking_qa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
OUTPUT_WORD = f"reporte_account_linking_qa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"

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


# ======================================================
# EJECUCIÓN
# ======================================================

def obtener_codigo_error(resp):
    try:
        json_resp = resp.json()
        
        # Para respuestas exitosas (200)
        if resp.status_code == 200:
            if json_resp.get("success") is True:
                return "200"
            return str(resp.status_code)
        
        # Para respuestas de error, intentar obtener el código del body
        if "code" in json_resp:
            return json_resp["code"]
        elif "error" in json_resp and isinstance(json_resp["error"], dict):
            return json_resp["error"].get("code", str(resp.status_code))
        elif "error" in json_resp and isinstance(json_resp["error"], str):
            return json_resp["error"]
        else:
            return str(resp.status_code)
    except:
        return str(resp.status_code) if resp.status_code else "N/A"


def ejecutar_pruebas():
    resultados = []
    SLEEP_BETWEEN_TESTS = 0.5  # Segundos de espera entre casos

    for i, tc in enumerate(TEST_CASES):
        # Crear payload
        payload = copy.deepcopy(BASE_PAYLOAD)

        # Asignar cuenta única para casos C200
        if tc["id"].startswith("C200"):
            payload["accounts"][0]["number"] = cuenta_desde_caso(tc["id"])

        tc["modificador"](payload)
        
        # Guardar payload 
        payload_str = json.dumps(payload, indent=2, ensure_ascii=False)

        # Ejecutar la solicitud
        print(f"Ejecutando caso {i+1}/{len(TEST_CASES)}: {tc['id']}")
        response = requests.post(URL, headers=HEADERS_BASE, json=payload)
        
        obtained = obtener_codigo_error(response)
        
        if tc['id'].startswith('C200'):
            try:
                json_resp = response.json()
                es_exitoso = (response.status_code == 200 and json_resp.get("success") is True)
            except:
                es_exitoso = False
            
            expected_display = "200"
            obtained_display = "200" if es_exitoso else str(response.status_code)
        else:
            es_exitoso = (tc['expected_code'] == obtained)
            expected_display = tc['expected_code']
            obtained_display = obtained

        resultados.append({
            "id": tc["id"],
            "requisito": tc["requisito"],
            "descripcion": tc["descripcion"],
            "expected_code": expected_display,
            "obtained_code": obtained_display,
            "http_status": response.status_code,
            "response": response.text,
            "payload": payload_str,
            "es_exitoso": es_exitoso  
        })
        
       
        if i < len(TEST_CASES) - 1:
            print(f"Esperando {SLEEP_BETWEEN_TESTS} segundos...")
            time.sleep(SLEEP_BETWEEN_TESTS)

    generar_html(resultados)
    #generar_excel(resultados)
    generar_word(resultados)
    resultados = []

    for tc in TEST_CASES:
        # Crear payload
        payload = copy.deepcopy(BASE_PAYLOAD)

        # Asignar cuenta única para casos C200
        if tc["id"].startswith("C200"):
            payload["accounts"][0]["number"] = cuenta_desde_caso(tc["id"])

        tc["modificador"](payload)
        
        # Guardar payload 
        payload_str = json.dumps(payload, indent=2, ensure_ascii=False)

        # Ejecutar la solicitud
        response = requests.post(URL, headers=HEADERS_BASE, json=payload)
        
        obtained = obtener_codigo_error(response)
        
        if tc['id'].startswith('C200'):
            try:
                json_resp = response.json()
                es_exitoso = (response.status_code == 200 and json_resp.get("success") is True)
            except:
                es_exitoso = False
            
            expected_display = "200"
            obtained_display = "200" if es_exitoso else str(response.status_code)
        else:
            es_exitoso = (tc['expected_code'] == obtained)
            expected_display = tc['expected_code']
            obtained_display = obtained

        resultados.append({
            "id": tc["id"],
            "requisito": tc["requisito"],
            "descripcion": tc["descripcion"],
            "expected_code": expected_display,
            "obtained_code": obtained_display,
            "http_status": response.status_code,
            "response": response.text,
            "payload": payload_str,
            "es_exitoso": es_exitoso  
        })

    generar_html(resultados)
    #generar_excel(resultados)
    generar_word(resultados)

# ======================================================
# WORD
# ======================================================

def generar_word(resultados):
    try:
        from docx import Document
        from docx.shared import Inches, Pt, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
    except ImportError:
        print("❌ Error: No está instalada la librería python-docx")
        print("   Instálala con: pip install python-docx")
        return
    
    document = Document()
    
    # Configurar estilos
    style = document.styles['Normal']
    style.font.name = 'Courier New'
    style.font.size = Pt(9)
    style.paragraph_format.space_before = Pt(0)
    style.paragraph_format.space_after = Pt(0)
    style.paragraph_format.line_spacing = 1
    
    # Título principal
    title = document.add_heading('Reporte de Pruebas - Account Linking', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Información general
    document.add_heading('Información General', level=1)
    p = document.add_paragraph()
    p.add_run('Fecha: ').bold = True
    p.add_run(datetime.now().strftime("%d/%m/%Y"))

    p = document.add_paragraph()
    p.add_run('Ambiente: ').bold = True
    p.add_run('QA')

    p = document.add_paragraph()
    p.add_run('Endpoint: ').bold = True
    p.add_run(URL)

    p = document.add_paragraph()
    p.add_run('Commit: ').bold = True
    p.add_run(HASHMAIL)

    p = document.add_paragraph()
    p.add_run('Fecha Commit: ').bold = True
    p.add_run(FECHMAIL)

    p = document.add_paragraph()
    p.add_run('Rama: ').bold = True
    p.add_run('main')

    p = document.add_paragraph()
    p.add_run('Mensaje: ').bold = True
    p.add_run(MSJSMAIL)

 
    
    # ======================================================
    # 1. CASOS 
    # ======================================================
    document.add_heading('1. Casos', level=1)
    
    tabla_casos = document.add_table(rows=1, cols=3)
    tabla_casos.style = 'Light Grid Accent 1'
    tabla_casos.autofit = True
    
    # Configurar ancho de columnas
    tabla_casos.columns[0].width = Inches(0.3346)   # N°
    tabla_casos.columns[1].width = Inches(2.6929)  # ID del Caso
    tabla_casos.columns[2].width = Inches(3.1220)  # Objetivo
    
    # Encabezados de la tabla
    encabezados = tabla_casos.rows[0].cells
    encabezados[0].text = 'N°'
    encabezados[1].text = 'ID del Caso'
    encabezados[2].text = 'Objetivo'
    
    # Dar formato a los encabezados
    for cell in encabezados:
        for paragraph in cell.paragraphs:
            paragraph.runs[0].font.bold = True
            paragraph.runs[0].font.size = Pt(11)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Agregar los casos a la tabla
    for i, resultado in enumerate(resultados, 1):
        # Agregar una nueva fila
        fila = tabla_casos.add_row()
        
        # N° (centrado)
        fila.cells[0].text = str(i)
        fila.cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # ID del Caso
        fila.cells[1].text = resultado['id']
        
        # Objetivo (descripción)
        fila.cells[2].text = resultado['descripcion']
    
    # Espacio después de la tabla
    document.add_paragraph('')
    
    # ======================================================
    # 2. EVIDENCIAS 
    # ======================================================
    document.add_page_break()
    document.add_heading('2. Evidencias', level=1)
    
    for i, resultado in enumerate(resultados, 1):
        # Título nivel 2: ID del caso
        document.add_heading(f"{resultado['id']}", level=2)
        
        # Objetivo (nivel 3)
        document.add_heading('Objetivo', level=3)
        document.add_paragraph(resultado['descripcion'])
        
        # Payload enviado
        document.add_heading('Payload Enviado', level=3)
        try:
            payload_json = json.loads(resultado['payload'])
            p = document.add_paragraph()
            run = p.add_run(json.dumps(payload_json, indent=2, ensure_ascii=False))
            run.font.name = 'Courier New'
            run.font.size = Pt(9)
        except:
            document.add_paragraph(resultado['payload'])
        
        # Resultado esperado
        document.add_heading('Resultado Esperado', level=3)
        document.add_paragraph(f"Código esperado: {resultado['expected_code']}")
        
        # Resultado obtenido
        document.add_heading('Resultado Obtenido', level=3)
        document.add_paragraph(f"Código HTTP: {resultado['http_status']}")
        document.add_paragraph(f"Código obtenido: {resultado['obtained_code']}")
        
        # Respuesta de la API
        document.add_heading('Respuesta de la API', level=3)
        try:
            response_json = json.loads(resultado['response'])
            p = document.add_paragraph()
            run = p.add_run(json.dumps(response_json, indent=2, ensure_ascii=False))
            run.font.name = 'Courier New'
            run.font.size = Pt(9)
        except:
            document.add_paragraph(resultado['response'])

        # Documentacion Tandem
        document.add_heading('Documentacion Tandem', level=3)
        document.add_heading('Audit Tandem', level=4)
        document.add_heading('Pantallas CAF', level=4)
        document.add_heading('Pantallas HPBT', level=4)

        # Tabla para Pantallas CAF (una columna, una celda)
        tabla_pantallas = document.add_table(rows=1, cols=1)
        tabla_pantallas.style = 'Light Grid Accent 1'
        tabla_pantallas.autofit = False
        tabla_pantallas.columns[0].width = Inches(6)  # Ancho de la tabla

        # Configurar la celda
        celda_pantallas = tabla_pantallas.cell(0, 0)
        celda_pantallas.text = 'Agregar aquí las pantallas CAF correspondientes si corresponde'
        for paragraph in celda_pantallas.paragraphs:
            for run in paragraph.runs:
                run.font.name = 'Consolas'
                run.font.size = Pt(8)
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Espacio después de la tabla
        document.add_paragraph('')
        
        # Estado del caso
        document.add_heading('Estado', level=3)
        estado = "OK" if resultado["es_exitoso"] else "FAIL"
        estado_paragraph = document.add_paragraph()
        run = estado_paragraph.add_run(estado)
        if resultado["es_exitoso"]:
            run.font.color.rgb = RGBColor(0, 128, 0)  # Verde
        else:
            run.font.color.rgb = RGBColor(255, 0, 0)  # Rojo
        run.bold = True
        
        # Observaciones
        document.add_heading('Observaciones', level=3)

        
        # Salto de página entre evidencias (excepto la última)
        if i < len(resultados):
            document.add_page_break()
    
    # Guardar documento
    document.save(OUTPUT_WORD)
    print("✔ Reporte Word generado:", OUTPUT_WORD)


# ======================================================
# EXCEL
# ======================================================

# def generar_excel(resultados):
#     wb = Workbook()
#     ws = wb.active
#     ws.title = "Resultados"

#     # Definir estilos
#     header_font = Font(bold=True, color="FFFFFF")
#     header_fill = PatternFill(start_color="2C3E50", end_color="2C3E50", fill_type="solid")
#     header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    
#     ok_fill = PatternFill(start_color="C8E6C9", end_color="C8E6C9", fill_type="solid")
#     error_fill = PatternFill(start_color="FFCDD2", end_color="FFCDD2", fill_type="solid")
    
#     border = Border(
#         left=Side(style='thin'),
#         right=Side(style='thin'),
#         top=Side(style='thin'),
#         bottom=Side(style='thin')
#     )

#     # Encabezados
#     headers = ["Nombre de caso", "Descripción", "Payload", "Código HTTP", "Expected code", "Estado", "Evidencia", "Observaciones"]
#     ws.append(headers)

#     # Aplicar formato a los encabezados
#     for col in range(1, len(headers) + 1):
#         cell = ws.cell(row=1, column=col)
#         cell.font = header_font
#         cell.fill = header_fill
#         cell.alignment = header_alignment
#         cell.border = border

#     # Agregar datos
#     for r in resultados:
#         estado = "OK" if r["es_exitoso"] else "FAIL"
        
#         row = [
#             r['id'],
#             r['descripcion'],
#             r['payload'],
#             r['http_status'],
#             r['expected_code'],
#             estado,
#             "",  # Evidencia (vacío)  ver como llenarlo
#             ""   # Observaciones (vacío) ver como llenarlo
#         ]
#         ws.append(row)

#         # Aplicar formato a la fila
#         current_row = ws.max_row
#         for col in range(1, len(headers) + 1):
#             cell = ws.cell(row=current_row, column=col)
#             cell.border = border
            
#             # Color según estado
#             if col == 6:  # Columna Estado
#                 if r["es_exitoso"]:
#                     cell.fill = ok_fill
#                 else:
#                     cell.fill = error_fill
            
#             # Alineación para algunas columnas
#             if col in [4, 5]:  # Código HTTP y Expected code
#                 cell.alignment = Alignment(horizontal="center")
#             elif col == 6:  # Estado
#                 cell.alignment = Alignment(horizontal="center", vertical="center")
#             elif col == 3:  # Payload
#                 cell.alignment = Alignment(wrap_text=True, vertical="top")

#     # Ajustar ancho de columnas
#     column_widths = {
#         'A': 15,  # Nombre de caso
#         'B': 40,  # Descripción
#         'C': 60,  # Payload
#         'D': 15,  # Código HTTP
#         'E': 20,  # Expected code
#         'F': 12,  # Estado
#         'G': 20,  # Evidencia
#         'H': 30,  # Observaciones
#     }
    
#     for col, width in column_widths.items():
#         ws.column_dimensions[col].width = width

#     # Guardar archivo
#     wb.save(OUTPUT_EXCEL)
#     print("✔ Reporte Excel generado:", OUTPUT_EXCEL)

# # ======================================================
# # HTML 
# ======================================================

def generar_html(resultados):
    
    # Agrupar por grupo
    grupos = defaultdict(list)
    for r in resultados:
        # Extraer el grupo del ID (C200, C400, etc.)
        grupo = r["id"].split()[0].split("-")[0] if "-" in r["id"] else r["id"].split()[0]
        grupos[grupo].append(r)
   
    nombres_grupos = {
        "C200": "CASOS ESPECIALES",
        "C400": "CASOS DE VALIDACIÓN",
        "C1801": "TIMEOUT HOST"
    }

    total = len(resultados)
    ok = sum(1 for r in resultados if r["es_exitoso"])
    error = total - ok
    porcentaje = round((ok / total) * 100, 2)

    resumen_grupos = {}
    for r in resultados:
        g = r["id"].split()[0].split("-")[0] if "-" in r["id"] else r["id"].split()[0]
        if g not in resumen_grupos:
            resumen_grupos[g] = {"ok": 0, "error": 0, "nombre": nombres_grupos.get(g, f"GRUPO {g}")}
        if r["es_exitoso"]:
            resumen_grupos[g]["ok"] += 1
        else:
            resumen_grupos[g]["error"] += 1

    bloques = ""
    for grupo, items in grupos.items():
        filas = ""
        for r in items:
            clase = "ok" if r["es_exitoso"] else "error"
            filas += f"""
            <tr class="{clase}">
                <td>{r['id']}</td>
                <td>{r['requisito']}</td>
                <td>{r['descripcion']}</td>
                <td><pre style="margin:0; font-size:11px; max-height:100px; overflow:auto;">{r['payload']}</pre></td>
                <td>{r['expected_code']}</td>
                <td>{r['obtained_code']}</td>
                <td>{r['http_status']}</td>
                <td><pre style="margin:0; font-size:11px; max-height:100px; overflow:auto;">{r['response']}</pre></td>
            </tr>
            """

        # Obtener el nombre descriptivo del grupo
        nombre_grupo = nombres_grupos.get(grupo, f"GRUPO {grupo}")
        
        bloques += f"""
        <h3>{grupo} – {nombre_grupo}</h3>
        <table>
            <tr>
                <th>ID</th>
                <th>Requisito</th>
                <th>Descripción</th>
                <th>Payload Enviado</th>
                <th>Esperado</th>
                <th>Obtenido</th>
                <th>HTTP</th>
                <th>Respuesta</th>
            </tr>
            {filas}
        </table>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial; font-size: 13px; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 25px; }}
            th, td {{ border: 1px solid #ccc; padding: 6px; vertical-align: top; }}
            th {{ background: #2c3e50; color: white; }}
            .ok {{ background: #c8e6c9; }}
            .error {{ background: #ffcdd2; }}
            .header {{ display:flex; justify-content:space-between; align-items:center; }}
            pre {{ 
                white-space: pre-wrap;
                word-wrap: break-word;
                margin: 0;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }}
            h3 {{ 
                background: #f5f5f5;
                padding: 10px;
                border-left: 4px solid #2c3e50;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>

    <div class="header">
        <h1>Reporte QA – Account Linking</h1>
        <img src="newBrand.svg" height="50">
    </div>

    <p><b>Fecha:</b> {datetime.now()}</p>
    <p><b>Ambiente:</b> CERTIFICACIÓN</p>
    <p><b>Endpoint:</b> {URL}</p>

    <h2>Resumen Ejecutivo</h2>

    <table>
        <tr><th>Total</th><th>OK</th><th>Error</th><th>% Éxito</th></tr>
        <tr>
            <td>{total}</td>
            <td style="background:#c8e6c9">{ok}</td>
            <td style="background:#ffcdd2">{error}</td>
            <td>{porcentaje}%</td>
        </tr>
    </table>

    <h3>Resultado por Grupo</h3>
    <table>
        <tr><th>Grupo</th><th>Nombre</th><th>OK</th><th>Error</th><th>Estado</th></tr>
    """

    for g, v in resumen_grupos.items():
        estado = "OK" if v["error"] == 0 else "FAIL"
        color = "#c8e6c9" if estado == "OK" else "#ffcdd2"
        nombre = v["nombre"]
        html += f"""
        <tr style="background:{color}">
            <td>{g}</td>
            <td>{nombre}</td>
            <td>{v['ok']}</td>
            <td>{v['error']}</td>
            <td>{estado}</td>
        </tr>
        """

    html += f"""
    </table>
    <hr>

    <h2>Resultados Detallados</h2>

    {bloques}

    </body>
    </html>
    """

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print("✔ Reporte HTML generado:", OUTPUT_HTML)
    

if __name__ == "__main__":
    ejecutar_pruebas()