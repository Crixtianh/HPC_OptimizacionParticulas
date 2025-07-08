#!/bin/bash
echo "📦 Empaquetando proyecto en archivo TAR..."

# Nombre del archivo TAR con timestamp
TAR_FILE="particle-simulation-$(date +%Y%m%d-%H%M%S).tar.gz"

# Crear archivo TAR excluyendo archivos innecesarios
tar -czf "$TAR_FILE" \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='*.tar.gz' \
    --exclude='build/' \
    --exclude='*.prof' \
    *.py *.pyx *.c *.txt *.so Dockerfile build_docker.sh test_docker.sh package_project.sh

if [ $? -eq 0 ]; then
    echo "✅ Proyecto empaquetado exitosamente!"
    echo "📁 Archivo creado: $TAR_FILE"
    echo "📊 Tamaño: $(du -h "$TAR_FILE" | cut -f1)"
    
    # Mostrar contenido del TAR
    echo ""
    echo "📋 Contenido del archivo TAR:"
    tar -tzf "$TAR_FILE"
    
    echo ""
    echo "🚀 Para transferir a una VM, usa:"
    echo "   scp $TAR_FILE usuario@ip-vm:/ruta/destino/"
    echo ""
    echo "📂 Para extraer en la VM:"
    echo "   tar -xzf $TAR_FILE"
else
    echo "❌ Error al crear el archivo TAR"
    exit 1
fi
