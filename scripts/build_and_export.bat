@echo off
echo ================================================
echo    CONSTRUYENDO Y EXPORTANDO IMAGENES DOCKER
echo ================================================

echo.
echo [1/4] Construyendo imagen del orquestador...
docker build -f Dockerfile.orchestrator -t particle-orchestrator:latest .
if %errorlevel% neq 0 (
    echo ERROR: Fallo al construir imagen del orquestador
    pause
    exit /b 1
)

echo.
echo [2/4] Construyendo imagen del worker...
docker build -f Dockerfile.worker -t particle-worker:latest .
if %errorlevel% neq 0 (
    echo ERROR: Fallo al construir imagen del worker
    pause
    exit /b 1
)

echo.
echo [3/4] Exportando imagen del orquestador a TAR...
docker save -o particle-orchestrator.tar particle-orchestrator:latest
if %errorlevel% neq 0 (
    echo ERROR: Fallo al exportar imagen del orquestador
    pause
    exit /b 1
)

echo.
echo [4/4] Exportando imagen del worker a TAR...
docker save -o particle-worker.tar particle-worker:latest
if %errorlevel% neq 0 (
    echo ERROR: Fallo al exportar imagen del worker
    pause
    exit /b 1
)

echo.
echo ================================================
echo    PROCESO COMPLETADO EXITOSAMENTE!
echo ================================================
echo.
echo Archivos TAR generados:
dir *.tar
echo.
echo Tamaños de archivos:
for %%f in (*.tar) do echo %%f: %%~zf bytes
echo.
echo SIGUIENTE PASO:
echo 1. Copiar particle-worker.tar a cada maquina virtual
echo 2. En cada VM: docker load -i particle-worker.tar
echo 3. En tu PC: docker-compose up orchestrator
echo 4. En cada VM: Ejecutar script de worker correspondiente
echo.
pause
