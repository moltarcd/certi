def buscar_en_columna():
    # Configuración predefinida - MODIFICA ESTOS VALORES SEGÚN TUS NECESIDADES
    archivo_entrada = "C:\\Proyectos\\certificacion-nds-emision\\capturascaf\\BF250512C3.TXT"  # Archivo de entrada
    archivo_salida = "C:\\Proyectos\\certificacion-nds-emision\\capturascaf\\BFresultmf.TXT"    # Archivo de salida
    valor_buscar = "t"  # Valor a buscar en la columna 65 (1 carácter)
    columna_busqueda = 64  # Columna donde buscar (basado en 1)

    try:
        with open(archivo_entrada, 'r', encoding='utf-8') as entrada, \
             open(archivo_salida, 'w', encoding='utf-8') as salida:
            
            contador_coincidencias = 0
            
            for linea in entrada:
                # Eliminar espacios en blanco al final (como newline)
                linea_limpia = linea.rstrip('\n')
                
                # Verificar si la línea tiene al menos 65 caracteres
                if len(linea_limpia) >= columna_busqueda:
                    # El índice es columna_busqueda - 1 porque Python usa base 0
                    if linea_limpia[columna_busqueda - 1].lower() == valor_buscar.lower():
                        salida.write(linea)
                        contador_coincidencias += 1
            
            print(f"Búsqueda completada. Se encontraron {contador_coincidencias} coincidencias.")
    
    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo de entrada '{archivo_entrada}'")
    except Exception as e:
        print(f"Ocurrió un error: {str(e)}")

if __name__ == "__main__":
    buscar_en_columna()