# Nombre del archivo de entrada y salida
archivo_entrada = 'cpf.txt'
archivo_salida = 'lineas_0.txt'

# Abrir archivos: el de entrada en modo lectura y el de salida en modo escritura
with open(archivo_entrada, 'r') as entrada, open(archivo_salida, 'w') as salida:
    # Leer cada línea del archivo de entrada
    for linea in entrada:
        # Verificar si la línea comienza con "   0:"
        if linea.startswith('   0:'):
            # Escribir la línea en el archivo de salida
            salida.write(linea)