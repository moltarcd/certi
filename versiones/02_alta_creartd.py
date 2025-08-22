# =========================
# CONFIGURACIÓN DE RUTAS
# =========================
nombre_archivo =       r"C:\Proyectos\certificacion-nds-emision\docaux\01_creartaltas.txt"  # debe estar creado
archivo_resultados =   r"C:\Proyectos\certificacion-nds-emision\docaux\01_creartdlogs.txt"
archivo_pan_completo = r"C:\Proyectos\certificacion-nds-emision\docaux\01_creartd_completas.txt"

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

def procesar_archivo_pan(nombre_archivo: str):
    try:
        # Archivos de salida

        
        with open(nombre_archivo, 'r') as archivo, \
             open(archivo_resultados, 'w') as res_out, \
             open(archivo_pan_completo, 'w') as pan_out:
            
            lineas = archivo.readlines()
            
            # Escribir encabezados
            encabezado = "Resultados de dígitos verificadores:"
            separador = "-" * 60
            print(encabezado)
            print(separador)
            res_out.write(f"{encabezado}\n{separador}\n")
            
            for linea in lineas:
                pan = linea.strip()
                if pan:
                    try:
                        dv = calcular_dv_luhn_izquierda(pan)
                        # Resultado completo (pantalla y archivo 1)
                        linea_resultado = f"PAN: {pan} \tDV: {dv} \t| PAN completo: {pan}{dv}"
                        print(linea_resultado)
                        res_out.write(f"{linea_resultado}\n")
                        
                        # Solo PAN completo (archivo 2)
                        pan_out.write(f"{pan}{dv}\n")
                        
                    except ValueError:
                        error_msg = f"Error: '{pan}' no es un número válido"
                        print(error_msg)
                        res_out.write(f"{error_msg}\n")
            
            print(separador)
            res_out.write(f"{separador}\n")
            
        print(f"\nResultados completos guardados en: {archivo_resultados}")
        print(f"Lista de PAN completos guardados en: {archivo_pan_completo}")
    
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{nombre_archivo}'")
    except Exception as e:
        print(f"Ocurrió un error: {str(e)}")


procesar_archivo_pan(nombre_archivo)