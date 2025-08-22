import os
import re
import difflib

def cargar_capturas(path_archivo):
    with open(path_archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()

    capturas = re.split(r'=== CAPTURA (\d+) ===', contenido)
    capturas_dict = {}
    for i in range(1, len(capturas), 2):
        num = int(capturas[i])
        texto = capturas[i+1].strip()
        capturas_dict[num] = texto
    return capturas_dict

def mostrar_diff_simple(texto1, texto2):
    lineas1 = texto1.splitlines()
    lineas2 = texto2.splitlines()
    diff = difflib.unified_diff(
        lineas1,
        lineas2,
        fromfile='Antes',
        tofile='Despues',
        lineterm='',
        n=0
    )
    resultado = []
    for linea in diff:
        if linea.startswith(('--- ', '+++ ', '-', '+')) and not linea.startswith(('---\t', '+++\t')):
            if not (linea.startswith('---') and 'Antes' not in linea):
                if not (linea.startswith('+++') and 'Despues' not in linea):
                    resultado.append(linea)
    return '\n'.join(resultado)

def comparar_archivos(archivo1, archivo2):
    caps1 = cargar_capturas(archivo1)
    caps2 = cargar_capturas(archivo2)
    todos_los_numeros = sorted(set(caps1.keys()) | set(caps2.keys()))

    resultado = []
    for num in todos_los_numeros:
        texto1 = caps1.get(num)
        texto2 = caps2.get(num)

        if texto1 is None:
            resultado.append(f"**CAPTURA {num}**: FALTA en {os.path.basename(archivo1)}")
        elif texto2 is None:
            resultado.append(f"**CAPTURA {num}**: FALTA en {os.path.basename(archivo2)}")
        elif texto1 == texto2:
            continue
        else:
            resultado.append(f"**CAPTURA {num}**: DIFERENTE")
            resultado.append(mostrar_diff_simple(texto1, texto2))
    return resultado

# =========================
# CONFIGURACIÓN DE RUTAS
# =========================
carpeta_antes = r"C:\Proyectos\certificacion-nds-emision\capturascaf\docaux\Antes"
carpeta_despues = r"C:\Proyectos\certificacion-nds-emision\capturascaf\docaux\Despues"
archivo_salida = r"C:\Proyectos\certificacion-nds-emision\capturascaf\docaux\comparacion_resultado.txt"

archivos = [a for a in os.listdir(carpeta_antes) if a.endswith('.txt')]

lineas_salida = []

for archivo in archivos:
    path1 = os.path.join(carpeta_antes, archivo)
    path2 = os.path.join(carpeta_despues, archivo)

    if os.path.exists(path2):
        resultados = comparar_archivos(path1, path2)
        if resultados:
            lineas_salida.append(f"{'Comparando archivo: ' + archivo:^80}")
            lineas_salida.extend(resultados)
            lineas_salida.append("")  # Espacio en blanco 1
            lineas_salida.append("")  # Espacio en blanco 2
            lineas_salida.append("")  # Espacio en blanco 3
    else:
        lineas_salida.append(f"{'⚠️ ' + archivo + ' está en Antes pero no en Despues':^80}")
        lineas_salida.append("")
        lineas_salida.append("")
        lineas_salida.append("")

# Guardar resultado
with open(archivo_salida, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lineas_salida))

print(f"✅ Comparación finalizada. Resultado guardado en:\n{archivo_salida}")
