#!/bin/bash

# Script para configurar dependencias del worker
# Este script verifica e instala las dependencias necesarias para el worker

echo "🔧 Setup Worker Dependencies"
echo "=============================="

# Función para verificar comando
check_command() {
    if command -v "$1" >/dev/null 2>&1; then
        echo "✅ $1 disponible: $(which $1)"
        return 0
    else
        echo "❌ $1 no encontrado"
        return 1
    fi
}

# Función para verificar módulo Python
check_python_module() {
    if python3 -c "import $1" 2>/dev/null; then
        echo "✅ Módulo $1 disponible"
        return 0
    else
        echo "❌ Módulo $1 no encontrado"
        return 1
    fi
}

echo "🔍 Verificando herramientas del sistema..."
check_command python3
check_command pip3
check_command sudo
check_command docker

echo ""
echo "🔍 Verificando módulos Python..."
check_python_module flask
check_python_module requests

# Verificar versiones
echo ""
echo "📋 Información del sistema:"
echo "  - OS: $(uname -a 2>/dev/null || echo 'Desconocido')"
echo "  - Python: $(python3 --version 2>/dev/null || echo 'No encontrado')"
echo "  - pip3: $(pip3 --version 2>/dev/null || echo 'No encontrado')"
echo "  - Docker: $(docker --version 2>/dev/null || echo 'No encontrado')"

# Opciones de instalación
echo ""
echo "💡 Opciones de instalación de dependencias:"
echo ""

# Opción 1: Usuario actual (sin sudo)
echo "📦 Opción 1: Instalación para usuario actual (recomendado)"
echo "   Comando: pip3 install --user flask requests"
echo "   Pros: No requiere sudo, seguro"
echo "   Contras: Solo disponible para el usuario actual"
echo ""

# Opción 2: Paquetes del sistema
echo "📦 Opción 2: Paquetes del sistema (Ubuntu/Debian)"
echo "   Comando: sudo apt update && sudo apt install python3-flask python3-requests"
echo "   Pros: Integración con el sistema, versiones estables"
echo "   Contras: Requiere sudo, versiones pueden ser antiguas"
echo ""

# Opción 3: pip global
echo "📦 Opción 3: Instalación global con pip"
echo "   Comando: sudo pip3 install flask requests"
echo "   Pros: Disponible para todos los usuarios"
echo "   Contras: Requiere sudo, puede conflictuar con paquetes del sistema"
echo ""

# Instalación interactiva
echo "🚀 ¿Deseas instalar las dependencias automáticamente?"
echo "   1) pip3 --user (recomendado)"
echo "   2) apt (paquetes del sistema)"
echo "   3) sudo pip3 (global)"
echo "   4) Solo verificar, no instalar"
echo ""

read -p "Selecciona una opción (1-4): " -n 1 -r
echo ""

case $REPLY in
    1)
        echo "🔄 Instalando con pip3 --user..."
        pip3 install --user flask requests
        if [ $? -eq 0 ]; then
            echo "✅ Instalación exitosa con pip3 --user"
        else
            echo "❌ Error en la instalación con pip3 --user"
        fi
        ;;
    2)
        echo "🔄 Instalando con apt..."
        sudo apt update && sudo apt install -y python3-flask python3-requests
        if [ $? -eq 0 ]; then
            echo "✅ Instalación exitosa con apt"
        else
            echo "❌ Error en la instalación con apt"
        fi
        ;;
    3)
        echo "🔄 Instalando con sudo pip3..."
        sudo pip3 install flask requests
        if [ $? -eq 0 ]; then
            echo "✅ Instalación exitosa con sudo pip3"
        else
            echo "❌ Error en la instalación con sudo pip3"
        fi
        ;;
    4)
        echo "ℹ️  Solo verificando, sin instalar"
        ;;
    *)
        echo "⚠️  Opción no válida, solo verificando"
        ;;
esac

# Verificación final
echo ""
echo "🔍 Verificación final..."
need_install=false

if ! check_python_module flask; then
    need_install=true
fi

if ! check_python_module requests; then
    need_install=true
fi

if [ "$need_install" = true ]; then
    echo ""
    echo "❌ Aún faltan dependencias"
    echo "💡 Puedes:"
    echo "   1. Ejecutar este script de nuevo y elegir otra opción"
    echo "   2. Instalar manualmente:"
    echo "      pip3 install --user flask requests"
    echo "      O: sudo apt install python3-flask python3-requests"
    echo "   3. Continuar y que start_worker.sh intente instalarlas"
    exit 1
else
    echo ""
    echo "✅ ¡Todas las dependencias están disponibles!"
    echo "🎯 Ya puedes ejecutar: ./start_worker.sh"
fi
