#!/usr/bin/env python3
"""
Script de inicio automático para ETAPA 6
Configura y ejecuta el sistema completo con carga automática de tareas
"""

import os
import sys
import time
import json
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_requirements():
    """Verificar que todos los archivos necesarios estén presentes"""
    required_files = [
        'elastic_orchestrator_v6.py',
        'auto_task_generator.py',
        'worker_service.py',
        'config_manager.py',
        '.env',
        'config_workers.json'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"❌ Archivos faltantes: {', '.join(missing_files)}")
        return False
    
    logger.info("✅ Todos los archivos requeridos están presentes")
    return True

def create_directories():
    """Crear directorios necesarios"""
    directories = [
        'logs',
        'results',
        'task_queues',
        'task_queues/processed'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"📁 Directorio creado/verificado: {directory}")

def setup_auto_task_system():
    """Configurar sistema de tareas automáticas"""
    logger.info("🔧 Configurando sistema de tareas automáticas...")
    
    # Verificar configuración de workers
    try:
        with open('config_workers.json', 'r') as f:
            config = json.load(f)
        
        workers = config.get('workers', [])
        if not workers:
            logger.warning("⚠️  No hay workers configurados en config_workers.json")
        else:
            logger.info(f"✅ {len(workers)} workers configurados")
            
    except Exception as e:
        logger.error(f"❌ Error leyendo configuración de workers: {e}")
        return False
    
    # Crear tareas iniciales
    try:
        from auto_task_generator import AutoTaskGenerator
        
        generator = AutoTaskGenerator()
        generator.create_startup_tasks()
        
        logger.info("✅ Tareas iniciales creadas")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creando tareas iniciales: {e}")
        return False

def start_orchestrator():
    """Iniciar el orquestador"""
    logger.info("🚀 Iniciando orquestador elástico v6...")
    
    try:
        from elastic_orchestrator_v6 import ElasticOrchestratorV6
        
        # Crear y iniciar orquestador
        orchestrator = ElasticOrchestratorV6()
        orchestrator.start()
        
        logger.info("✅ Orquestador iniciado exitosamente")
        return orchestrator
        
    except Exception as e:
        logger.error(f"❌ Error iniciando orquestador: {e}")
        return None

def print_system_info():
    """Mostrar información del sistema"""
    print("\n" + "="*70)
    print("🎭 SISTEMA DE ORQUESTACIÓN ELÁSTICO V6 - CARGA AUTOMÁTICA")
    print("="*70)
    print()
    print("🧠 MEMORIAS ACTIVAS:")
    print("   1. Monitor de Workers (ping constante)")
    print("   2. Monitor de Tareas (distribución automática)")
    print("   3. Cargador Automático de Tareas (cola automática)")
    print()
    print("🤖 FUNCIONALIDADES AUTOMÁTICAS:")
    print("   • Generación automática de tareas predeterminadas")
    print("   • Carga automática desde archivos de cola")
    print("   • Distribución inteligente de tareas")
    print("   • Recuperación automática de fallos")
    print("   • Monitoreo continuo de rendimiento")
    print()
    print("📁 DIRECTORIOS:")
    print("   • task_queues/        - Archivos de cola de tareas")
    print("   • task_queues/processed/ - Archivos procesados")
    print("   • results/            - Resultados de ejecución")
    print("   • logs/               - Logs del sistema")
    print("="*70)

def print_usage_instructions():
    """Mostrar instrucciones de uso"""
    print("\n📋 INSTRUCCIONES DE USO:")
    print("-" * 50)
    print("1. El sistema generará tareas automáticamente cada 30 segundos")
    print("2. Las tareas se cargan automáticamente desde task_queues/")
    print("3. Los workers distribuyen las tareas automáticamente")
    print("4. Los resultados se guardan en results/")
    print("5. Usa el menú interactivo para monitorear el sistema")
    print()
    print("🎛️  MENÚ INTERACTIVO:")
    print("   • Estado de workers - Ver workers activos/inactivos")
    print("   • Estado de tareas - Ver cola y estadísticas")
    print("   • Carga automática - Estadísticas del sistema automático")
    print("   • Agregar tareas - Agregar tareas manuales adicionales")
    print()
    print("💡 TIPS:")
    print("   • Las tareas se procesan automáticamente en orden de prioridad")
    print("   • Los archivos en task_queues/ se procesan automáticamente")
    print("   • El sistema se recupera automáticamente de fallos")
    print("   • Usa Ctrl+C para detener el sistema de forma segura")

def main():
    """Función principal"""
    print_system_info()
    
    # Verificar requisitos
    if not check_requirements():
        print("\n❌ Error: Faltan archivos requeridos")
        sys.exit(1)
    
    # Crear directorios
    create_directories()
    
    # Configurar sistema
    if not setup_auto_task_system():
        print("\n❌ Error: No se pudo configurar el sistema de tareas")
        sys.exit(1)
    
    # Iniciar orquestador
    orchestrator = start_orchestrator()
    if not orchestrator:
        print("\n❌ Error: No se pudo iniciar el orquestador")
        sys.exit(1)
    
    # Mostrar instrucciones
    print_usage_instructions()
    
    # Esperar un momento para que el sistema se estabilice
    print("\n🔄 Esperando que el sistema se estabilice...")
    time.sleep(5)
    
    # Mostrar estado inicial
    print("\n📊 ESTADO INICIAL DEL SISTEMA:")
    print("-" * 30)
    
    # Estado de workers
    worker_status = orchestrator.get_worker_status()
    active_workers = sum(1 for w in worker_status["workers"].values() if w["status"] == "active")
    print(f"Workers activos: {active_workers}/{len(worker_status['workers'])}")
    
    # Estado de tareas
    task_status = orchestrator.get_task_status()
    task_stats = task_status["statistics"]
    print(f"Tareas en cola: {task_stats['pending']}")
    print(f"Tareas completadas: {task_stats['completed']}")
    
    # Estado de carga automática
    auto_stats = orchestrator.get_auto_task_stats()
    print(f"Archivos procesados: {auto_stats['processed_files']}")
    print(f"Generación automática: {'Activa' if auto_stats['auto_generation_active'] else 'Inactiva'}")
    
    try:
        # Ejecutar bucle principal del orquestador
        print("\n🎯 Sistema iniciado exitosamente!")
        print("Presiona Ctrl+C para detener el sistema")
        print("=" * 70)
        
        # Llamar al main del orquestador (interfaz interactiva)
        from elastic_orchestrator_v6 import main as orchestrator_main
        orchestrator_main()
        
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo sistema...")
        orchestrator.stop()
        print("✅ Sistema detenido exitosamente")
    
    except Exception as e:
        logger.error(f"❌ Error en ejecución: {e}")
        orchestrator.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()
