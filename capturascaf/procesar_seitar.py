import pandas as pd
import sys
from datetime import datetime

def procesar_archivo(nombre_archivo):
    columnas = ['Fecha', 'Logical NET', 'FIID', 'sucursal', 'UBICACIÓN', 'TIPO', 'ESTADO', 
                'CPF^CLASS', 'T^CONV', 'FECHA^CONV', 'F^ULTACT', 'FECHA^ALTA', 'TOT^G', 'TOT^VENC', 'TOT^A']
    
    try:
        df = pd.read_csv(nombre_archivo, header=None, names=columnas)
    except Exception as e:
        print(f"Error al leer el archivo {nombre_archivo}: {e}")
        return None
    
    df['TOT^A'] = pd.to_numeric(df['TOT^A'], errors='coerce').fillna(0).astype(int)
    resultado = df.groupby('sucursal').size().reset_index(name='Cuenta')
    resultado['sucursal'] = resultado['sucursal'].astype(str)
    return resultado.sort_values('sucursal')

def generar_reporte(tabla1, tabla2, archivo_salida, nombre_archivo1, nombre_archivo2):
    todas_sucursales = sorted(set(tabla1['sucursal']).union(set(tabla2['sucursal'])))
    
    max_sucursal = max(len(s) for s in todas_sucursales + ['Sucursal'])
    
    valores_cuenta = list(pd.concat([tabla1['Cuenta'], tabla2['Cuenta']]))
    valores_cuenta.append('Cuenta de TOT^A')
    max_cuenta = max(len(str(c)) for c in valores_cuenta)
    
    max_sucursal = max(max_sucursal, 15)
    max_cuenta = max(max_cuenta, 15)
    ancho_seccion = max_sucursal + max_cuenta + 3
    
    # Crear diccionarios para búsqueda rápida
    dict1 = dict(zip(tabla1['sucursal'], tabla1['Cuenta']))
    dict2 = dict(zip(tabla2['sucursal'], tabla2['Cuenta']))
    
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        # Encabezado
        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        separador = '=' * ancho_seccion
        separador_doble = f"{separador}      |      {separador}"
        
        f.write(separador_doble + "\n")
        titulo1 = f"Resultados para archivo: {nombre_archivo1}".ljust(ancho_seccion)
        titulo2 = f"Resultados para archivo: {nombre_archivo2}".ljust(ancho_seccion)
        f.write(f"{titulo1}      |      {titulo2}\n")
        
        fecha_line = f"Generado el: {fecha_actual}".ljust(ancho_seccion)
        f.write(f"{fecha_line}      |      {fecha_line}\n")
        f.write(separador_doble + "\n")
        
        # Encabezados de tabla
        encabezado = f"{'Sucursal'.ljust(max_sucursal)}{'Cuenta de TOT^A'.rjust(max_cuenta)}"
        f.write(f"{encabezado.ljust(ancho_seccion)}      |      {encabezado.ljust(ancho_seccion)}\n")
        
        sep_columnas = f"{'='*max_sucursal}{'='*max_cuenta}"
        f.write(f"{sep_columnas.ljust(ancho_seccion)}      |      {sep_columnas.ljust(ancho_seccion)}\n")
        
        # Escribir datos alineados
        for sucursal in todas_sucursales:
            # Formatear línea para archivo 1
            cuenta1 = dict1.get(sucursal, '')
            linea1 = f"{sucursal.ljust(max_sucursal)}{str(cuenta1).rjust(max_cuenta) if cuenta1 != '' else '':>{max_cuenta}}"
            
            # Formatear línea para archivo 2
            cuenta2 = dict2.get(sucursal, '')
            linea2 = f"{sucursal.ljust(max_sucursal)}{str(cuenta2).rjust(max_cuenta) if cuenta2 != '' else '':>{max_cuenta}}"
            
            # Solo mostrar sucursal en el lado correspondiente
            if cuenta1 == '':
                linea1 = " " * (max_sucursal + max_cuenta)
            if cuenta2 == '':
                linea2 = " " * (max_sucursal + max_cuenta)
            
            f.write(f"{linea1.ljust(ancho_seccion)}      |      {linea2.ljust(ancho_seccion)}\n")

def main():
    if len(sys.argv) < 3:
        print("Uso: python script.py archivo1.txt archivo2.txt")
        return
    
    archivo1 = sys.argv[1]
    archivo2 = sys.argv[2]
    archivo_salida = "resultados_sucursales.txt"
    
    print(f"\nProcesando archivos... Los resultados se guardarán en {archivo_salida}")
    
    print(f"\nProcesando archivo: {archivo1}")
    tabla1 = procesar_archivo(archivo1)
    
    print(f"\nProcesando archivo: {archivo2}")
    tabla2 = procesar_archivo(archivo2)
    
    if tabla1 is not None and tabla2 is not None:
        generar_reporte(tabla1, tabla2, archivo_salida, archivo1, archivo2)
        print("\nProceso completado. Resultados guardados en:", archivo_salida)
    else:
        print("\nError al procesar los archivos. Verifica los mensajes anteriores.")

if __name__ == "__main__":
    main()