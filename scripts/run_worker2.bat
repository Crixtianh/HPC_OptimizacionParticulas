@echo off
echo ================================================
echo           EJECUTANDO WORKER 2 (VM2)
echo ================================================

echo.
echo Verificando imagen Docker...
docker images | findstr particle-worker >nul
if %errorlevel% neq 0 (
    echo ERROR: No se encuentra la imagen particle-worker
    echo Ejecuta primero: load_images.bat
    pause
    exit /b 1
)

echo.
echo Deteniendo contenedor existente si existe...
docker stop particle-worker-2 2>nul
docker rm particle-worker-2 2>nul

echo.
echo Creando directorios locales...
if not exist "results" mkdir results
if not exist "logs" mkdir logs

echo.
echo Iniciando Worker 2...
docker run -d ^
  --name particle-worker-2 ^
  -p 8002:8000 ^
  -v "%cd%\results:/app/results" ^
  -v "%cd%\logs:/app/logs" ^
  -e WORKER_ID=worker2 ^
  -e WORKER_NAME=Worker-VM2 ^
  --restart unless-stopped ^
  particle-worker:latest python worker_service.py --port 8000 --worker-id worker2

if %errorlevel% neq 0 (
    echo ERROR: Fallo al iniciar Worker 2
    pause
    exit /b 1
)

echo.
echo ================================================
echo         WORKER 2 INICIADO EXITOSAMENTE!
echo ================================================
echo.
echo Worker 2 ejecutandose en: http://localhost:8002
echo.
echo Comandos utiles:
echo - Ver logs: docker logs -f particle-worker-2
echo - Ver estado: docker ps
echo - Detener: docker stop particle-worker-2
echo - Reiniciar: docker restart particle-worker-2
echo.
echo Verificando que el worker responde...
timeout /t 5 /nobreak
curl -s http://localhost:8002/ping 2>nul && echo Worker 2 respondiendo correctamente! || echo WARNING: Worker 2 no responde aun, esperando...
echo.
pause
