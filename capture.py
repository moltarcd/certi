import pyautogui
import time
import pyperclip
import os
from datetime import datetime
import pygetwindow as gw
import win32gui
import win32con

# === CONFIGURACIÓN ===
INPUT_FILE = r"C:\Proyectos\certificacion-nds-emision\capturascaf\valores.txt"          # Un valor por línea
TARGET_TITLE = "OutsideView - Untitled Workspace* - CAF"
OUTPUT_FOLDER = r"C:\Proyectos\certificacion-nds-emision\capturascaf\docaux\Antes"

# Coordenadas del campo donde se ingresa el dato en el terminal
INPUT_FIELD_X = 300   # ⚠️ AJUSTA: Usa el script de calibración abajo
INPUT_FIELD_Y = 200   # ⚠️ AJUSTA

# Zona de pantalla donde aparece el mensaje "RECORD RETRIEVED FROM"
# Formato: (left, top, width, height)
REGION_FOR_MESSAGE = (100, 100, 600, 200)  # Ajusta según tu pantalla

# Tiempos
MAX_WAIT_FOR_RECORD = 10  # Máximo tiempo esperando el mensaje
DELAY_BETWEEN_ACTIONS = 0.2
NUM_CAPTURES_PER_VALUE = 8

# === FUNCIONES AUXILIARES ===
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
        print(f"❌ No se encontró la ventana: {window_title}")
        return False

def wait_for_stability(seconds=0.5):
    time.sleep(seconds)

def click_at_input_field():
    pyautogui.click(INPUT_FIELD_X, INPUT_FIELD_Y)
    wait_for_stability(0.5)

def type_value(value):
    pyautogui.press('backspace', presses=15)  # Limpia campo (ajusta según longitud esperada)
    pyautogui.typewrite(str(value), interval=0.05)

def press_f2():
    pyautogui.press('f2')
    wait_for_stability(0.5)

def wait_for_record_retrieved():
    """
    Espera hasta que aparezca 'RECORD RETRIEVED FROM' en la región de pantalla.
    Usa OCR básico con pyautogui + pillow (screenshot + texto).
    """
    print("⏳ Esperando 'RECORD RETRIEVED FROM'...")
    start_time = time.time()

    while time.time() - start_time < MAX_WAIT_FOR_RECORD:
        try:
            screenshot = pyautogui.screenshot(region=REGION_FOR_MESSAGE)
            text = pytesseract.image_to_string(screenshot).upper()

            if "RECORD RETRIEVED FROM" in text:
                print("✅ Registro cargado.")
                return True
        except Exception as e:
            # Si no tienes pytesseract, ignora este bloque (ver alternativa abajo)
            pass

        time.sleep(0.5)
    
    print("⏰ Tiempo agotado esperando el mensaje.")
    return False