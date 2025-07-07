@echo off
echo ================================================
echo           EJECUTANDO WORKER 1 (VM1)
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
docker stop particle-worker-1 2>nul
docker rm particle-worker-1 2>nul

echo.
echo Creando directorios locales...
if not exist "results" mkdir results
if not exist "logs" mkdir logs

echo.
echo Iniciando Worker 1...
docker run -d ^
  --name particle-worker-1 ^
  -p 8001:8000 ^
  -v "%cd%\results:/app/results" ^
  -v "%cd%\logs:/app/logs" ^
  -e WORKER_ID=worker1 ^
  -e WORKER_NAME=Worker-VM1 ^
  --restart unless-stopped ^
  particle-worker:latest python worker_service.py --port 8000 --worker-id worker1

if %errorlevel% neq 0 (
    echo ERROR: Fallo al iniciar Worker 1
    pause
    exit /b 1
)

echo.
echo ================================================
echo         WORKER 1 INICIADO EXITOSAMENTE!
echo ================================================
echo.
echo Worker 1 ejecutandose en: http://localhost:8001
echo.
echo Comandos utiles:
echo - Ver logs: docker logs -f particle-worker-1
echo - Ver estado: docker ps
echo - Detener: docker stop particle-worker-1
echo - Reiniciar: docker restart particle-worker-1
echo.
echo Verificando que el worker responde...
timeout /t 5 /nobreak
curl -s http://localhost:8001/ping 2>nul && echo Worker 1 respondiendo correctamente! || echo WARNING: Worker 1 no responde aun, esperando...
echo.
pause
