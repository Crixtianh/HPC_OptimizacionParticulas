@echo off
echo ================================================
echo       CARGANDO IMAGENES DOCKER DESDE TAR
echo ================================================

echo.
echo Verificando archivos TAR...
if not exist "particle-worker.tar" (
    echo ERROR: No se encuentra particle-worker.tar
    echo Asegurate de copiar el archivo desde el computador principal
    pause
    exit /b 1
)

echo.
echo [1/2] Cargando imagen del worker...
docker load -i particle-worker.tar
if %errorlevel% neq 0 (
    echo ERROR: Fallo al cargar imagen del worker
    pause
    exit /b 1
)

echo.
echo [2/2] Verificando imagen cargada...
docker images | findstr particle-worker
if %errorlevel% neq 0 (
    echo ERROR: La imagen no se cargo correctamente
    pause
    exit /b 1
)

echo.
echo ================================================
echo    IMAGEN CARGADA EXITOSAMENTE!
echo ================================================
echo.
echo SIGUIENTE PASO:
echo Ejecutar el script del worker correspondiente:
echo - run_worker1.bat (para VM1)
echo - run_worker2.bat (para VM2)  
echo - run_worker3.bat (para VM3)
echo.
pause
