@echo off
REM Script para Windows para construir y ejecutar el sistema de orquestación

echo === Sistema de Orquestación de Simulaciones ===
echo Construyendo imágenes Docker...

REM Construir imágenes
docker-compose build

echo Iniciando servicios...
docker-compose up -d

echo Esperando que los servicios se inicien...
timeout /t 15 /nobreak

echo Verificando estado de los contenedores...
docker-compose ps

echo.
echo === Información de Acceso ===
echo Orquestador API: http://localhost:5000
echo Worker 1: http://localhost:8001
echo Worker 2: http://localhost:8002
echo Worker 3: http://localhost:8003
echo.

echo === Comandos útiles ===
echo Ver logs del orquestador: docker-compose logs -f orchestrator
echo Ver logs de todos los workers: docker-compose logs -f worker1 worker2 worker3
echo Verificar estado: curl http://localhost:5000/status
echo Hacer ping a workers: curl http://localhost:5000/ping_all
echo Ejecutar tareas: curl -X POST http://localhost:5000/execute_tasks
echo Parar servicios: docker-compose down
echo.

set /p response="¿Desea hacer ping inicial a los workers? (y/n): "
if /i "%response%"=="y" (
    echo Haciendo ping a workers...
    timeout /t 5 /nobreak
    curl -s http://localhost:5000/ping_all
)

echo.
echo Sistema iniciado correctamente!
