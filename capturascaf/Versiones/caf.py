###########Instalacion###########
#sE DEBE TENER INSTALADO EN LA PC PYHTON Y QUE LAS VARIABLES APUNTEN CORRECTAMENTE
####Crear entorno virtual #######
#   python -m venv venv
#   venv\Scripts\activate
##################################
#######Instalar Dependencias######
#pip install pyautogui pyperclip pygetwindow pywin32
##################################
import pyautogui
import time
import pyperclip
from datetime import datetime

def clean_text(text):
    lines = text.split('\n')
    cleaned_lines = []
    prev_line_was_empty = False
    
    for line in lines:
        stripped_line = line.rstrip()  # Elimina espacios al final
        if not stripped_line:
            if not prev_line_was_empty:
                cleaned_lines.append(stripped_line)
                prev_line_was_empty = True
        else:
            cleaned_lines.append(stripped_line)
            prev_line_was_empty = False
    
    return '\n'.join(cleaned_lines)

def capture_outsideview_data(num_captures=8, delay=1):
    """
        num_captures (int): Número de veces que se realizará la captura
        delay (float): Tiempo de espera entre acciones (en segundos)
    """
    captured_data = []
    
    # Espera 3 segundos para dar tiempo a posicionarse en la aplicación
    print(f"Preparándose para capturar {num_captures} veces...")
    time.sleep(2)
    
    for i in range(num_captures):
       
        # Seleccionar todo (Ctrl+A)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(delay)
        
        # Copiar (Ctrl+C)
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(delay)

        # Simular F9
        pyautogui.press('f9')
        time.sleep(delay)

        # Obtener datos del portapapeles
        try:
            clipboard_data = pyperclip.paste()
            cleaned_data = clean_text(clipboard_data)
            captured_data.append(cleaned_data)
            print(f"Captura {i+1} completada - Caracteres capturados: {len(clipboard_data)}")
        except Exception as e:
            print(f"Error al acceder al portapapeles en captura {i+1}: {e}")
        
        # Esperar antes de la próxima captura
        time.sleep(delay)
    
    # Guardar en archivo TXT
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"captura_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        for i, data in enumerate(captured_data, 1):
            f.write(f"=== CAPTURA {i} ===\n")
            f.write(data)
            f.write("\n\n")  # Dos saltos de línea entre capturas
    
    print(f"\n¡Proceso completado! Datos guardados en: {filename}")

if __name__ == "__main__":
    # Configuración 
    NUM_CAPTURES = 8  # Número de veces que se repetirá la captura
    DELAY_BETWEEN_ACTIONS = 0.2  # Tiempo entre acciones en segundos
    
    # Ejecutar la automatización
    capture_outsideview_data(num_captures=NUM_CAPTURES, delay=DELAY_BETWEEN_ACTIONS)