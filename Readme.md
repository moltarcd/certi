# Generador de Reportes

## Descripción

Este proyecto está desarrollado en Python y tiene como objetivo:

- Pruebas de Apis.
- Generar Reportes Automatizados sobre el resultado de las pruebas.




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
python main.py
```

> Reemplazar `main.py` por el archivo principal del proyecto si corresponde.

---

## Estructura del Proyecto

```text
├── env/
├── reports/
├── old_reports/
├── requirements.txt
├── main.py
└── README.md
```

### Directorios

- **reports/**: contiene los reportes generados en la ejecución actual.
- **old_reports/**: almacena reportes históricos de ejecuciones anteriores.
- **env/**: entorno virtual del proyecto.

---

## Funcionalidad de Mantenimiento

Antes de generar nuevos reportes, el sistema puede:

1. Limpiar archivos temporales y caché de ejecución.
2. Mover reportes existentes a la carpeta `old_reports`.
3. Generar una nueva versión de los reportes.

Esto permite mantener un historial de ejecuciones y evitar sobrescribir información previamente generada.

---

## Control de Versiones

Para registrar cambios y publicar actualizaciones en el repositorio:

```bash
git add .
git commit -m "version 1.0 - Actualizacion de fuentes en reportes"
git push origin master
```

---

## Versionado

### v1.0

- Actualización de fuentes utilizadas en la generación de reportes.
- Mejoras de mantenimiento y organización de archivos históricos.

---

## Autor

Equipo de Desarrollo - TecnoSoftware