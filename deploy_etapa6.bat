@echo off
REM Script de despliegue rápido para ETAPA 6 - Windows
REM ===================================================

echo.
echo 🚀 DESPLEGANDO SISTEMA ETAPA 6 - WINDOWS
echo ==========================================

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no encontrado. Instalar Python 3.8 o superior
    pause
    exit /b 1
)

echo ✅ Python encontrado

REM Verificar archivos principales
echo.
echo 📁 Verificando archivos principales...
set files=elastic_orchestrator_v6.py worker_service.py config_manager.py task_generator.py .env config_workers.json
for %%f in (%files%) do (
    if not exist "%%f" (
        echo ❌ Archivo no encontrado: %%f
        pause
        exit /b 1
    )
    echo ✅ %%f
)

REM Crear directorios necesarios
echo.
echo 📂 Creando directorios...
if not exist "logs" mkdir logs
if not exist "results" mkdir results
echo ✅ Directorios creados

REM Instalar dependencias
echo.
echo 📦 Instalando dependencias...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Error instalando dependencias
    pause
    exit /b 1
)
echo ✅ Dependencias instaladas

REM Verificar configuración
echo.
echo ⚙️  Verificando configuración...
python verify_etapa6.py
if %errorlevel% neq 0 (
    echo ❌ Error en verificación
    pause
    exit /b 1
)

echo.
echo 🎉 SISTEMA LISTO PARA ETAPA 6
echo.
echo 📋 Próximos pasos:
echo 1. Configurar IPs en .env y config_workers.json
echo 2. En máquina maestro: python elastic_orchestrator_v6.py
echo 3. En máquinas worker: python worker_service.py --worker-id worker1 --port 5001
echo 4. Generar tareas: python task_generator.py
echo 5. Monitorear: curl http://localhost:5000/stats
echo.

pause
