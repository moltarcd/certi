# Generador de Reportes

## Descripción

Este proyecto está desarrollado en Python y tiene como objetivo:

- Pruebas de Apis.
- Generar Reportes Automatizados sobre el resultado de las pruebas.
- Integracion de pruebas de stress y reutilizacion de reportes


---

## Requisitos

- Python 3.10 o superior
- pip

---

## Instalación

### 1. Crear entorno virtual

```powershell
python -m venv env
```

### 2. Activar entorno virtual

```powershell
.\env\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```powershell
pip install -r requirements.txt
```

---

## Ejecución

Para ejecutar el proyecto:

```powershell
python main.py o bien ejecutando directamente el 
```

---

## Estructura del Proyecto

```text
├── env/
├── reports/
├── response/
├── swagger-screenshots/
├── old_reports/
├── utils/
├── requirements.txt
├── main.py
└── README.md
```

### Directorios

- **reports/**: contiene los reportes generados en la ejecución actual.
- **old_reports/**: almacena reportes históricos de ejecuciones anteriores.
- **env/**: entorno virtual del proyecto.
- **response/**:  test de cada api
- **util**: Herramientas de soporte (borrar reportes viejos, crear tarjetas nuevas, etc) 


---

## Control de Versiones

Para registrar cambios y publicar actualizaciones en el repositorio:

```bash
git add .
git commit -m "version 1.1 - Actualizacion readme"
git push origin master

```

---

## Versionado

### v1.0

- Actualización de fuentes utilizadas en la generación de reportes.
- Mejoras de mantenimiento y organización de archivos históricos.



---

## Funcionalidad 

## 🏗️ Arquitectura General del Framework

Todos los scripts de automatización comparten un motor de ejecución desacoplado donde la lógica de orquestación, la plantilla base de datos y los escenarios de prueba residen de forma independiente.

```text
               +----------------------------------+
               |  BASE_PAYLOAD (Plantilla Válida) |
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               |     TEST_CASES (Mutaciones)      |
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               |       copy.deepcopy(Payload)     |
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               |      Invocación HTTP (requests)  |
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               |    obtener_codigo_error(resp)    |
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               |   Evaluación: Expected vs Actual  |
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               | APITestReporter (HTML / DOCX / XLS)
               +----------------------------------+
```

## Principales Beneficios
- Aislamiento por deepcopy: Cada prueba utiliza copy.deepcopy(BASE_PAYLOAD) antes de aplicar mutaciones, garantizando que un test case jamás contamine la estructura base del siguiente.
- Desacoplamiento Total: Incorporar nuevos escenarios no requiere alterar la lógica de comunicación HTTP ni la generación de reportes.
- Normalización de Respuestas: Homogeneiza respuestas dispares (HTTP 200, 201, 4xx, 5xx o estructuras JSON variantes) en un código funcional uniforme.


## 📍 Endpoints, Contexto y Headers

### Endpoints Bajo Prueba

| Script | Servicio | Endpoint (QA) |
| :--- | :--- | :--- |
| `account_linking_tests.py` | Vinculación de Cuentas | `https://api-qa.newpay.com.ar/v1/account-linking/bind` |
| `cbu_management.py` | Administración de CBU | `https://api-qa.newpay.com.ar/v2/cbu_management/accounts/account/cbu` |
| `debit_card_management.py` | Alta de TD| `https://api-qa.newpay.com.ar/v1/debit_card_management/cards` |  
| `debit_card_data.py`|  Consulta de TD | 
| `debit_card_rules_management.py`|  Prendido y Apagado | 
| `debit_card_security_code.py`|  Cvv2 | 
| `debit_lost_stolen_card.py`|  Denuncia de TD | 


## 📁 Estructura del Proyecto y Módulos

Los archivos mantienen un orden estandarizado en tres bloques (`Imports`, `Configuración` y `Ejecución`).

### Organización de Archivos

```text
.
├── account_linking_tests.py      # Runner del servicio Account Linking
├── cbu_management.py             # Runner del servicio CBU Management
├── debit_card_management.py      # Runner del servicio Debit Card
├── reporter.py                   # Clases APITestReporter y TestCaseResult
└── responses/
    ├── account_linking_test.py   # BASE_PAYLOAD y TEST_CASES
    ├── cbu_management_test.py    # BASE_PAYLOAD y TEST_CASES
    └── debit_card_management_test.py

```

### Módulos Estándar e Integraciones
- requests: Encargado de realizar las peticiones HTTP (POST, GET, PUT, DELETE).
- copy: Proporciona deepcopy para clonar la plantilla del payload.
- datetime: Mide latencias de respuesta y genera timestamps para evidencias.
- collections.defaultdict: Agrupa estadísticas globales de ejecución (PASS, FAIL, etc.) sin comprobar existencia de llaves.
- time: Introduce micro-pausas (time.sleep(0.5)) entre llamadas en account_linking_tests.py para evitar saturación y falsos positivos por rate-limiting.

# ⚙️ Funciones Core del Framework

- obtener_codigo_error(resp)
- ejecutar_pruebas()`

## 1. `obtener_codigo_error(resp)`

Extrae y estandariza el código de negocio retornado por la API, resolviendo la inconsistencia de esquemas de respuesta entre microservicios. Se debe ajustar en casos de las APIS con mensajes personalizados.


### Flujo Account Linking / CBU

```text
[ HTTP Resp ]
       |
       v
¿Status 200 / "ok" en JSON?
       |
   +---+---+
   |       |
  SÍ      NO
   |       |
   v       v
 "200"  json_resp["errors"][0]["code"]
```

### Flujo Debit Card

```text
[ HTTP Resp ]
       |
       v
¿Status 201?
       |
   +---+---+
   |       |
  SÍ      NO
   |       |
   v       v
 "201"  Fallbacks evaluados en orden:
          1. error.code
          2. error.status
          3. code
          4. status
          5. str(resp.status_code)
```

---

## 2. `ejecutar_pruebas()`

Orquesta la suite completa de ejecución siguiendo los pasos detallados a continuación.

### Flujo de Ejecución

#### 1. Inicialización

Se crea la colección de resultados y se instancia el componente de reporter.

```python
resultados = []
reporter = APITestReporter()
```

#### 2. Iteración de Escenarios

Se recorren todos los escenarios definidos en la colección `TEST_CASES`.

#### 3. Clonación y Mutación del Payload

Para garantizar el aislamiento entre escenarios, se genera una copia  del payload base y se aplican las modificaciones específicas del caso de prueba.

```python
payload = copy.deepcopy(BASE_PAYLOAD)

for campo, valor in test_case["changes"].items():
    payload[campo] = valor
```

#### 4. Ejecución HTTP

Se invoca el endpoint bajo prueba utilizando la librería `requests`.

```python
response = requests.post(
    URL,
    headers=HEADERS_BASE,
    json=payload
)
```

#### 5. Normalización de Respuesta

Se obtiene el código de http(error o OK) a través del método:

```python
codigo_obtenido = obtener_codigo_error(response)
```

#### 6. Validación

Se compara el código retornado por la API contra el valor esperado configurado para el escenario.

```python
resultado = (
    codigo_obtenido == test_case["expected_code"]
)
```

#### 7. Registro de Evidencias

Se crea un objeto `TestCaseResult` con toda la información necesaria:

- Nombre del caso de prueba.
- Payload enviado.
- Respuesta recibida.
- Código esperado.
- Código obtenido.
- Duración de ejecución.
- Resultado final (`PASS` / `FAIL`).

#### 8. Generación de Reportes

Finalmente, se consolidan las métricas globales y se exportan los artefactos de evidencias.

---

# 📊 Consolidación de Evidencias (Reporter)

El framework utiliza dos componentes principales definidos en `reporter.py`.

## `TestCaseResult`

Objeto DTO que representa el resultado individual de cada escenario ejecutado.

### Atributos

| Atributo | Descripción |
|-----------|-------------|
| `nombre_test` | Nombre descriptivo del escenario |
| `resultado` | Estado final (`PASS` / `FAIL`) |
| `codigo_esperado` | Código definido en el caso de prueba |
| `codigo_obtenido` | Código retornado por la API |
| `duracion` | Tiempo de ejecución en milisegundos |
| `detalle` | Payloads de request y response para análisis posterior |

---

## `APITestReporter`

Componente encargado de gestionar la consolidación de resultados y la generación de evidencias de ejecución.

### Responsabilidades

- Recolectar todos los objetos `TestCaseResult`.
- Calcular métricas globales de ejecución.
- Determinar la cobertura funcional ejecutada.
- Calcular el porcentaje de éxito de la ejecución.
- Medir el tiempo total consumido por la suite.
- Exportar archivos finales de evidencias y reportes.

### Métricas Consolidadas

El reporter genera indicadores tales como:

- Total de casos ejecutados.
- Casos aprobados (`PASS`).
- Casos fallidos (`FAIL`).
- Porcentaje de éxito.
- Tiempo total de ejecución.
- Evidencias detalladas por escenario.

---

## Resumen del Proceso

```text
TEST_CASES
     |
     v
Clonación del Payload Base
     |
     v
Mutación de Datos de Prueba
     |
     v
Invocación HTTP
     |
     v
obtener_codigo_error()
     |
     v
Validación vs Expected Code
     |
     v
Creación de TestCaseResult
     |
     v
APITestReporter
     |
     v
Métricas + Evidencias + Reportes
```

# 🚀 Guía Paso a Paso: Cómo Agregar un Nuevo Caso de Prueba

El framework permite definir escenarios mediante objetos de configuración, donde cada caso especifica:

- Identificador único (`id`)
- Requisito funcional asociado (`requisito`)
- Descripción del escenario (`descripcion`)
- Código esperado (`expected_code`)
- Función modificadora del payload (`modificador`)

La lógica de ejecución reutiliza un payload base y aplica la transformación definida en `modificador` antes de invocar la API.

---

## Caso 1: Probar el Escenario Exitoso (Happy Path)

Para validar el comportamiento esperado de la operación, la función modificadora debe devolver el payload original sin realizar cambios.

Se utiliza una función identidad:

```python
lambda p: p
```

### Ejemplo

```python
{
    "id": "C200-01 Alta CBU OK - Caja de ahorro pesos",
    "requisito": "Happy Path",
    "descripcion": "Alta exitosa de CBU con datos completos en regla",
    "expected_code": "200",
    "modificador": lambda p: p
}
```

### Resultado Esperado

```text
Payload Base
      |
      v
Sin modificaciones
      |
      v
Invocación API
      |
      v
Código esperado: 200
```

---

## Caso 2: Modificar un Campo Existente (`setear`)

Utiliza la función:

```python
setear("nombre_campo", nuevo_valor)
```

Este tipo de modificación permite validar:

- Valores inválidos.
- Longitudes máximas y mínimas.
- Dominios no permitidos.
- Formatos incorrectos.
- Reglas de negocio específicas.

### Ejemplo

```python
{
    "id": "C400-01 Error - Tipo de cuenta inválido",
    "requisito": "VAL-ACCT-01",
    "descripcion": "Verifica que el sistema rechace un tipo de cuenta inexistente (ej: 99)",
    "expected_code": "400",
    "modificador": setear("account_type", "99")
}
```

### Resultado Esperado

```text
Payload Base
      |
      v
account_type = "99"
      |
      v
Invocación API
      |
      v
Código esperado: 400
```

---

## Caso 3: Eliminar un Campo Requerido (`borrar`)

Utiliza la función:

```python
borrar("nombre_campo")
```

Este escenario permite verificar el comportamiento de las validaciones obligatorias y restricciones de esquema.

### Ejemplo

```python
{
    "id": "C400-02 Error - CBU omitido",
    "requisito": "REQ-CBU-01",
    "descripcion": "Valida rechazo de la petición cuando la propiedad 'cbu' no es enviada",
    "expected_code": "400",
    "modificador": borrar("cbu")
}
```

### Resultado Esperado

```text
Payload Base
      |
      v
Eliminar campo "cbu"
      |
      v
Invocación API
      |
      v
Código esperado: 400
```

### Casos de Uso Frecuentes

- Campos obligatorios ausentes.
- Validaciones de esquema JSON.
- Reglas de integridad de datos.
- Validaciones de contratos API.

---

## Caso 4: Modificaciones Múltiples o Complejas

Cuando es necesario alterar más de un atributo simultáneamente, 


---

## Autor

Equipo de QA - APIS BAnking