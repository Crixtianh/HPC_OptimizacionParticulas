#!/bin/bash

# Script de inicio para ETAPA 6 - Sistema con Cola de Tareas
# ========================================================

echo "🚀 INICIANDO SISTEMA CON COLA DE TAREAS - ETAPA 6"
echo "=================================================="

# Verificar dependencias
echo "🔍 Verificando dependencias..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no encontrado"
    exit 1
fi

# Verificar archivos necesarios
REQUIRED_FILES=(
    "elastic_orchestrator_v6.py"
    "config_manager.py"
    ".env"
    "config_workers.json"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Archivo requerido no encontrado: $file"
        exit 1
    fi
done

echo "✅ Dependencias verificadas"

# Crear directorios necesarios
mkdir -p logs
mkdir -p results

# Verificar configuración
echo "🔧 Verificando configuración..."

# Leer IPs desde .env
WORKER_01_IP=$(grep "WORKER_01_IP=" .env | cut -d'=' -f2)
WORKER_02_IP=$(grep "WORKER_02_IP=" .env | cut -d'=' -f2)

echo "   Worker 01: $WORKER_01_IP"
echo "   Worker 02: $WORKER_02_IP"

# Verificar conectividad básica
echo "🔍 Verificando conectividad a workers..."

if ping -c 1 -W 3 $WORKER_01_IP &> /dev/null; then
    echo "✅ Worker 01 ($WORKER_01_IP) alcanzable"
else
    echo "⚠️  Worker 01 ($WORKER_01_IP) no alcanzable"
fi

if ping -c 1 -W 3 $WORKER_02_IP &> /dev/null; then
    echo "✅ Worker 02 ($WORKER_02_IP) alcanzable"
else
    echo "⚠️  Worker 02 ($WORKER_02_IP) no alcanzable"
fi

echo ""
echo "=================================================="
echo "🧠 SISTEMA ELÁSTICO V6 CON COLA DE TAREAS:"
echo "   1. Monitor de Workers (ping constante)"
echo "   2. Distribuidor de Tareas (automático)"
echo "   3. Almacenamiento de Resultados"
echo "   4. Recuperación de Fallos"
echo "=================================================="
echo ""

# Preguntar si continuar
read -p "¿Iniciar sistema elástico v6? (Y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Nn]$ ]]; then
    echo "👋 Cancelado por el usuario"
    exit 0
fi

# Limpiar logs anteriores si existen
if [ -f "logs/elastic_orchestrator.log" ]; then
    echo "🧹 Limpiando logs anteriores..."
    > logs/elastic_orchestrator.log
fi

# Configurar trap para limpieza
cleanup() {
    echo ""
    echo "🛑 Deteniendo sistema elástico v6..."
    if [ ! -z "$ORCHESTRATOR_PID" ]; then
        kill $ORCHESTRATOR_PID 2>/dev/null
    fi
    echo "💾 Resultados guardados en directorio: results/"
    exit 0
}
trap cleanup SIGINT SIGTERM

# Iniciar el orquestador elástico v6
echo "🎯 Iniciando orquestador elástico v6..."
python3 elastic_orchestrator_v6.py &
ORCHESTRATOR_PID=$!

echo "📊 PID del orquestador: $ORCHESTRATOR_PID"
echo "📋 Logs en: logs/elastic_orchestrator.log"
echo "💾 Resultados en: results/"
echo "🛑 Presiona Ctrl+C para detener"
echo ""

# Mostrar logs en tiempo real
echo "=================================================="
echo "📋 LOGS EN TIEMPO REAL:"
echo "=================================================="

# Esperar a que se cree el archivo de log
sleep 2

# Mostrar logs en tiempo real
tail -f logs/elastic_orchestrator.log 2>/dev/null &
TAIL_PID=$!

# Esperar a que termine el proceso principal
wait $ORCHESTRATOR_PID

# Limpiar proceso de tail
kill $TAIL_PID 2>/dev/null

echo ""
echo "✅ Sistema elástico v6 detenido"
