#!/usr/bin/env python3
"""
Generador manual de tareas para ETAPA 6
Crea archivos de tareas que deben colocarse manualmente en task_queues/
"""

import json
import uuid
import os
from datetime import datetime
from typing import Dict, List, Any
import argparse

def generate_basic_tasks() -> List[Dict[str, Any]]:
    """Generar tareas básicas de prueba"""
    tasks = []
    
    # Tareas básicas Python
    tasks.append({
        "task_id": f"manual_python_basic_{uuid.uuid4().hex[:8]}",
        "algorithm": "benchmark.py",
        "parameters": {
            "NUM_PARTICULAS": 100,
            "NUM_PASOS": 500,
            "SEMILLA": 42
        },
        "priority": 3,
        "description": "Tarea Python básica manual",
        "created_at": datetime.now().isoformat(),
        "status": "pending",
        "source": "manual_generator"
    })
    
    # Tareas básicas Cython
    tasks.append({
        "task_id": f"manual_cython_basic_{uuid.uuid4().hex[:8]}",
        "algorithm": "benchmark_cython.py",
        "parameters": {
            "NUM_PARTICULAS": 100,
            "NUM_PASOS": 500,
            "SEMILLA": 42
        },
        "priority": 5,
        "description": "Tarea Cython básica manual",
        "created_at": datetime.now().isoformat(),
        "status": "pending",
        "source": "manual_generator"
    })
    
    return tasks

def generate_performance_tasks() -> List[Dict[str, Any]]:
    """Generar tareas de prueba de rendimiento"""
    tasks = []
    
    # Configuraciones de prueba
    configs = [
        {"particles": 50, "steps": 200, "priority": 5, "desc": "Ligera"},
        {"particles": 200, "steps": 600, "priority": 3, "desc": "Media"},
        {"particles": 500, "steps": 1000, "priority": 1, "desc": "Pesada"}
    ]
    
    for config in configs:
        # Python
        tasks.append({
            "task_id": f"manual_python_{config['desc'].lower()}_{uuid.uuid4().hex[:8]}",
            "algorithm": "benchmark.py",
            "parameters": {
                "NUM_PARTICULAS": config["particles"],
                "NUM_PASOS": config["steps"],
                "SEMILLA": 123
            },
            "priority": config["priority"],
            "description": f"Prueba {config['desc']} Python manual",
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            "source": "manual_generator"
        })
        
        # Cython
        tasks.append({
            "task_id": f"manual_cython_{config['desc'].lower()}_{uuid.uuid4().hex[:8]}",
            "algorithm": "benchmark_cython.py",
            "parameters": {
                "NUM_PARTICULAS": config["particles"],
                "NUM_PASOS": config["steps"],
                "SEMILLA": 123
            },
            "priority": config["priority"] + 1,
            "description": f"Prueba {config['desc']} Cython manual",
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            "source": "manual_generator"
        })
    
    return tasks

def generate_stress_tasks(count: int = 10) -> List[Dict[str, Any]]:
    """Generar tareas de estrés"""
    tasks = []
    
    for i in range(count):
        algorithm = "benchmark.py" if i % 2 == 0 else "benchmark_cython.py"
        
        task = {
            "task_id": f"manual_stress_{i+1:02d}_{uuid.uuid4().hex[:8]}",
            "algorithm": algorithm,
            "parameters": {
                "NUM_PARTICULAS": 200 + (i * 20),
                "NUM_PASOS": 500 + (i * 50),
                "SEMILLA": 100 + i
            },
            "priority": 2,
            "description": f"Prueba de estrés manual #{i+1}",
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            "source": "manual_generator"
        }
        tasks.append(task)
    
    return tasks

def generate_custom_tasks(particles: int, steps: int, count: int = 5) -> List[Dict[str, Any]]:
    """Generar tareas personalizadas"""
    tasks = []
    
    for i in range(count):
        # Alternar algoritmos
        algorithm = "benchmark.py" if i % 2 == 0 else "benchmark_cython.py"
        
        # Variar parámetros ligeramente
        var_particles = particles + (i * 10)
        var_steps = steps + (i * 25)
        
        task = {
            "task_id": f"manual_custom_{i+1:02d}_{uuid.uuid4().hex[:8]}",
            "algorithm": algorithm,
            "parameters": {
                "NUM_PARTICULAS": var_particles,
                "NUM_PASOS": var_steps,
                "SEMILLA": 200 + i
            },
            "priority": 3,
            "description": f"Tarea personalizada manual #{i+1}",
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            "source": "manual_generator"
        }
        tasks.append(task)
    
    return tasks

def save_task_file(tasks: List[Dict[str, Any]], filename: str = None) -> str:
    """Guardar archivo de tareas"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"manual_tasks_{timestamp}.json"
    
    # Asegurar que termina en .json
    if not filename.endswith('.json'):
        filename += '.json'
    
    # Crear estructura del archivo
    task_file = {
        "generated_at": datetime.now().isoformat(),
        "task_count": len(tasks),
        "source": "manual_generator",
        "description": "Tareas generadas manualmente",
        "tasks": tasks
    }
    
    # Guardar archivo
    with open(filename, 'w') as f:
        json.dump(task_file, f, indent=2)
    
    return filename

def show_task_preview(tasks: List[Dict[str, Any]]):
    """Mostrar vista previa de tareas"""
    print(f"\n📋 VISTA PREVIA DE TAREAS ({len(tasks)} total):")
    print("=" * 60)
    
    for i, task in enumerate(tasks[:5]):  # Mostrar solo las primeras 5
        print(f"{i+1}. {task['task_id']}")
        print(f"   Algoritmo: {task['algorithm']}")
        print(f"   Partículas: {task['parameters']['NUM_PARTICULAS']}")
        print(f"   Pasos: {task['parameters']['NUM_PASOS']}")
        print(f"   Prioridad: {task['priority']}")
        print(f"   Descripción: {task['description']}")
        print()
    
    if len(tasks) > 5:
        print(f"   ... y {len(tasks) - 5} tareas más")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Generador manual de tareas para ETAPA 6')
    parser.add_argument('--type', choices=['basic', 'performance', 'stress', 'custom'], 
                       default='basic', help='Tipo de tareas a generar')
    parser.add_argument('--count', type=int, default=5, 
                       help='Número de tareas (para stress y custom)')
    parser.add_argument('--particles', type=int, default=300, 
                       help='Número de partículas (para custom)')
    parser.add_argument('--steps', type=int, default=800, 
                       help='Número de pasos (para custom)')
    parser.add_argument('--output', help='Nombre del archivo de salida')
    parser.add_argument('--preview', action='store_true', 
                       help='Solo mostrar vista previa, no guardar')
    
    args = parser.parse_args()
    
    print("📝 GENERADOR MANUAL DE TAREAS - ETAPA 6")
    print("=" * 50)
    
    # Generar tareas según tipo
    if args.type == 'basic':
        tasks = generate_basic_tasks()
        print("🔹 Generando tareas básicas (2 tareas)")
        
    elif args.type == 'performance':
        tasks = generate_performance_tasks()
        print("🔹 Generando tareas de rendimiento (6 tareas)")
        
    elif args.type == 'stress':
        tasks = generate_stress_tasks(args.count)
        print(f"🔹 Generando tareas de estrés ({args.count} tareas)")
        
    elif args.type == 'custom':
        tasks = generate_custom_tasks(args.particles, args.steps, args.count)
        print(f"🔹 Generando tareas personalizadas ({args.count} tareas)")
    
    # Mostrar vista previa
    show_task_preview(tasks)
    
    if args.preview:
        print("\n👁️  Vista previa completada (no se guardó archivo)")
        return
    
    # Guardar archivo
    filename = save_task_file(tasks, args.output)
    print(f"\n💾 Archivo guardado: {filename}")
    print(f"📁 Para usar: Copia {filename} a task_queues/")
    
    # Mostrar instrucciones
    print(f"\n📋 INSTRUCCIONES:")
    print(f"1. Copia el archivo a la carpeta task_queues/:")
    print(f"   cp {filename} task_queues/")
    print(f"2. El orquestador lo procesará automáticamente en ~10 segundos")
    print(f"3. El archivo se moverá a task_queues/processed/ después de procesarse")
    
    print(f"\n✅ Listo para usar!")

if __name__ == "__main__":
    main()
