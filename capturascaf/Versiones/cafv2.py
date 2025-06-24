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
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('outsideview_capture.log')
        ]
    )

def capture_outsideview_data(num_captures=2, initial_delay=3, action_delay=0.5, window_title=None):
    """
    Automatiza la captura de datos de OutsideView.
    
    Args:
        num_captures (int): Número de capturas a realizar
        initial_delay (float): Tiempo de espera inicial (en segundos)
        action_delay (float): Tiempo entre acciones (en segundos)
        window_title (str): Título de la ventana a enfocar (opcional)
    """
    setup_logging()
    captured_data = []
    
    logging.info(f"Iniciando captura automática para {num_captures} iteraciones")
    logging.info(f"Tiempo de espera inicial: {initial_delay} segundos")
    
    try:
        # Espera inicial
        time.sleep(initial_delay)
        
        # Enfocar ventana si se especificó el título
        if window_title:
            try:
                win = pyautogui.getWindowsWithTitle(window_title)[0]
                win.activate()
                time.sleep(1)  # Esperar para que la ventana se active
                logging.info(f"Ventana '{window_title}' enfocada")
            except Exception as e:
                logging.warning(f"No se pudo enfocar la ventana: {e}")
        
        for i in range(num_captures):
            logging.info(f"Iniciando captura {i+1}/{num_captures}")
            
            # Simular F9
            pyautogui.press('f9')
            time.sleep(action_delay)
            
            # Seleccionar todo (Ctrl+A) y copiar (Ctrl+C)
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(action_delay)
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(action_delay)
            
            # Obtener datos del portapapeles
            try:
                clipboard_data = pyperclip.paste()
                if clipboard_data.strip():  # Verificar que no esté vacío
                    captured_data.append(clipboard_data)
                    logging.info(f"Captura {i+1} completada - Tamaño: {len(clipboard_data)} caracteres")
                else:
                    logging.warning(f"Captura {i+1} vacía - Se omitió")
            except Exception as e:
                logging.error(f"Error al acceder al portapapeles en captura {i+1}: {e}")
            
            # Esperar antes de la próxima captura
            time.sleep(action_delay)
        
        # Guardar en archivo TXT si hay datos
        if captured_data:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"outsideview_capturas_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                for i, data in enumerate(captured_data, 1):
                    f.write(f"=== CAPTURA {i} === (Hora: {datetime.now().strftime('%H:%M:%S')})\n")
                    f.write(data)
                    f.write("\n\n")
            
            logging.info(f"\n¡Proceso completado! Datos guardados en: {filename}")
        else:
            logging.warning("No se capturaron datos válidos. No se creó archivo de salida.")
            
    except KeyboardInterrupt:
        logging.info("Proceso interrumpido por el usuario")
    except Exception as e:
        logging.error(f"Error inesperado: {e}", exc_info=True)

if __name__ == "__main__":
    # Configuración (ajustar según necesidades)
    CONFIG = {
        'num_captures': 2,          # Número de capturas
        'initial_delay': 5,         # Tiempo para prepararse (segundos)
        'action_delay': 0.5,       # Tiempo entre acciones (segundos)
        'window_title': "OutsideView - Untitled Workspace* - CAF (2)"  # Título de la ventana (None para no enfocar) ### OutsideView - Untitled Workspace* - CAF (2)
    }
    
    # Ejecutar la automatización
    capture_outsideview_data(**CONFIG)