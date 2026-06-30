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


# ======================================================
# CONFIGURACIÓN 
# ======================================================

URL = "https://api-qa.newpay.com.ar/v1/debit_card_security_code/code_information?bank_code=007"

HEADERS_BASE = {
    "Content-Type": "application/json",
    "Authorization": "Bearer aa16d813d4cd9dc86453cb40b113"
}

OUTPUT_HTML = f"reporte_debit_card_security_code_qa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
OUTPUT_EXCEL = f"reporte_debit_card_security_code_qa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
OUTPUT_WORD = f"reporte_debit_card_security_code_qa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"

# Payload base 
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


# ======================================================
# EJECUCIÓN 
# ======================================================

def obtener_codigo_error(resp):
    try:
        json_resp = resp.json()
        
        # Para respuestas exitosas (200)
        if resp.status_code == 200:
            if "card_number" in json_resp:
                return "200"
            return str(resp.status_code)
        
        # Para el formato de error específico de esta API: {"error": {"code": "DCSC-XXXX", ...}}
        if "error" in json_resp and isinstance(json_resp["error"], dict):
            error = json_resp["error"]
            if "code" in error:
                return error["code"]
            elif "status" in error:
                # Extraer el código HTTP del status (ej: "400 BAD_REQUEST" -> "400")
                status_parts = error["status"].split()
                if status_parts:
                    return status_parts[0]
        
        # Para errores sin estructura específica
        if "code" in json_resp:
            return json_resp["code"]
        elif "status" in json_resp:
            return str(json_resp["status"])
        else:
            return str(resp.status_code)
    except:
        return str(resp.status_code) if resp.status_code else "N/A"


def obtener_respuesta_formateada(resp):
    try:
        json_resp = resp.json()
        return json.dumps(json_resp, indent=2, ensure_ascii=False)
    except:
        return resp.text


def ejecutar_pruebas():
    resultados = []

    for tc in TEST_CASES:
        # Crear payload 
        payload = copy.deepcopy(BASE_PAYLOAD)
        tc["modificador"](payload)
        
        # Guardar payload 
        payload_str = json.dumps(payload, indent=2, ensure_ascii=False)

        # Usar URL personalizada si existe, sino la URL por defecto
        url = tc.get("url_override", URL)
        
        # Usar headers personalizados si existen, sino los headers base
        headers = tc.get("headers_override", HEADERS_BASE.copy())

        # Ejecutar la solicitud (POST según la documentación)
        response = requests.post(url, headers=headers, json=payload)
        
        obtained = obtener_codigo_error(response)
        obtained_response = obtener_respuesta_formateada(response)
        
        # Determinar si el caso es exitoso según el tipo
        if tc['id'].startswith('C200'):
            # Para casos C200, el éxito es HTTP 200 con estructura de respuesta exitosa
            try:
                json_resp = response.json()
                es_exitoso = (response.status_code == 200 and "card_number" in json_resp)
            except:
                es_exitoso = False
            
            expected_display = "200"
            obtained_display = "200" if es_exitoso else str(response.status_code)
            expected_response_display = tc.get('expected_response', '')
        else:
            # Para casos de error, comparamos los códigos de error personalizados
            es_exitoso = (tc['expected_code'] == obtained)
            expected_display = tc['expected_code']
            obtained_display = obtained
            expected_response_display = tc.get('expected_response', '')

        resultados.append({
            "id": tc["id"],
            "requisito": tc["requisito"],
            "descripcion": tc["descripcion"],
            "expected_code": expected_display,
            "expected_response": expected_response_display,
            "obtained_code": obtained_display,
            "obtained_response": obtained_response,
            "http_status": response.status_code,
            "response": response.text,
            "payload": payload_str,
            "es_exitoso": es_exitoso
        })

    generar_html(resultados)
    generar_excel(resultados)
    generar_word(resultados)


# ======================================================
# FUNCIONES DE REPORTE 
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
    style.font.name = 'Arial'
    style.font.size = Pt(11)
    
    # Título principal
    title = document.add_heading('Reporte de Pruebas - Debit Card Security Code', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Información general
    document.add_heading('Información General', level=1)
    document.add_paragraph(f'Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
    document.add_paragraph(f'Ambiente: QA')
    document.add_paragraph(f'Endpoint: {URL}')
    document.add_paragraph('')

    
    # ======================================================
    # 1. CASOS 
    # ======================================================
    document.add_heading('1. Casos', level=1)
    
    # Crear tabla con 3 columnas: N°, ID del Caso, Objetivo
    tabla_casos = document.add_table(rows=1, cols=3)
    tabla_casos.style = 'Light Grid Accent 1'
    tabla_casos.autofit = True
    
    # Configurar ancho de columnas
    tabla_casos.columns[0].width = Inches(0.5)   # N°
    tabla_casos.columns[1].width = Inches(2.5)   # ID del Caso
    tabla_casos.columns[2].width = Inches(5)     # Objetivo
    
    # Encabezados de la tabla
    encabezados = tabla_casos.rows[0].cells
    encabezados[0].text = 'N°'
    encabezados[1].text = 'ID del Caso'
    encabezados[2].text = 'Objetivo'
    
    # Dar formato a los encabezados
    for cell in encabezados:
        for paragraph in cell.paragraphs:
            paragraph.runs[0].font.bold = True
            paragraph.runs[0].font.size = Pt(12)
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
        if resultado['expected_response']:
            document.add_paragraph(f"Respuesta esperada:")
            try:
                expected_json = json.loads(resultado['expected_response'].replace("'", '"'))
                p = document.add_paragraph()
                run = p.add_run(json.dumps(expected_json, indent=2, ensure_ascii=False))
                run.font.name = 'Courier New'
                run.font.size = Pt(9)
            except:
                document.add_paragraph(resultado['expected_response'])
        
        # Resultado obtenido
        document.add_heading('Resultado Obtenido', level=3)
        document.add_paragraph(f"Código HTTP: {resultado['http_status']}")
        document.add_paragraph(f"Código obtenido: {resultado['obtained_code']}")
        document.add_paragraph(f"Respuesta obtenida:")
        
        # Respuesta de la API
        try:
            response_json = json.loads(resultado['obtained_response'])
            p = document.add_paragraph()
            run = p.add_run(json.dumps(response_json, indent=2, ensure_ascii=False))
            run.font.name = 'Courier New'
            run.font.size = Pt(9)
        except:
            document.add_paragraph(resultado['obtained_response'])

        # Documentacion Tandem
        document.add_heading('Documentacion Tandem', level=3)
        document.add_heading('Audit Tandem', level=4)
        document.add_heading('Pantallas CAF', level=4)

        # Tabla para Pantallas CAF (una columna, una celda)
        tabla_pantallas = document.add_table(rows=1, cols=1)
        tabla_pantallas.style = 'Light Grid Accent 1'
        tabla_pantallas.autofit = False
        tabla_pantallas.columns[0].width = Inches(6)

        # Configurar la celda
        celda_pantallas = tabla_pantallas.cell(0, 0)
        celda_pantallas.text = 'Agregar aquí las pantallas CAF correspondientes si corresponde'
        for paragraph in celda_pantallas.paragraphs:
            for run in paragraph.runs:
                run.font.name = 'Consolas'
                run.font.size = Pt(8)
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

        document.add_paragraph('')
        
        # Estado del caso
        document.add_heading('Estado', level=3)
        estado = "OK" if resultado["es_exitoso"] else "FAIL"
        estado_paragraph = document.add_paragraph()
        run = estado_paragraph.add_run(estado)
        if resultado["es_exitoso"]:
            run.font.color.rgb = RGBColor(0, 128, 0)
        else:
            run.font.color.rgb = RGBColor(255, 0, 0)
        run.bold = True
        
        document.add_heading('Observaciones', level=3)

        if i < len(resultados):
            document.add_page_break()
    
    document.save(OUTPUT_WORD)
    print("✔ Reporte Word generado:", OUTPUT_WORD)


def generar_excel(resultados):
    wb = Workbook()
    ws = wb.active
    ws.title = "Resultados"

    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="2C3E50", end_color="2C3E50", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    
    ok_fill = PatternFill(start_color="C8E6C9", end_color="C8E6C9", fill_type="solid")
    error_fill = PatternFill(start_color="FFCDD2", end_color="FFCDD2", fill_type="solid")
    
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    headers = ["Nombre de caso", "Descripción", "Payload", "Código HTTP", "Expected code", "Expected Response", "Estado", "Evidencia", "Observaciones"]
    ws.append(headers)

    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = border

    for r in resultados:
        estado = "OK" if r["es_exitoso"] else "FAIL"
        
        row = [
            r['id'],
            r['descripcion'],
            r['payload'],
            r['http_status'],
            r['expected_code'],
            r['expected_response'],
            estado,
            "",
            ""
        ]
        ws.append(row)

        current_row = ws.max_row
        for col in range(1, len(headers) + 1):
            cell = ws.cell(row=current_row, column=col)
            cell.border = border
            
            if col == 7:
                if r["es_exitoso"]:
                    cell.fill = ok_fill
                else:
                    cell.fill = error_fill
            
            if col in [4, 5]:
                cell.alignment = Alignment(horizontal="center")
            elif col == 7:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif col in [3, 6]:
                cell.alignment = Alignment(wrap_text=True, vertical="top")

    column_widths = {
        'A': 15, 'B': 40, 'C': 60, 'D': 15, 'E': 20, 'F': 40, 'G': 12, 'H': 20, 'I': 30
    }
    
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width

    wb.save(OUTPUT_EXCEL)
    print("✔ Reporte Excel generado:", OUTPUT_EXCEL)


def generar_html(resultados):
    
    grupos = defaultdict(list)
    for r in resultados:
        grupo = r["id"].split()[0].split("-")[0] if "-" in r["id"] else r["id"].split()[0]
        grupos[grupo].append(r)
   
    nombres_grupos = {
        "C200": "CASOS EXITOSOS",
        "C400": "ERRORES DE NEGOCIO Y VALIDACIÓN",
        "C401": "ERRORES DE AUTENTICACIÓN",
        "C404": "RECURSO NO ENCONTRADO",
        "C500": "ERRORES DE SERVIDOR",
        "C504": "GATEWAY TIMEOUT"
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
                <td><pre style="margin:0; font-size:11px; max-height:100px; overflow:auto;">{r['expected_response']}</pre></td>
                <td>{r['obtained_code']}</td>
                <td>{r['http_status']}</td>
                <td><pre style="margin:0; font-size:11px; max-height:100px; overflow:auto;">{r['obtained_response']}</pre></td>
            </tr>
            """

        nombre_grupo = nombres_grupos.get(grupo, f"GRUPO {grupo}")
        
        bloques += f"""
        <h3>{grupo} – {nombre_grupo}</h3>
        <table>
            <tr>
                <th>ID</th>
                <th>Requisito</th>
                <th>Descripción</th>
                <th>Payload Enviado</th>
                <th>Código Esp.</th>
                <th>Respuesta Esp.</th>
                <th>Código Obtenido</th>
                <th>HTTP</th>
                <th>Respuesta Obtenida</th>
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
        <h1>Reporte QA – Debit Card Security Code</h1>
        <img src="newBrand.svg" height="50">
    </div>

    <p><b>Fecha:</b> {datetime.now()}</p>
    <p><b>Ambiente:</b> QA</p>
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