@echo off
echo 🐳 Construyendo imagen Docker para simulación de partículas...
echo 📋 Incluye: benchmark.py + benchmark_cython.py

REM Construir la imagen
docker build -t particle-simulation:latest .

if %ERRORLEVEL% EQU 0 (
    echo ✅ Imagen construida exitosamente!
    echo 📦 Imagen disponible: particle-simulation:latest
    
    REM Mostrar información de la imagen
    docker images particle-simulation:latest
    
    echo.
    echo 🧪 PRUEBA RÁPIDA - BENCHMARK.PY:
    echo docker run particle-simulation:latest python benchmark.py 25 50 42
    docker run --rm particle-simulation:latest python benchmark.py 25 50 42
    
    echo.
    echo 🧪 PRUEBA RÁPIDA - BENCHMARK_CYTHON.PY:
    echo docker run particle-simulation:latest python benchmark_cython.py 25 50 42
    docker run --rm particle-simulation:latest python benchmark_cython.py 25 50 42
    
    echo.
    echo 🎉 AMBOS benchmarks funcionando correctamente!
    echo 💡 Para pruebas completas, ejecuta: test_docker.bat
    
) else (
    echo ❌ Error al construir la imagen Docker
    exit /b 1
)

pause
