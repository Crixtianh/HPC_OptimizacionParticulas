@echo off
echo 🐳 Construyendo imagen Docker para simulación de partículas...

REM Construir la imagen
docker build -t particle-simulation:latest .

if %ERRORLEVEL% EQU 0 (
    echo ✅ Imagen construida exitosamente!
    echo 📦 Imagen disponible: particle-simulation:latest
    
    REM Mostrar información de la imagen
    docker images particle-simulation:latest
    
    echo.
    echo 🧪 Probando ejecución con parámetros por defecto:
    echo docker run particle-simulation:latest python benchmark.py
    docker run --rm particle-simulation:latest python benchmark.py
    
    echo.
    echo 🧪 Probando ejecución con parámetros personalizados:
    echo docker run particle-simulation:latest python benchmark.py 50 100 42
    docker run --rm particle-simulation:latest python benchmark.py 50 100 42
) else (
    echo ❌ Error al construir la imagen Docker
    exit /b 1
)

pause
