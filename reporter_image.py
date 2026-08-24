import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

# --- IMPORTACIONES PARA GENERACIÓN DE IMÁGENES ---
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print(
        "❌ Error: Se requiere la librería Pillow. Instálala con: pip install Pillow"
    )
    sys.exit(1)

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

try:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Inches, Pt, RGBColor
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
    payload: str
    response: str
    es_exitoso: bool
    expected_response: str = ""


# ==============================================================================
# FUNCIÓN AUXILIAR: GENERAR CAPTURA ESTILO POSTMAN (PNG)
# ==============================================================================
def generar_imagen_respuesta_postman(
    id_caso, response_str, http_status, output_dir="reportes"
):
    """Genera una imagen PNG con la estética del panel de respuesta de Postman."""
    os.makedirs(output_dir, exist_ok=True)

    # 1. Formatear JSON de respuesta
    try:
        if not response_str:
            raise ValueError("Respuesta vacía")
        if isinstance(response_str, str):
            clean_str = response_str.strip().replace("'", '"')
            json_obj = json.loads(clean_str)
        else:
            json_obj = response_str
        formatted_json = json.dumps(json_obj, indent=2, ensure_ascii=False)
    except Exception:
        formatted_json = str(response_str)

    # 2. Configuración de dimensiones y colores estilo Postman Dark Mode
    WIDTH = 900
    HEADER_HEIGHT = 80
    lines = formatted_json.split("\n")
    line_count = len(lines)
    JSON_PANEL_HEIGHT = max((line_count * 22) + 80, 180)
    HEIGHT = HEADER_HEIGHT + JSON_PANEL_HEIGHT

    BG_COLOR = (26, 26, 26)
    PANEL_BG = (18, 18, 18)
    TEXT_COLOR = (212, 212, 212)
    JSON_KEY_COLOR = (156, 220, 254)
    JSON_STRING_COLOR = (206, 145, 120)

    status_str = str(http_status)
    is_error = status_str.startswith(("4", "5"))
    STATUS_BG = (55, 15, 15) if is_error else (15, 55, 25)
    STATUS_TEXT = (255, 120, 120) if is_error else (120, 255, 150)

    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    try:
        font_main = ImageFont.truetype("DejaVuSans.ttf", 14)
        font_mono = ImageFont.truetype("DejaVuSansMono.ttf", 13)
        font_status = ImageFont.truetype("DejaVuSans-Bold.ttf", 14)
    except IOError:
        font_main = ImageFont.load_default()
        font_mono = ImageFont.load_default()
        font_status = ImageFont.load_default()

    # Pestaña Postman
    pestaña_txt = f"PUT {id_caso.split()[0]} - Response"
    draw.rounded_rectangle([20, 10, 280, 45], radius=6, fill=(40, 40, 40))
    draw.text((32, 18), pestaña_txt, font=font_main, fill=TEXT_COLOR)

    # Barra decorativa
    draw.rounded_rectangle(
        [20, 50, WIDTH - 20, 70], radius=4, fill=(32, 32, 32)
    )

    # Panel principal
    panel_coords = [15, HEADER_HEIGHT + 10, WIDTH - 15, HEIGHT - 15]
    draw.rounded_rectangle(
        panel_coords, radius=8, fill=PANEL_BG, outline=(45, 45, 45)
    )

    draw.text(
        (30, HEADER_HEIGHT + 25), "Body", font=font_main, fill=(100, 180, 255)
    )
    draw.text(
        (80, HEADER_HEIGHT + 25),
        "{} JSON",
        font=font_mono,
        fill=(140, 140, 140),
    )

    # Badge HTTP Status
    status_label = f"{status_str} "
    if status_str == "200":
        status_label += "OK"
    elif status_str == "400":
        status_label += "Bad Request"
    elif status_str == "401":
        status_label += "Unauthorized"
    elif status_str == "500":
        status_label += "Internal Server Error"
    else:
        status_label += "Response"

    w_status = draw.textlength(status_label, font=font_status) + 24
    draw.rounded_rectangle(
        [
            WIDTH - 30 - w_status,
            HEADER_HEIGHT + 18,
            WIDTH - 30,
            HEADER_HEIGHT + 48,
        ],
        radius=6,
        fill=STATUS_BG,
    )
    draw.text(
        (WIDTH - 20 - w_status, HEADER_HEIGHT + 24),
        status_label,
        font=font_status,
        fill=STATUS_TEXT,
    )

    # Renderizado del JSON con resaltado sintáctico
    current_y = HEADER_HEIGHT + 65
    x_offset = 35

    for line in lines:
        line_display = line[:110]
        if '"' in line_display:
            parts = line_display.split('"')
            curr_x = x_offset
            for idx, part in enumerate(parts):
                if idx % 2 == 1:  # Contenido entre comillas
                    text_part = f'"{part}"'
                    color = (
                        JSON_KEY_COLOR
                        if (idx + 1 < len(parts) and ":" in parts[idx + 1])
                        else JSON_STRING_COLOR
                    )
                else:
                    text_part = part
                    color = TEXT_COLOR

                draw.text(
                    (curr_x, current_y), text_part, font=font_mono, fill=color
                )
                curr_x += draw.textlength(text_part, font=font_mono)
        else:
            draw.text(
                (x_offset, current_y),
                line_display,
                font=font_mono,
                fill=TEXT_COLOR,
            )

        current_y += 22

    clean_id = re.sub(r"[^a-zA-Z0-9_]", "_", id_caso.split()[0])
    img_filename = f"postman_resp_{clean_id}.png"
    img_path = os.path.join(output_dir, img_filename)
    img.save(img_path)
    return img_path


class APITestReporter:

    def __init__(
        self,
        url_endpoint,
        output_dir="reportes",
        json_metadata_path="metadata_mail.json",
    ):
        self.url_endpoint = url_endpoint
        self.output_dir = output_dir

        self.metadata = {
            "commit": "Local Run - No Commit",
            "fecha_commit": datetime.now().strftime("%Y-%m-%d"),
            "autor": "QA Automation Team",
            "rama": "local",
            "mensaje": "Ejecución manual de pruebas locales",
        }

        if os.path.exists(json_metadata_path):
            try:
                with open(json_metadata_path, "r", encoding="utf-8") as f:
                    datos_json = json.load(f)
                    if isinstance(datos_json, dict):
                        self.metadata.update(datos_json)
            except Exception as e:
                print(
                    f"⚠ Advertencia: No se pudo leer {json_metadata_path}: {e}"
                )

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        script_basename = os.path.basename(sys.argv[0])
        script_name, _ = os.path.splitext(script_basename)
        if not script_name or script_name == "<stdin>":
            script_name = "reporte_api"

        self.titulo_reporte = script_name.replace("_", " ").title()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.output_html = os.path.join(
            self.output_dir, f"reporte_{script_name}_{timestamp}.html"
        )
        self.output_excel = os.path.join(
            self.output_dir, f"reporte_{script_name}_{timestamp}.xlsx"
        )
        self.output_word = os.path.join(
            self.output_dir, f"reporte_{script_name}_{timestamp}.docx"
        )

    def generar_html(self, resultados: list):
        """Método para generación de HTML (implementar según requerimientos)"""
        pass

    def generar_excel(self, resultados: list):
        """Método para generación de Excel (implementar según requerimientos)"""
        pass

    def generar_todos(self, resultados: list):
        resultados_dict = [
            r.__dict__ if isinstance(r, TestCaseResult) else r
            for r in resultados
        ]
        self.generar_html(resultados_dict)
        self.generar_excel(resultados_dict)
        self.generar_word(resultados_dict)

    def generar_word(self, resultados: list):
        try:
            from docx import Document
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            from docx.shared import Inches, Pt, RGBColor
        except ImportError:
            print("❌ Error: No está instalada la librería python-docx")
            return

        document = Document()

        style = document.styles["Normal"]
        style.font.name = "Courier New"
        style.font.size = Pt(11)

        title = document.add_heading(
            f"Reporte de Pruebas - {self.titulo_reporte}", 0
        )
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        document.add_heading("Información General", level=1)
        document.add_paragraph(
            f'Fecha Reporte: {datetime.now().strftime("%d/%m/%Y ")}'
        )
        document.add_paragraph(f"Ambiente: QA")
        document.add_paragraph(f"Endpoint: {self.url_endpoint}")
        document.add_paragraph(f'Commit: {self.metadata["commit"]}')
        document.add_paragraph(
            f'Fecha Commit: {self.metadata["fecha_commit"]}'
        )
        document.add_paragraph(f'Autor: {self.metadata["autor"]}')
        document.add_paragraph(f'Rama: {self.metadata["rama"]}')
        document.add_paragraph(f'Mensaje: {self.metadata["mensaje"]}')
        document.add_paragraph("")

        # 1. CASOS
        document.add_heading("1. Casos", level=1)
        tabla_casos = document.add_table(rows=1, cols=3)
        tabla_casos.style = "Light Grid Accent 1"
        tabla_casos.autofit = True

        tabla_casos.columns[0].width = Inches(0.5)
        tabla_casos.columns[1].width = Inches(2.5)
        tabla_casos.columns[2].width = Inches(5)

        encabezados = tabla_casos.rows[0].cells
        encabezados[0].text = "N°"
        encabezados[1].text = "ID del Caso"
        encabezados[2].text = "Objetivo"

        for cell in encabezados:
            for paragraph in cell.paragraphs:
                paragraph.runs[0].font.bold = True
                paragraph.runs[0].font.size = Pt(12)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

        for i, resultado in enumerate(resultados, 1):
            fila = tabla_casos.add_row()
            fila.cells[0].text = str(i)
            fila.cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            fila.cells[1].text = resultado["id"]
            fila.cells[2].text = resultado["descripcion"]

        document.add_paragraph("")

        # 2. EVIDENCIAS
        document.add_page_break()
        document.add_heading("2. Evidencias", level=1)

        for i, resultado in enumerate(resultados, 1):
            r_data = (
                resultado.__dict__
                if hasattr(resultado, "__dict__")
                else resultado
            )

            document.add_heading(f"{r_data['id']}", level=2)

            document.add_heading("Objetivo", level=3)
            document.add_paragraph(r_data["descripcion"])

            document.add_heading("Payload Enviado", level=3)
            try:
                payload_json = json.loads(r_data["payload"])
                p = document.add_paragraph()
                run = p.add_run(
                    json.dumps(payload_json, indent=2, ensure_ascii=False)
                )
                run.font.name = "Courier New"
                run.font.size = Pt(9)
            except Exception:
                document.add_paragraph(r_data["payload"])

            document.add_heading("Resultado Esperado", level=3)
            document.add_paragraph(
                f"Código esperado: {r_data['expected_code']}"
            )

            document.add_heading("Resultado Obtenido", level=3)
            document.add_paragraph(
                f"Código obtenido: {r_data['obtained_code']}"
            )

            # =============================================================
            # PARTE EN TEXTO Y EN IMAGEN DE LA RESPUESTA
            # =============================================================

            # --- OPCIÓN 1: RESPUESTA EN TEXTO ---
            document.add_heading("Respuesta de la API (Texto)", level=3)
            try:
                response_json = json.loads(r_data["response"])
                p = document.add_paragraph()
                run = p.add_run(
                    json.dumps(response_json, indent=2, ensure_ascii=False)
                )
                run.font.name = "Courier New"
                run.font.size = Pt(9)
            except Exception:
                p = document.add_paragraph()
                run = p.add_run(str(r_data["response"]))
                run.font.name = "Courier New"
                run.font.size = Pt(9)

            # --- OPCIÓN 2: RESPUESTA EN IMAGEN ---
            document.add_heading("Respuesta de la API (Captura Postman)", level=3)
            try:
                img_path = generar_imagen_respuesta_postman(
                    id_caso=r_data["id"],
                    response_str=r_data["response"],
                    http_status=r_data["http_status"],
                    output_dir=self.output_dir,
                )
                if os.path.exists(img_path):
                    document.add_picture(img_path, width=Inches(6.0))
            except Exception as e:
                document.add_paragraph(
                    f"⚠ No se pudo generar la captura: {e}"
                )

            # Documentación adicional
            document.add_heading("Documentación Tandem", level=3)
            document.add_heading("Audit Tandem", level=4)
            tabla_pantallas = document.add_table(rows=1, cols=1)
            tabla_pantallas.style = "Light Grid Accent 1"
            tabla_pantallas.columns[0].width = Inches(6)
            celda_pantallas = tabla_pantallas.cell(0, 0)
            celda_pantallas.text = (
                "Agregar aquí las pantallas/logs correspondientes si aplica"
            )

            estado = "OK" if r_data["es_exitoso"] else "FAIL"
            estado_paragraph = document.add_paragraph()
            estado_paragraph.add_run("Estado: ")
            run = estado_paragraph.add_run(estado)
            run.font.color.rgb = (
                RGBColor(0, 128, 0)
                if r_data["es_exitoso"]
                else RGBColor(255, 0, 0)
            )
            run.bold = True

            if i < len(resultados):
                document.add_page_break()

        document.save(self.output_word)
        print(
            "✔ Reporte Word generado con respuesta en Texto e Imagen:",
            self.output_word,
        )