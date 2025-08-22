import random
import os

# =========================
# CONFIGURACIÓN DE PARÁMETROS
# =========================
cantidad_a_generar = 15
ruta_salida = r"C:\Proyectos\certificacion-nds-emision\docaux\01_creartaltas.txt"  # imput para creartd.py

def generar_numeros(fijos='43453105', cantidad=50):
    numeros_generados = set()

    while len(numeros_generados) < cantidad:
        sufijo = random.randint(10_000_00, 99_999_99)  # evita ceros iniciales y mantiene 7 dígitos
        numero_completo = fijos + str(sufijo)
        numeros_generados.add(numero_completo)

    return list(numeros_generados)

# Generación y guardado
numeros = generar_numeros(cantidad=cantidad_a_generar)

# Guardar en archivo .txt
with open(ruta_salida, 'w') as f:
    for numero in numeros:
        f.write(numero + '\n')

print(f'Se generaron {len(numeros)} números y se guardaron en:\n{ruta_salida}')
