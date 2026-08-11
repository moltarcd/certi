# performance/locustfile.py
import os
import sys
from locust import HttpUser, task, between

# 1. Resolvemos las rutas locales para poder importar tus archivos del framework de QA
# Nos movemos un nivel arriba de la carpeta 'performance' para acceder a la raíz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 2. Importamos las constantes directamente desde tus scripts funcionales
# (Hacemos referencia a la misma ruta de imports que usas en tu test)
from responses.debit_lost_stolen_card_test import BASE_PAYLOAD, TEST_CASES
from debit_lost_stolen_card import HEADERS_BASE  # Ajusta si HEADERS_BASE se importa de otro archivo local

class BankingPerformanceUser(HttpUser):
    # Simula un tiempo de espera aleatorio entre 1 y 3 segundos entre peticiones por usuario virtual
    wait_time = between(1, 3)
    
    def on_start(self):
        """Asigna las cabeceras exactas de tus pruebas funcionales."""
        # Clonamos el diccionario para evitar que hilos concurrentes de Locust muten el original
        self.headers = HEADERS_BASE.copy()

    @task(3)
    def test_debit_card_stolen_flow(self):
        """Simula flujo de Robo aplicando el modificador del test case de tu framework."""
        payload = BASE_PAYLOAD.copy()
        
        # Buscamos el caso C200-01 (o el correspondiente a Robo) para extraer su modificador dinámico
        case = next((tc for tc in TEST_CASES if tc.get("id") == "C200-01"), None)
        
        if case and "modificador" in case:
            # Aplicamos la función modificadora (ej: setear("reason", 2)) sobre el payload
            case["modificador"](payload)
            
        # Ejecutamos POST concatenando el endpoint relativo con el host de ejecución
        with self.client.post(
            "/v1/debit_lost_stolen_card_reporting/?bank_code=007", 
            json=payload, 
            headers=self.headers, 
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}: {response.text}")

    @task(1)
    def test_debit_card_lost_flow(self):
        """Simula el flujo de Extravío."""
        payload = BASE_PAYLOAD.copy()
        case = next((tc for tc in TEST_CASES if tc.get("id") == "C200-01"), None)
        
        if case and "modificador" in case:
            case["modificador"](payload)
            
        self.client.post(
            "/v1/debit_lost_stolen_card_reporting/?bank_code=007", 
            json=payload, 
            headers=self.headers
        )