#!/bin/bash
echo "📦 Empaquetando proyecto COMPLETO - ETAPA 4..."

# Nombre del archivo TAR con versionado
TAR_FILE="particle-simulation-ETAPA4-$(date +%Y%m%d-%H%M%S).tar.gz"

echo "🔍 Archivos a incluir:"
echo "  📋 Benchmarks: benchmark.py, benchmark_cython.py"
echo "  🐳 Docker: Dockerfile, Dockerfile.worker"
echo "  📝 Config: requirements.txt, requirements_worker.txt, config_workers.json"
echo "  🎭 Orquestador: orchestrator.py, test_communication.py"
echo "  🖥️  Worker: worker_service.py, start_worker.sh"
echo "  📚 Docs: README_ETAPA2.md, README_ETAPA4.md"

# Crear archivo TAR excluyendo archivos innecesarios
tar -czf "$TAR_FILE" \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='*.tar.gz' \
    --exclude='build/' \
    --exclude='*.prof' \
    --exclude='logs/' \
    *.py *.pyx *.c *.txt *.so *.json *.sh *.bat Dockerfile* README_*.md .dockerignore

if [ $? -eq 0 ]; then
    echo "✅ Proyecto ETAPA 4 empaquetado exitosamente!"
    echo "📁 Archivo creado: $TAR_FILE"
    echo "📊 Tamaño: $(du -h "$TAR_FILE" | cut -f1)"
    
    # Mostrar contenido del TAR
    echo ""
    echo "📋 Contenido del archivo TAR:"
    tar -tzf "$TAR_FILE" | sort
    
    echo ""
    echo "🚀 COMANDOS PARA TRANSFERIR A VMs:"
    echo "   scp $TAR_FILE usuario@192.168.1.93:/home/usuario/"
    echo "   scp $TAR_FILE usuario@192.168.1.155:/home/usuario/"
    
    echo ""
    echo "📂 COMANDOS PARA EXTRAER EN VMs:"
    echo "   tar -xzf $TAR_FILE"
    echo "   cd TAREA/"
    echo "   chmod +x *.sh"
    echo "   pip3 install flask requests"
    echo "   docker build -t particle-simulation:latest ."
    echo "   ./start_worker.sh"
    
else
    echo "❌ Error al crear el archivo TAR"
    exit 1
fi
