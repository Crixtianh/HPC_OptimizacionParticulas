@echo off
echo ====================================================================
echo          SISTEMA DE ORQUESTACION ELASTICO V6 - CARGA AUTOMATICA
echo ====================================================================
echo.
echo Iniciando sistema con carga automatica de tareas...
echo.

REM Crear directorios necesarios
mkdir logs 2>nul
mkdir results 2>nul
mkdir task_queues 2>nul
mkdir task_queues\processed 2>nul

REM Verificar archivos necesarios
if not exist elastic_orchestrator_v6.py (
    echo ERROR: No se encuentra elastic_orchestrator_v6.py
    pause
    exit /b 1
)

if not exist auto_task_generator.py (
    echo ERROR: No se encuentra auto_task_generator.py
    pause
    exit /b 1
)

if not exist config_workers.json (
    echo ERROR: No se encuentra config_workers.json
    pause
    exit /b 1
)

echo Archivos verificados correctamente.
echo.

REM Ejecutar script de inicio
echo Iniciando orquestador con carga automatica...
python start_etapa6_auto.py

echo.
echo Sistema finalizado.
pause
