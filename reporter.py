import os
import sys
import json
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

# Manejo seguro de importación opcional para docx manteniendo tu lógica original
try:
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
except ImportError:
    pass


@dataclass
class TestCaseResult:
    id: str
    requisito: str
    descripcion: str
    expected_code: str
    obtained_code: str
    http_status: int
    payload: str  # JSON formateado string
    response: str  # JSON formateado o texto string
    es_exitoso: bool
    expected_response: str = ""


class APITestReporter:

    def __init__(self, url_endpoint, output_dir="reportes", json_metadata_path="metadata_mail.json"):
        self.url_endpoint = url_endpoint
        self.output_dir = output_dir
        
        # 1. Configurar valores por defecto por seguridad (Fallback)
        self.metadata = {
            "commit": "Local Run - No Commit",
            "fecha_commit": datetime.now().strftime("%Y-%m-%d"),
            "autor": "QA Automation Team",
            "rama": "local",
            "mensaje": "Ejecución manual de pruebas locales"
        }
        
        # 2. Intentar leer el archivo JSON de forma performante
        if os.path.exists(json_metadata_path):
            try:
                with open(json_metadata_path, "r", encoding="utf-8") as f:
                    datos_json = json.load(f)
                    if isinstance(datos_json, dict):
                        self.metadata.update(datos_json)
            except Exception as e:
                print(f"⚠ Advertencia: No se pudo leer {json_metadata_path} debido a un error: {e}")
                print("Se utilizarán los metadatos locales por defecto.")
        
        # 3. Crear la carpeta si no existe
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        # 4. Obtener el nombre del script ejecutor de forma dinámica
        script_basename = os.path.basename(sys.argv[0])
        script_name, _ = os.path.splitext(script_basename)
        if not script_name or script_name == '<stdin>':
            script_name = "reporte_api"
            
        self.titulo_reporte = script_name.replace("_", " ").title()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 5. Guardar las rutas de archivos finales
        self.output_html = os.path.join(self.output_dir, f"reporte_{script_name}_{timestamp}.html")
        self.output_excel = os.path.join(self.output_dir, f"reporte_{script_name}_{timestamp}.xlsx")
        self.output_word = os.path.join(self.output_dir, f"reporte_{script_name}_{timestamp}.docx")

    def generar_todos(self, resultados: list):
        """Método de conveniencia para disparar la suite completa de reportes."""
        # Convierte a diccionarios si viene como dataclasses para mantener compatibilidad exacta
        resultados_dict = [
            r.__dict__ if isinstance(r, TestCaseResult) else r for r in resultados
        ]
        self.generar_html(resultados_dict)
        self.generar_excel(resultados_dict)
        self.generar_word(resultados_dict)
        
########################
######   WORD  ########
#######################
 
    def generar_word(self, resultados: list):
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
        style.font.size = Pt(11)
        
        # Título principal
        title = document.add_heading(f'Reporte de Pruebas - {self.titulo_reporte}', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        #Información general
        document.add_heading('Información General', level=1)
        document.add_paragraph(f'Fecha Reporte: {datetime.now().strftime("%d/%m/%Y ")}')
        document.add_paragraph(f'Ambiente: QA')
        document.add_paragraph(f'Endpoint: {self.url_endpoint}')
        document.add_paragraph(f'Commit: {self.metadata["commit"]}')
        document.add_paragraph(f'Fecha Commit: {self.metadata["fecha_commit"]}')
        document.add_paragraph(f'Autor: {self.metadata["autor"]}')
        document.add_paragraph(f'Rama: {self.metadata["rama"]}')
        document.add_paragraph(f'Mensaje: {self.metadata["mensaje"]}')
        document.add_paragraph('')

        # ======================================================
        # 1. CASOS 
        # ======================================================
        document.add_heading('1. Casos', level=1)
        
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
            fila = tabla_casos.add_row()
            
            fila.cells[0].text = str(i)
            fila.cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            fila.cells[1].text = resultado['id']
            fila.cells[2].text = resultado['descripcion']
        
        document.add_paragraph('')
        
        # ======================================================
        # 2. EVIDENCIAS 
        # ======================================================
        document.add_page_break()
        document.add_heading('2. Evidencias', level=1)
        
        for i, resultado in enumerate(resultados, 1):
            # Convertir a diccionario si llega como Dataclass para asegurar la lectura por clave str
            r_data = resultado.__dict__ if hasattr(resultado, '__dict__') else resultado

            document.add_heading(f"{r_data['id']}", level=2)
            
            document.add_heading('Objetivo', level=3)
            document.add_paragraph(r_data['descripcion'])
            
            document.add_heading('Payload Enviado', level=3)
            try:
                payload_json = json.loads(r_data['payload'])
                p = document.add_paragraph()
                run = p.add_run(json.dumps(payload_json, indent=2, ensure_ascii=False))
                run.font.name = 'Courier New'
                run.font.size = Pt(9)
            except:
                document.add_paragraph(r_data['payload'])
            
            # =============================================================
            # RESULTADO ESPERADO (Formateado como JSON Body de la API)
            # =============================================================
            document.add_heading('Resultado Esperado', level=3)
            document.add_paragraph(f"Código esperado: {r_data['expected_code']}")
            
            exp_resp = r_data.get('expected_response', '')
            if exp_resp:
                try:
                    # 1. Limpieza previa por si viene con comillas simples o saltos de línea huérfanos
                    if isinstance(exp_resp, str):
                        cleaned_resp = exp_resp.strip()
                        # Si es un string JSON válido pero usa comillas simples de Python, las normalizamos a dobles
                        if cleaned_resp.startswith("{") or cleaned_resp.startswith("["):
                            # Reemplazo seguro de comillas simples a dobles para que json.loads no falle
                            import re
                            cleaned_resp = cleaned_resp.replace("'", '"')
                            expected_json = json.loads(cleaned_resp)
                        else:
                            raise ValueError()
                    elif isinstance(exp_resp, dict) or isinstance(exp_resp, list):
                        expected_json = exp_resp
                    else:
                        raise ValueError()

                    # 2. Imprimir el cuerpo JSON con la estructura e indentación idéntica a la API
                    p = document.add_paragraph()
                    run = p.add_run(json.dumps(expected_json, indent=2, ensure_ascii=False))
                    run.font.name = 'Courier New'
                    run.font.size = Pt(9)
                    
                except Exception:
                    # Fallback: Si no es un JSON convertible (texto plano o error), se imprime directo con estilo Courier
                    p = document.add_paragraph()
                    run = p.add_run(str(exp_resp))
                    run.font.name = 'Courier New'
                    run.font.size = Pt(9)
            # =============================================================
            
            document.add_heading('Resultado Obtenido', level=3)
            document.add_paragraph(f"Código obtenido: {r_data['obtained_code']}")
            
            document.add_heading('Respuesta de la API', level=3)
            try:
                response_json = json.loads(r_data['response'])
                p = document.add_paragraph()
                run = p.add_run(json.dumps(response_json, indent=2, ensure_ascii=False))
                run.font.name = 'Courier New'
                run.font.size = Pt(9)
            except:
                document.add_paragraph(r_data['response'])

            document.add_heading('Documentación Tandem', level=3)
            
            document.add_heading('Audit Tandem', level=4)            
            tabla_pantallas = document.add_table(rows=1, cols=1)
            tabla_pantallas.style = 'Light Grid Accent 1'
            tabla_pantallas.autofit = False
            tabla_pantallas.columns[0].width = Inches(6)
            celda_pantallas = tabla_pantallas.cell(0, 0)
            celda_pantallas.text = 'Agregar aquí las pantallas/logs correspondientes si aplica'
            for paragraph in celda_pantallas.paragraphs:
                for run in paragraph.runs:
                    run.font.name = 'Courier New'
                    run.font.size = Pt(8)
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            document.add_paragraph('')
            
            document.add_heading('Pantallas Base24', level=4)
            tabla_pantallas = document.add_table(rows=1, cols=1)
            tabla_pantallas.style = 'Light Grid Accent 1'
            tabla_pantallas.autofit = False
            tabla_pantallas.columns[0].width = Inches(6)
            celda_pantallas = tabla_pantallas.cell(0, 0)
            celda_pantallas.text = 'Agregar aquí las pantallas/logs correspondientes si aplica'
            for paragraph in celda_pantallas.paragraphs:
                for run in paragraph.runs:
                    run.font.name = 'Courier New'
                    run.font.size = Pt(8)
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            document.add_paragraph('')
            
            document.add_heading('Log Centro de Servicios', level=3)            
            tabla_pantallas = document.add_table(rows=1, cols=1)
            tabla_pantallas.style = 'Light Grid Accent 1'
            tabla_pantallas.autofit = False
            tabla_pantallas.columns[0].width = Inches(6)
            celda_pantallas = tabla_pantallas.cell(0, 0)
            celda_pantallas.text = 'Agregar aquí las pantallas/logs correspondientes si aplica'
            for paragraph in celda_pantallas.paragraphs:
                for run in paragraph.runs:
                    run.font.name = 'Courier New'
                    run.font.size = Pt(8)
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            document.add_paragraph('')
            

          ##  document.add_heading('Estado', level=3)  ## Estado como titulo ver como ponerlo en la misma liena
            estado = "OK" if r_data["es_exitoso"] else "FAIL"
            estado_paragraph = document.add_paragraph()
            estado_paragraph.add_run("Estado: ")
            run = estado_paragraph.add_run(estado)
            if r_data["es_exitoso"]:
                run.font.color.rgb = RGBColor(0, 128, 0)
            else:
                run.font.color.rgb = RGBColor(255, 0, 0)

            run.bold = True

            
            document.add_heading('Observaciones', level=3)

            if i < len(resultados):
                document.add_page_break()
        
        document.save(self.output_word)  # Parametrizado
        print("✔ Reporte Word generado:", self.output_word)




########################
######   EXCEL  ########
#######################

    def generar_excel(self, resultados: list):
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

        headers = ["Nombre de caso", "Descripción", "Payload", "Código HTTP", "Expected code", "Estado", "Evidencia", "Observaciones"]
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
                estado,
                "",
                ""
            ]
            ws.append(row)

            current_row = ws.max_row
            for col in range(1, len(headers) + 1):
                cell = ws.cell(row=current_row, column=col)
                cell.border = border
                
                if col == 6:
                    if r["es_exitoso"]:
                        cell.fill = ok_fill
                    else:
                        cell.fill = error_fill
                
                if col in [4, 5]:
                    cell.alignment = Alignment(horizontal="center")
                elif col == 6:
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                elif col == 3:
                    cell.alignment = Alignment(wrap_text=True, vertical="top")

        column_widths = {
            'A': 15, 'B': 40, 'C': 60, 'D': 15, 'E': 20, 'F': 12, 'G': 20, 'H': 30,
        }
        
        for col, width in column_widths.items():
            ws.column_dimensions[col].width = width

        wb.save(self.output_excel)  # Parametrizado
        print("✔ Reporte Excel generado:", self.output_excel)

########################
######   HTML  ########
#######################

    def generar_html(self, resultados: list):
        grupos = defaultdict(list)
        for r in resultados:
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
        <p><b>Endpoint:</b> {self.url_endpoint}</p>

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

        with open(self.output_html, "w", encoding="utf-8") as f:
            f.write(html)

        print("✔ Reporte HTML generado:", self.output_html)