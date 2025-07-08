@echo off
REM Script de inicio para ETAPA 5 - Sistema Elástico (Windows)

echo 🚀 INICIANDO SISTEMA ELÁSTICO - ETAPA 5
echo =======================================

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no encontrado
    pause
    exit /b 1
)

REM Verificar archivos necesarios
if not exist "elastic_orchestrator.py" (
    echo ❌ Archivo requerido no encontrado: elastic_orchestrator.py
    pause
    exit /b 1
)

if not exist "config_manager.py" (
    echo ❌ Archivo requerido no encontrado: config_manager.py
    pause
    exit /b 1
)

if not exist ".env" (
    echo ❌ Archivo requerido no encontrado: .env
    pause
    exit /b 1
)

echo ✅ Dependencias verificadas

REM Crear directorio de logs
if not exist "logs" mkdir logs

REM Leer configuración
echo 🔧 Verificando configuración...
findstr "WORKER_01_IP" .env
findstr "WORKER_02_IP" .env

echo.
echo ======================================
echo 🧠 SISTEMA ELÁSTICO CON 2 MEMORIAS:
echo    1. Monitor de Workers (ping constante)
echo    2. Monitor de Tareas (preparación ETAPA 6)
echo ======================================
echo.

REM Confirmar inicio
set /p "confirm=¿Iniciar sistema elástico? (Y/n): "
if /i "%confirm%"=="n" (
    echo 👋 Cancelado por el usuario
    pause
    exit /b 0
)

REM Limpiar logs anteriores
if exist "logs\elastic_orchestrator.log" (
    echo 🧹 Limpiando logs anteriores...
    type nul > "logs\elastic_orchestrator.log"
)

echo 🎯 Iniciando orquestador elástico...
echo 📋 Logs en: logs\elastic_orchestrator.log
echo 🛑 Presiona Ctrl+C para detener
echo.

REM Iniciar el orquestador elástico
python elastic_orchestrator.py

echo.
echo ✅ Sistema elástico detenido
pause
