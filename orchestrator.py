#!/usr/bin/env python3
"""
Orquestador de simulaciones distribuidas
Maneja múltiples workers y ejecuta tareas de simulación
"""

import json
import time
import requests
import threading
import logging
import yaml
from datetime import datetime
from flask import Flask, jsonify, request
from typing import Dict, List, Optional
import os

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/orchestrator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WorkerManager:
    def __init__(self):
        self.workers = {}
        self.worker_status = {}
        self.task_queue = []
        self.completed_tasks = []
        self.running_tasks = {}
        
    def register_worker(self, worker_id: str, host: str, port: int):
        """Registrar un nuevo worker"""
        self.workers[worker_id] = {
            'host': host,
            'port': port,
            'url': f'http://{host}:{port}',
            'last_ping': None,
            'status': 'unknown'
        }
        self.worker_status[worker_id] = 'offline'
        logger.info(f"Worker registrado: {worker_id} en {host}:{port}")

    def ping_worker(self, worker_id: str) -> bool:
        """Hacer ping a un worker específico"""
        if worker_id not in self.workers:
            return False
            
        worker = self.workers[worker_id]
        try:
            response = requests.get(
                f"{worker['url']}/ping", 
                timeout=5
            )
            if response.status_code == 200:
                self.workers[worker_id]['last_ping'] = datetime.now()
                self.worker_status[worker_id] = 'online'
                logger.debug(f"Worker {worker_id} respondió correctamente")
                return True
        except requests.exceptions.RequestException as e:
            logger.debug(f"Worker {worker_id} no responde: {e}")
        
        self.worker_status[worker_id] = 'offline'
        return False

    def ping_all_workers(self):
        """Hacer ping a todos los workers"""
        logger.info("Haciendo ping a todos los workers...")
        online_count = 0
        for worker_id in self.workers:
            if self.ping_worker(worker_id):
                online_count += 1
        
        logger.info(f"Workers online: {online_count}/{len(self.workers)}")
        return online_count

    def get_available_workers(self) -> List[str]:
        """Obtener lista de workers disponibles"""
        return [
            worker_id for worker_id, status in self.worker_status.items() 
            if status == 'online'
        ]

    def execute_task_on_worker(self, worker_id: str, task: Dict) -> Optional[Dict]:
        """Ejecutar una tarea en un worker específico"""
        if worker_id not in self.workers or self.worker_status[worker_id] != 'online':
            logger.error(f"Worker {worker_id} no está disponible")
            return None

        worker = self.workers[worker_id]
        try:
            logger.info(f"Ejecutando tarea en {worker_id}: {task}")
            
            response = requests.post(
                f"{worker['url']}/execute",
                json=task,
                timeout=300  # 5 minutos timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Tarea completada en {worker_id}")
                return result
            else:
                logger.error(f"Error en worker {worker_id}: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error ejecutando tarea en {worker_id}: {e}")
            return None

class TaskScheduler:
    def __init__(self, worker_manager: WorkerManager):
        self.worker_manager = worker_manager
        self.tasks = []
        self.load_tasks_from_config()
        
    def load_tasks_from_config(self):
        """Cargar tareas desde archivo de configuración"""
        try:
            with open('/app/configs/tasks.yaml', 'r') as f:
                config = yaml.safe_load(f)
                self.tasks = config.get('tasks', [])
            logger.info(f"Cargadas {len(self.tasks)} tareas desde configuración")
        except FileNotFoundError:
            logger.warning("Archivo de configuración no encontrado, usando tareas por defecto")
            self._create_default_tasks()
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            self._create_default_tasks()

    def _create_default_tasks(self):
        """Crear tareas por defecto si no hay configuración"""
        self.tasks = [
            {
                'id': 'task_1',
                'type': 'benchmark',
                'parameters': {
                    'num_particulas': 100,
                    'num_pasos': 1000,
                    'semilla': 42
                },
                'priority': 1
            },
            {
                'id': 'task_2',
                'type': 'benchmark_cython',
                'parameters': {
                    'num_particulas': 200,
                    'num_pasos': 2000,
                    'semilla': 123
                },
                'priority': 1
            },
            {
                'id': 'task_3',
                'type': 'benchmark',
                'parameters': {
                    'num_particulas': 500,
                    'num_pasos': 5000,
                    'semilla': 456
                },
                'priority': 2
            }
        ]

    def distribute_tasks(self):
        """Distribuir tareas entre workers disponibles"""
        available_workers = self.worker_manager.get_available_workers()
        
        if not available_workers:
            logger.warning("No hay workers disponibles")
            return
            
        logger.info(f"Distribuyendo {len(self.tasks)} tareas entre {len(available_workers)} workers")
        
        # Distribuir tareas de forma round-robin
        for i, task in enumerate(self.tasks):
            worker_id = available_workers[i % len(available_workers)]
            
            # Ejecutar tarea en thread separado
            thread = threading.Thread(
                target=self._execute_task_async,
                args=(worker_id, task)
            )
            thread.daemon = True
            thread.start()

    def _execute_task_async(self, worker_id: str, task: Dict):
        """Ejecutar tarea de forma asíncrona"""
        try:
            start_time = datetime.now()
            result = self.worker_manager.execute_task_on_worker(worker_id, task)
            end_time = datetime.now()
            
            if result:
                # Guardar resultado
                result_data = {
                    'task_id': task['id'],
                    'worker_id': worker_id,
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'duration': (end_time - start_time).total_seconds(),
                    'result': result
                }
                
                self._save_result(result_data)
                logger.info(f"Tarea {task['id']} completada exitosamente en {worker_id}")
            else:
                logger.error(f"Tarea {task['id']} falló en {worker_id}")
                
        except Exception as e:
            logger.error(f"Error ejecutando tarea {task['id']}: {e}")

    def _save_result(self, result_data: Dict):
        """Guardar resultado en archivo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/app/results/result_{result_data['task_id']}_{timestamp}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(result_data, f, indent=2)

# Instancias globales
worker_manager = WorkerManager()
task_scheduler = TaskScheduler(worker_manager)

# Flask app para API REST
app = Flask(__name__)

@app.route('/status')
def get_status():
    """Obtener estado del orquestador"""
    return jsonify({
        'workers': worker_manager.worker_status,
        'total_workers': len(worker_manager.workers),
        'online_workers': len(worker_manager.get_available_workers()),
        'tasks_total': len(task_scheduler.tasks)
    })

@app.route('/workers')
def get_workers():
    """Obtener información de workers"""
    return jsonify(worker_manager.workers)

@app.route('/ping_all')
def ping_all():
    """Hacer ping a todos los workers"""
    online_count = worker_manager.ping_all_workers()
    return jsonify({
        'online_workers': online_count,
        'total_workers': len(worker_manager.workers),
        'status': worker_manager.worker_status
    })

@app.route('/execute_tasks', methods=['POST'])
def execute_tasks():
    """Ejecutar todas las tareas"""
    try:
        task_scheduler.distribute_tasks()
        return jsonify({'message': 'Tareas iniciadas correctamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def periodic_health_check():
    """Verificación periódica de salud de workers"""
    while True:
        try:
            worker_manager.ping_all_workers()
            time.sleep(30)  # Ping cada 30 segundos
        except Exception as e:
            logger.error(f"Error en health check: {e}")
            time.sleep(60)

def main():
    """Función principal"""
    logger.info("Iniciando Orquestador de Simulaciones")
    
    # Obtener IPs de workers desde variables de entorno
    worker1_ip = os.getenv('WORKER1_IP', 'localhost')
    worker2_ip = os.getenv('WORKER2_IP', 'localhost')  
    worker3_ip = os.getenv('WORKER3_IP', 'localhost')
    
    logger.info(f"Configurando workers:")
    logger.info(f"  Worker 1: {worker1_ip}:8001")
    logger.info(f"  Worker 2: {worker2_ip}:8002")
    logger.info(f"  Worker 3: {worker3_ip}:8003")
    
    # Registrar workers
    worker_manager.register_worker('worker1', worker1_ip, 8001)
    worker_manager.register_worker('worker2', worker2_ip, 8002)
    worker_manager.register_worker('worker3', worker3_ip, 8003)
    
    # Iniciar thread de health check
    health_thread = threading.Thread(target=periodic_health_check)
    health_thread.daemon = True
    health_thread.start()
    
    # Esperar un poco para que los workers se inicien
    logger.info("Esperando que los workers se inicien...")
    time.sleep(10)
    
    # Hacer ping inicial
    worker_manager.ping_all_workers()
    
    # Iniciar servidor Flask
    logger.info("Iniciando servidor API en puerto 5000")
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    main()
