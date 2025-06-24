import os
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn

# =========================
# CONFIGURACIÓN DE RUTAS
# =========================

# Carpetas que contienen archivos TXT
carpeta_antes = r'C:\Proyectos\capturascaf\docaux\Antes'
carpeta_despues = r'C:\Proyectos\capturascaf\docaux\Despues'

# Carpeta de salida del documento Word
carpeta_salida = r'C:\Proyectos\capturascaf\docaux'
nombre_archivo_salida = 'reporte_pruebas.docx'
ruta_salida = os.path.join(carpeta_salida, nombre_archivo_salida)

# =========================
# FUNCIONES
# =========================

def insertar_tabla_con_txt(doc, ruta_txt):
    """Inserta tabla con formato Consolas 8pt desde archivo txt"""
    with open(ruta_txt, encoding='utf-8') as f:
        contenido = f.read()

    tabla = doc.add_table(rows=1, cols=1)
    tabla.style = 'Table Grid'
    celda = tabla.cell(0, 0)
    celda.text = ""

    for linea in contenido.splitlines():
        p = celda.add_paragraph()
        run = p.add_run(linea)
        run.font.name = 'Consolas'
        run.font.size = Pt(8)
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Consolas')

def procesar_carpeta(doc, carpeta, titulo_seccion):
    """Procesa todos los .txt de una carpeta, insertando título y tabla"""
    doc.add_heading(titulo_seccion, level=2)
    doc.add_heading("Ejecucion de Caso:", level=3)

    archivos_txt = [f for f in os.listdir(carpeta) if f.lower().endswith('.txt')]
    archivos_txt.sort()

    for archivo in archivos_txt:
        ruta_completa = os.path.join(carpeta, archivo)
        doc.add_heading(archivo, level=4)  # nombre del archivo como subtítulo
        insertar_tabla_con_txt(doc, ruta_completa)

# =========================
# CREACIÓN DEL DOCUMENTO
# =========================

# Crear carpeta de salida si no existe
os.makedirs(carpeta_salida, exist_ok=True)

doc = Document()

doc.add_heading("Ejecución de Pruebas", level=1)
doc.add_heading("Objetivo", level=2)
doc.add_heading("Casos", level=2)

procesar_carpeta(doc, carpeta_antes, "Evidencias Antes")
procesar_carpeta(doc, carpeta_despues, "Evidencias Después")

# Guardar
doc.save(ruta_salida)
print(f"Documento guardado en: {ruta_salida}")
