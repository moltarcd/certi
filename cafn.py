###########Instalacion###########
#sE DEBE TENER INSTALADO EN LA PC PYHTON Y QUE LAS VARIABLES APUNTEN CORRECTAMENTE
####Crear entorno virtual #######
#   python -m venv venv
#   venv\Scripts\activate
##################################
#######Instalar Dependencias######
#pip install pyautogui pyperclip pygetwindow pywin32
#ver
##################################
import pyautogui
import time
import pyperclip
from datetime import datetime
import pygetwindow as gw
import win32gui
import win32con
import os

def clean_text(text):
    lines = text.split('\n')
    cleaned_lines = []
    prev_line_was_empty = False
    
    for line in lines:
        stripped_line = line.rstrip()
        if not stripped_line:
            if not prev_line_was_empty:
                cleaned_lines.append(stripped_line)
                prev_line_was_empty = True
        else:
            cleaned_lines.append(stripped_line)
            prev_line_was_empty = False
    
    return '\n'.join(cleaned_lines)

def bring_window_to_foreground(window_title):
    try:
        win = gw.getWindowsWithTitle(window_title)[0]
        if not win.isMinimized:
            win32gui.ShowWindow(win._hWnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(win._hWnd)
        return True
    except IndexError:
        print(f"❌ No se encontró la ventana con título: {window_title}")
        return False

def capture_outsideview_data(num_captures=8, delay=1, output_folder="capturas"):
    target_title = "OutsideView - Untitled Workspace* - CAF"

    # Crear la carpeta si no existe
    os.makedirs(output_folder, exist_ok=True)

    if not bring_window_to_foreground(target_title):
        return

    captured_data = []
    print(f"Preparándose para capturar {num_captures} veces...")
    time.sleep(2)
    
    for i in range(num_captures):
        # Asegurarse de que la ventana siga siendo la activa
        bring_window_to_foreground(target_title)
        time.sleep(delay)

        pyautogui.hotkey('ctrl', 'a')
        time.sleep(delay)
        
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(delay)

        pyautogui.press('f9')
        time.sleep(delay)

        try:
            clipboard_data = pyperclip.paste()
            cleaned_data = clean_text(clipboard_data)
            captured_data.append(cleaned_data)
            print(f"✅ Captura {i+1} completada - Caracteres capturados: {len(clipboard_data)}")
        except Exception as e:
            print(f"⚠️ Error al acceder al portapapeles en captura {i+1}: {e}")
        
        time.sleep(delay)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"captura_{timestamp}.txt"
    full_path = os.path.join(output_folder, filename)
    
    with open(full_path, 'w', encoding='utf-8') as f:
        for i, data in enumerate(captured_data, 1):
            f.write(f"=== CAPTURA {i} ===\n")
            f.write(data)
            f.write("\n\n")
    
    print(f"\n📄 ¡Proceso completado! Datos guardados en: {full_path}")

if __name__ == "__main__":
    NUM_CAPTURES = 8
    DELAY_BETWEEN_ACTIONS = 0.2
    OUTPUT_FOLDER = r"C:\Proyectos\certificacion-nds-emision\capturascaf\Antes"  # Puedes cambiar esto por la ruta que prefieras
    
    capture_outsideview_data(
        num_captures=NUM_CAPTURES, 
        delay=DELAY_BETWEEN_ACTIONS,
        output_folder=OUTPUT_FOLDER
    )