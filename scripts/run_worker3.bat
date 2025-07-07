@echo off
echo ================================================
echo           EJECUTANDO WORKER 3 (VM3)
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
docker stop particle-worker-3 2>nul
docker rm particle-worker-3 2>nul

echo.
echo Creando directorios locales...
if not exist "results" mkdir results
if not exist "logs" mkdir logs

echo.
echo Iniciando Worker 3...
docker run -d ^
  --name particle-worker-3 ^
  -p 8003:8000 ^
  -v "%cd%\results:/app/results" ^
  -v "%cd%\logs:/app/logs" ^
  -e WORKER_ID=worker3 ^
  -e WORKER_NAME=Worker-VM3 ^
  --restart unless-stopped ^
  particle-worker:latest python worker_service.py --port 8000 --worker-id worker3

if %errorlevel% neq 0 (
    echo ERROR: Fallo al iniciar Worker 3
    pause
    exit /b 1
)

echo.
echo ================================================
echo         WORKER 3 INICIADO EXITOSAMENTE!
echo ================================================
echo.
echo Worker 3 ejecutandose en: http://localhost:8003
echo.
echo Comandos utiles:
echo - Ver logs: docker logs -f particle-worker-3
echo - Ver estado: docker ps
echo - Detener: docker stop particle-worker-3
echo - Reiniciar: docker restart particle-worker-3
echo.
echo Verificando que el worker responde...
timeout /t 5 /nobreak
curl -s http://localhost:8003/ping 2>nul && echo Worker 3 respondiendo correctamente! || echo WARNING: Worker 3 no responde aun, esperando...
echo.
pause
