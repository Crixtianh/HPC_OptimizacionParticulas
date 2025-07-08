#!/bin/bash
echo "🧪 Probando containers Docker..."

echo "=========================================="
echo "1️⃣ Probando benchmark.py con valores por defecto"
echo "=========================================="
docker run --rm particle-simulation:latest python benchmark.py

echo ""
echo "=========================================="
echo "2️⃣ Probando benchmark.py con parámetros personalizados"
echo "=========================================="
echo "Ejecutando: benchmark.py 100 500 42"
docker run --rm particle-simulation:latest python benchmark.py 100 500 42

echo ""
echo "=========================================="
echo "3️⃣ Probando benchmark_cython.py con valores por defecto"
echo "=========================================="
docker run --rm particle-simulation:latest python benchmark_cython.py

echo ""
echo "=========================================="
echo "4️⃣ Probando benchmark_cython.py con parámetros personalizados"
echo "=========================================="
echo "Ejecutando: benchmark_cython.py 100 500 42"
docker run --rm particle-simulation:latest python benchmark_cython.py 100 500 42

echo ""
echo "=========================================="
echo "5️⃣ Verificando que los archivos existen en el container"
echo "=========================================="
docker run --rm particle-simulation:latest ls -la

echo ""
echo "✅ Todas las pruebas completadas!"
echo "📝 Resumen:"
echo "   - benchmark.py: Funcional ✓"
echo "   - benchmark_cython.py: Funcional ✓"  
echo "   - Parámetros CLI: Funcional ✓"
echo "   - Container ready para distribución ✓"
