#!/bin/bash

echo "🚀 INICIANDO WORKER SERVICE"
echo "=" * 40

# Obtener IP local
LOCAL_IP=$(hostname -I | awk '{print $1}')
if [ "$need_install" = true ]; then
    echo "🔧 Intentando instalar dependencias automáticamente..."
    if ! install_dependencies; then
        echo ""
        echo "❌ Error instalando dependencias automáticamente"
        echo "💡 Opciones manuales:"
        echo "   1. Con apt (recomendado): sudo apt install python3-flask python3-requests"
        echo "   2. Con pip:              pip3 install --user flask requests"
        echo "   3. Con pip global:       sudo pip3 install flask requests"
        echo ""
        echo "🔍 Información de debug:"
        echo "   - Python version: $(python3 --version 2>/dev/null || echo 'No encontrado')"
        echo "   - pip3 available: $(which pip3 2>/dev/null || echo 'No encontrado')"
        echo "   - sudo available: $(which sudo 2>/dev/null || echo 'No encontrado')"
        echo ""
        
        read -p "¿Continuar de todas formas? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "ℹ️  Saliendo. Instala las dependencias manualmente e inténtalo de nuevo."
            exit 1
        fi
        echo "⚠️  Continuando sin verificar dependencias..."
    fi
else
    echo "✅ Dependencias verificadas"
fil: $LOCAL_IP"

# Determinar Worker ID basado en IP
if [[ "$LOCAL_IP" == "192.168.1.93" ]]; then
    WORKER_ID="worker-01"
elif [[ "$LOCAL_IP" == "192.168.1.155" ]]; then
    WORKER_ID="worker-02"
else
    WORKER_ID="worker-$LOCAL_IP"
fi

echo "🏷️  Worker ID: $WORKER_ID"

# Verificar que Docker esté funcionando
echo "🔍 Verificando Docker..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker no está funcionando. Intentando iniciar..."
    sudo systemctl start docker
    sleep 5
    
    if ! docker info > /dev/null 2>&1; then
        echo "💥 Error: No se pudo iniciar Docker"
        echo "   Ejecuta manualmente: sudo systemctl start docker"
        exit 1
    fi
fi

echo "✅ Docker está funcionando"

# Verificar que la imagen particle-simulation existe
echo "🔍 Verificando imagen particle-simulation..."
if ! docker images | grep -q "particle-simulation"; then
    echo "⚠️  Imagen particle-simulation no encontrada."
    echo ""
    echo "🔧 Para crear la imagen:"
    echo "   1. Asegúrate de que el proyecto esté extraído"
    echo "   2. cd TAREA/"
    echo "   3. docker build -t particle-simulation:latest ."
    echo ""
    read -p "¿Continuar sin la imagen? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    echo "⚠️  Continuando sin verificar imagen..."
else
    echo "✅ Imagen particle-simulation encontrada"
fi

# Instalar dependencias Python si no están disponibles
echo "🔍 Verificando dependencias Python..."

# Función para instalar dependencias
install_dependencies() {
    echo "📦 Instalando Flask y requests..."
    
    # Opción 1: Intentar con pip3 --user (sin sudo)
    echo "🔄 Intentando con pip3 --user..."
    if pip3 install --user flask==2.3.3 requests==2.31.0; then
        echo "✅ Dependencias instaladas con pip3 --user"
        return 0
    else
        echo "⚠️  pip3 --user falló"
    fi
    
    # Opción 2: Intentar con pip3 sin versión específica
    echo "🔄 Intentando con pip3 --user (versiones simples)..."
    if pip3 install --user flask requests; then
        echo "✅ Dependencias instaladas con pip3 --user (versiones simples)"
        return 0
    else
        echo "⚠️  pip3 --user (versiones simples) falló"
    fi
    
    # Opción 3: Verificar sudo y apt
    echo "🔄 Verificando acceso sudo..."
    if ! sudo -n true 2>/dev/null; then
        echo "⚠️  Sudo requiere contraseña o no está disponible"
        echo "💡 Solicita acceso sudo para instalar dependencias del sistema..."
        if ! sudo true; then
            echo "❌ No se pudo obtener acceso sudo"
            return 1
        fi
    fi
    
    # Opción 4: Intentar con apt (paquetes del sistema)
    echo "🔄 Intentando con paquetes del sistema (apt)..."
    if sudo apt update && sudo apt install -y python3-flask python3-requests; then
        echo "✅ Dependencias instaladas con apt"
        return 0
    else
        echo "⚠️  apt install falló"
    fi
    
    # Opción 5: Intentar con pip3 y sudo
    echo "🔄 Intentando con sudo pip3..."
    if sudo pip3 install flask requests; then
        echo "✅ Dependencias instaladas con sudo pip3"
        return 0
    else
        echo "⚠️  sudo pip3 falló"
    fi
    
    return 1
}

# Verificar si las dependencias están disponibles
need_install=false
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Flask no encontrado"
    need_install=true
fi

if ! python3 -c "import requests" 2>/dev/null; then
    echo "⚠️  Requests no encontrado"
    need_install=true
fi

if [ "$need_install" = true ]; then
    if ! install_dependencies; then
        echo "❌ Error instalando dependencias"
        echo "� Instala manualmente: sudo apt install python3-flask python3-requests"
        echo "💡 O con pip: pip3 install --user flask requests"
        
        read -p "¿Continuar de todas formas? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
        echo "⚠️  Continuando sin verificar dependencias..."
    fi
else
    echo "✅ Dependencias verificadas"
fi

# Verificar si el puerto 8080 está libre
echo "🔍 Verificando puerto 8080..."
if netstat -tuln | grep -q ":8080 "; then
    echo "⚠️  Puerto 8080 ya está en uso"
    echo "🔧 Puedes detener el proceso anterior o usar otro puerto"
    
    read -p "¿Continuar de todas formas? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Crear directorio de logs si no existe
mkdir -p logs

# Configurar variables de entorno
export WORKER_ID=$WORKER_ID
export FLASK_ENV=production

echo "=" * 40
echo "🎯 Iniciando worker service..."
echo "🌐 Accesible en: http://$LOCAL_IP:8080"
echo "🛑 Presiona Ctrl+C para detener"
echo "=" * 40

# Iniciar worker service con logging
python3 worker_service.py 2>&1 | tee logs/worker_$(date +%Y%m%d_%H%M%S).log
