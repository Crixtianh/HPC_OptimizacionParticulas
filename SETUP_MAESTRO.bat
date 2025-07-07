@echo off
title Sistema de Orquestacion de Simulaciones - Configuracion Maestra
color 0A

:menu
cls
echo ================================================================
echo        SISTEMA DE ORQUESTACION DE SIMULACIONES
echo            Configuracion para Ambiente Distribuido
echo ================================================================
echo.
echo Selecciona el modo de operacion:
echo.
echo 1. MODO LOCAL (todo en esta computadora)
echo 2. MODO DISTRIBUIDO (preparar para multiples VMs)
echo 3. EJECUTAR ORQUESTADOR (despues de configurar VMs)
echo 4. VERIFICAR SISTEMA
echo 5. MONITOREAR SISTEMA
echo 6. LIMPIAR TODO
echo 7. SALIR
echo.
set /p choice="Selecciona una opcion (1-7): "

if "%choice%"=="1" goto local_mode
if "%choice%"=="2" goto distributed_mode
if "%choice%"=="3" goto run_orchestrator
if "%choice%"=="4" goto verify_system
if "%choice%"=="5" goto monitor_system
if "%choice%"=="6" goto cleanup
if "%choice%"=="7" goto exit
goto menu

:local_mode
cls
echo ================================================================
echo                     MODO LOCAL
echo ================================================================
echo.
echo Configurando sistema completo en esta computadora...
echo.
echo [1/2] Construyendo imagenes Docker...
docker-compose build
if %errorlevel% neq 0 (
    echo ERROR: Fallo al construir imagenes
    pause
    goto menu
)

echo.
echo [2/2] Iniciando sistema completo...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ERROR: Fallo al iniciar sistema
    pause
    goto menu
)

echo.
echo ================================================================
echo            SISTEMA LOCAL INICIADO EXITOSAMENTE!
echo ================================================================
echo.
echo Servicios disponibles:
echo - Orquestador: http://localhost:5000
echo - Worker 1: http://localhost:8001
echo - Worker 2: http://localhost:8002  
echo - Worker 3: http://localhost:8003
echo.
echo Prueba el sistema:
timeout /t 10 /nobreak
curl -s http://localhost:5000/status 2>nul && echo Sistema funcionando correctamente! || echo Sistema iniciando, espera unos segundos...
echo.
pause
goto menu

:distributed_mode
cls
echo ================================================================
echo                   MODO DISTRIBUIDO
echo ================================================================
echo.
echo Preparando sistema para multiples maquinas virtuales...
echo.
echo [1/3] Construyendo y exportando imagenes...
call scripts\build_and_export.bat
if %errorlevel% neq 0 (
    echo ERROR: Fallo en construccion de imagenes
    pause
    goto menu
)

echo.
echo [2/3] Creando paquetes para VMs...
call scripts\create_vm_packages.bat
if %errorlevel% neq 0 (
    echo ERROR: Fallo en creacion de paquetes
    pause
    goto menu
)

echo.
echo [3/3] Generando instrucciones...
echo.
echo ================================================================
echo          PAQUETES CREADOS PARA DISTRIBUCION!
echo ================================================================
echo.
echo SIGUIENTE PASO - DISTRIBUIR A MAQUINAS VIRTUALES:
echo.
echo VM1: Copiar carpeta VM_Packages\VM1_Package\
echo VM2: Copiar carpeta VM_Packages\VM2_Package\
echo VM3: Copiar carpeta VM_Packages\VM3_Package\
echo.
echo EN CADA VM EJECUTAR EN ORDEN:
echo 1. docker-install.bat (solo si no tienen Docker)
echo 2. load_images.bat
echo 3. run_workerX.bat (segun corresponda)
echo.
echo Cuando termines con las VMs, regresa aqui y selecciona opcion 3
echo para ejecutar el orquestador.
echo.
pause
goto menu

:run_orchestrator
cls
echo ================================================================
echo                EJECUTANDO ORQUESTADOR
echo ================================================================
echo.
echo Verificando que las imagenes esten listas...
docker images | findstr particle-orchestrator >nul
if %errorlevel% neq 0 (
    echo ERROR: No se encuentra imagen del orquestador
    echo Ejecuta primero la opcion 2 (Modo Distribuido)
    pause
    goto menu
)

echo.
echo Ejecutando orquestador...
call scripts\run_orchestrator.bat
pause
goto menu

:verify_system
cls
echo ================================================================
echo                VERIFICANDO SISTEMA
echo ================================================================
echo.
call scripts\verify_system.bat
goto menu

:monitor_system
cls
echo ================================================================
echo                MONITOREANDO SISTEMA
echo ================================================================
echo.
echo Iniciando monitoreo en tiempo real...
echo Presiona Ctrl+C para volver al menu
echo.
python scripts\orchestrator_client.py monitor --interval 5
pause
goto menu

:cleanup
cls
echo ================================================================
echo                    LIMPIAR SISTEMA
echo ================================================================
echo.
echo ¿Estas seguro de que quieres limpiar todo? (y/n)
set /p confirm="Confirmar: "
if /i not "%confirm%"=="y" goto menu

echo.
echo Deteniendo contenedores...
docker-compose down 2>nul
docker stop particle-orchestrator particle-worker-1 particle-worker-2 particle-worker-3 2>nul

echo Eliminando contenedores...
docker rm particle-orchestrator particle-worker-1 particle-worker-2 particle-worker-3 2>nul

echo Eliminando imagenes...
docker rmi particle-orchestrator:latest particle-worker:latest 2>nul

echo Eliminando archivos TAR...
del particle-*.tar 2>nul

echo Eliminando paquetes VM...
if exist VM_Packages rmdir /s /q VM_Packages

echo.
echo ================================================================
echo                LIMPIEZA COMPLETADA!
echo ================================================================
pause
goto menu

:exit
cls
echo ================================================================
echo            Gracias por usar el Sistema de Orquestacion
echo ================================================================
echo.
echo Para mas informacion consulta:
echo - README.md
echo - INSTALACION_DISTRIBUIDA.md
echo.
echo Desarrollado para CompAltoRend
echo.
timeout /t 3 /nobreak
exit

:error
echo.
echo ================================================================
echo                        ERROR
echo ================================================================
echo Ha ocurrido un error inesperado.
echo Revisa los logs y vuelve a intentar.
pause
goto menu
