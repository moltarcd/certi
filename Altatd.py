import random
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import base64

# =========================
# CONFIGURACIÓN DE RUTAS Y PARÁMETROS
# =========================
directorio = r"C:\Proyectos\certificacion-nds-emision\docaux"
os.makedirs(directorio, exist_ok=True)

ruta_intermedia = os.path.join(directorio, "01_creartaltas.txt")           # Números sin DV
archivo_resultados = os.path.join(directorio, "01_creartdlogs.txt")        # Logs con DV
archivo_pan_completo = os.path.join(directorio, "01_creartd_completas.txt") # PANs completos (sin encriptar)
archivo_encriptado = os.path.join(directorio, "01_encrypted_results.txt")  # Resultado final encriptado

cantidad_a_generar = 15

# Configuración de cifrado AES
clave_secreta = b"hI9Hlt&aDraTAcHa6efRiq8jA1lstoSt"  # 32 bytes (AES-256)
iv = b"abcdefgh12345678"  # 16 bytes (bloque AES)
backend = default_backend()


# =========================
# PASO 1: GENERAR NÚMEROS CON PREFIJO FIJO
# =========================
def generar_numeros(prefijo: str, cantidad: int) -> list:
    numeros_generados = set()
    while len(numeros_generados) < cantidad:
        sufijo = random.randint(10_000_00, 99_999_99)  # 7 dígitos sin ceros iniciales
        numero_completo = prefijo + str(sufijo)
        numeros_generados.add(numero_completo)
    return list(numeros_generados)


# =========================
# PASO 2: CÁLCULO DEL DÍGITO VERIFICADOR (LUHN desde la izquierda)
# =========================
def calcular_dv_luhn_izquierda(pan_sin_dv: str) -> int:
    digitos = [int(d) for d in pan_sin_dv]
    suma = 0
    for i, d in enumerate(digitos):
        if i % 2 == 0:  # Posiciones impares desde la izquierda (0-indexed)
            doble = d * 2
            if doble > 9:
                doble -= 9
            suma += doble
        else:
            suma += d
    dv = (10 - (suma % 10)) % 10
    return dv


def procesar_pans_con_dv(lista_pans: list) -> list:
    try:
        with open(archivo_resultados, 'w') as res_out, \
             open(archivo_pan_completo, 'w') as pan_out:
            encabezado = "Resultados de dígitos verificadores:"
            separador = "-" * 60
            print(encabezado)
            print(separador)
            res_out.write(f"{encabezado}\n{separador}\n")

            pans_completos = []
            for pan in lista_pans:
                dv = calcular_dv_luhn_izquierda(pan)
                pan_completo = f"{pan}{dv}"
                linea_resultado = f"PAN: {pan} \tDV: {dv} \t| PAN completo: {pan_completo}"
                print(linea_resultado)
                res_out.write(f"{linea_resultado}\n")
                pan_out.write(f"{pan_completo}\n")
                pans_completos.append(pan_completo)

            res_out.write(f"{separador}\n")
            print(separador)
        return pans_completos
    except Exception as e:
        print(f"Error al procesar dígitos verificadores: {str(e)}")
        return []


# =========================
# PASO 3: ENCRIPTACIÓN REAL CON AES-CBC + PKCS7 + Base64
# =========================
def encrypt_text(text: str) -> str:
    """Encripta un texto usando AES-CBC con PKCS7 padding"""
    # Añadir padding PKCS7
    padder = padding.PKCS7(128).padder()
    texto_plano_padded = padder.update(text.encode('utf-8')) + padder.finalize()

    # Crear cifrado AES-CBC
    cipher = Cipher(algorithms.AES(clave_secreta), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    texto_cifrado = encryptor.update(texto_plano_padded) + encryptor.finalize()

    # Codificar en Base64
    return base64.b64encode(texto_cifrado).decode('utf-8')


def encriptar_pans(pans_completos: list):
    try:
        with open(archivo_encriptado, 'w') as outfile:
            # Escribir encabezado
            outfile.write("Texto a encriptar\t\tHash\n")
            outfile.write("----------------\t\t----------------\n")

            for pan in pans_completos:
                pan = pan.strip()
                if pan:
                    try:
                        encrypted = encrypt_text(pan)
                        outfile.write(f"{pan}\t\t{encrypted}\n")
                        print(f"{pan}\t\t{encrypted}")
                    except Exception as e:
                        print(f"Error procesando línea '{pan}': {str(e)}")
        print(f"\nProceso completado. Resultados encriptados guardados en: {archivo_encriptado}")
    except Exception as e:
        print(f"Error al escribir archivo encriptado: {str(e)}")


# =========================
# FUNCIÓN PRINCIPAL
# =========================
def main():
    print("=== GENERACIÓN Y ENCRIPTACIÓN DE PANS ===")
    prefijo = input("Ingrese el prefijo para generar los PANs (ej. 43453105): ").strip()

    if not prefijo.isdigit():
        print("Error: El prefijo debe ser numérico.")
        return

    if len(prefijo) < 6 or len(prefijo) > 12:
        print("Advertencia: El prefijo debería tener entre 6 y 12 dígitos. Continuando igual...")

    # PASO 1: Generar números
    print(f"\nGenerando {cantidad_a_generar} números con prefijo '{prefijo}'...")
    numeros_generados = generar_numeros(prefijo, cantidad_a_generar)

    # Guardar en archivo intermedio (entrada para creartd)
    with open(ruta_intermedia, 'w') as f:
        for numero in numeros_generados:
            f.write(numero + '\n')
    print(f"Números generados guardados en: {ruta_intermedia}")

    # PASO 2: Calcular DV y generar PANs completos
    print("\nCalculando dígitos verificadores (Luhn izquierda)...")
    pans_completos = procesar_pans_con_dv(numeros_generados)

    if not pans_completos:
        print("No se generaron PANs completos. Finalizando.")
        return

    # PASO 3: Encriptar PANs completos con AES real
    print("\nEncriptando PANs completos con AES-CBC + Base64...")
    encriptar_pans(pans_completos)


# =========================
# EJECUCIÓN
# =========================
if __name__ == "__main__":
    main()