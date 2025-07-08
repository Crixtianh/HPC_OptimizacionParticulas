#!/usr/bin/env python3
"""
Generador automático de tareas predeterminadas para ETAPA 6
Crea listas de tareas automáticamente sin intervención manual
"""

import json
import uuid
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import threading
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AutoTaskGenerator:
    """Generador automático de tareas predeterminadas"""
    
    def __init__(self, queue_dir: str = "task_queues"):
        self.queue_dir = queue_dir
        self.running = False
        self.generation_thread = None
        
        # Crear directorio de colas si no existe
        os.makedirs(self.queue_dir, exist_ok=True)
        
        # Configuraciones predeterminadas
        self.task_templates = self._load_task_templates()
        
        # Configuración de generación
        self.generation_interval = 30  # Generar nuevas tareas cada 30 segundos
        self.max_queue_size = 10  # Máximo número de tareas en cola
        
    def _load_task_templates(self) -> List[Dict[str, Any]]:
        """Cargar plantillas de tareas predeterminadas"""
        return [
            # Tareas de prueba básicas
            {
                "name": "test_basic_python",
                "algorithm": "benchmark.py",
                "parameters": {
                    "NUM_PARTICULAS": 100,
                    "NUM_PASOS": 500,
                    "SEMILLA": 42
                },
                "priority": 3,
                "description": "Prueba básica Python",
                "frequency": "high"  # Se genera frecuentemente
            },
            {
                "name": "test_basic_cython",
                "algorithm": "benchmark_cython.py",
                "parameters": {
                    "NUM_PARTICULAS": 100,
                    "NUM_PASOS": 500,
                    "SEMILLA": 42
                },
                "priority": 5,
                "description": "Prueba básica Cython",
                "frequency": "high"
            },
            
            # Tareas de carga media
            {
                "name": "test_medium_load",
                "algorithm": "benchmark.py",
                "parameters": {
                    "NUM_PARTICULAS": 250,
                    "NUM_PASOS": 750,
                    "SEMILLA": 123
                },
                "priority": 2,
                "description": "Prueba carga media",
                "frequency": "medium"
            },
            {
                "name": "test_medium_cython",
                "algorithm": "benchmark_cython.py",
                "parameters": {
                    "NUM_PARTICULAS": 250,
                    "NUM_PASOS": 750,
                    "SEMILLA": 123
                },
                "priority": 4,
                "description": "Prueba carga media Cython",
                "frequency": "medium"
            },
            
            # Tareas de carga pesada
            {
                "name": "test_heavy_load",
                "algorithm": "benchmark.py",
                "parameters": {
                    "NUM_PARTICULAS": 500,
                    "NUM_PASOS": 1000,
                    "SEMILLA": 456
                },
                "priority": 1,
                "description": "Prueba carga pesada",
                "frequency": "low"
            },
            {
                "name": "test_heavy_cython",
                "algorithm": "benchmark_cython.py",
                "parameters": {
                    "NUM_PARTICULAS": 500,
                    "NUM_PASOS": 1000,
                    "SEMILLA": 456
                },
                "priority": 3,
                "description": "Prueba carga pesada Cython",
                "frequency": "low"
            },
            
            # Tareas de estrés
            {
                "name": "stress_test",
                "algorithm": "benchmark.py",
                "parameters": {
                    "NUM_PARTICULAS": 1000,
                    "NUM_PASOS": 1500,
                    "SEMILLA": 789
                },
                "priority": 1,
                "description": "Prueba de estrés",
                "frequency": "very_low"
            },
            
            # Tareas de rendimiento comparativo
            {
                "name": "performance_comparison",
                "algorithm": "benchmark_cython.py",
                "parameters": {
                    "NUM_PARTICULAS": 300,
                    "NUM_PASOS": 800,
                    "SEMILLA": 999
                },
                "priority": 6,
                "description": "Comparación de rendimiento",
                "frequency": "medium"
            }
        ]
    
    def generate_task_from_template(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """Generar tarea desde plantilla"""
        # Agregar variación aleatoria a los parámetros
        import random
        
        # Crear copia de parámetros
        params = template["parameters"].copy()
        
        # Agregar variación pequeña para hacer cada tarea única
        if "NUM_PARTICULAS" in params:
            variation = random.randint(-10, 10)
            params["NUM_PARTICULAS"] = max(50, params["NUM_PARTICULAS"] + variation)
        
        if "NUM_PASOS" in params:
            variation = random.randint(-50, 50)
            params["NUM_PASOS"] = max(100, params["NUM_PASOS"] + variation)
        
        if "SEMILLA" in params:
            params["SEMILLA"] = random.randint(1, 10000)
        
        # Crear tarea
        task = {
            "task_id": f"{template['name']}_{uuid.uuid4().hex[:8]}",
            "algorithm": template["algorithm"],
            "parameters": params,
            "priority": template["priority"],
            "description": template["description"],
            "template_name": template["name"],
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            "source": "auto_generator"
        }
        
        return task
    
    def should_generate_task(self, template: Dict[str, Any]) -> bool:
        """Determinar si se debe generar una tarea basada en frecuencia"""
        import random
        
        frequency = template.get("frequency", "medium")
        
        # Probabilidades basadas en frecuencia
        probabilities = {
            "very_high": 0.8,
            "high": 0.6,
            "medium": 0.4,
            "low": 0.2,
            "very_low": 0.1
        }
        
        return random.random() < probabilities.get(frequency, 0.3)
    
    def generate_task_batch(self) -> List[Dict[str, Any]]:
        """Generar lote de tareas"""
        tasks = []
        
        for template in self.task_templates:
            if self.should_generate_task(template):
                task = self.generate_task_from_template(template)
                tasks.append(task)
        
        return tasks
    
    def save_task_queue(self, tasks: List[Dict[str, Any]]) -> str:
        """Guardar cola de tareas en archivo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"auto_tasks_{timestamp}.json"
        filepath = os.path.join(self.queue_dir, filename)
        
        queue_data = {
            "generated_at": datetime.now().isoformat(),
            "task_count": len(tasks),
            "source": "auto_generator",
            "tasks": tasks
        }
        
        with open(filepath, 'w') as f:
            json.dump(queue_data, f, indent=2)
        
        logger.info(f"📁 Cola de tareas guardada: {filename} ({len(tasks)} tareas)")
        return filepath
    
    def generate_performance_benchmark_tasks(self) -> List[Dict[str, Any]]:
        """Generar tareas específicas para benchmarking de rendimiento"""
        tasks = []
        
        # Configuraciones de prueba escalables
        test_configs = [
            {"particles": 50, "steps": 200, "priority": 5},
            {"particles": 100, "steps": 400, "priority": 4},
            {"particles": 200, "steps": 600, "priority": 3},
            {"particles": 400, "steps": 800, "priority": 2},
            {"particles": 800, "steps": 1000, "priority": 1}
        ]
        
        for i, config in enumerate(test_configs):
            # Tarea Python
            python_task = {
                "task_id": f"perf_python_{i+1}_{uuid.uuid4().hex[:6]}",
                "algorithm": "benchmark.py",
                "parameters": {
                    "NUM_PARTICULAS": config["particles"],
                    "NUM_PASOS": config["steps"],
                    "SEMILLA": 42 + i
                },
                "priority": config["priority"],
                "description": f"Benchmark Python - {config['particles']} partículas",
                "template_name": "performance_benchmark",
                "created_at": datetime.now().isoformat(),
                "status": "pending",
                "source": "auto_generator"
            }
            tasks.append(python_task)
            
            # Tarea Cython
            cython_task = {
                "task_id": f"perf_cython_{i+1}_{uuid.uuid4().hex[:6]}",
                "algorithm": "benchmark_cython.py",
                "parameters": {
                    "NUM_PARTICULAS": config["particles"],
                    "NUM_PASOS": config["steps"],
                    "SEMILLA": 42 + i
                },
                "priority": config["priority"] + 1,  # Prioridad ligeramente mayor
                "description": f"Benchmark Cython - {config['particles']} partículas",
                "template_name": "performance_benchmark",
                "created_at": datetime.now().isoformat(),
                "status": "pending",
                "source": "auto_generator"
            }
            tasks.append(cython_task)
        
        return tasks
    
    def start_auto_generation(self):
        """Iniciar generación automática de tareas"""
        if self.running:
            logger.warning("⚠️  El generador automático ya está en ejecución")
            return
        
        self.running = True
        self.generation_thread = threading.Thread(
            target=self._generation_loop,
            name="AutoTaskGenerator",
            daemon=True
        )
        self.generation_thread.start()
        
        logger.info("🚀 Generador automático de tareas iniciado")
    
    def stop_auto_generation(self):
        """Detener generación automática"""
        if not self.running:
            return
        
        self.running = False
        if self.generation_thread and self.generation_thread.is_alive():
            self.generation_thread.join(timeout=5)
        
        logger.info("🛑 Generador automático de tareas detenido")
    
    def _generation_loop(self):
        """Loop principal de generación automática"""
        logger.info("🔄 Iniciando loop de generación automática...")
        
        while self.running:
            try:
                # Verificar si hay suficientes tareas en cola
                pending_files = self.get_pending_task_files()
                total_pending_tasks = sum(self.count_tasks_in_file(f) for f in pending_files)
                
                if total_pending_tasks < self.max_queue_size:
                    # Generar nuevas tareas
                    tasks = self.generate_task_batch()
                    
                    if tasks:
                        filepath = self.save_task_queue(tasks)
                        logger.info(f"✅ Generadas {len(tasks)} tareas automáticamente")
                    else:
                        logger.debug("🔍 No se generaron tareas en este ciclo")
                else:
                    logger.debug(f"📋 Cola suficiente: {total_pending_tasks} tareas pendientes")
                
                # Esperar antes del próximo ciclo
                time.sleep(self.generation_interval)
                
            except Exception as e:
                logger.error(f"❌ Error en generación automática: {e}")
                time.sleep(5)
    
    def get_pending_task_files(self) -> List[str]:
        """Obtener archivos de tareas pendientes"""
        if not os.path.exists(self.queue_dir):
            return []
        
        files = []
        for filename in os.listdir(self.queue_dir):
            if filename.endswith('.json') and filename.startswith('auto_tasks_'):
                filepath = os.path.join(self.queue_dir, filename)
                files.append(filepath)
        
        return files
    
    def count_tasks_in_file(self, filepath: str) -> int:
        """Contar tareas en archivo"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            return len(data.get('tasks', []))
        except:
            return 0
    
    def create_startup_tasks(self):
        """Crear tareas de inicio inmediatamente"""
        logger.info("🎯 Creando tareas de inicio...")
        
        # Crear tareas básicas de inicio
        startup_tasks = []
        
        # Tareas de verificación
        startup_tasks.extend([
            {
                "task_id": f"startup_verify_python_{uuid.uuid4().hex[:6]}",
                "algorithm": "benchmark.py",
                "parameters": {
                    "NUM_PARTICULAS": 50,
                    "NUM_PASOS": 100,
                    "SEMILLA": 1
                },
                "priority": 10,
                "description": "Verificación inicial Python",
                "template_name": "startup_verification",
                "created_at": datetime.now().isoformat(),
                "status": "pending",
                "source": "auto_generator"
            },
            {
                "task_id": f"startup_verify_cython_{uuid.uuid4().hex[:6]}",
                "algorithm": "benchmark_cython.py",
                "parameters": {
                    "NUM_PARTICULAS": 50,
                    "NUM_PASOS": 100,
                    "SEMILLA": 1
                },
                "priority": 10,
                "description": "Verificación inicial Cython",
                "template_name": "startup_verification",
                "created_at": datetime.now().isoformat(),
                "status": "pending",
                "source": "auto_generator"
            }
        ])
        
        # Tareas de benchmarking inicial
        startup_tasks.extend(self.generate_performance_benchmark_tasks())
        
        # Guardar tareas de inicio
        filepath = self.save_task_queue(startup_tasks)
        logger.info(f"🎉 Tareas de inicio creadas: {len(startup_tasks)} tareas")
        
        return filepath

def main():
    """Función principal para pruebas"""
    generator = AutoTaskGenerator()
    
    print("🤖 GENERADOR AUTOMÁTICO DE TAREAS")
    print("=" * 50)
    
    # Crear tareas de inicio
    generator.create_startup_tasks()
    
    # Iniciar generación automática
    generator.start_auto_generation()
    
    try:
        print("🔄 Generación automática en progreso...")
        print("Presiona Ctrl+C para detener")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo generador...")
        generator.stop_auto_generation()
        print("✅ Generador detenido")

if __name__ == "__main__":
    main()
