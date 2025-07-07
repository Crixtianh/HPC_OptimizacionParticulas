@echo off
echo ================================================
echo       VERIFICACION COMPLETA DEL SISTEMA
echo ================================================

echo.
echo [1/4] Verificando orquestador...
curl -s http://localhost:5000/status >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Orquestador funcionando correctamente
    curl -s http://localhost:5000/status
) else (
    echo ✗ Orquestador NO responde
    echo   Verificar: docker ps ^| findstr orchestrator
)

echo.
echo [2/4] Verificando conectividad con workers...
curl -s http://localhost:5000/ping_all >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ API de ping funcionando
    curl -s http://localhost:5000/ping_all
) else (
    echo ✗ No se puede hacer ping a workers
)

echo.
echo [3/4] Verificando contenedores Docker...
docker ps | findstr particle >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Contenedores ejecutándose:
    docker ps | findstr particle
) else (
    echo ✗ No se encontraron contenedores particle ejecutándose
    echo   Contenedores disponibles:
    docker ps -a | findstr particle
)

echo.
echo [4/4] Resumen del sistema...
echo.
echo === ESTADO DEL SISTEMA ===
curl -s http://localhost:5000/status 2>nul | findstr "online_workers\|total_workers" || echo "No se puede obtener estado del sistema"

echo.
echo === COMANDOS ÚTILES ===
echo - Ver logs orquestador: docker logs -f particle-orchestrator
echo - Monitorear sistema: python scripts\orchestrator_client.py monitor
echo - Ejecutar tareas: curl -X POST http://localhost:5000/execute_tasks
echo - Ver estado completo: curl http://localhost:5000/status
echo.
echo === PRÓXIMOS PASOS ===
echo 1. Si todo está funcionando: curl -X POST http://localhost:5000/execute_tasks
echo 2. Para monitoreo continuo: python scripts\orchestrator_client.py monitor
echo 3. Para ver resultados: dir results\
echo.
pause
