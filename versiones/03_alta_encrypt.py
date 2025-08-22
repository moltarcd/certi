from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import base64

# Configuración de cifrado
clave_secreta = b"hI9Hlt&aDraTAcHa6efRiq8jA1lstoSt"  # 32 bytes
iv = b"abcdefgh12345678"
backend = default_backend()

def encrypt_text(text):
    """Función para encriptar"""
    padder = padding.PKCS7(128).padder()
    texto_plano_padded = padder.update(text.encode()) + padder.finalize()
    cipher = Cipher(algorithms.AES(clave_secreta), modes.CBC(iv), backend=backend)
    texto_cifrado = cipher.encryptor().update(texto_plano_padded) + cipher.encryptor().finalize()
    return base64.b64encode(texto_cifrado).decode()

# =========================
# CONFIGURACIÓN DE RUTAS
# =========================
input_filename  = r'C:\Proyectos\certificacion-nds-emision\docaux\01_creartd_completas.txt'
output_filename = r'C:\Proyectos\certificacion-nds-emision\docaux\01_encrypted_results.txt'

with open(input_filename, 'r') as infile, open(output_filename, 'w') as outfile:
    # Escribir encabezados
    outfile.write("Texto a encriptar\t\tHash\n")
    outfile.write("----------------\t\t----------------\n")
    
    for line in infile:
        line = line.strip()  # Eliminar espacios y saltos de línea
        if line:  # Solo procesar líneas no vacías
            try:
                encrypted = encrypt_text(line)
                # Escribir en el archivo de salida
                outfile.write(f"{line}\t\t{encrypted}\n")
                # También mostrar en consola (opcional)
                print(f"{line}\t\t{encrypted}")
            except Exception as e:
                print(f"Error procesando línea '{line}': {str(e)}")

print(f"\nProceso completado. Resultados guardados en {output_filename}")