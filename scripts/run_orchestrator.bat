@echo off
echo ================================================
echo         EJECUTANDO ORQUESTADOR (PC PRINCIPAL)
echo ================================================

echo.
echo Verificando imagen Docker...
docker images | findstr particle-orchestrator >nul
if %errorlevel% neq 0 (
    echo ERROR: No se encuentra la imagen particle-orchestrator
    echo Ejecuta primero: build_and_export.bat
    pause
    exit /b 1
)

echo.
echo Deteniendo contenedor existente si existe...
docker stop particle-orchestrator 2>nul
docker rm particle-orchestrator 2>nul

echo.
echo Creando directorios locales...
if not exist "logs" mkdir logs
if not exist "results" mkdir results

echo.
echo Configurando IPs de workers...
echo IMPORTANTE: Asegurate de que las IPs sean correctas
echo Si no sabes las IPs de tus VMs, usa: ipconfig (Windows) o ip addr (Linux)
echo.
set /p VM1_IP="IP de la VM1 (Worker 1) [ejemplo: 192.168.1.100]: "
set /p VM2_IP="IP de la VM2 (Worker 2) [ejemplo: 192.168.1.101]: "
set /p VM3_IP="IP de la VM3 (Worker 3) [ejemplo: 192.168.1.102]: "

echo.
echo Iniciando Orquestador...
docker run -d ^
  --name particle-orchestrator ^
  -p 5000:5000 ^
  -v "%cd%\logs:/app/logs" ^
  -v "%cd%\results:/app/results" ^
  -v "%cd%\configs:/app/configs" ^
  -e WORKER1_IP=%VM1_IP% ^
  -e WORKER2_IP=%VM2_IP% ^
  -e WORKER3_IP=%VM3_IP% ^
  --restart unless-stopped ^
  particle-orchestrator:latest

if %errorlevel% neq 0 (
    echo ERROR: Fallo al iniciar Orquestador
    pause
    exit /b 1
)

echo.
echo ================================================
echo      ORQUESTADOR INICIADO EXITOSAMENTE!
echo ================================================
echo.
echo Orquestador ejecutandose en: http://localhost:5000
echo.
echo Workers configurados:
echo - Worker 1: http://%VM1_IP%:8001
echo - Worker 2: http://%VM2_IP%:8002  
echo - Worker 3: http://%VM3_IP%:8003
echo.
echo Comandos utiles:
echo - Ver logs: docker logs -f particle-orchestrator
echo - Ver estado: curl http://localhost:5000/status
echo - Ping workers: curl http://localhost:5000/ping_all
echo - Ejecutar tareas: curl -X POST http://localhost:5000/execute_tasks
echo.
echo Esperando que el orquestador se inicie...
timeout /t 10 /nobreak

echo.
echo Verificando estado del sistema...
curl -s http://localhost:5000/status 2>nul && echo Orquestador respondiendo correctamente! || echo WARNING: Orquestador no responde aun, esperando...

echo.
echo ================================================
echo Para monitorear el sistema usa:
echo python scripts\orchestrator_client.py monitor
echo ================================================
pause
