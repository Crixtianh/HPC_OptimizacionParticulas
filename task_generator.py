#!/usr/bin/env python3
"""
Generador de tareas de prueba para ETAPA 6
Crea múltiples tareas con diferentes parámetros para probar el sistema
"""

import json
import time
from elastic_orchestrator_v6 import ElasticOrchestratorV6

def generate_test_tasks(orchestrator):
    """Generar tareas de prueba variadas"""
    
    test_scenarios = [
        # Tareas rápidas
        {
            "name": "Tareas Rápidas",
            "tasks": [
                {"algorithm": "benchmark.py", "params": {"NUM_PARTICULAS": 50, "NUM_PASOS": 250, "SEMILLA": 42}, "priority": 3},
                {"algorithm": "benchmark_cython.py", "params": {"NUM_PARTICULAS": 50, "NUM_PASOS": 250, "SEMILLA": 43}, "priority": 3},
                {"algorithm": "benchmark.py", "params": {"NUM_PARTICULAS": 75, "NUM_PASOS": 300, "SEMILLA": 44}, "priority": 3},
            ]
        },
        # Tareas medianas
        {
            "name": "Tareas Medianas",
            "tasks": [
                {"algorithm": "benchmark.py", "params": {"NUM_PARTICULAS": 100, "NUM_PASOS": 500, "SEMILLA": 45}, "priority": 2},
                {"algorithm": "benchmark_cython.py", "params": {"NUM_PARTICULAS": 100, "NUM_PASOS": 500, "SEMILLA": 46}, "priority": 2},
                {"algorithm": "benchmark.py", "params": {"NUM_PARTICULAS": 150, "NUM_PASOS": 600, "SEMILLA": 47}, "priority": 2},
                {"algorithm": "benchmark_cython.py", "params": {"NUM_PARTICULAS": 150, "NUM_PASOS": 600, "SEMILLA": 48}, "priority": 2},
            ]
        },
        # Tareas lentas
        {
            "name": "Tareas Lentas",
            "tasks": [
                {"algorithm": "benchmark.py", "params": {"NUM_PARTICULAS": 200, "NUM_PASOS": 800, "SEMILLA": 49}, "priority": 1},
                {"algorithm": "benchmark_cython.py", "params": {"NUM_PARTICULAS": 200, "NUM_PASOS": 800, "SEMILLA": 50}, "priority": 1},
                {"algorithm": "benchmark.py", "params": {"NUM_PARTICULAS": 250, "NUM_PASOS": 1000, "SEMILLA": 51}, "priority": 1},
            ]
        },
        # Tareas prioritarias
        {
            "name": "Tareas Prioritarias",
            "tasks": [
                {"algorithm": "benchmark_cython.py", "params": {"NUM_PARTICULAS": 80, "NUM_PASOS": 400, "SEMILLA": 52}, "priority": 5},
                {"algorithm": "benchmark.py", "params": {"NUM_PARTICULAS": 80, "NUM_PASOS": 400, "SEMILLA": 53}, "priority": 5},
            ]
        }
    ]
    
    print("🧪 GENERANDO TAREAS DE PRUEBA PARA ETAPA 6")
    print("=" * 60)
    
    task_ids = []
    
    for scenario in test_scenarios:
        print(f"\n📋 {scenario['name']}:")
        
        for i, task in enumerate(scenario['tasks']):
            task_id = orchestrator.add_task(
                task['algorithm'],
                task['params'],
                task['priority']
            )
            task_ids.append(task_id)
            
            print(f"   ✅ Tarea {i+1}: {task['algorithm']} - Prioridad {task['priority']}")
            print(f"      Parámetros: {task['params']}")
            print(f"      ID: {task_id[:8]}...")
            
            # Pequeña pausa para evitar saturar el sistema
            time.sleep(0.1)
    
    print(f"\n🎉 ¡{len(task_ids)} tareas generadas exitosamente!")
    print("📊 Las tareas se distribuirán automáticamente a los workers disponibles")
    
    return task_ids

def monitor_task_progress(orchestrator, task_ids, check_interval=5):
    """Monitorear progreso de las tareas"""
    print(f"\n🔍 MONITOREANDO PROGRESO DE TAREAS")
    print("=" * 60)
    print("⏳ Presiona Ctrl+C para detener el monitoreo")
    
    try:
        while True:
            task_status = orchestrator.get_task_status()
            stats = task_status['statistics']
            
            print(f"\n📊 Estado actual:")
            print(f"   Pendientes: {stats['pending']}")
            print(f"   Asignadas: {stats['assigned']}")
            print(f"   Ejecutando: {stats['running']}")
            print(f"   Completadas: {stats['completed']}")
            print(f"   Fallidas: {stats['failed']}")
            
            if stats['completed'] + stats['failed'] >= len(task_ids):
                print("\n🎉 ¡Todas las tareas han terminado!")
                break
            
            # Mostrar workers ocupados
            worker_status = orchestrator.get_worker_status()
            busy_workers = [w for w in worker_status['workers'].values() if w['current_task']]
            
            if busy_workers:
                print(f"\n🔄 Workers ocupados:")
                for worker in busy_workers:
                    print(f"   {worker['id']}: ejecutando {worker['current_task']}")
            
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        print("\n⏹️  Monitoreo detenido por el usuario")

def show_final_results(orchestrator, task_ids):
    """Mostrar resultados finales"""
    print(f"\n📈 RESULTADOS FINALES")
    print("=" * 60)
    
    # Estadísticas generales
    stats = orchestrator.get_statistics()
    print(f"⏱️  Tiempo total del sistema: {stats['uptime_formatted']}")
    print(f"📤 Tareas distribuidas: {stats['tasks_distributed']}")
    print(f"✅ Tareas completadas: {stats['tasks_completed']}")
    print(f"❌ Tareas fallidas: {stats['tasks_failed']}")
    print(f"📊 Tasa de éxito: {stats['task_completion_rate']:.1f}%")
    
    # Estadísticas de tareas
    task_stats = stats['task_statistics']
    print(f"\n⏱️  Estadísticas de tiempo:")
    print(f"   Tiempo promedio: {task_stats['avg_execution_time']:.2f}s")
    print(f"   Tiempo mínimo: {task_stats['min_execution_time']:.2f}s")
    print(f"   Tiempo máximo: {task_stats['max_execution_time']:.2f}s")
    
    # Estadísticas por worker
    worker_status = orchestrator.get_worker_status()
    print(f"\n👥 Estadísticas por worker:")
    
    for worker_id, worker_data in worker_status['workers'].items():
        print(f"   {worker_id}:")
        print(f"      Tareas completadas: {worker_data['total_tasks_completed']}")
        print(f"      Tiempo promedio: {worker_data['average_task_time']:.2f}s")
        print(f"      Tasa de éxito: {worker_data['success_rate']:.1%}")
        print(f"      Score de carga: {worker_data['load_score']:.2f}")

def main():
    """Función principal"""
    print("🧪 GENERADOR DE TAREAS DE PRUEBA - ETAPA 6")
    print("=" * 60)
    
    # Crear orquestador
    orchestrator = ElasticOrchestratorV6()
    
    # Verificar que el orquestador esté funcionando
    print("🔍 Verificando sistema...")
    worker_status = orchestrator.get_worker_status()
    available_workers = worker_status['summary']['available_workers']
    
    if available_workers == 0:
        print("❌ No hay workers disponibles. Asegúrate de que:")
        print("   1. El orquestador elástico esté ejecutándose")
        print("   2. Los workers estén conectados y activos")
        return
    
    print(f"✅ {available_workers} workers disponibles")
    
    # Menú de opciones
    while True:
        print("\n🎛️  OPCIONES DE PRUEBA:")
        print("1. Generar conjunto completo de tareas de prueba")
        print("2. Generar tareas rápidas (5 tareas)")
        print("3. Generar tareas variadas (10 tareas)")
        print("4. Generar tareas de estrés (20 tareas)")
        print("5. Monitorear tareas en progreso")
        print("6. Mostrar estadísticas actuales")
        print("7. Salir")
        
        choice = input("\nSelecciona una opción (1-7): ").strip()
        
        if choice == "1":
            task_ids = generate_test_tasks(orchestrator)
            print("\n¿Monitorear progreso automáticamente? (y/N):")
            if input().lower().startswith('y'):
                monitor_task_progress(orchestrator, task_ids)
                show_final_results(orchestrator, task_ids)
                
        elif choice == "2":
            print("\n🚀 Generando 5 tareas rápidas...")
            task_ids = []
            for i in range(5):
                task_id = orchestrator.add_task(
                    "benchmark.py",
                    {"NUM_PARTICULAS": 50, "NUM_PASOS": 200, "SEMILLA": 42 + i},
                    3
                )
                task_ids.append(task_id)
                print(f"   ✅ Tarea {i+1}: {task_id[:8]}...")
            print(f"🎉 {len(task_ids)} tareas rápidas generadas")
            
        elif choice == "3":
            print("\n📊 Generando 10 tareas variadas...")
            task_ids = []
            algorithms = ["benchmark.py", "benchmark_cython.py"]
            
            for i in range(10):
                algorithm = algorithms[i % 2]
                task_id = orchestrator.add_task(
                    algorithm,
                    {
                        "NUM_PARTICULAS": 100 + (i * 20),
                        "NUM_PASOS": 400 + (i * 50),
                        "SEMILLA": 42 + i
                    },
                    2
                )
                task_ids.append(task_id)
                print(f"   ✅ Tarea {i+1}: {algorithm} - {task_id[:8]}...")
            print(f"🎉 {len(task_ids)} tareas variadas generadas")
            
        elif choice == "4":
            print("\n💪 Generando 20 tareas de estrés...")
            task_ids = []
            algorithms = ["benchmark.py", "benchmark_cython.py"]
            
            for i in range(20):
                algorithm = algorithms[i % 2]
                task_id = orchestrator.add_task(
                    algorithm,
                    {
                        "NUM_PARTICULAS": 150 + (i * 10),
                        "NUM_PASOS": 500 + (i * 25),
                        "SEMILLA": 42 + i
                    },
                    1 + (i % 3)  # Prioridades variables
                )
                task_ids.append(task_id)
                if (i + 1) % 5 == 0:
                    print(f"   ✅ {i+1}/20 tareas generadas...")
            print(f"🎉 {len(task_ids)} tareas de estrés generadas")
            
        elif choice == "5":
            task_status = orchestrator.get_task_status()
            all_tasks = [t['id'] for t in task_status['tasks']]
            if all_tasks:
                monitor_task_progress(orchestrator, all_tasks)
            else:
                print("❌ No hay tareas para monitorear")
                
        elif choice == "6":
            show_final_results(orchestrator, [])
            
        elif choice == "7":
            print("👋 Saliendo del generador de tareas...")
            break
            
        else:
            print("❌ Opción inválida")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Generador detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
