#!/bin/bash
echo "🐳 Construyendo imagen Docker para simulación de partículas..."

# Construir la imagen
docker build -t particle-simulation:latest .

if [ $? -eq 0 ]; then
    echo "✅ Imagen construida exitosamente!"
    echo "📦 Imagen disponible: particle-simulation:latest"
    
    # Mostrar información de la imagen
    docker images particle-simulation:latest
    
    echo ""
    echo "🧪 Probando ejecución con parámetros por defecto:"
    echo "docker run particle-simulation:latest python benchmark.py"
    docker run --rm particle-simulation:latest python benchmark.py
    
    echo ""
    echo "🧪 Probando ejecución con parámetros personalizados:"
    echo "docker run particle-simulation:latest python benchmark.py 50 100 42"
    docker run --rm particle-simulation:latest python benchmark.py 50 100 42
else
    echo "❌ Error al construir la imagen Docker"
    exit 1
fi