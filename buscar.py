def buscar_en_columnas(archivo_entrada, archivo_salida, valor_buscar):
    """
    Busca un valor en las columnas 62-63 de cada línea y guarda las coincidencias.
    
    Args:
        archivo_entrada (str): Ruta del archivo de texto de entrada.
        archivo_salida (str): Ruta del archivo de texto de salida.
        valor_buscar (str): Valor a buscar (1-2 caracteres) en columnas 62-63.
    """
    # Validar que el valor a buscar tenga 1 o 2 caracteres
    if len(valor_buscar) == 0 or len(valor_buscar) > 2:
        print("Error: El valor a buscar debe tener 1 o 2 caracteres.")
        return
    
    try:
        with open(archivo_entrada, 'r') as entrada, open(archivo_salida, 'w') as salida:
            lineas_encontradas = 0
            
            for linea in entrada:
                # Eliminar espacios en blanco al final y saltos de línea
                linea_limpia = linea.rstrip('\n')
                
                # Verificar si la línea tiene al menos 63 caracteres
                if len(linea_limpia) >= 63:
                    # Extraer los caracteres en las posiciones 61 y 62 (índices basados en 0)
                    columna_62_63 = linea_limpia[61:63]
                    
                    # Comparar con el valor buscado
                    if valor_buscar == columna_62_63[:len(valor_buscar)]:
                        salida.write(linea)
                        lineas_encontradas += 1
            
            print(f"Búsqueda completada. Se encontraron {lineas_encontradas} coincidencias.")
            print(f"Resultados guardados en: {archivo_salida}")
    
    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo {archivo_entrada}")
    except Exception as e:
        print(f"Ocurrió un error: {str(e)}")


if __name__ == "__main__":
    # Configuración  
    archivo_entrada = "C:\Proyectos\certificacion-nds-emision\docaux\BF250512C3.TXT"      # Archivo de entrada predefinido
    archivo_salida = "C:\Proyectos\certificacion-nds-emision\docaux\BFresultB24.TXT"  # Archivo de salida predefinido
    valor_buscar = "EG"                 # Valor a buscar predefinido
    
    # Mostrar configuración que se está usando
    print("\nConfiguración actual:")
    print(f"Archivo de entrada: {archivo_entrada}")
    print(f"Archivo de salida: {archivo_salida}")
    print(f"Buscando: '{valor_buscar}' en columnas 62-63\n")
    
    # Ejecutar la búsqueda
    buscar_en_columnas(archivo_entrada, archivo_salida, valor_buscar)
    
   