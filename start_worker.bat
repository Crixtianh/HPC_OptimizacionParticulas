@echo off
echo 🚀 INICIANDO WORKER SERVICE (Windows)
echo =======================================

REM Obtener IP local (aproximado en Windows)
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do set LOCAL_IP=%%a
set LOCAL_IP=%LOCAL_IP: =%

echo 🌐 IP Local: %LOCAL_IP%

REM Determinar Worker ID
set WORKER_ID=worker-windows

echo 🏷️  Worker ID: %WORKER_ID%

REM Verificar Docker
echo 🔍 Verificando Docker...
docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker no está funcionando
    echo    Inicia Docker Desktop y vuelve a intentar
    pause
    exit /b 1
)

echo ✅ Docker está funcionando

REM Verificar imagen
echo 🔍 Verificando imagen particle-simulation...
docker images | findstr "particle-simulation" >nul
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Imagen particle-simulation no encontrada
    echo.
    echo 🔧 Para crear la imagen:
    echo    docker build -t particle-simulation:latest .
    echo.
    set /p continue="¿Continuar sin la imagen? (y/N): "
    if /i not "%continue%"=="y" exit /b 1
)

REM Verificar Python y dependencias
echo 🔍 Verificando Python...
python -c "import flask, requests" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo 📦 Instalando dependencias...
    pip install flask==2.3.3 requests==2.31.0
)

REM Configurar variables
set WORKER_ID=%WORKER_ID%
set FLASK_ENV=production

echo =======================================
echo 🎯 Iniciando worker service...
echo 🌐 Accesible en: http://%LOCAL_IP%:8080
echo 🛑 Presiona Ctrl+C para detener
echo =======================================

python worker_service.py

pause
