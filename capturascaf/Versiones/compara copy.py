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

def mostrar_diff(texto1, texto2):
    lineas1 = texto1.splitlines()
    lineas2 = texto2.splitlines()
    diff = difflib.unified_diff(lineas1, lineas2, fromfile='Antes', tofile='Despues', lineterm='')
    return '\n'.join(diff)

def comparar_archivos(archivo1, archivo2):
    caps1 = cargar_capturas(archivo1)
    caps2 = cargar_capturas(archivo2)
    todos_los_numeros = sorted(set(caps1.keys()) | set(caps2.keys()))

    resultado = []
    for num in todos_los_numeros:
        texto1 = caps1.get(num)
        texto2 = caps2.get(num)

        if texto1 is None:
            resultado.append(f"CAPTURA {num}: FALTA en {os.path.basename(archivo1)}")
        elif texto2 is None:
            resultado.append(f"CAPTURA {num}: FALTA en {os.path.basename(archivo2)}")
        elif texto1 == texto2:
            resultado.append(f"CAPTURA {num}: OK (idéntica)")
        else:
            resultado.append(f"CAPTURA {num}: DIFERENTE")
            resultado.append(mostrar_diff(texto1, texto2))
    return resultado

# Carpetas reales en tu entorno
carpeta_antes = r"C:\Proyectos\capturascaf\CIclo4\Antes"
carpeta_despues = r"C:\Proyectos\capturascaf\CIclo4\Despues"

archivos = [a for a in os.listdir(carpeta_antes) if a.endswith('.txt')]

for archivo in archivos:
    path1 = os.path.join(carpeta_antes, archivo)
    path2 = os.path.join(carpeta_despues, archivo)

    if os.path.exists(path2):
        print(f"\n📄 Comparando archivo: {archivo}")
        resultados = comparar_archivos(path1, path2)
        for r in resultados:
            print(r)
    else:
        print(f"\n⚠️ {archivo} está en 'Antes' pero no en 'Despues'")
