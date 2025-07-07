@echo off
echo ================================================
echo        INSTALADOR DE DOCKER PARA WINDOWS
echo ================================================

echo.
echo IMPORTANTE: Este script debe ejecutarse como ADMINISTRADOR
echo.
echo Verificando privilegios de administrador...
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Este script requiere privilegios de administrador
    echo Haz clic derecho en el script y selecciona "Ejecutar como administrador"
    pause
    exit /b 1
)

echo.
echo [1/5] Verificando si Docker ya esta instalado...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Docker ya esta instalado:
    docker --version
    echo.
    echo ¿Deseas continuar con la instalacion de todas formas? (y/n)
    set /p choice="Opcion: "
    if /i not "%choice%"=="y" (
        echo Instalacion cancelada.
        pause
        exit /b 0
    )
)

echo.
echo [2/5] Habilitando Hyper-V y contenedores de Windows...
dism.exe /online /enable-feature /featurename:Microsoft-Hyper-V /all /norestart
dism.exe /online /enable-feature /featurename:Containers /all /norestart

echo.
echo [3/5] Descargando Docker Desktop...
echo Esto puede tomar varios minutos dependiendo de tu conexion...

powershell -Command "& {
    $url = 'https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe'
    $output = 'Docker-Desktop-Installer.exe'
    Write-Host 'Descargando Docker Desktop...'
    Invoke-WebRequest -Uri $url -OutFile $output
    Write-Host 'Descarga completada.'
}"

if not exist "Docker-Desktop-Installer.exe" (
    echo ERROR: No se pudo descargar Docker Desktop
    echo Descarga manualmente desde: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo.
echo [4/5] Instalando Docker Desktop...
echo NOTA: Se abrira el instalador de Docker. Sigue las instrucciones en pantalla.
start /wait Docker-Desktop-Installer.exe install --quiet

echo.
echo [5/5] Limpiando archivos temporales...
del Docker-Desktop-Installer.exe

echo.
echo ================================================
echo          INSTALACION COMPLETADA!
echo ================================================
echo.
echo IMPORTANTE: 
echo 1. REINICIA tu computadora/VM
echo 2. Despues del reinicio, inicia Docker Desktop
echo 3. Acepta los terminos y condiciones
echo 4. Espera a que Docker se inicie completamente
echo 5. Verifica con: docker --version
echo.
echo Despues del reinicio ejecuta: load_images.bat
echo.
set /p restart="¿Deseas reiniciar ahora? (y/n): "
if /i "%restart%"=="y" (
    echo Reiniciando en 10 segundos...
    shutdown /r /t 10
) else (
    echo Recuerda reiniciar manualmente antes de usar Docker
)
pause
