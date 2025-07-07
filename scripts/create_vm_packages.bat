@echo off
echo ================================================
echo    CREADOR DE PAQUETES PARA MAQUINAS VIRTUALES
echo ================================================

echo.
echo [1/6] Verificando archivos TAR...
if not exist "particle-worker.tar" (
    echo ERROR: No se encuentra particle-worker.tar
    echo Ejecuta primero: build_and_export.bat
    pause
    exit /b 1
)

echo.
echo [2/6] Creando directorios para paquetes VM...
if exist "VM_Packages" rmdir /s /q VM_Packages
mkdir VM_Packages
mkdir VM_Packages\VM1_Package
mkdir VM_Packages\VM2_Package
mkdir VM_Packages\VM3_Package

echo.
echo [3/6] Copiando archivos comunes a todos los paquetes...
for %%d in (VM1_Package VM2_Package VM3_Package) do (
    copy particle-worker.tar VM_Packages\%%d\
    copy scripts\load_images.bat VM_Packages\%%d\
    copy scripts\docker-install.bat VM_Packages\%%d\
    copy VM_SETUP.md VM_Packages\%%d\
)

echo.
echo [4/6] Copiando scripts específicos para cada VM...
copy scripts\run_worker1.bat VM_Packages\VM1_Package\
copy scripts\run_worker2.bat VM_Packages\VM2_Package\
copy scripts\run_worker3.bat VM_Packages\VM3_Package\

echo.
echo [5/6] Creando archivos README específicos...

echo # Paquete para VM1 (Worker 1) > VM_Packages\VM1_Package\README.txt
echo. >> VM_Packages\VM1_Package\README.txt
echo Este paquete contiene todo lo necesario para ejecutar Worker 1 >> VM_Packages\VM1_Package\README.txt
echo. >> VM_Packages\VM1_Package\README.txt
echo INSTRUCCIONES: >> VM_Packages\VM1_Package\README.txt
echo 1. Instalar Docker (si no esta instalado): docker-install.bat >> VM_Packages\VM1_Package\README.txt
echo 2. Cargar imagen: load_images.bat >> VM_Packages\VM1_Package\README.txt
echo 3. Ejecutar worker: run_worker1.bat >> VM_Packages\VM1_Package\README.txt
echo. >> VM_Packages\VM1_Package\README.txt
echo Worker 1 ejecutara en puerto 8001 >> VM_Packages\VM1_Package\README.txt

echo # Paquete para VM2 (Worker 2) > VM_Packages\VM2_Package\README.txt
echo. >> VM_Packages\VM2_Package\README.txt
echo Este paquete contiene todo lo necesario para ejecutar Worker 2 >> VM_Packages\VM2_Package\README.txt
echo. >> VM_Packages\VM2_Package\README.txt
echo INSTRUCCIONES: >> VM_Packages\VM2_Package\README.txt
echo 1. Instalar Docker (si no esta instalado): docker-install.bat >> VM_Packages\VM2_Package\README.txt
echo 2. Cargar imagen: load_images.bat >> VM_Packages\VM2_Package\README.txt
echo 3. Ejecutar worker: run_worker2.bat >> VM_Packages\VM2_Package\README.txt
echo. >> VM_Packages\VM2_Package\README.txt
echo Worker 2 ejecutara en puerto 8002 >> VM_Packages\VM2_Package\README.txt

echo # Paquete para VM3 (Worker 3) > VM_Packages\VM3_Package\README.txt
echo. >> VM_Packages\VM3_Package\README.txt
echo Este paquete contiene todo lo necesario para ejecutar Worker 3 >> VM_Packages\VM3_Package\README.txt
echo. >> VM_Packages\VM3_Package\README.txt
echo INSTRUCCIONES: >> VM_Packages\VM3_Package\README.txt
echo 1. Instalar Docker (si no esta instalado): docker-install.bat >> VM_Packages\VM3_Package\README.txt
echo 2. Cargar imagen: load_images.bat >> VM_Packages\VM3_Package\README.txt
echo 3. Ejecutar worker: run_worker3.bat >> VM_Packages\VM3_Package\README.txt
echo. >> VM_Packages\VM3_Package\README.txt
echo Worker 3 ejecutara en puerto 8003 >> VM_Packages\VM3_Package\README.txt

echo.
echo [6/6] Mostrando resumen de paquetes creados...
echo.
echo ================================================
echo         PAQUETES CREADOS EXITOSAMENTE!
echo ================================================
echo.
echo Directorios creados:
dir VM_Packages
echo.
echo Contenido de cada paquete:
for %%d in (VM1_Package VM2_Package VM3_Package) do (
    echo.
    echo --- %%d ---
    dir VM_Packages\%%d /b
)

echo.
echo ================================================
echo                 SIGUIENTE PASO
echo ================================================
echo.
echo DISTRIBUCION A MAQUINAS VIRTUALES:
echo.
echo 1. VM1: Copiar toda la carpeta VM_Packages\VM1_Package\
echo    Metodos: USB, red compartida, SCP, etc.
echo.
echo 2. VM2: Copiar toda la carpeta VM_Packages\VM2_Package\
echo    Metodos: USB, red compartida, SCP, etc.
echo.
echo 3. VM3: Copiar toda la carpeta VM_Packages\VM3_Package\
echo    Metodos: USB, red compartida, SCP, etc.
echo.
echo EN CADA VM EJECUTAR EN ORDEN:
echo 1. docker-install.bat (solo si no tienen Docker)
echo 2. load_images.bat
echo 3. run_workerX.bat (segun corresponda)
echo.
echo EN TU PC PRINCIPAL:
echo run_orchestrator.bat
echo.
pause
